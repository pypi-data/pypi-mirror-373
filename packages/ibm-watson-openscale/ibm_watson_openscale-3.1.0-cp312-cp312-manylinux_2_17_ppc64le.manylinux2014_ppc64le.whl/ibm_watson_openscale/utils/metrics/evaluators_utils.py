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


import os
import hashlib

CUSTOM_SOFTWARE_SPEC = "custom-rt24.1-py3.11-by-watsonx.gov"
PKG_EXT_NAME = "custom-rt24.1-py3.11-watsonx.gov"
CONDA_YML = "conda_yml"


def initialize_scoring_wrapper(params, metric_type, metric_parameters):
    def scoring_wrapper(
        params=params, metric_type=metric_type, metric_parameters=metric_parameters
    ):
        import pandas as pd
        from ibm_metrics_plugin.metrics.llm.config.entities import (
            LLMTaskType,
            LLMMetricType,
        )
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        from ibm_watson_openscale import APIClient

        if metric_type == LLMMetricType.FAITHFULNESS.value:
            import subprocess

            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])

        api_key = params.get("wos_credentials", {}).get("api_key")
        iam_url = params.get("wos_credentials", {}).get("iam_url")
        service_url = params.get("wos_credentials", {}).get("service_url")
        context_columns = params.get("context_columns")
        question_column = params.get("question_column")
        record_ids_column = "record_ids"

        config_json = {
            "configuration": {
                "record_level": True,
                "context_columns": context_columns,
                "question_column": question_column,
                LLMTaskType.RAG.value: {
                    metric_type: metric_parameters,
                },
            }
        }
        authenticator = IAMAuthenticator(apikey=api_key, url=iam_url)

        def score(payload):
            wos_client = APIClient(
                authenticator=authenticator,
                service_url=service_url,
            )
            input_column = payload["input_data"][0]["fields"]
            data = pd.DataFrame(
                payload["input_data"][0]["values"],
                columns=input_column,
            )
            if metric_type == LLMMetricType.ANSWER_RELEVANCE.value:
                df_input = pd.DataFrame(data, columns=[question_column])
            else:
                df_input = pd.DataFrame(
                    data, columns=context_columns + [question_column]
                )
            record_ids = data[record_ids_column].to_list()
            df_output = None
            if metric_type in (
                LLMMetricType.FAITHFULNESS.value,
                LLMMetricType.ANSWER_RELEVANCE.value,
            ):
                prediction_column = list(
                    set(input_column)
                    - set(context_columns or [] + [question_column, record_ids_column])
                )
                df_output = pd.DataFrame(data, columns=prediction_column)
            metrics_result = wos_client.llm_metrics.compute_metrics(
                config_json,
                sources=df_input,
                predictions=df_output,
                background_mode=False,
                record_ids=record_ids,
            )
            rq_result = metrics_result.get(metric_type)
            response = {
                "predictions": [
                    {
                        "fields": ["record_level_metrics"],
                        "values": [
                            str(i) for i in rq_result.get("record_level_metrics")
                        ],
                    }
                ]
            }
            return response

        return score

    return scoring_wrapper


def get_create_software_spec(wx_ai_client):
    current_file_path = os.path.abspath(__file__)
    directory_path = os.path.dirname(current_file_path)
    file_path = f"{directory_path}/mp_eval_dep.yaml"

    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    _hash = md5_hash.hexdigest()
    software_spec_name = f"{CUSTOM_SOFTWARE_SPEC}_{_hash}"
    pkg_ext_name = f"{PKG_EXT_NAME}_{_hash}"

    software_spec_uid = wx_ai_client.software_specifications.get_id_by_name(
        software_spec_name
    )
    if software_spec_uid == "Not Found":
        pkg_ext_metadata = {
            wx_ai_client.package_extensions.ConfigurationMetaNames.NAME: pkg_ext_name,
            wx_ai_client.software_specifications.ConfigurationMetaNames.DESCRIPTION: "Created by watsonx.governance SDK for watson nlp generative ai evaluator.",
            wx_ai_client.package_extensions.ConfigurationMetaNames.TYPE: CONDA_YML,
        }
        pkg_asset_details = wx_ai_client.package_extensions.store(
            meta_props=pkg_ext_metadata,
            file_path=file_path,
        )
        pkg_asset_id = wx_ai_client.package_extensions.get_id(pkg_asset_details)

        base_id = wx_ai_client.software_specifications.get_id_by_name(
            "runtime-24.1-py3.11"
        )
        software_spec_metadata = {
            wx_ai_client.software_specifications.ConfigurationMetaNames.NAME: software_spec_name,
            wx_ai_client.software_specifications.ConfigurationMetaNames.DESCRIPTION: "Created by watsonx.governance SDK for watson nlp generative ai evaluator.",
            wx_ai_client.software_specifications.ConfigurationMetaNames.BASE_SOFTWARE_SPECIFICATION: {
                "guid": base_id
            },
            wx_ai_client.software_specifications.ConfigurationMetaNames.PACKAGE_EXTENSIONS: [
                {"guid": pkg_asset_id}
            ],
        }
        software_spec_asset_details = wx_ai_client.software_specifications.store(
            meta_props=software_spec_metadata
        )

        software_spec_uid = wx_ai_client.software_specifications.get_id(
            software_spec_asset_details
        )

    return software_spec_uid
