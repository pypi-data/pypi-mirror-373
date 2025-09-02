
# coding: utf-8

# Copyright 2021 IBM All Rights Reserved.
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
from ibm_watson_openscale.utils.utils import validate_type, get
# from ibm_watson_openscale.utils.utils import check_plan_usage, update_plan_usage
from ibm_watson_openscale.supporting_classes.metrics.utils import is_entitled_on_cloud
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_watson_openscale.utils.usage_client import UsageClient

import pandas as pd
import json
import math

# job timeout in seconds
JOB_TIMEOUT = 300


class AIMetrics():

    def __init__(self, ai_client: "WatsonOpenScaleV2Adapter") -> None:
        validate_type(ai_client, "ai_client", BaseService, True)
        self.ai_client = ai_client
        # authenticator.token_manager
        if type(self.ai_client.authenticator) is BearerTokenAuthenticator:
            self.token = self.ai_client.authenticator.bearer_token
        else:
            self.token = self.ai_client.authenticator.token_manager.get_token()
        self.usage_client = UsageClient(self.ai_client)
        self.is_paid_plan = False
        self.limit = 50000

    def compute_metrics(self, spark=None, configuration=None, data_frame=None, metric_aggregator=None, **kwargs):
        """
        Compute research metrics based on the configuration.
        :param SparkSession spark: Spark session object to be used for computing metrics.
        :param dict configuration: Configuration for computing metrics.
        :param Union[DataFrame, pd.DataFrame] data_frame: data frame containing the data on which metrics to be computed.          
        :return: Key/Value pair where key is the metric group name and value is an object consisting of the metric results for all individual metrics.
        :rtype: dict

        This is how the configuration parameter dict will look like

        >>>
        from ibm_metrics_plugin.common.utils.constants import FairnessMetricType
        configuration = {}
        configuration['configuration'] = {
            "problem_type": "binary",
            "label_column": "Risk",
            "fairness": {
                            "metrics_configuration": {
                                FairnessMetricType.SPD.value: {
                                    "features": [ ["Sex"],["Age"] ]
                                },
                                FairnessMetricType.SED.value: {
                                    "features": [ ["Sex"],["Sex","Age"] ],
                                    "concentration": 1.0 
                                } 
                            },
                            "protected_attributes": [
                                {
                                    "feature": "Sex",
                                    "reference_group": ["male"]
                                },
                                {
                                    "feature": "Age",
                                    "reference_group": [[26, 55],[56,75]]
                                }
                            ],
                            "favourable_label": ["No Risk"],
                            "unfavourable_label": ["Risk"]
                        }
        }

        A way you might use me is:
        >>> client.ai_metrics.compute_metrics(spark, configuration, data_frame)

        """

        self.__validate_params(
            spark, data_frame, metric_aggregator, configuration)

        try:
            metric_manager_module = __import__(
                "ibm_metrics_plugin.core.metrics_manager", fromlist=["MetricManager"])
        except Exception as e:
            msg = "Unable to find metric-plugins library to compute metrics. Please install it "
            raise Exception(msg)

        # Set additional configuration information if required
        conf = self.__set_additional_configuration(
            configuration, self.ai_client.is_cp4d)

        # Allow user to compute metrics only for a plan having the usage within limit on cloud
        self.__check_plan_usage()

        count = 1
        record_length = len(data_frame)
        if self.limit < record_length:
            # Modify the records in case of a lite plan
            if not self.is_paid_plan:
                data_frame = data_frame.iloc[:self.limit].copy()
            else:
                count = math.ceil(record_length/self.limit)

        metric_manager = getattr(metric_manager_module, "MetricManager")()
        metrics = metric_manager.evaluate(
            spark=spark, configuration=conf, data_frame=data_frame, metric_aggregator=metric_aggregator, **kwargs)

        if not self.ai_client.is_cp4d:
            self.usage_client.update_plan_usage(count)

        return metrics

    def compute_metrics_as_job(self, spark_credentials: dict, configuration: dict, background=True, timeout=JOB_TIMEOUT, **kwargs):
        """
         Compute research metrics as spark job on remote spark.

        :param dict spark_credentials: Remote spark connection information.
        :param dict configuration: Configuration for computing metrics. Configuration also include the information about where to read data from. Eg: Hive or DB2.
        :return: Key/Value pair where key is the metric group name and value is an object consisting of the metric results for all individual metrics.
        :rtype: dict

        This is how the parameters look like

        >>>
        spark_credentials = {
            "connection": {
                "endpoint": "<JOB_ENDPOINT>",
                "location_type": "cpd_iae",
                "display_name": "<IAE_INSTANCE_NAME>",
                "instance_id": "<IAE_INSTANCE_ID>",
                "volume": "<MY_VOLUME>"
            },
            "credentials": {
                "username": "admin",
                "apikey":"<API_KEY"
            }
        }
        from ibm_metrics_plugin.common.utils.constants import FairnessMetricType
        metric_config = {
            "problem_type":"binary",
            "label_column" : "Risk",
            "fairness": {
                            "metrics_configuration": {
                                FairnessMetricType.SPD.value: {
                                    "features": [ ["Sex"],["Age"] ]                                
                                }    
                            },
                            "protected_attributes": [
                                {
                                    "feature": "Sex",
                                    "reference_group": ["male"],
                                    "monitored_group": ["female"],
                                    "threshold": 0.95,
                                },
                                {
                                    "feature": "Age",
                                    "reference_group": [[26, 55],[56,75]],
                                    "monitored_group": [[18, 25]],
                                    "threshold": 0.95,
                                },
                            ],
                            "favourable_label": ["No Risk"],
                            "unfavourable_label": ["Risk"],
                            "min_records": 100
                        }
        }
        configuration = {
            "spark_settings": {
                "max_num_executors": 4,
                "executor_cores": 1,
                "executor_memory": "1",
                "driver_cores": 1,
                "driver_memory": "1"
            },
            "arguments": {
                "storage": {
                    "type": "hive",
                    "connection": {
                        "location_type": "metastore",
                        "metastore_url": "<METASTORE_URL>"
                    }
                },
                "tables": [
                    {
                        "type": "training",
                        "database": "<DB_NAME>",
                        "schema": "",
                        "table": "<TABLE_NAME>"
                    }
                ]   
            }
        }
        configuration['arguments']['metric_configuration'] = metric_config

        A way you might use me is:
        >>> client.ai_metrics.compute_metrics_as_job(spark_credentials, configuration)

        """
        print("Computing metrics as spark Job")

        engine_client_module = None
        evaluation_job_module = None

        try:
            engine_client_module = __import__(
                "ibm_wos_utils.joblib.clients.engine_client", fromlist=["EngineClient"])
            evaluation_job_module = __import__(
                "ibm_metrics_plugin.core.metrics_evaluation_job", fromlist=["MetricsEvaluationJob"])
        except Exception as e:
            msg = "Unable to find ibm-wos-utils library to compute metrics as Job. Please install it "
            raise Exception(msg)

        # Allow user to compute metrics only for a plan having the usage within limit on cloud
        self.__check_plan_usage()

        self.engine_client = getattr(
            engine_client_module, "EngineClient")(spark_credentials)

        metrics_evaluation_job = getattr(
            evaluation_job_module, "MetricsEvaluationJob")
        files = kwargs.get("data_file_list")

        job_response = self.engine_client.engine.run_job(
            job_name="metrics_evaluation_job", job_class=metrics_evaluation_job, job_args=configuration, data_file_list=files, background=background, timeout=timeout)

        if not self.ai_client.is_cp4d:
            self.usage_client.update_plan_usage()

        return job_response

    def __get_job_status(self, job_response):
        """Check the metrics evaluation job status"""
        try:
            from ibm_wos_utils.joblib.utils.notebook_utils import JobStatus
        except Exception:
            msg = "Unable to find ibm-wos-utils library to get Job status. Please install it."
            raise Exception(msg)

        return JobStatus(self.engine_client, job_response)

    def get_job_output(self, job_response):
        """Check the metrics evaluation job status and return the output on completion."""
        job_status = self.__get_job_status(job_response)
        job_status.print_status()

        if job_status.status == "FINISHED":
            job_output = self.engine_client.engine.get_file(
                job_response.get("output_file_path") + "/output.json").decode("utf-8")
        elif job_status.status == "FAILED" or job_status.job_state in ("error", "dead", "killed", "failed"):
            job_output = self.engine_client.engine.get_file(job_response.get(
                "output_file_path") + "/exception.json").decode("utf-8")

        return json.loads(job_output)

    def fit_transformer(self, spark=None, configuration=None, data_frame=None, **kwargs):
        """
            Train a metric transformer.
        :param SparkSession spark: Spark session object to be used for evaluation.
        :param dict configuration: Configuration for fitting the transformer.
        :param Union[DataFrame, pd.DataFrame] data_frame: Dataframe on which the transformer is to be trained upon.
        :return: Instance of WOSTransformer
        :rtype: WOSTransformer

        This is how the configuration parameter dict will look like

        >>>
        from ibm_metrics_plugin.common.utils.constants import FairnessMetricType
        configuration = {}
        configuration["configuration"] = {
            "fairness": {
                "metrics_configuration": {
                    FairnessMetricType.FST.value: {
                        "params": {
                            "epsilon": 0.01,
                            "criteria": "MSP"
                        },
                        "features": {"probabilities": <PROBABILITY_COLUMN_NAME>, "protected": <PROTECTED_ATTRIBUTE_NAME>}
                    }
                }     
            }
        }

        A way you might use me is:
        >>> client.ai_metrics.fit_transformer(spark, configuration, data_frame)

        """

        self.__validate_params(spark, data_frame, None, configuration)

        try:
            metric_manager_module = __import__(
                "ibm_metrics_plugin.core.metrics_manager", fromlist=["MetricManager"])
        except Exception as e:
            msg = "Unable to find metric-plugins library to compute metrics. Please install it "
            raise Exception(msg)

        # Allow user to compute metrics only for a plan having the usage within limit on cloud
        self.__check_plan_usage()

        count = 1
        record_length = len(data_frame)
        if self.limit < record_length:
            # Modify the records in case of a lite plan
            if not self.is_paid_plan:
                data_frame = data_frame.iloc[:self.limit].copy()
            else:
                count = math.ceil(record_length/self.limit)

        conf = self.__set_additional_configuration(
            configuration, self.ai_client.is_cp4d)

        metric_manager = getattr(metric_manager_module, "MetricManager")()
        result = metric_manager.fit_transformer(
            spark=spark, configuration=conf, data_frame=data_frame, **kwargs)

        if not self.ai_client.is_cp4d:
            self.usage_client.update_plan_usage(count)

        return result

    def fit_transformer_as_job(self, spark_credentials: dict, configuration: dict, **kwargs):
        """
         Fit metric transformer as spark Job

        :param dict spark_credentials: Remote spark connection information.
        :param dict configuration: Configuration for fitting the transformer. Configuration also include the information about where to read data from. Eg: Hive or DB2.
        :return: Instance of WOSTransformer
        :rtype: WOSTransformer

        This is how the parameters look like

        >>>
        spark_credentials = {
            "connection": {
                "endpoint": "<JOB_ENDPOINT>",
                "location_type": "cpd_iae",
                "display_name": "<IAE_INSTANCE_NAME>",
                "instance_id": "<IAE_INSTANCE_ID>",
                "volume": "<MY_VOLUME>"
            },
            "credentials": {
                "username": "admin",
                "apikey":"<API_KEY"
            }
        }
        from ibm_metrics_plugin.common.utils.constants import FairnessMetricType
        metric_config = {
            "problem_type":"binary",
            "label_column" : "Risk",
            "fairness": {
                "metrics_configuration": {
                    FairnessMetricType.FST.value: {
                        "params": {
                            "epsilon": 0.01,
                            "criteria": "MSP"
                        },
                        "features": {"probabilities": <PROBABILITY_COLUMN_NAME>, "protected": <PROTECTED_ATTRIBUTE_NAME>}
                    }
                }     
            }
        }
        configuration = {
            "spark_settings": {
                "max_num_executors": 4,
                "executor_cores": 1,
                "executor_memory": "1",
                "driver_cores": 1,
                "driver_memory": "1"
            },
            "arguments": {
                "storage": {
                    "type": "hive",
                    "connection": {
                        "location_type": "metastore",
                        "metastore_url": "<METASTORE_URL>"
                    }
                },
                "tables": [
                    {
                        "type": "training",
                        "database": "<DB_NAME>",
                        "schema": "",
                        "table": "<TABLE_NAME>"
                    }
                ]   
            }
        }
        configuration['arguments']['metric_configuration'] = metric_config

        A way you might use me is:

        >>> client.ai_metrics.fit_transformer_as_job(spark_credentials, configuration)
        """

        # This requires dependency on WOS utils
        print("Fit transformer as spark Job")

        engine_client_module = None
        evaluation_job_module = None

        try:
            engine_client_module = __import__(
                "ibm_wos_utils.joblib.clients.engine_client", fromlist=["EngineClient"])
            evaluation_job_module = __import__(
                "ibm_metrics_plugin.core.fit_transformer_job", fromlist=["FitTransformerJob"])
        except Exception as e:
            msg = "Unable to find ibm-wos-utils library to compute metrics as Job. Please install it "
            raise Exception(msg)

        # Allow user to compute metrics only for a plan having the usage within limit on cloud
        self.__check_plan_usage()

        fairness_metrics_conf = get(
            configuration, "arguments.metric_configuration.fairness.metrics_configuration")

        conf = self.__set_additional_configuration_for_job(
            configuration, self.ai_client.is_cp4d)

        engine_client = getattr(engine_client_module,
                                "EngineClient")(spark_credentials)
        metrics_evaluation_job = getattr(
            evaluation_job_module, "FitTransformerJob")
        files = kwargs.get("data_file_list")
        timeout = kwargs.get("timeout")
        if timeout is None:
            timeout = 600

        job_response = engine_client.engine.run_job(job_name="fit_transformer_job", job_class=metrics_evaluation_job,
                                                    job_args=configuration, data_file_list=files, background=False, timeout=timeout)

        transformer = None
        state = job_response.get("state")
        print("Fit transformer job complete with state {}".format(state))
        if state and str(state).lower() in ["finished", "success"]:
            try:
                metric_type_module = __import__(
                    "ibm_metrics_plugin.common.utils.constants", fromlist=["FairnessMetricType"])
            except Exception as e:
                msg = "Unable to find ibm-metrics-plugin library to compute metrics. Please install it "
                raise Exception(msg)
            metric_type = getattr(metric_type_module, "FairnessMetricType")
            fairness_tpsd_type = None
            for fairness_metric_type in fairness_metrics_conf:
                if fairness_metric_type in [metric_type.TPSD.value, metric_type.TP.value]:
                    fairness_tpsd_type = metric_type
            if fairness_tpsd_type is None:
                import pickle
                transformer_pickle = engine_client.engine.download_directory(
                    job_response["output_file_path"] + "/transformer.pkl")
                transformer = pickle.loads(transformer_pickle)
        else:
            print("Job failed with response: {}".format(job_response))

        if not self.ai_client.is_cp4d:
            self.usage_client.update_plan_usage()

        return transformer

    def transform_result(self, metrics_result, metric_group_type, metric_type, **kwargs):
        """Transform the json metric result to the required object.
        For SHAP metric, the result is transformed to SHAP explanation objects which can then be used to plot the explanations.
        An exception is thrown when invoked for metric which do not support transformation of result."""
        try:
            from ibm_metrics_plugin.common.utils.constants import MetricGroupType, ExplainabilityMetricType
            from ibm_metrics_plugin.metrics.explainability.explainers.shap.shap_explanation import ShapExplanation
        except Exception:
            msg = "Unable to find metric-plugins library. Please install it "
            raise Exception(msg)

        results = self.__get_value(metrics_result, "metrics_result")
        if metric_group_type == MetricGroupType.EXPLAINABILITY.value and metric_type == ExplainabilityMetricType.SHAP.value:
            explain_results = self.__get_value(results, metric_group_type)
            shap_result = self.__get_value(explain_results, metric_type)
            return ShapExplanation.get_shap_explanation(shap_result, **kwargs)
        else:
            raise Exception(
                "There is no transformation supported for the given metric group type and metric type.")

    def show_supported_fairness_metrics(self):
        self.__show_supported_metrics(show_fairness=True)

    def show_supported_explainers(self):
        self.__show_supported_metrics(show_explainers=True)

    def __show_supported_metrics(self, show_fairness=False, show_explainers=False):
        try:
            metric_type_module = __import__("ibm_metrics_plugin.common.utils.constants", fromlist=[
                                            "FairnessMetricType,ExplainabilityMetricType"])
        except Exception as e:
            msg = "Unable to find ibm-metrics-plugin library to list supported metrics. Please install the library "
            raise Exception(msg)
        if show_fairness:
            metric_type = getattr(metric_type_module, "FairnessMetricType")
            print(
                "# from ibm_metrics_plugin.common.utils.constants import FairnessMetricType")
            print("Following fairness metrics are supported")
            print("")
            for m in metric_type:
                print("{}".format(m))
            print("")

        if show_explainers:
            metric_type = getattr(metric_type_module,
                                  "ExplainabilityMetricType")
            print(
                "# from ibm_metrics_plugin.common.utils.constants import ExplainabilityMetricType")
            print("Following Explainers are supported")
            print("")
            for m in metric_type:
                print("{}".format(m))
            print("")

    def __validate_params(self, spark, data_frame, metric_aggregator, configuration):
        data_frame_instance = None
        spark_session_instance = None
        accumulator_instance = None
        expected_data_frame_type = [pd.DataFrame]
        if spark:
            try:
                spark_session_module = __import__("pyspark.sql.session", fromlist=[
                                                  "SparkSession", "DataFrame"])
                accumulators_module = __import__(
                    "pyspark.accumulators", fromlist=["Accumulator"])

                spark_session_instance = getattr(
                    spark_session_module, "SparkSession")
                data_frame_instance = getattr(
                    spark_session_module, "DataFrame")
                accumulator_instance = getattr(
                    accumulators_module, "Accumulator")
                expected_data_frame_type.append(data_frame_instance)
            except Exception as e:
                msg = "Unable to find spark library. Please install it "
                raise Exception(msg)

            validate_type(spark, "spark", spark_session_instance, True)
            validate_type(metric_aggregator, "metric_aggregator",
                          accumulator_instance, False)

        validate_type(data_frame, "data_frame", expected_data_frame_type, True)
        validate_type(configuration, "configuration", dict, True)

    def __set_additional_configuration_for_job(self, configuration, is_cp4d):
        conf = configuration.copy()
        conf["arguments"]["metric_configuration"]["is_cp4d"] = is_cp4d
        return conf

    def __set_additional_configuration(self, configuration, is_cp4d):
        conf = configuration.copy()
        conf["configuration"]["is_cp4d"] = is_cp4d
        return conf

    def __check_plan_usage(self):
        if self.ai_client.is_cp4d is not True:
            self.is_paid_plan = is_entitled_on_cloud(self.ai_client.service_url,
                                 self.ai_client.service_instance_id, self.token)
            self.limit = self.usage_client.check_plan_usage_and_get_limit(is_paid_plan=self.is_paid_plan)

    def __get_value(self, result, key):
        value = result.get(key)
        if not value:
            raise Exception(
                "Unable to find {0} attribute in the result.".format(key))
        return value
