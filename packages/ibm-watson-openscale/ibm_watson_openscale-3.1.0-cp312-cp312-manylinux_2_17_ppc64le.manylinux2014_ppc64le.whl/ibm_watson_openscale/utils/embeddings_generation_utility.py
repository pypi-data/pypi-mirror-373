# coding: utf-8

# Copyright 2024 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from datetime import datetime
from time import sleep
from typing import TYPE_CHECKING, Dict

import pandas as pd
from ibm_cloud_sdk_core import BaseService
from tqdm.auto import tqdm

from ibm_watson_openscale.entity.subscription import Subscription
from ibm_watson_openscale.utils import (StatusStateType,
                                        validate_columns_in_dataframe,
                                        validate_pandas_dataframe,
                                        replace_nulls_in_columns,
                                        validate_type)
from ibm_watson_openscale.utils.request_utils import (patch_payload_splitter,
                                                      request_payload_splitter)

if TYPE_CHECKING:
    from ibm_watson_openscale.client import WatsonOpenScaleV2Adapter


class EmbeddingsGenerationUtility():

    def __init__(self, client: "WatsonOpenScaleV2Adapter",
                 subscription_id: str, data_set_type: str = "payload_logging",
                 project_id: str = None, space_id: str = None) -> None:
        validate_type(client, "client", BaseService, True)
        self.client = client
        self.subscription_id = subscription_id
        self.data_set_type = data_set_type
        self.project_id = project_id
        self.space_id = space_id

        self.subscription = Subscription(client=self.client,
                                         subscription_id=self.subscription_id,
                                         project_id=self.project_id,
                                         space_id=self.space_id)

        self.__initialize()

    def __initialize(self):

        data_sets = self.client.data_sets.list(type=self.data_set_type, target_target_type="subscription",
                                               target_target_id=self.subscription_id, project_id=self.project_id,
                                               space_id=self.space_id).result.data_sets
        if len(data_sets) != 1:
            raise ValueError(
                f"There are {len(data_sets)} datasets of type '{self.data_set_type}' in subscription '{self.subscription_id}'.")

        self.data_set_id = data_sets[0].metadata.id

    def __get_configuration(self) -> Dict:

        configuration = {
            "configuration": {
                "asset_type": self.subscription.asset_type,
                "problem_type": self.subscription.problem_type,
                "input_data_type": self.subscription.input_data_type,
                "feature_columns": self.subscription.feature_columns,
                "categorical_columns": self.subscription.categorical_columns,
                "prediction_column": self.subscription.prediction_column,
                "meta_columns": self.subscription.meta_columns,
                "record_id_column": self.subscription.record_id_column,
                "drift_v2": {
                    "metrics_configuration": {
                        "advanced_controls": {
                            "enable_embedding_drift": True
                        }
                    }
                }
            }
        }

        from ibm_metrics_plugin.common.utils.constants import ProblemType
        if self.subscription.problem_type == ProblemType.RAG.value:
            configuration["configuration"]["context_columns"] = self.subscription.context_columns
            configuration["configuration"]["question_column"] = self.subscription.question_column

        return configuration

    def __check_request_status(self, request_id: str, request_name: str):

        details = self.client.data_sets.get_update_status(
            data_set_id=self.data_set_id, request_id=request_id)
        state = details.result.state

        while state not in (StatusStateType.ACTIVE, StatusStateType.ERROR):
            sleep(5)
            details = self.client.data_sets.get_update_status(
                data_set_id=self.data_set_id, request_id=request_id)
            state = details.result.state

        if state is StatusStateType.ERROR:
            raise Exception(
                f"{request_name} in data set {self.data_set_id} with request {request_id} failed with reason: {details.result.failure}")

    def compute_and_store_embeddings(self, scored_data=None, start: datetime = None,
                                     end: datetime = None, limit: int = 1000, force: bool = False,
                                     embeddings_fn: callable = None, data_set_chunk_size: int = 100,
                                     embeddings_chunk_size: int = 100, **kwargs):
        """
        Computes and stores embeddings

        Args:
            scored_data (pd.DataFrame, optional): The input dataframe. Defaults to None.
            start (datetime, optional): Start timestamp to fetch records. Defaults to None.
            end (datetime, optional): End timestamp to fetch records. Defaults to None.
            limit (int, optional): Limit on number of records to fetch. Defaults to 1000.
            force (bool, optional): Force generate embeddings for existing records. Defaults to False.
            embeddings_fn (callable, optional): The embedding function. Defaults to None.
            data_set_chunk_size (int, optional): The chunk size to fetch records from data set. Defaults to 100.
            embeddings_chunk_size (int, optional): The chunk size to generate embeddings in one call. Defaults to 100.
        """

        # 1. Check if scored_data is none or not.
        if scored_data is None:
            scored_data = self.read_data(start=start, end=end, limit=limit,
                                        force=force, data_set_chunk_size=data_set_chunk_size, **kwargs)
        else:
            validate_pandas_dataframe(scored_data, "scored data", mandatory=True)
            # Handle null values in the DataFrame. 
            columns_list = scored_data.columns.tolist() 
            scored_data = replace_nulls_in_columns(scored_data, columns_list)
            # Store the records with nulls handled
            scored_data = self.store_records(scored_data)

        # 2. Generate local embeddings
        from ibm_metrics_plugin.common.utils.embeddings_utils import \
            compute_embeddings
        scored_data = compute_embeddings(configuration=self.__get_configuration(),
                                         data=scored_data, embeddings_fn=embeddings_fn,
                                         embeddings_chunk_size=embeddings_chunk_size, **kwargs)

        self.store_embeddings(scored_data)
        return scored_data

    def read_data(self, start: datetime = None, end: datetime = None, limit: int = 1000,
                  force: bool = False, data_set_chunk_size: int = 100, **kwargs) -> pd.DataFrame:
        """
        Reads the dataset records and returns a dataframe

        1. If start, end, limit are provided:
          - start is provided, but end is not. Use current utc timestamp as end
          - If force = False, fetch records between timestamps where embeddings are not present.
          - If force = True, fetch all records between timestamps.
        2. If start, end are not provided:
          - If force = False, fetch all records where embeddings are not present.
          - If force = True, fetch all records.

        Args:
            start (datetime, optional): Start timestamp to fetch records. Defaults to None.
            end (datetime, optional): End timestamp to fetch records. Defaults to None.
            limit (int, optional): Limit on number of records to fetch. Defaults to 1000.
            force (bool, optional): If true, reads records which already have embeddings too. Defaults to False.
            data_set_chunk_size (int, optional): The chunk size to fetch records from data set. Defaults to 100.

        Raises:
            ValueError: If no records matching the criteria are found

        Returns:
            pd.DataFrame: The dataset records
        """

        filter_ = None
        if not force:
            filter_ = "wos_embeddings_status__:in:null;unknown;preparing"

        order = f"{self.subscription.record_timestamp_column}:desc"

        includes = self.subscription.feature_columns + \
            [self.subscription.record_id_column,
                self.subscription.prediction_column]
        if self.subscription.meta_columns:
            includes += self.subscription.meta_columns

        if self.subscription.prediction_probability_column:
            includes.append(self.subscription.prediction_probability_column)

        if self.subscription.input_token_count_column:
            includes.append(self.subscription.input_token_count_column)

        if self.subscription.output_token_count_column:
            includes.append(self.subscription.output_token_count_column)

        includes = list(set(includes))
        includes = ",".join(includes)
        exclude_annotations = True

        offset = 0
        records_dfs = []

        if start:
            start = start.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if end:
            end = end.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        total_count = self.client.data_sets.get_list_of_records(data_set_id=self.data_set_id,
                                                                start=start, end=end, limit=0,
                                                                include_total_count=True,
                                                                filter=filter_, project_id=self.project_id,
                                                                space_id=self.space_id).result["total_count"]

        if not total_count:
            raise ValueError(
                f"No records found matching the criteria in '{self.data_set_type}' table of {self.subscription_id} subscription for embeddings generation.")

        t = tqdm(total=min(total_count, limit), unit="records",
                 desc=f"Reading {self.data_set_type} records... ")
        while offset < limit:
            response = self.client.data_sets.get_list_of_records(data_set_id=self.data_set_id,
                                                                 start=start, end=end, offset=offset,
                                                                 limit=data_set_chunk_size, includes=includes,
                                                                 exclude_annotations=exclude_annotations,
                                                                 output_type="pandas", order=order,
                                                                 filter=filter_, project_id=self.project_id,
                                                                 space_id=self.space_id)
            offset += data_set_chunk_size
            records_dfs.append(response.result)
            t.update(len(response.result))
        t.close()

        return pd.concat(records_dfs, axis=0).reset_index(drop=True)

    def store_embeddings(self, scored_data: pd.DataFrame, **kwargs):
        """
        Stores embeddings

        Args:
            scored_data (pd.DataFrame): The dataframe with embedding columns
        """
        idx = 0
        t = tqdm(total=len(scored_data), unit="records",
                 desc="Storing embeddings... ")
        configuration = self.__get_configuration()
        for annotation_documents, status_documents in patch_payload_splitter(configuration, scored_data):
            # 1. Patch embeddings as annotations
            dataset_response = self.client.data_sets.patch_records(
                data_set_id=self.data_set_id, patch_document=annotation_documents, project_id=self.project_id, space_id=self.space_id)

            # 2. Confirm status
            request_id = dataset_response.headers._store["location"][1].split(
                "/")[-1]
            self.__check_request_status(
                request_id=request_id, request_name="Storing embeddings")

            # 3. Patch wos_embeddings_status__
            dataset_response = self.client.data_sets.patch_records(
                data_set_id=self.data_set_id, patch_document=status_documents, project_id=self.project_id, space_id=self.space_id)

            # 4. Confirm status
            request_id = dataset_response.headers._store["location"][1].split(
                "/")[-1]
            self.__check_request_status(
                request_id=request_id, request_name="Updating embeddings status")

            idx = idx + len(status_documents)
            t.update(len(status_documents))
        t.close()

    def store_records(self, scored_data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Stores records in dataset table.

        Args:
            scored_data (pd.DataFrame): The input data

        Returns:
            pd.DataFrame: The dataframe with record id column added.
        """
        validate_columns_in_dataframe(
            scored_data, "scored_data", self.subscription.feature_columns)
        scored_data.reset_index(drop=True)

        meta_columns = []
        if self.subscription.meta_columns is not None:
            meta_columns = [
                column for column in self.subscription.meta_columns if column in scored_data]
            missing_columns = [
                column for column in self.subscription.meta_columns if column not in scored_data]
            if missing_columns:
                missing_columns = ", ".join(missing_columns)
                message = f"The columns '{missing_columns}' are present in the subscription as meta columns. "
                message += f"But they are not present in the scored data."
                print(message)

        validate_columns_in_dataframe(scored_data, "scored_data", [
                                      self.subscription.prediction_column])
        output_columns = [self.subscription.prediction_column]
        if self.subscription.prediction_probability_column and self.subscription.prediction_probability_column in scored_data:
            output_columns.append(
                self.subscription.prediction_probability_column)
        if self.subscription.input_token_count_column and self.subscription.input_token_count_column in scored_data:
            output_columns.append(self.subscription.input_token_count_column)
        if self.subscription.output_token_count_column and self.subscription.output_token_count_column in scored_data:
            output_columns.append(self.subscription.output_token_count_column)

        idx = 0
        scored_data[self.subscription.record_id_column] = None
        t = tqdm(total=len(scored_data), unit="records",
                 desc="Storing records... ")
        for pl_record, count in request_payload_splitter(scored_data, self.subscription.feature_columns, output_columns, meta_columns):
            dataset_response = self.client.data_sets.store_records(data_set_id=self.data_set_id, request_body=[
                                                                   pl_record], project_id=self.project_id, space_id=self.space_id, background_mode=True)
            request_id = dataset_response.headers._store["location"][1].split(
                "/")[-1]
            self.__check_request_status(
                request_id=request_id, request_name="Storing records")
            scored_data[self.subscription.record_id_column].iloc[idx:idx +
                                                                 count] = [f"{pl_record.scoring_id}-{i+1}" for i in range(count)]
            idx = idx + count
            t.update(count)
        t.close()

        return scored_data
