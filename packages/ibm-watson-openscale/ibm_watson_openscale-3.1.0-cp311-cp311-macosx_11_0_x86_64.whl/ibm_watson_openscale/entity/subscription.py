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

from typing import TYPE_CHECKING, List, Optional

from ibm_watson_openscale.utils import validate_enum

try:
    from ibm_metrics_plugin.common.utils.constants import (AssetType,
                                                           InputDataType,
                                                           ProblemType)
    from ibm_metrics_plugin.common.utils.python_utils import get
except ImportError:
    pass

if TYPE_CHECKING:
    from ibm_watson_openscale.client import WatsonOpenScaleV2Adapter


class Subscription:

    def __init__(self, client: "WatsonOpenScaleV2Adapter",
                 subscription_id: str,
                 project_id: Optional[str] = None,
                 space_id: Optional[str] = None) -> None:
        """
        Initialize the subscription object

        Args:
            client (WatsonOpenScaleV2Adapter): The watson openscale client
            subscription_id (str): The subscription id
            project_id (str, optional): The project id. Defaults to None.
            space_id (str, optional): The space id. Defaults to None.
        """
        self.client = client
        self.id = subscription_id
        self.project_id = project_id
        self.space_id = space_id

        self.entity = self.client.subscriptions.get(subscription_id=self.id, project_id=self.project_id,
                                                    space_id=self.space_id).result.entity.to_dict()

        self.__asset_type = None
        self.__problem_type = None
        self.__input_data_type = None
        self.__record_id_column = None
        self.__record_timestamp_column = None
        self.__feature_columns = None
        self.__categorical_columns = None
        self.__meta_columns = None

        self.__prediction_column = None
        self.__prediction_probability_column = None
        self.__input_token_count_column = None
        self.__output_token_count_column = None

        self.__context_columns = None
        self.__question_column = None

    @property
    def asset_type(self) -> str:
        """
        Returns the asset type of the subscription

        Returns:
            str: The asset type
        """
        if self.__asset_type is None:
            self.__asset_type = get(self.entity, "asset.asset_type")
            validate_enum(
                self.__asset_type, f"'asset_type' in subscription {self.id}", AssetType)

        return self.__asset_type

    @property
    def problem_type(self) -> str:
        """
        Returns the problem type of the subscription

        Returns:
            str: The problem type
        """
        if self.__problem_type is None:
            self.__problem_type = get(self.entity, "asset.problem_type")
            validate_enum(
                self.__problem_type, f"'problem_type' in subscription {self.id}", ProblemType)

        return self.__problem_type

    @property
    def input_data_type(self) -> str:
        """
        Returns the input data type of the subscription

        Returns:
            str: The input data type
        """
        if self.__input_data_type is None:
            self.__input_data_type = get(self.entity, "asset.input_data_type")
            validate_enum(
                self.__input_data_type, f"'input_data_type' in subscription {self.id}", InputDataType)

        return self.__input_data_type

    @property
    def record_id_column(self) -> str:
        """
        Returns the record id column from the output data schema of the subscription 

        Returns:
            str: The record id column
        """
        if self.__record_id_column is None:
            self.__record_id_column = self.__get_column_with_modeling_role(
                role="record-id")
        return self.__record_id_column

    @property
    def record_timestamp_column(self) -> str:
        """
        Returns the record timestamp column from the output data schema of the subscription 

        Returns:
            str: The record timestamp column
        """
        if self.__record_timestamp_column is None:
            self.__record_timestamp_column = self.__get_column_with_modeling_role(
                role="record-timestamp")
        return self.__record_timestamp_column

    @property
    def meta_columns(self):
        """
        Returns the meta columns from the output data schema of the subscription.
        Does not include the openscale generated columns.

        Returns:
            str: The meta columns
        """
        if self.__meta_columns is None:
            self.__meta_columns = [field.get("name") for field in
                                   get(self.entity,
                                       "asset_properties.output_data_schema.fields", [])
                                   if not get(field, "metadata.deleted") and
                                   get(field, "metadata.modeling_role") == "meta-field" and
                                   get(field, "metadata.measure") != "wos-generated"]
        return self.__meta_columns

    @property
    def feature_columns(self) -> List[str]:
        """
        Returns the list of feature columns specified in the subscription's asset properties.

        Returns:
            List[str]: The feature columns
        """
        if self.__feature_columns is None:
            self.__feature_columns = get(
                self.entity, "asset_properties.feature_fields", [])
        return self.__feature_columns

    @property
    def categorical_columns(self) -> List[str]:
        """
        Returns the list of categorical columns specified in the subscription's asset properties.

        Returns:
            List[str]: The categorical columns
        """
        if self.__categorical_columns is None:
            self.__categorical_columns = get(
                self.entity, "asset_properties.categorical_fields", [])
        return self.__categorical_columns

    @property
    def context_columns(self) -> List[str]:
        """
        Returns the list of context columns specified in the subscription's asset properties.

        Returns:
            List[str]: The context columns
        """
        if self.__context_columns is None:
            self.__context_columns = get(
                self.entity, "asset_properties.context_fields", [])
        return self.__context_columns

    @property
    def prediction_column(self) -> str:
        """
        Returns the prediction column specified in the subscription's asset properties.

        Returns:
            str: The prediction column
        """
        if self.__prediction_column is None:
            self.__prediction_column = get(
                self.entity, "asset_properties.prediction_field")
        return self.__prediction_column

    @property
    def question_column(self) -> str:
        """
        Returns the question column specified in the subscription's asset properties.

        Returns:
            str: The question column
        """
        if self.__question_column is None:
            self.__question_column = get(
                self.entity, "asset_properties.question_field")
        return self.__question_column

    @property
    def prediction_probability_column(self) -> Optional[str]:
        """
        Returns the prediction probability column from the output data schema of the subscription 

        Returns:
            str: The prediction probability column
        """
        if self.__prediction_probability_column is None:
            self.__prediction_probability_column = self.__get_column_with_modeling_role(
                role="prediction-probability")
        return self.__prediction_probability_column

    @property
    def input_token_count_column(self) -> Optional[str]:
        """
        Returns the input token count column from the output data schema of the subscription 

        Returns:
            str: The input token count column
        """
        if self.__input_token_count_column is None:
            self.__input_token_count_column = self.__get_column_with_modeling_role_and_measure(
                role="meta-field", measure="input-token-count")
        return self.__input_token_count_column

    @property
    def output_token_count_column(self) -> Optional[str]:
        """
        Returns the output token column from the output data schema of the subscription 

        Returns:
            str: The output token column
        """
        if self.__output_token_count_column is None:
            self.__output_token_count_column = self.__get_column_with_modeling_role_and_measure(
                role="meta-field", measure="output-token-count")
        return self.__output_token_count_column

    def __get_column_with_modeling_role(self, role: str) -> str | None:
        """
        Returns the column with the specified modeling role from the output data schema of the subscription.
        If no such column found, it returns None

        Args:
            role (str): The modeling role

        Returns:
            str | None: The column, if found.
        """
        columns = [field.get("name") for field in
                   get(self.entity,
                       "asset_properties.output_data_schema.fields", [])
                   if not get(field, "metadata.deleted") and
                   get(field, "metadata.modeling_role") == role]
        if len(columns):
            return columns[0]

    def __get_column_with_modeling_role_and_measure(self, role: str, measure: str) -> str | None:
        """
        Returns the column with the specified modeling role from the output data schema of the subscription.
        If no such column found, it returns None

        Args:
            role (str): The modeling role
            measure (str): The measure

        Returns:
            str | None: The column, if found.
        """
        columns = [field.get("name") for field in
                   get(self.entity,
                       "asset_properties.output_data_schema.fields", [])
                   if not get(field, "metadata.deleted") and
                   (get(field, "metadata.modeling_role") == role) and
                   (get(field, "metadata.measure") == measure)]
        if len(columns):
            return columns[0]
