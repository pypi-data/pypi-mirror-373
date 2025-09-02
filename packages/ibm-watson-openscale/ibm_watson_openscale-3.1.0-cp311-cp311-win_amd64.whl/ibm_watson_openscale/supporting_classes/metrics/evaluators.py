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

from ibm_watson_openscale.utils.metrics.evaluators_utils import (
    initialize_scoring_wrapper,
    get_create_software_spec,
)

FAITHFULNESS = "faithfulness"
RETRIEVAL_QUALITY = "retrieval_quality"
ANSWER_RELEVANCE = "answer_relevance"
SUPPORTED_METRICS = (FAITHFULNESS, RETRIEVAL_QUALITY, ANSWER_RELEVANCE)


class LLMAJEvaluators:
    """
    Manages evaluator for LLM as judge
    """

    def __init__(self, watson_openscale) -> None:
        self.watson_openscale = watson_openscale

    def add(
        self,
        metric_type,
        wx_ai_credentials,
        space_id,
        question_column,
        context_columns=None,
        hardware_spec="M",
        metric_parameters={},
        func_name=None,
        create_integrated_system=True,
    ):
        """
        create and deploy a python function with predefined template.
        create an integrated system with the deployment details.
        """
        try:
            from ibm_watsonx_ai import APIClient
        except ImportError:
            msg = "Unable to find ibm_watsonx_ai library. Please install it."
            raise Exception(msg)

        if metric_type not in SUPPORTED_METRICS:
            raise Exception(f"Metric {metric_type} is not supported.")
        if metric_type in (FAITHFULNESS, RETRIEVAL_QUALITY) and not context_columns:
            raise ValueError("Missing `context_columns` field.")

        func_name = func_name if func_name else f"{metric_type}_with_nlp"
        python_func = initialize_scoring_wrapper(
            params={
                "wos_credentials": {
                    "api_key": self.watson_openscale.authenticator.token_manager.apikey,
                    "iam_url": self.watson_openscale.authenticator.token_manager.url,
                    "service_url": self.watson_openscale.service_url.split(
                        "/openscale/"
                    )[0],
                },
                "context_columns": context_columns,
                "question_column": question_column,
            },
            metric_type=metric_type,
            metric_parameters=metric_parameters,
        )

        try:
            wx_ai_client = APIClient(wx_ai_credentials)
            wx_ai_client.set.default_space(space_id)
            sofware_spec_uid = get_create_software_spec(wx_ai_client)
            meta_data = {
                wx_ai_client.repository.FunctionMetaNames.NAME: func_name,
                wx_ai_client.repository.FunctionMetaNames.SOFTWARE_SPEC_UID: sofware_spec_uid,
            }

            function_details = wx_ai_client.repository.store_function(
                meta_props=meta_data, function=python_func
            )
            function_uid = function_details["metadata"]["id"]
            hardware_spec_id = wx_ai_client.hardware_specifications.get_id_by_name(
                hardware_spec
            )
            function_deployment_details = wx_ai_client.deployments.create(
                function_uid,
                {
                    wx_ai_client.deployments.ConfigurationMetaNames.NAME: func_name
                    + "_deployment",
                    wx_ai_client.deployments.ConfigurationMetaNames.ONLINE: {},
                    wx_ai_client.deployments.ConfigurationMetaNames.HARDWARE_SPEC: {
                        "id": hardware_spec_id
                    },
                },
            )
            func_deployment_uid = wx_ai_client.deployments.get_uid(function_deployment_details)
            func_scoring_url = (
                wx_ai_client.deployments.get_scoring_href(function_deployment_details)
                + "?version=2021-05-01"
            )
        except Exception as e:
            return str(e)

        response = {
            "deployment_uid": func_deployment_uid,
            "scoring_url": func_scoring_url,
        }

        if create_integrated_system:
            gen_ai_evaluator = self.watson_openscale.integrated_systems.add(
                name=func_name,
                description="Created by watsonx.governance SDK",
                type="generative_ai_evaluator",
                parameters={"evaluator_type": "custom", "sub_type": "watson_nlp"},
                credentials={
                    "apikey": self.watson_openscale.authenticator.token_manager.apikey,
                    "auth_provider": "cloud",
                    "auth_url": self.watson_openscale.authenticator.token_manager.url,
                    "auth_type": "api_key",
                },
                connection={"endpoint": func_scoring_url},
            )

            result = gen_ai_evaluator.result._to_dict()
            response["evaluator_id"] = result["metadata"]["id"]

        return response