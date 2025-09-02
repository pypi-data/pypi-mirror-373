
# coding: utf-8

# Copyright 2023 IBM All Rights Reserved.
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

# TODO: Add parameters validation in every method

from ibm_cloud_sdk_core import BaseService
from ibm_watson_openscale.utils.utils import validate_type
# from ibm_watson_openscale.utils.utils import check_plan_usage, update_plan_usage
from ibm_watson_openscale.supporting_classes.metrics.utils import is_entitled_on_cloud
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_watson_openscale.supporting_classes.metrics.evaluators import LLMAJEvaluators
from ibm_watson_openscale.utils.usage_client import UsageClient

import pandas as pd
from ibm_watson_openscale.base_classes.tables import Table
from itertools import chain
import warnings
import math
warnings.filterwarnings('ignore')


class LLMMetrics():

    def __init__(self, ai_client: "WatsonOpenScaleV2Adapter") -> None:
        validate_type(ai_client, "ai_client", BaseService, True)
        self.ai_client = ai_client
        self.is_bearer_token = False
        self.evaluators = LLMAJEvaluators(ai_client)
        if type(self.ai_client.authenticator) is BearerTokenAuthenticator:
            self.token = self.ai_client.authenticator.bearer_token
            self.is_bearer_token = True
        else:
            self.token = self.ai_client.authenticator.token_manager.get_token()
        self.usage_client = UsageClient(self.ai_client)
        self.is_paid_plan = False
        self.limit = 1000

    def compute_metrics(self, configuration: dict, sources: pd.DataFrame = None, predictions: pd.DataFrame = None, references: pd.DataFrame = None, custom_evaluators=[], **kwargs):
        """
        Compute LLM based metrics based on the configuration.
        :param DataFrame sources: data frame containing the input data (if required or else empty dataframe).
        :param DataFrame predictions: data frame containing the input data (if required or else empty dataframe).
        :param DataFrame references: data frame containing the referene data (if required or else empty dataframe).
        :param List custom_evaluators: List of custom evaluator functions that compute additional custom metrics
        :return: Key/Value pair where key is the metric name and value is an object consisting of the metric results for all individual metrics.
        :rtype: dict

        This is how the configuration parameter dict will look like

        >>>
        from ibm_metrics_plugin.metrics.llm.utils.constants import LLMTextMetricGroup, LLMSummarizationMetrics, HAP_SCORE
        metric_config = {
            "configuration": {
                LLMTextMetricGroup.SUMMARIZATION.value: {  #This is metric group
                    LLMSummarizationMetrics.ROUGE_SCORE.value: { #This is individual metric and contains it's specific parameters if required
                        "use_aggregator": True,
                        "use_stemmer": True
                    },
                    LLMSummarizationMetrics.SARI.value: { #This is individual metric and contains it's specific parameters if required
                    },
                    LLMSummarizationMetrics.BLEURT_SCORE.value: {},
                    HAP_SCORE: {},
                    LLMSummarizationMetrics.SACREBLEU.value: {},
                    LLMSummarizationMetrics.WIKI_SPLIT.value: {},
                    LLMSummarizationMetrics.METEOR.value: {},
                    LLMSummarizationMetrics.NORMALIZED_RECALL.value: {},
                    LLMSummarizationMetrics.NORMALIZED_PRECISION.value: {},
                    LLMSummarizationMetrics.NORMALIZED_F1_SCORE.value: {},
                }
            }
        }
        A way you might use me is:
        >>> client.llm_metrics.compute_metrics(configuration, sources, predictions, references)
        User can pass custom_evaluators as argument to compute custom metrics.
        eg: def fun1(sources: pd.DataFrame, predictions: pd.DataFrame, references: pd.DataFrame):
        # compute custom metrics and returns it as a dict
        custom_evaluators = [fun1]
        >>> client.llm_metrics.compute_metrics(configuration, sources, predictions, references, custom_evaluators = custom_evaluators)
        """
        metrics = {}
        self.__validate_params(configuration, sources, predictions, references)

        llm_metric_manager = self.__get_metrics_manager(
            configuration, kwargs)

        # Modify the records in case of a lite plan
        count = 1
        # Modifications for red-teaming
        if sources is None:
            # Setting record_length to number of attack vectors
            if self.__is_key_present(configuration, "robustness"):
                if self.__is_key_present(configuration, "adversarial_robustness"):
                    record_length = 48
                elif self.__is_key_present(configuration, "prompt_leakage_risk"):
                    record_length = 56
                elif self.__is_key_present(configuration, "adversarial_robustness") and self.__is_key_present(configuration, "prompt_leakage_risk"):
                    record_length = 104
            else:
                record_length = len(predictions) or len(references)
        else:
            record_length = len(sources)

        if self.limit < record_length:
            # Modify the records in case of a lite plan
            if not self.is_paid_plan:
                sources = sources.iloc[:self.limit].copy()
                predictions = predictions.iloc[:self.limit].copy()
                references = references.iloc[:self.limit].copy()
            else:
                count = math.ceil(record_length/self.limit)

        metrics = llm_metric_manager.compute(
            sources, predictions, references, **kwargs)

        for fun in custom_evaluators:
            custom_metric = fun(sources, predictions, references, **kwargs)
            metrics.update(custom_metric)

        if not self.ai_client.is_cp4d:
            self.usage_client.update_plan_usage(count)

        return metrics

    def get_metrics_result(self, configuration: dict, metrics_result, **kwargs):
        """
        Get the result of metrics which are run on the server. Used for faithfulness metric.
        :param configuration: The configuration of the metrics to get the response
        :param metrics_result: The metrics result dictionary containing the details of the computation tasks triggered. This will be output of the method 'compute_metrics'.
        :return: Key/Value pair where key is the metric name and value is an object consisting of the metric results for all individual metrics.

        This is how the configuration parameter dict will look like

        >>>
        from ibm_metrics_plugin.metrics.llm.utils.constants import LLMTextMetricGroup, LLMSummarizationMetrics, HAP_SCORE
        metric_config = {
            "configuration": {
                LLMTextMetricGroup.RAG.value: {  #This is metric group
                    LLMSummarizationMetrics.ROUGE_SCORE.value: { #This is individual metric and contains it's specific parameters if required
                        "use_aggregator": True,
                        "use_stemmer": True
                    },
                    LLMSummarizationMetrics.FAITHFULNESS.value: { #This is individual metric and contains it's specific parameters if required
                    },
                    LLMSummarizationMetrics.ANSWER_RELEVANCE.value: {}
                }
            }
        }
        A way you might use me is:
        >>> metrics_result = client.llm_metrics.compute_metrics(configuration, sources, predictions, references)
        >>> final_result = client.llm_metrics.get_metrics_result(configuration=configuration, metrics_result=metrics_result)
        """
        validate_type(configuration, "configuration", dict, True)

        llm_metric_manager = self.__get_metrics_manager(
            configuration, kwargs)

        return llm_metric_manager.get_metrics_result(
            metrics_result, **kwargs)

    def __get_metrics_manager(self, configuration, kwargs):
        try:
            metric_manager_module = __import__(
                "ibm_metrics_plugin.metrics.llm.core.llm_metrics_manager", fromlist=["LLMMetricManager"])
        except Exception as e:
            msg = "Unable to find metric-plugins library with LLM support to compute metrics. Please install it using `pip install ibm-metrics-plugin`"
            raise Exception(msg)

        self.__check_entitlement_and_usage()
        
        kwargs["is_cp4d"] = self.ai_client.is_cp4d
        kwargs["origin"] = "sdk"
        llm_metric_manager = getattr(
            metric_manager_module, "LLMMetricManager")(configuration, **kwargs)

        kwargs["is_bearer_token"] = self.is_bearer_token
        kwargs["authenticator"] = self.ai_client.authenticator
        kwargs["service_url"] = self.ai_client.service_url
        kwargs["host"] = self.ai_client.host
        kwargs['service_instance_id'] = self.ai_client.service_instance_id
        return llm_metric_manager

    def __show_supported_metrics_old(self, metric_type_module):

            metric_type = getattr(metric_type_module, "LLMSummarizationMetrics")
            print("Following Text Summrization metrics are supported")
            for m in metric_type:
                print("   {}".format(m))
            print("        ----------        ")

            metric_type = getattr(metric_type_module, "LLMGenerationMetrics")
            print("Following Text Generation metrics are supported")
            for m in metric_type:
                print("   {}".format(m))
            print("        ----------        ")

            metric_type = getattr(metric_type_module, "LLMExtractionMetrics")
            print("Following Text Extraction metrics are supported")
            for m in metric_type:
                print("   {}".format(m))
            print("        ----------        ")

            metric_type = getattr(metric_type_module, "LLMQAMetrics")
            print("Following Question and Answer metrics are supported")
            for m in metric_type:
                print("   {}".format(m))
            print("        ----------        ")

    def show_supported_metrics(self, task_type=None, metric_id=None, metric_group=None):
            """
                Displays information about supported metrics and task types based on the provided parameters.

                This method can be called in the following ways:

                1. Show_supported_metrics() → Displays all supported metrics, task types, and metric groups.
                2. Show_supported_metrics(task_type="generation") → Displays all metrics supported by the specified task type.
                3. Show_supported_metrics(metric_id="bleu") → Displays all task types that support the specified metric.
                4. Show_supported_metrics(metric_group="rouge_score") → Displays all metrics that come under the specified metric group.
                5. Show_supported_metrics(task_type="generation", metric_id="bleu") → Displays whether the specified metric is supported by the specified task type.
                6. Show_supported_metrics(metric_group="rouge_score", metric_id="rouge1") → Displays whether the specified metric is part of the specified metric group.
            """

            try:
                from ibm_metrics_plugin.metrics.llm.config.entities import LLMTaskType, LLMMetricType, LLMSubMetrics
            except Exception as e:
                try:
                    metric_type_module = __import__("ibm_metrics_plugin.metrics.llm.utils.constants", fromlist=[
                        "LLMSummarizationMetrics,LLMGenerationMetrics, LLMExtractionMetrics, LLMQAMetrics"])
                    self.__show_supported_metrics_old(metric_type_module)
                    return
                except Exception as e:
                    msg = "Unable to find metric-plugins latest version library with LLM support to list metrics. Please install it using `pip install ibm-metrics-plugin`"
                    raise Exception(msg)

            if isinstance(task_type, LLMTaskType):
                task_type = task_type.value
            if isinstance(metric_id, (LLMMetricType, LLMSubMetrics)):
                metric_id = metric_id.value
            if isinstance(metric_group, (LLMMetricType, LLMSubMetrics)):
                metric_group = metric_group.value

            all_task_type = [met.value for met in LLMTaskType]
            all_metrics = {met.value: met for met in sorted(chain(LLMMetricType, LLMSubMetrics), key=lambda x: x.value)}
            all_metric_group = list(set([met.metrics_group for met in LLMSubMetrics if met.metrics_group is not None]))

            # Function to display all supported metrics
            def __display_all_supported_metrics():
                headers = ['Metric ID', 'Metric Group', 'Supported Task Type(s)', 'Is Reference Free']
                result_metrics = []
                for metric_obj in all_metrics.values():
                    result_metrics.append([
                        metric_obj.value,
                        metric_obj.metrics_group if hasattr(metric_obj, "metrics_group") else None,
                        metric_obj.supported_tasks,
                        "Yes" if metric_obj.is_reference_free else "No"
                    ])
                __display_table(headers=headers, record=result_metrics,
                                title_table="The following are the supported metrics:")

            # Function to display all supported task types
            def __display_all_supported_task_type():
                result_task_type = [[task_type] for task_type in all_task_type]
                __display_table(headers=['Task Type(s)'], record=result_task_type,
                                title_table="The following are supported task types.")

            # Function to display all supported metric_group
            def __display_all_supported_metric_group():
                result_task_type = [[met_group] for met_group in all_metric_group]
                __display_table(headers=['Metric Group'], record=result_task_type,
                                title_table="The following supported metric groups have their sub-metrics:")

            # Function to display error messages
            def __display_error_msg(error_message):
                print(f"\033[31m {error_message} \033[0m")

            # Function to display tables
            def __display_table(headers, record, title_table):
                Table(headers, record).list(title=title_table)

            # Function to display all supported metrics for a provided task type
            def __display_supported_metrics(_task_type=None, metric_group_id=None):
                header = ['Metric ID', 'Metric Group', 'Supported Task Type(s)', 'Is Reference Free']
                result = []
                if _task_type is not None:
                    for metric_obj in __get_supported_metrics(_task_type):
                        result.append([
                            metric_obj.value,
                            metric_obj.metrics_group if hasattr(metric_obj, "metrics_group") else None,
                            metric_obj.supported_tasks,
                            "Yes" if metric_obj.is_reference_free else "No"
                        ])
                    title = f"Metrics supported by the {_task_type} task type:"
                elif metric_group_id is not None:
                    if metric_group_id not in all_metric_group:
                        __display_error_msg(
                            error_message=f"Metric group {metric_group_id} does not have any sub_metrics.")
                        __display_supported_task_type(metric_id=metric_group_id)
                        __display_all_supported_metric_group()
                        return
                    else:
                        for metric_obj in all_metrics[metric_group_id].sub_metrics:
                            result.append([
                                metric_obj.value,
                                metric_obj.metrics_group if hasattr(metric_obj, "metrics_group") else None,
                                metric_obj.supported_tasks,
                                "Yes" if metric_obj.is_reference_free else "No"
                            ])
                        title = f"Metrics that come under the {metric_group_id} metric group are:"

                __display_table(headers=header, record=result, title_table=title)

            # Function to display all supported task_type for provided metric_id
            def __display_supported_task_type(metric_id):
                metric_obj = all_metrics[metric_id]
                header = ['Metric ID', 'Metric Group', 'Supported Task Type(s)', 'Is Reference Free']
                result = [[
                    metric_obj.value,
                    metric_obj.metrics_group if hasattr(metric_obj, "metrics_group") else None,
                    metric_obj.supported_tasks,
                    "Yes" if metric_obj.is_reference_free else "No"
                ]]
                __display_table(headers=header, record=result, title_table=f"{metric_id} metric details:")

            # Function to return all supported metrics under provided task_type
            def __get_supported_metrics(_task_type=None):
                metrics = []
                for m in chain(LLMMetricType, LLMSubMetrics):
                    if _task_type in m.supported_tasks:
                        metrics.append(m)

                return sorted(metrics, key=lambda x: x.value)

            # checking metric_id is valid
            if metric_id is not None and metric_id not in all_metrics.keys():
                # Invalid metric_id
                __display_error_msg(f"The metric: {metric_id} is not valid.")
                __display_all_supported_metrics()
                return

            # checking metric_id is valid
            if task_type is not None and task_type not in all_task_type:
                # Invalid task_type
                __display_error_msg(f"The task type: {task_type} is not valid.")
                __display_all_supported_task_type()
                return

            # checking metric_group is valid
            if metric_group is not None and metric_group not in all_metrics.keys():
                # Invalid metric_id
                __display_error_msg(f"The metric group: {metric_group} is not valid.")
                __display_table(headers=["metric group"], record=[[met] for met in all_metric_group],
                                title_table="The following supported metric groups have their sub-metrics:")
                return

            # Main conditional logic
            # If task_type is not None
            if task_type is not None:
                if metric_id is not None:
                    # Metric valid and check if supported by task_type
                    if metric_id in [metric.value for metric in __get_supported_metrics(task_type)]:
                        print(f"The {metric_id} metric is supported by the {task_type} task type.")
                        __display_supported_task_type(metric_id=metric_id)
                    else:
                        #  Display all metrics supported by task_type when metric is not supported by task_type
                        __display_error_msg(f"Metric {metric_id} is not supported for the task type: {task_type}")
                        __display_supported_metrics(_task_type=task_type)

                else:
                    # Display all metrics supported by task_type when metric_id not provided
                    __display_supported_metrics(_task_type=task_type)

            # If metric_group is not None
            elif metric_group is not None:
                if (metric_id is not None and hasattr(all_metrics[metric_group], "sub_metrics") and
                        all_metrics[metric_group].sub_metrics is not None):
                    # Metric valid and check if supported by metric group
                    if metric_id in [met.value for met in all_metrics[metric_group].sub_metrics]:
                        print(f"{metric_id} metric comes under the {metric_group} metric group.")
                        __display_supported_task_type(metric_id=metric_id)
                    else:
                        #  Display all metrics supported by task_type when metric is not supported by task_type
                        __display_error_msg(f"Metric {metric_id} does not come under the metric group: {metric_group}")
                        __display_supported_metrics(metric_group_id=metric_group)

                else:
                    # Display all metrics supported by task_type when metric_id not provided
                    __display_supported_metrics(metric_group_id=metric_group)

            # If metric_id alone not None
            elif metric_id is not None:
                # Show task types supports the metric_id
                metric_obj = all_metrics[metric_id]
                header = ['Metric ID', 'Metric Group', 'Supported Task_Type(s)', 'Is Reference Free']
                result = [[
                    metric_obj.value,
                    metric_obj.metrics_group if hasattr(metric_obj, "metrics_group") else None,
                    metric_obj.supported_tasks,
                    "Yes" if metric_obj.is_reference_free else "No"
                ]]
                __display_table(headers=header, record=result,
                                title_table=f"The {metric_id} metric supports the following task type(s):")

            else:
                # Display all supported metrics and task types if no parameters provided
                __display_all_supported_metrics()
                __display_all_supported_task_type()
                __display_all_supported_metric_group()

            configuration_structure = '''
                \033[1;34mIf metric_group is not None use below configuration     If metric_group is None use below configuration\033[0m

                    "configuration": {                                           "configuration": {
                        "task_type": {                                                "task_type": {
                            "metric_group": {                    \033[1;34mor\033[0m                        "metric_id": {}
                                "metric_id": {}                                                }
                            }                                                               }
                        }                                                       
                    }                                                       
                '''
            print("\n\n\033[1;31mMetrics-plugin configuration structure\033[0m")
            print(configuration_structure)


    def __validate_params(self, configuration, sources, predictions, references):

        validate_type(configuration, "configuration", dict, True)
        validate_type(sources, "data_frame", [pd.DataFrame], False)
        validate_type(predictions, "data_frame", [pd.DataFrame], False)
        validate_type(references, "data_frame", [pd.DataFrame], False)

    def display_result(self, results):
        try:
            from ibm_metrics_plugin.metrics.llm.common.impl.robustness_metric import RobustnessMetrics
        except Exception:
            msg = "Unable to find metric-plugins library. Please install it "
            raise Exception(msg)
        return RobustnessMetrics.display_robustness_results(results)

    def __check_entitlement_and_usage(self):
        if self.ai_client.is_cp4d is not True:
            # Allow user to compute metrics only if he has wos entitlements
            self.is_paid_plan = is_entitled_on_cloud(self.ai_client.service_url,
                                 self.ai_client.service_instance_id, self.token)
            # Allow user to compute metrics only for a plan having the usage within limit on cloud
            self.limit = self.usage_client.check_plan_usage_and_get_limit(is_paid_plan=self.is_paid_plan, is_llm=True)

    def __is_key_present(self, config, key):
        """
        Recursively checks if the given key exists in the config_json.
        :param config: input config_json.
        :param key: Key to find.
        :return: True if key exists, otherwise False.
        """
        return key in config or any(self.__is_key_present(v, key) for v in config.values() if isinstance(v, dict))