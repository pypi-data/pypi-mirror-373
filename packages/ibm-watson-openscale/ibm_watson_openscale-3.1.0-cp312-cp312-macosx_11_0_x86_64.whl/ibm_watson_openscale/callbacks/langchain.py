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

import json
import pandas as pd
from typing import Any

try:
    from langchain.schema import LLMResult
    from langchain.callbacks.base import BaseCallbackHandler
except:
    pass


class WatsonxGovCallbackHandler(BaseCallbackHandler):

    def __init__(self, watsonxgov_client, configuration: dict, source: dict = {}, reference: dict = None, **kwargs):

        if not configuration:
            raise ValueError(
                "An error occurred while invoking watsonx.gov callback. Error: The metrics configuration is invalid.")

        if not watsonxgov_client:
            raise ValueError(
                "An error occurred while invoking watsonx.gov callback. Error: watsonx.gov client object is invalid.")

        self.watsonxgov_client = watsonxgov_client
        self.metric_config = configuration
        self.computed_metrics = None
        self.reference = reference
        self.source = source

        from ibm_metrics_plugin.metrics.llm.utils.metrics_util import generate_uuids
        self.record_id = kwargs.pop("record_id", generate_uuids(1)[0])
        self.debug = kwargs.pop("debug", False)
        self.background_mode = kwargs.pop("background_mode", False)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:

        generations = response.generations
        prediction = generations[0][0].text

        df_input = pd.DataFrame([self.source])
        df_reference = pd.DataFrame([self.reference])
        df_output = pd.DataFrame({"generated_summary": [prediction]})

        try:
            print("Evaluating for record", self.record_id)
            result = self.watsonxgov_client.llm_metrics.compute_metrics(self.metric_config,
                                                                        sources=df_input,
                                                                        predictions=df_output,
                                                                        references=df_reference,
                                                                        record_ids=[
                                                                            self.record_id],
                                                                        background_mode=self.background_mode)

            record_level_result = {}

            for metric in result:
                record_level_result[metric] = {
                    "record_level_metrics": result[metric]["record_level_metrics"]}

            self.computed_metrics = record_level_result

            if self.debug:
                print("-"*66)
                print("Source :", self.source)
                print("prediction :", prediction)
                print("Reference :", self.reference)
                print("\nEvaluated Metrics")
                print(json.dumps(record_level_result, indent=2))
                print("\nEvaluation Completed\n")

        except Exception as e:
            print("An error occurred while invoking the watsonx.gov callback handler.", e)

    @staticmethod
    def aggregate_result(record_level_metrics: list = []):
        """
        Convert the record level metrics into the metrics result format with summaries
        """
        from ibm_metrics_plugin.metrics.llm.utils.metrics_util import get_summaries
        metrics_result = {}
        # Consolidate the record level metrics
        for val in record_level_metrics:
            for metric in val:
                if metric not in metrics_result:
                    metrics_result[metric] = {"record_level_metrics": []}
                metrics_result[metric]["record_level_metrics"].extend(
                    val[metric]["record_level_metrics"])

        # Generate summaries for metrics
        for metric, value in metrics_result.items():
            metrics_summary = {}
            for metric_vals in value["record_level_metrics"]:
                for m, val in metric_vals.items():
                    if m != "record_id" and type(val) in (float, int):
                        if m in metrics_summary:
                            metrics_summary[m].append(val)
                        else:
                            metrics_summary[m] = [val]

            if len(metrics_summary) == 1:
                metrics_result[metric].update(
                    get_summaries(metrics_summary[metric]))
            else:
                metrics_result[metric].update(
                    {k: get_summaries(v) for k, v in metrics_summary.items()})

        return metrics_result
