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


from copy import deepcopy
from datetime import timedelta
from time import sleep, time
from typing import TYPE_CHECKING, List, Optional

import pandas as pd
from ibm_cloud_sdk_core import BaseService
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
    MetricThresholdOverride, PatchDocument, Target)
from ibm_watson_openscale.entity.drift_v2_monitor_instance import \
    DriftV2MonitorInstance
from ibm_watson_openscale.entity.subscription import Subscription
from ibm_watson_openscale.supporting_classes.enums import StatusStateType
from ibm_watson_openscale.utils.configuration_utility import \
    ConfigurationUtilityLLM
from ibm_watson_openscale.utils.utils import (get,
                                              validate_columns_in_dataframe,
                                              validate_pandas_dataframe,
                                              validate_type)

if TYPE_CHECKING:
    from ibm_watson_openscale.client import WatsonOpenScaleV2Adapter


class DriftV2Utility():

    BASELINE_MAX_SAMPLES = 100
    RUNTIME_MIN_SAMPLES = 10

    def __init__(self, client: "WatsonOpenScaleV2Adapter",
                 subscription_id: str,
                 project_id: str = None, space_id: str = None) -> None:
        validate_type(client, "client", BaseService, True)
        self.client = client
        self.subscription_id = subscription_id
        self.project_id = project_id
        self.space_id = space_id

        self.subscription = Subscription(client=self.client,
                                         subscription_id=self.subscription_id,
                                         project_id=self.project_id,
                                         space_id=self.space_id)

        from ibm_metrics_plugin.common.utils.constants import AssetType
        if self.subscription.asset_type != AssetType.PROMPT.value:
            raise ValueError(
                "This utility only supports Drift v2 configuration and evaluation for Prompt subscriptions.")

        self.monitor_instance = DriftV2MonitorInstance(client=self.client,
                                                       subscription_id=self.subscription_id,
                                                       project_id=self.project_id,
                                                       space_id=self.space_id)

    def configure(self, scored_data: pd.DataFrame,
                  data_mart_id: Optional[str] = None,
                  baseline_max_samples: Optional[int] = None,
                  min_samples: Optional[int] = None,
                  max_samples: Optional[int] = None,
                  thresholds: Optional[List[MetricThresholdOverride]] = None,
                  update_metadata_only: bool = False,
                  embeddings_fn: callable = None,
                  **kwargs):

        if self.monitor_instance.is_configured:
            self.__print_message()

        validate_pandas_dataframe(
            scored_data, "scored data", mandatory=True)
        validate_columns_in_dataframe(
            scored_data, "scored data", self.subscription.feature_columns)

        meta_columns = []
        if self.subscription.meta_columns is not None:
            meta_columns = [
                column for column in self.subscription.meta_columns if column in scored_data]
            missing_columns = [
                column for column in self.subscription.meta_columns if column not in scored_data]
            if missing_columns:
                missing_columns = ", ".join(missing_columns)
                message = f"The columns '{missing_columns}' are present in the subscription as meta columns. "
                message += f"But they are not present in the scored data. Drift v2 metrics will not be computed on them."
                print(message)

        validate_columns_in_dataframe(scored_data, "scored data", [
                                      self.subscription.prediction_column])

        if data_mart_id is None:
            data_mart_id = self.client.service_instance_id

        if baseline_max_samples is None:
            baseline_max_samples = self.monitor_instance.baseline_max_samples

        if len(scored_data) < baseline_max_samples:
            raise ValueError(
                f"The size of training data '{len(scored_data)}' is smaller than baseline max samples '{baseline_max_samples}'.")

        common_parameters = {
            "asset_type": self.subscription.asset_type,
            "input_data_type": self.subscription.input_data_type,
            "problem_type": self.subscription.problem_type,
            "prompt_variable_columns": self.subscription.feature_columns,
            "meta_columns": meta_columns,
            "prediction_column": self.subscription.prediction_column,
            "prediction_probability_column": self.subscription.prediction_probability_column
        }

        if self.subscription.input_token_count_column in scored_data:
            common_parameters["input_token_count_column"] = self.subscription.input_token_count_column
        else:
            print(f"'{self.subscription.input_token_count_column}' column not present in scored data provided. The input metadata drift metric on the column will not be computed.")

        if self.subscription.output_token_count_column in scored_data:
            common_parameters["output_token_count_column"] = self.subscription.output_token_count_column
        else:
            print(f"'{self.subscription.output_token_count_column}' column not present in scored data provided. The output metadata drift metric on the column will not be computed.")

        if self.subscription.prediction_probability_column not in scored_data:
            print(f"'{self.subscription.prediction_probability_column}' column not present in scored data provided. The output drift metric will not be computed.")
            scored_data[self.subscription.prediction_probability_column] = None

        from ibm_metrics_plugin.common.utils.constants import ProblemType
        if self.subscription.problem_type == ProblemType.RAG.value:
            validate_columns_in_dataframe(
                scored_data, "scored data", self.subscription.context_columns)
            common_parameters["context_columns"] = self.subscription.context_columns
            validate_columns_in_dataframe(
                scored_data, "scored data", [self.subscription.question_column])
            common_parameters["question_column"] = self.subscription.question_column

        from ibm_metrics_plugin.common.utils.constants import RANDOM_SEED
        training_data = scored_data.sample(
            n=baseline_max_samples, random_state=RANDOM_SEED)

        configuration_utility = ConfigurationUtilityLLM(
            training_data=training_data,
            common_parameters=common_parameters,
            embeddings_fn=embeddings_fn,
            **kwargs
        )

        drift_v2_parameters = kwargs.get("drift_v2_parameters", {})

        enable_embedding_drift_flag = get(
            drift_v2_parameters, "advanced_controls.enable_embedding_drift")

        if enable_embedding_drift_flag is None:
            advanced_controls = get(
                drift_v2_parameters, "advanced_controls", {})
            advanced_controls["enable_embedding_drift"] = True
            drift_v2_parameters["advanced_controls"] = advanced_controls

        start_time = time()
        print("Generating Drift v2 Archive...")
        path = configuration_utility.generate_drift_v2_archive_llm(drift_v2_parameters=drift_v2_parameters,
                                                                   display_link=False)
        print(
            f"Generated Drift v2 Archive in {timedelta(seconds=(time()-start_time))}...")

        start_time = time()
        print("Uploading Drift v2 Archive...")
        self.client.monitor_instances.upload_drift_v2_archive(subscription_id=self.subscription_id,
                                                              archive_path=path)
        print(
            f"Uploaded Drift v2 Archive in {timedelta(seconds=(time()-start_time))}...")

        if (thresholds is None) and self.monitor_instance.thresholds is not None:
            thresholds = [MetricThresholdOverride.from_dict(
                threshold) for threshold in self.monitor_instance.thresholds]

        if self.monitor_instance.is_configured:
            self.__update_drift_v2_monitor(min_samples=min_samples, max_samples=max_samples,
                                           thresholds=thresholds, update_metadata_only=update_metadata_only,
                                           **kwargs)
        else:
            self.__create_drift_v2_monitor(data_mart_id=data_mart_id, min_samples=min_samples,
                                           max_samples=max_samples, thresholds=thresholds, **kwargs)

    def evaluate(self, **kwargs):
        start_time = time()
        print("Running Drift v2 monitor...")
        response = self.client.monitor_instances.run(monitor_instance_id=self.monitor_instance.id,
                                                     project_id=self.project_id,
                                                     space_id=self.space_id, **kwargs).result

        state = response.entity.status.state
        print(
            f"Running Drift v2 monitor. state: {state}. Time elapsed: {timedelta(seconds=(time() - start_time))}...")

        while (state not in (StatusStateType.FINISHED, StatusStateType.FAILED, StatusStateType.ERROR)):
            sleep(10)
            response = self.client.monitor_instances.get_run_details(
                monitor_instance_id=self.monitor_instance.id,
                monitoring_run_id=response.metadata.id,
                project_id=self.project_id,
                space_id=self.space_id).result
            state = response.entity.status.state
            print(
                f"Running Drift v2 monitor. state: {state}. Time elapsed: {timedelta(seconds=(time() - start_time))}...")

    def __print_message(self):
        print(
            f"The subscription '{self.subscription_id}' has Drift v2 monitor configured with id '{self.monitor_instance.id}'")
        print(f"The utility will re-configure Drift v2.")

    def __get_patch_payload(self,
                            min_samples: Optional[int] = None,
                            max_samples: Optional[int] = None,
                            update_metadata_only: Optional[bool] = False,
                            thresholds: Optional[List[MetricThresholdOverride]] = None) -> List["PatchDocument"]:

        payload = []
        dict_ = {
            "op": "replace",
            "path": "/parameters/train_archive",
            "value": False
        }
        payload.append(PatchDocument.from_dict(dict_))

        if self.monitor_instance.advanced_controls is not None:
            new_advanced_controls = deepcopy(
                self.monitor_instance.advanced_controls)
            new_advanced_controls["enable_embedding_drift"] = True
            dict_ = {
                "op": "replace",
                "path": "/parameters/advanced_controls",
                "value": new_advanced_controls
            }
            payload.append(PatchDocument.from_dict(dict_))

        if not update_metadata_only:
            dict_ = {
                "op": "replace",
                "path": "/status/state",
                "value": "active"
            }
            payload.append(PatchDocument.from_dict(dict_))

        if min_samples is not None:
            dict_ = {
                "op": "replace",
                "path": "/parameters/min_samples",
                "value": min_samples
            }
            payload.append(PatchDocument.from_dict(dict_))

        if max_samples is not None:
            dict_ = {
                "op": "replace",
                "path": "/parameters/max_samples",
                "value": max_samples
            }
            payload.append(PatchDocument.from_dict(dict_))

        if thresholds:
            dict_ = {
                "op": "replace",
                "path": "/thresholds",
                "value": [threshold.to_dict() for threshold in thresholds]
            }
            payload.append(PatchDocument.from_dict(dict_))

        return payload

    def __create_drift_v2_monitor(self, data_mart_id: Optional[str] = None,
                                  min_samples: Optional[int] = None,
                                  max_samples: Optional[int] = None,
                                  thresholds: Optional[List[MetricThresholdOverride]] = None,
                                  **kwargs):
        target = Target(target_id=self.subscription_id,
                        target_type="subscription")

        if min_samples is None:
            min_samples = self.monitor_instance.runtime_min_samples

        if max_samples is None:
            max_samples = self.monitor_instance.runtime_max_samples

        advanced_controls = {
            "enable_embedding_drift": True
        }
        parameters = {
            "min_samples": min_samples,
            "train_archive": False,
            "advanced_controls": advanced_controls
        }
        if max_samples is not None:
            parameters["max_samples"] = max_samples

        start_time = time()
        print("Enabling Drift v2 monitor...")
        response = self.client.monitor_instances.create(monitor_definition_id="drift_v2",
                                                        data_mart_id=data_mart_id,
                                                        target=target,
                                                        parameters=parameters,
                                                        project_id=self.project_id,
                                                        space_id=self.space_id,
                                                        thresholds=thresholds,
                                                        background_mode=True,
                                                        **kwargs).result

        state = response.entity.status.state
        print(
            f"Enabling Drift v2 monitor. state: {state}. Time elapsed: {timedelta(seconds=(time() - start_time))}...")

        while (state not in (StatusStateType.ACTIVE, StatusStateType.ERROR)):
            sleep(2)
            response = self.client.monitor_instances.get(
                monitor_instance_id=response.metadata.id).result
            state = response.entity.status.state
            print(
                f"Enabling Drift v2 monitor. state: {state}. Time elapsed: {timedelta(seconds=(time() - start_time))}...")
            if state == StatusStateType.ACTIVE:
                # Re-initialized the monitor instance when it became active.
                self.monitor_instance = DriftV2MonitorInstance(client=self.client, subscription_id=self.subscription_id,
                                                               project_id=self.project_id, space_id=self.space_id)

    def __update_drift_v2_monitor(self, min_samples: Optional[int] = None,
                                  max_samples: Optional[int] = None,
                                  thresholds: Optional[List[MetricThresholdOverride]] = None,
                                  update_metadata_only: bool = False,
                                  **kwargs):
        patch_document = self.__get_patch_payload(min_samples=min_samples, max_samples=max_samples,
                                                  update_metadata_only=update_metadata_only, thresholds=thresholds)
        start_time = time()
        print("Updating Drift v2 monitor...")
        response = self.client.monitor_instances.update(monitor_instance_id=self.monitor_instance.id,
                                                        patch_document=patch_document,
                                                        update_metadata_only=update_metadata_only).result

        state = response.entity.status.state
        print(
            f"Updating Drift v2 monitor. state: {state}. Time elapsed: {timedelta(seconds=(time() - start_time))}...")

        while (state not in (StatusStateType.ACTIVE, StatusStateType.ERROR)):
            sleep(2)
            response = self.client.monitor_instances.get(
                monitor_instance_id=response.metadata.id).result
            state = response.entity.status.state
            print(
                f"Updating Drift v2 monitor. state: {state}. Time elapsed: {timedelta(seconds=(time() - start_time))}...")
            if state == StatusStateType.ACTIVE:
                # Re-initialized the monitor instance when it became active.
                self.monitor_instance = DriftV2MonitorInstance(client=self.client, subscription_id=self.subscription_id,
                                                               project_id=self.project_id, space_id=self.space_id)
