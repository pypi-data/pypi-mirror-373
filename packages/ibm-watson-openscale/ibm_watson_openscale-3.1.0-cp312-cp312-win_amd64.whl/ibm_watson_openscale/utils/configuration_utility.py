# coding: utf-8

# Copyright 2023, 2024 IBM All Rights Reserved.
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

import logging
import os
import tarfile
import warnings
from collections import Counter
from copy import deepcopy
from io import BytesIO
from json import dumps, loads
from random import sample
from time import time
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd
from ibm_metrics_plugin.common.utils.constants import (AssetType,
                                                       InputDataType,
                                                       MetricGroupType,
                                                       ProblemType)

from ibm_watson_openscale.utils import (check_package_exists,
                                        create_download_link, get,
                                        validate_enum, validate_image_path,
                                        validate_pandas_dataframe,
                                        validate_type)
from ibm_watson_openscale.utils.async_utils import run_in_event_loop
from ibm_watson_openscale.utils.constants import DRIFT_DEPRECATION_MESSAGE


class ConfigurationUtility():

    SEED = 272
    SCORE_BATCH_SIZE = 5000
    SCORE_BATCH_SIZE_IMAGE = 50

    def __init__(self, training_data: pd.DataFrame, common_parameters: dict, scoring_fn: callable = None,
                 batch_size: int = None, **kwargs):

        check_package_exists()
        validate_type(training_data, "training_data", pd.DataFrame, True)
        validate_type(common_parameters, "common_parameters", dict, True)

        self.training_data = training_data
        self.common_parameters = common_parameters
        self.batch_size = batch_size

        self.asset_type = self.common_parameters.get("asset_type")
        validate_enum(self.asset_type,
                      "'asset_type' in common_parameters", AssetType, False)
        if not self.asset_type:
            warnings.warn(
                "asset_type is needed in common parameters", FutureWarning)
            self.asset_type = AssetType.MODEL.value

        self.problem_type = self.common_parameters.get("problem_type")
        validate_enum(self.problem_type,
                      "'problem_type' in common_parameters", ProblemType, True)
        self.problem_type = ProblemType(self.problem_type)
        if not self.problem_type.is_supported(self.asset_type):
            raise ValueError(
                f"Problem type '{self.problem_type.value}' is not supported for '{self.asset_type.value}' assets.")

        self.input_data_type = self.common_parameters.get("input_data_type")
        validate_enum(self.input_data_type,
                      "'input_data_type' in common_parameters", InputDataType, True)

        if self.batch_size is not None and (not isinstance(self.batch_size, int) or self.batch_size <= 0):
            raise ValueError(
                f"Invalid value for 'batch_size' was given: {self.batch_size}. Must be an integer > 0")
        elif not self.batch_size:
            if self.input_data_type == InputDataType.IMAGE.value:
                self.batch_size = ConfigurationUtility.SCORE_BATCH_SIZE_IMAGE
            else:
                self.batch_size = ConfigurationUtility.SCORE_BATCH_SIZE

        self.label_column = self.common_parameters.get("label_column")
        validate_type(self.label_column,
                      "'label_column' in common_parameters", str, True)

        self.prediction_column = self.common_parameters.get(
            "prediction_column")
        validate_type(self.prediction_column,
                      "'prediction_column' in common_parameters", str, True)

        self.image_path_column = self.common_parameters.get(
            "image_path_column")
        if self.input_data_type == InputDataType.IMAGE.value:
            validate_type(self.image_path_column,
                          "'image_path_column' in common_parameters", str, True)
            validate_image_path(self.training_data, **self.common_parameters)

        self.meta_columns = self.common_parameters.get("meta_columns", [])
        validate_type(self.meta_columns,
                      "'meta_columns' in common_parameters", list, False)
        if self.meta_columns is None:
            self.meta_columns = []

        self.probability_column = None
        self.class_probabilities = None
        if self.problem_type.is_classification():
            self.probability_column = self.common_parameters.get(
                "probability_column")

            if self.probability_column is not None:
                validate_type(
                    self.probability_column,
                    "'probability_column' in common_parameters",
                    str,
                    True)

            self.class_probabilities = self.common_parameters.get(
                "class_probabilities")
            if not (not self.class_probabilities):
                # if class_probabilities is specified, it must be a list
                validate_type(
                    self.class_probabilities,
                    "'class_probabilities' in common_parameters",
                    list,
                    True)

            # explicitly set class_probabilities to None
            self.class_probabilities = None if not self.class_probabilities else \
                self.class_probabilities

        if self.problem_type.is_classification() and \
            not self.probability_column and \
                not self.class_probabilities:
            raise Exception(
                "One of 'probability_column' or 'class_probabilities' " +
                "must be specified for classification models.")

        if self.problem_type.is_classification() and \
                self.probability_column and \
                self.class_probabilities:
            raise Exception(
                "Both 'probability_column' and 'class_probabilities' were detected in the configuration." +
                "One of 'probability_column' or 'class_probabilities' " +
                "must be specified for classification models.")

        self.feature_columns = self.common_parameters.get(
            "feature_columns") or []
        if not self.feature_columns and self.input_data_type != InputDataType.IMAGE.value:
            self.feature_columns = list(self.training_data.columns)
            self.feature_columns.remove(self.label_column)

            if self.prediction_column in self.training_data.columns:
                # remove prediction column from feature columns
                self.feature_columns.remove(self.prediction_column)

            if self.probability_column and self.probability_column in self.training_data.columns:
                # remove probability column from feature columns
                self.feature_columns.remove(self.probability_column)

            if self.class_probabilities and \
                    (set(self.class_probabilities) <= set(self.training_data.columns)):
                # remove class probability columns from feature columns
                self.feature_columns = [
                    x for x in self.feature_columns if x not in self.class_probabilities]

            if self.meta_columns:
                # remove meta columns from the feature columns
                self.feature_columns = [
                    column for column in self.feature_columns if column not in self.meta_columns]

            # Setting this in common parameters as this is being used downstream.
            self.common_parameters["feature_columns"] = self.feature_columns

        validate_type(self.feature_columns,
                      "'feature_columns' in common_parameters", list, True)

        self.categorical_columns = self.common_parameters.get(
            "categorical_columns") or []
        if not self.categorical_columns and self.input_data_type != InputDataType.IMAGE.value:
            self.categorical_columns = list(self.training_data[self.feature_columns].select_dtypes(
                include=["bool", "object"]).columns)

            # Setting this in common parameters as this is being used downstream.
            self.common_parameters["categorical_columns"] = self.categorical_columns

        validate_type(self.categorical_columns,
                      "'categorical_columns' in common_parameters", list, True)

        self.text_columns = self.common_parameters.get("text_columns", [])
        # Read class labels order from user. A workaround when the order of all classes can't be determined by scoring
        self.class_labels = self.common_parameters.get("class_labels") or []
        validate_type(self.class_labels,
                      "'class_labels' in common_parameters", list, False)

        # Monitor Flags
        self.enable_explainability = self.common_parameters.get(
            "enable_explainability", True)
        self.enable_fairness = self.common_parameters.get(
            "enable_fairness", True)
        self.enable_drift_v2 = self.common_parameters.get(
            "enable_drift_v2", True)
        self.enable_drift = self.common_parameters.get("enable_drift", False)

        if self.enable_drift:
            warnings.warn(DRIFT_DEPRECATION_MESSAGE, FutureWarning)

        # Remaining initializations
        self.training_stats = {}
        self.data_schema = {}
        self.explain_configuration = {}
        self.scored_perturbations = None
        self.explainability_parameters = {}
        self.scoring_fn = scoring_fn
        self.training_data_global_explanation = None
        self.global_explanation_method = None

        if (self.enable_drift_v2 or self.enable_explainability) and \
                (not self.class_labels) and (self.problem_type.is_classification()):
            # Set the class labels if they are not set
            # for classification problems
            self.__set_class_labels()

    def get_explainability_archive(self, parameters: Dict, **kwargs) -> bytes:
        """Creates the explain archive

        :param parameters: The explain parameters
        :type parameters: Dict
        :raises ValueError: When the `class_labels` do not match.
        :return: The Explain Archive
        :rtype: bytes
        """

        self.explainability_parameters = {** parameters}

        self.__validate_explainability_params()

        if self.explainability_parameters and self.explainability_parameters.get(
                "global_explanation"):
            # set the default global explanation method as lime
            self.global_explanation_method = self.explainability_parameters.get(
                "global_explanation").get("explanation_method") or "lime"
        else:
            self.global_explanation_method = None

        archive_data = {}
        # Add training data statistics
        if self.scoring_fn and self.problem_type.is_classification():
            self.__set_class_labels_in_explain()
        archive_data["training_statistics.json"] = dumps(
            {"training_statistics": self.explain_configuration}, indent=4)

        # Add lime scored perturbations
        if self.scoring_fn and self.input_data_type != "hybrid":
            self.scored_perturbations = self.__get_lime_scored_perturbations()
            archive_data["lime_scored_perturbations.json"] = dumps(
                self.scored_perturbations, indent=4)

        # Add shap related files
        if self.explainability_parameters:
            archive_data.update(self.__get_shap_background_data_sets())
            archive_data.update(
                self.__get_global_explanation(archive_data, **kwargs))
            archive_data["configuration.json"] = dumps(
                {"parameters": self.explainability_parameters}, indent=4)

        return self.create_archive_as_bytes(data=archive_data)

    def __validate_explainability_params(self):
        if self.input_data_type == "hybrid":
            if bool(get(self.explainability_parameters, "global_explanation.enabled")):
                raise Exception("The global explanation is not supported for the input data type '{0}'.".format(
                    self.input_data_type))
            if bool(get(self.explainability_parameters, "shap.enabled")):
                raise Exception("The SHAP explanation method is not supported for the input data type '{0}'.".format(
                    self.input_data_type))
            if len(self.text_columns) > 1:
                raise Exception(
                    "Explainability is not supported for models with more than one text column.")

    def get_drift_v2_archive(self, parameters: Dict, **kwargs) -> bytes:
        """Creates the Drift v2 archive

        :param parameters: The Drift v2 parameters
        :type parameters: Dict
        :return: The Drift v2 archive
        :rtype: bytes
        """

        from ibm_metrics_plugin.metrics.drift_v2.impl.drift_metric_evaluator import \
            DriftMetricsEvaluator
        from ibm_metrics_plugin.metrics.drift_v2.utils.drift_utils import \
            serialise_as_json

        feature_importance = kwargs.get("feature_importance")
        most_important_features = []
        if feature_importance is not None:
            # 1. If the user has provided feature_importance, give it first priority
            # Also, check for most_important_features
            # All validation happens in metrics plugin
            most_important_features = []
        elif self.training_data_global_explanation is not None:
            # 2. If feature importance was not provided, use the training data
            # global explanation, if available
            feature_importance = self.training_data_global_explanation
        else:
            # 3. Fallback. Compute training data global explanation.
            self.__compute_global_explanation_for_drift_v2(**kwargs)
            feature_importance = self.training_data_global_explanation

        metrics_config = self.__get_drift_metrics_config(parameters)
        data = None
        if not parameters.get("max_samples"):
            self.training_data = self.__score_data(
                data=self.training_data, **kwargs)
            data = self.training_data.copy()
        else:
            from ibm_metrics_plugin.common.utils.python_utils import \
                stratified_sample
            data = stratified_sample(
                data=self.training_data,
                column=self.label_column,
                max_samples=parameters.get("max_samples"))
            data = self.__score_data(data=data, **kwargs)

        evaluator = DriftMetricsEvaluator()
        drift_data_set, _ = run_in_event_loop(evaluator.fit(configuration=metrics_config,
                                                            data_frame=data,
                                                            feature_importance=feature_importance,
                                                            most_important_features=most_important_features))

        data = serialise_as_json(drift_data_set)

        return self.create_archive_as_bytes(data)

    @classmethod
    def get_global_explanation(cls, explainability_archive: Union[bytes, str] = None, metrics_result: Dict = None) -> Dict:
        """Get the global explanation from the given explainability archive or metrics_result.

        :param explainability_archive: The explainability archive could be bytes or the path to explainability.tar.gz file., defaults to None
        :type explainability_archive: Union[bytes, str], optional
        :param metrics_result: The metrics_result is the output of ai_metrics.compute_metrics method., defaults to None
        :type metrics_result: Dict, optional
        :raises Exception: If both explainability_archive and metrics_result are not present.
        :return: The global explanation
        :rtype: Dict
        """
        """
        Get the global explanation from the given explainability archive or metrics_result.

        Arguments:
            explainability_archive: 
            metrics_result: The metrics_result is the output of ai_metrics.compute_metrics method.
        """
        global_exp = None

        if explainability_archive:
            if isinstance(explainability_archive, bytes):
                archive_bytes = explainability_archive
            else:
                with open(explainability_archive, "rb") as f:
                    archive_bytes = f.read()

            archive_obj = BytesIO(archive_bytes)
            with tarfile.open(fileobj=archive_obj) as tar:
                for member in tar.getmembers():
                    if "training_data_global_explanation.json" in member.name:
                        with tar.extractfile(member) as f:
                            global_exp = loads(f.read()).get(
                                "global_explanation")
                            break
        elif metrics_result:
            global_exp = get(
                metrics_result, "metrics_result.explainability.shap.global_explanation")
        else:
            raise Exception(
                "The arguments provided to the method are invalid. One of explainability_archive or metrics_result should be provided as input.")

        return global_exp

    def __get_lime_scored_perturbations(self):
        from ibm_wos_utils.explainability.utils.perturbations import \
            Perturbations
        perturbations_count = get(
            self.explainability_parameters, "lime.perturbations_count", 5000)
        perturbations = Perturbations(
            training_stats=self.explain_configuration, problem_type=self.problem_type.value, perturbations_count=perturbations_count, output_data_schema=self.data_schema)
        perturbs_df = perturbations.generate_perturbations()

        # use score function to score generated perturbations
        res = self.scoring_fn_helper(
            perturbs_df, self.common_parameters)

        if self.problem_type.is_classification():
            if isinstance(res, pd.DataFrame):
                scored_perturbations = {
                    "probabilities": res[self.probability_column].tolist(),
                    "predictions": res[self.prediction_column].tolist()
                }
            elif isinstance(res, tuple) or isinstance(res, np.ndarray):
                probabilities = res[0]
                predictions = res[1]
                scored_perturbations = {
                    "probabilities": probabilities.tolist(),
                    "predictions": predictions.tolist()
                }
        else:

            if isinstance(res, pd.DataFrame):
                scored_perturbations = {
                    "predictions": res[self.prediction_column].tolist()
                }
            elif isinstance(res, tuple) or isinstance(res, np.ndarray):
                scored_perturbations = {
                    "predictions": res.tolist()
                }

        return scored_perturbations

    def __get_shap_background_data(self):
        base_values = self.explain_configuration.get(
            "base_values").copy()
        background_df = pd.DataFrame({
            self.feature_columns[int(k)]: [v] for k, v in base_values.items()})

        # Set dtype for int columns in background_df
        if self.data_schema:
            features_schema = {f.get("name"): f.get("type")
                               for f in self.data_schema.get("fields")}
            for f in self.feature_columns:
                feature_data_type = features_schema.get(f)
                if feature_data_type:
                    feature_data_type = feature_data_type.lower()
                    if any(i in feature_data_type for i in ["int", "integer", "long"]):
                        background_df[f] = background_df[f].astype(int)

        return background_df

    def __get_training_global_explanation(self, training_data, background_data=None):
        from ibm_metrics_plugin.common.utils.constants import (
            ExplainabilityMetricType, MetricGroupType)
        from ibm_metrics_plugin.core.metrics_manager import MetricManager
        from ibm_metrics_plugin.metrics.explainability.util.explain_util import ExplainUtil
        from ibm_metrics_plugin.metrics.explainability.entity.constants import MAX_GLOBAL_EXP_SIZE

        if self.global_explanation_method == ExplainabilityMetricType.SHAP.value:
            metrics_config = self.__get_shap_metrics_config()
            metrics_result = MetricManager().evaluate(spark=None,
                                                      configuration=metrics_config,
                                                      data_frame=training_data,
                                                      scoring_fn=self.scoring_fn,
                                                      background_data=background_data)
            metrics_result["metrics_result"][MetricGroupType.EXPLAINABILITY.value][self.global_explanation_method]["global_explanation"]["background_data_set"] = get(
                self.explainability_parameters, "shap.background_data_set")
        else:
            metrics_config = self.__get_lime_metrics_config()
            metrics_result = MetricManager().evaluate(spark=None,
                                                      configuration=metrics_config,
                                                      data_frame=training_data,
                                                      scoring_fn=self.scoring_fn)
        exps = metrics_result["metrics_result"][
            MetricGroupType.EXPLAINABILITY.value][self.global_explanation_method]

        global_explanation = exps.get("global_explanation")
        local_explanations = exps.get("local_explanations")
        local_exps = sample(local_explanations, 1000) if len(
            local_explanations) > 1000 else local_explanations
        if self.global_explanation_method == ExplainabilityMetricType.SHAP.value:
            local_exps = self.__convert_local_shap_explanations(local_explanations=local_exps,
                                                                class_labels=global_explanation.get("class_labels"))
        else:
            from ibm_metrics_plugin.metrics.explainability.explainers.lime.lime_tabular_explainer import \
                get_lime_explanations_distribution
            local_exps = get_lime_explanations_distribution(local_explanations=local_exps,
                                                            global_explanation=global_explanation)

        # Compute class_labels_count
        if not self.problem_type.is_classification() and self.label_column:
            global_explanation["class_labels_count"] = self.training_data[self.label_column]\
                .value_counts().to_dict()

        self.training_data_global_explanation = global_explanation.copy()
        current_explanation = {
            "global_explanation": global_explanation,
            "local_explanations": local_exps
        }

        max_exp_size = int(
            get(self.explainability_parameters, "global_explanation.max_explanation_size", MAX_GLOBAL_EXP_SIZE))
        min_distribution_size = int(get(
            self.explainability_parameters, "global_explanation.min_distribution_size", 200))
        min_distribution_features_count = int(get(
            self.explainability_parameters, "global_explanation.min_distribution_features_count", 50))

        current_explanation = ExplainUtil.transform_explanation_summary(
            explanation=current_explanation, max_exp_size=max_exp_size, min_distribution_size=min_distribution_size, min_distribution_features_count=min_distribution_features_count)

        return current_explanation

    def __get_shap_metrics_config(self):
        from ibm_metrics_plugin.common.utils.constants import (
            ExplainabilityMetricType, MetricGroupType)
        from ibm_metrics_plugin.metrics.explainability.entity.constants import (
            ShapAggregationMethod, ShapAlgorithm)

        if self.data_schema:
            features_schema = {f.get("name"): f.get("type")
                               for f in self.data_schema.get("fields")}
        else:
            features_schema = {}

        shap_params = deepcopy(self.explainability_parameters.get(
            ExplainabilityMetricType.SHAP.value)) or {}

        # Set aggregation methods
        agg_methods = self.explainability_parameters["global_explanation"].get(
            "aggregation_methods")
        if agg_methods:
            shap_params["aggregation_methods"] = agg_methods
        else:
            shap_params["aggregation_methods"] = [
                ShapAggregationMethod.MEAN_ABS.value, ShapAggregationMethod.MAX_ABS.value]

        # set algorithm
        algorithm = self.explainability_parameters["shap"].get("algorithm")
        if not algorithm:
            shap_params["algorithm"] = ShapAlgorithm.KERNEL.value

        return {
            "configuration": {
                "problem_type": self.problem_type.value,
                "input_data_type": self.input_data_type,
                "asset_type": self.asset_type,
                "feature_columns": self.feature_columns,
                "categorical_columns": self.categorical_columns,
                "label_column": self.label_column,
                "features_schema": features_schema,
                MetricGroupType.EXPLAINABILITY.value: {
                    "metrics_configuration": {
                        ExplainabilityMetricType.SHAP.value: shap_params
                    }
                }
            }
        }

    def __get_drift_metrics_config(self, parameters):
        from ibm_metrics_plugin.common.utils.constants import MetricGroupType

        parameters["archive_creation_flag"] = False

        return {
            "configuration": {
                "problem_type": self.problem_type.value,
                "input_data_type": self.input_data_type,
                "asset_type": self.asset_type,
                "feature_columns": self.feature_columns,
                "image_path_column": self.image_path_column,
                "meta_columns": self.meta_columns,
                "categorical_columns": self.categorical_columns,
                "label_column": self.label_column,
                "prediction_column": self.prediction_column,
                "probability_column": self.__get_probability_column(),
                MetricGroupType.DRIFT.value: {
                    "metrics_configuration": parameters
                }
            }
        }

    def __get_lime_metrics_config(self):
        from ibm_metrics_plugin.common.utils.constants import (
            ExplainabilityMetricType, MetricGroupType)

        if self.data_schema:
            features_schema = {f.get("name"): f.get("type")
                               for f in self.data_schema.get("fields")}
        else:
            features_schema = {}

        lime_params = deepcopy(self.explainability_parameters.get(
            ExplainabilityMetricType.LIME.value)) or {"perturbations_count": 5000}
        lime_params["include_input_features"] = True

        metrics_config = {
            "configuration": {
                "problem_type": self.problem_type.value,
                "input_data_type": self.input_data_type,
                "asset_type": self.asset_type,
                "feature_columns": self.feature_columns,
                "categorical_columns": self.categorical_columns,
                "label_column": self.label_column,
                "features_schema": features_schema,
                "prediction": self.prediction_column,
                "probability": self.__get_probability_column(),
                MetricGroupType.EXPLAINABILITY.value: {
                    "metrics_configuration": {
                        ExplainabilityMetricType.LIME.value: lime_params
                    }
                }
            }
        }
        metrics_config["configuration"][MetricGroupType.EXPLAINABILITY.value]["training_statistics"] = self.explain_configuration
        scored_perturbations = self.scored_perturbations if self.scored_perturbations else \
            self.__get_lime_scored_perturbations()
        if scored_perturbations:
            metrics_config["configuration"][MetricGroupType.EXPLAINABILITY.value]["metrics_configuration"][
                ExplainabilityMetricType.LIME.value]["scored_perturbations"] = scored_perturbations
        return metrics_config

    def __convert_local_shap_explanations(self, local_explanations, class_labels):
        converted_exps = {}
        if local_explanations:
            shap_values = []
            base_values = []
            feature_values = []
            first_local_exp = local_explanations[0]
            feature_names = first_local_exp.get("feature_names")
            for e in local_explanations:
                shap_values.append(e.get("shap_values"))
                base_values.append(e.get("base_values"))
                feature_values.append(e.get("feature_values"))

            shap_values = np.asarray(shap_values)
            if len(shap_values.shape) == 3:
                shap_values = shap_values.transpose(1, 0, 2)

            converted_exps = {
                "class_labels": class_labels,
                "feature_names": feature_names,
                "feature_values": feature_values,
                "feature_importances": shap_values.tolist()
            }

        return converted_exps

    def __get_shap_background_data_sets(self):
        archive_data = {}
        shap_params = self.explainability_parameters.get("shap") or {}
        if bool(shap_params.get("enabled")):
            background_data_sets = shap_params.get(
                "background_data_sets") or []
            background_data_set = shap_params.get("background_data_set")

            # Add user provided background data files to archive
            for bd in background_data_sets:
                file_name = bd.get("file_name")
                with open(file_name) as f:
                    archive_data[bd.get("file_name")] = f.read()

            # Add training data generated background data
            background_df = self.__get_shap_background_data()
            archive_data["shap_training_background_data.csv"] = background_df.to_csv(
                index=False)
            background_data_sets.append(
                {"name": "training_background_data", "file_name": "shap_training_background_data.csv"})
            if not background_data_set:
                background_data_set = "training_background_data"

            self.explainability_parameters["shap"]["background_data_sets"] = background_data_sets
            self.explainability_parameters["shap"]["background_data_set"] = background_data_set

        return archive_data

    def __get_global_explanation(self, archive_data, **kwargs):
        archive_data_to_add = {}
        global_exp_params = self.explainability_parameters.get(
            "global_explanation") or {}
        shap_params = self.explainability_parameters.get("shap") or {}

        # Generate training data global explanation if enabled
        if not self.scoring_fn and bool(global_exp_params.get("enabled")):
            raise Exception(
                "Scoring function is required for configuring global explanation.")

        sample_size = get(self.explainability_parameters,
                          "global_explanation.training_data_sample_size", 1000)
        sample_size = min(len(self.training_data), sample_size)
        training_data_sample = self.training_data.sample(
            n=sample_size, random_state=ConfigurationUtility.SEED)

        if self.scoring_fn and bool(global_exp_params.get("enabled")):
            if bool(shap_params.get("enabled")) and self.global_explanation_method == "shap":
                background_data_set = shap_params.get("background_data_set")
                background_data_sets = shap_params.get("background_data_sets")
                background_file_name = next((b.get("file_name") for b in background_data_sets if b.get(
                    "name") == background_data_set), None)
                background_df = pd.read_csv(
                    BytesIO(bytes(archive_data.get(background_file_name), "utf-8")))
                archive_data_to_add["shap_training_data_global_explanation.json"] = dumps(self.__get_training_global_explanation(
                    training_data=training_data_sample, background_data=background_df))
            else:
                training_data_sample = self.__score_data(
                    data=training_data_sample, **kwargs)
                archive_data_to_add["lime_training_data_global_explanation.json"] = dumps(
                    self.__get_training_global_explanation(training_data=training_data_sample))

        return archive_data_to_add

    # def __check_label_target_dtypes_compatible(self):
    #     """Checks if the data types of label and target columns are compatible

    #     :raises ValueError: 1. If only one of the data type is string.
    #                         2. If one of them is integer and one of them is float, AND, the float can't be coerced to int.
    #     """
    #     label_column_dtype = self.__convert_numpy_dtypes_to_native(self.training_data[self.label_column].dtype)

    #     if self.prediction_column in self.training_data:
    #         prediction_vector = self.training_data[self.prediction_column]
    #     else:
    #         scored_result = self.scoring_fn(self.training_data[self.feature_columns].sample(10))
    #         prediction_vector = scored_result[1] if self.problem_type.is_classification() else scored_result

    #     prediction_column_dtype = self.__convert_numpy_dtypes_to_native(prediction_vector.dtype)

    #     # Raise error if the data types do not match:
    #     msg = f"The data types of the label column {self.label_column} and the prediction column {self.prediction_column} do not match. "
    #     msg += f"{self.label_column}'s data type is {label_column_dtype}. "
    #     msg += f"{self.prediction_column}'s data type is {prediction_column_dtype}."

    #     if label_column_dtype != prediction_column_dtype:
    #         raise ValueError(msg)

    # def __convert_numpy_dtypes_to_native(self, dtype: np.dtype) -> str:
    #     """Convert the column dtypes (numpy) to native types.

    #     Args:
    #         dtype (_type_): The dtype to convert.

    #     Raises:
    #         ValueError: If the dtype is not supported.

    #     Returns:
    #         _type_: The native type
    #     """

    #     if np.issubdtype(dtype, np.integer):
    #         return "int"

    #     if np.issubdtype(dtype, np.floating):
    #         return "float"

    #     if dtype.name.startswith("bool"):
    #         return "bool"

    #     if dtype.name.startswith('str') or dtype.name.startswith('unicode'):
    #         return "str"

    #     if dtype.name.startswith("datetime"):
    #         return "datetime"

    #     raise ValueError(f"Unsupported data type {dtype}.")

    def __set_class_labels(self):
        training_data_class_labels = self.training_data[self.label_column].unique(
        ).tolist()

        if not self.scoring_fn:
            self.class_labels = training_data_class_labels
            return

        self.class_labels = [None] * len(training_data_class_labels)
        empty_values = sum([label is None for label in self.class_labels])

        num_rows_to_score = 5
        iteration = 0

        while (empty_values > 0) and (iteration < 100):
            labels_to_score = list(
                set(training_data_class_labels) - set(self.class_labels))
            df = self.training_data[self.training_data[self.label_column].isin(labels_to_score)].groupby(self.label_column)\
                .apply(lambda x: x if len(x) < num_rows_to_score else x.sample(num_rows_to_score)).reset_index(drop=True)
            scored_labels = self.__get_labels(df)
            self.class_labels = [
                scored_labels[i] if label is None else label for i, label in enumerate(self.class_labels)]
            empty_values = sum([label is None for label in self.class_labels])
            if empty_values == 1:
                idx = self.class_labels.index(None)
                self.class_labels[idx] = (
                    set(training_data_class_labels) - set(self.class_labels)).pop()
                return
            iteration += 1

        if empty_values > 1:
            missing_labels = set(training_data_class_labels) - \
                set(self.class_labels)
            msg = f"Unable to find the correct order for training data labels: {training_data_class_labels}: "
            msg += f"from the model predictions. Missing labels: {missing_labels}. "
            msg += f"Please provide 'class_labels' in the common parameters to resolve this."

            raise Exception(msg)

    def __set_class_labels_in_explain(self):
        class_labels_in_stats = self.explain_configuration.get(
            "class_labels")
        if sorted(self.class_labels) != sorted(class_labels_in_stats):
            raise ValueError(
                "The list of class labels {0} in the training statistics and the class labels {1} provided in the input are not equal.".format(class_labels_in_stats, self.class_labels))
        self.explain_configuration["class_labels"] = self.class_labels
        return

    def __get_labels(self, df):
        if (self.prediction_column in self.training_data) and (self.probability_column in self.training_data):
            predictions = self.training_data[self.prediction_column].values
            probabilities = self.training_data[self.probability_column].values
        else:
            data = self.scoring_fn_helper(df, self.common_parameters)
            if isinstance(data, pd.DataFrame):
                probabilities, predictions = data[self.probability_column], data[self.prediction_column]
            elif isinstance(data, tuple) or isinstance(data, np.ndarray):
                probabilities = data[0]
                predictions = data[1]

        if predictions is None or (len(probabilities) != len(predictions)):
            return

        labels = [None]*len(probabilities[0])
        for probability, prediction in zip(probabilities, predictions):
            if probability is None:
                continue
            max_prob = max(probability)
            if Counter(probability)[max_prob] == 1:
                labels[np.argmax(probability)] = prediction.item() if type(
                    prediction).__module__ == np.__name__ else prediction
        return labels

    def create_archive_as_bytes(self, data):
        archive_data = None
        with BytesIO() as archive:
            with tarfile.open(fileobj=archive, mode="w:gz") as tf:
                for filename, filedata in data.items():
                    if isinstance(filedata, bytes):
                        content = BytesIO(filedata)
                    else:
                        content = BytesIO(filedata.encode("utf8"))
                    tarinfo = tarfile.TarInfo(filename)
                    tarinfo.size = len(content.getvalue())
                    tarinfo.mtime = time()
                    tf.addfile(
                        tarinfo=tarinfo, fileobj=content)
            archive_data = archive.getvalue()

        return archive_data

    def get_drift_archive(self, parameters):
        warnings.warn(DRIFT_DEPRECATION_MESSAGE, FutureWarning)
        from ibm_wos_utils.drift.drift_trainer import DriftTrainer

        drift_detection_input = {
            "enable_drift": self.enable_drift,
            "feature_columns": self.feature_columns,
            "categorical_columns": self.categorical_columns,
            "label_column": self.label_column,
            "problem_type": self.problem_type.value,
            "model_drift": parameters.get("model_drift"),
            "data_drift": parameters.get("data_drift")
        }

        # add score function
        drift_detection_input["model_drift"]["score"] = self.scoring_fn

        # train drift detection model, learn data constraints and get archive as bytes
        drift_archive = DriftTrainer(
            training_dataframe=self.training_data,
            drift_detection_input=drift_detection_input).run(persist_archive=False)
        return drift_archive

    def __compute_training_stats(self, fairness_parameters: Optional[Dict], **kwargs):
        drop_na = kwargs.get("drop_na", True)
        from ibm_watson_openscale.utils.training_stats import TrainingStats

        training_data_info = {**self.common_parameters}

        if self.enable_fairness:
            training_data_info["fairness_inputs"] = fairness_parameters

        training_stats = TrainingStats(
            training_data_frame=self.training_data,
            training_data_info=training_data_info,
            drop_na=drop_na
        )

        self.training_stats = training_stats.get_training_statistics()
        self.training_stats["notebook_version"] = self.common_parameters.get(
            "notebook_version")
        self.data_schema = get(self.training_stats,
                               "common_configuration.output_data_schema")
        if self.data_schema is None:
            self.data_schema = get(self.training_stats,
                                   "common_configuration.input_data_schema")

        print("Training Statistics generated.")

    def __compute_explainability_configuration(self, **kwargs):
        from ibm_watson_openscale.utils.training_stats import TrainingStats

        training_data_info = {**self.common_parameters}
        training_data_info["enable_fairness"] = False
        training_data_info["enable_explainability"] = True

        training_stats = TrainingStats(
            training_data_frame=self.training_data,
            training_data_info=training_data_info,
            drop_na=True
        ).get_training_statistics()

        self.explain_configuration = training_stats.get(
            "explainability_configuration", {})
        self.__set_class_labels_in_explain()
        self.global_explanation_method = "lime"

    def __compute_global_explanation_for_drift_v2(self, **kwargs):
        from ibm_metrics_plugin.common.utils.python_utils import \
            stratified_sample

        # We are only taking 100 rows as sample size.
        sample_size = min(len(self.training_data), 100)

        if self.problem_type.is_classification():
            num_classes = self.training_data[self.label_column].nunique()

            # Take the max of total number of classes and sample size.
            # This is for cases where number of classes > 100. Corner case
            sample_size = max(sample_size, num_classes)

            # The ideas is to group the original data on the label column
            # Then for each group i.e. each label class, do the sample
            training_data_sample = stratified_sample(
                data=self.training_data, column=self.label_column, max_samples=sample_size)
        else:
            training_data_sample = self.training_data.sample(
                n=sample_size, random_state=ConfigurationUtility.SEED)

        self.__compute_explainability_configuration()
        print(
            f"Computing feature importance for Drift v2 using {self.global_explanation_method} global explanation.")
        self.__get_training_global_explanation(
            training_data=self.__score_data(data=training_data_sample, **kwargs))
        print(f"Feature importance computed")

    def __write_package_to_local(self, archive_data, display_link: bool = True):
        with tarfile.open("configuration_archive.tar.gz", mode="w:gz") as tf:
            for filename, filedata in archive_data.items():
                if isinstance(filedata, bytes):
                    content = BytesIO(filedata)
                else:
                    content = BytesIO(filedata.encode("utf8"))
                tarinfo = tarfile.TarInfo(filename)
                tarinfo.size = len(content.getvalue())
                tarinfo.mtime = time()
                tf.addfile(tarinfo=tarinfo, fileobj=content)

        if display_link:
            create_download_link(
                path="configuration_archive.tar.gz", title="Download Common Configuration Package")
        else:
            print(f"Common Configuration Package stored in local directory. \
                Look for file named: configuration_archive.tar.gz.")

    def scoring_fn_helper(self, input_df, schema={}):
        """
        Helper function to return the scored data based on model type and problem type

        Args:
            training_df (pandas.DataFrame): Pandas DataFrame containing the training data
            schema (dict, optional): A dictionary containing different columns. Defaults to {}.
        """
        from inspect import signature
        scoring_fn_args = signature(self.scoring_fn).parameters
        if self.asset_type == AssetType.MODEL.value and self.input_data_type == InputDataType.STRUCTURED.value:
            # Finding the no. of arguments to verify whether the score function is old or new
            if len(scoring_fn_args) > 1:
                # new score function
                return self.scoring_fn(input_df, schema)

            # old score function
            return self.scoring_fn(input_df)

        # Unstructured models
        return self.scoring_fn(input_df, schema)

    def __score_data(self, data, **kwargs):
        if self.problem_type.is_classification():
            is_scoring_required = False
            probability_column_name = None

            if self.class_probabilities and not (set(self.class_probabilities) <= set(data.columns)):
                probability_column_name = "ProbabilityVector"
                is_scoring_required = True
                self.probability_column = probability_column_name

            if not is_scoring_required and \
                self.probability_column and \
                    self.probability_column not in data:
                probability_column_name = self.probability_column
                is_scoring_required = True

            # if isinstance(self.probability_column, str) and \
            #         self.probability_column not in data:
            #     is_scoring_required = True
            # elif isinstance(self.probability_column, list) and \
            #         not (set(self.prediction_column) <= set(data.columns)):
            #     is_scoring_required = True
            #     probability_column_name = "ProbabilityVector" if \
            #         len(self.probability_column) > 1 else self.probability_column[0]
            if is_scoring_required:
                data = self.__split_and_score(
                    data, **kwargs, probability_column_name=probability_column_name)
            elif self.class_probabilities and (set(self.class_probabilities) <= set(data.columns)):
                # handle condition where all class probability columns are part of training data
                # combine all class probabilities into "ProbabilityVector" column
                data["ProbabilityVector"] = data[self.class_probabilities].values.tolist()
        elif (not self.problem_type.is_classification() and self.prediction_column not in data):
            data = self.__split_and_score(data, **kwargs)

        return data

    def __split_and_score(self, input_df: pd.DataFrame, **kwargs):
        output_df = pd.DataFrame()
        probabilities = []
        predictions = []
        start = 0
        schema = deepcopy(self.common_parameters)
        if "probability_column_name" in kwargs:
            schema["probability_column"] = kwargs.get(
                "probability_column_name")

        end = min(self.batch_size, len(input_df))

        while start < len(input_df):
            data = self.scoring_fn_helper(input_df.iloc[start:end], schema)
            if isinstance(data, pd.DataFrame):
                output_df = pd.concat(
                    [output_df, data], ignore_index=True, axis=0)
            elif isinstance(data, tuple) or isinstance(data, np.ndarray):
                if not self.problem_type.is_classification():
                    predictions.append(data)
                else:
                    probabilities.append(data[0])
                    predictions.append(data[1])

            start = end
            end = min(start + self.batch_size, len(input_df))

        if output_df.empty:
            if self.problem_type.is_classification():
                input_df = input_df.assign(
                    **{self.prediction_column: np.concatenate(predictions), self.probability_column: np.concatenate(probabilities).tolist()})
                return input_df
            else:
                input_df = input_df.assign(
                    **{self.prediction_column: np.concatenate(predictions)})
                return input_df
        else:
            return output_df

    def __get_probability_column(self):
        if not self.problem_type.is_classification():
            return None

        if self.class_probabilities:
            return "ProbabilityVector"

        return self.probability_column

    def create_configuration_package(self, explainability_parameters: Optional[Dict], fairness_parameters: Optional[Dict], drift_v2_parameters: Optional[Dict], **kwargs):
        """Create the configuration package for a subscription in IBM Watson OpenScale

        :param explainability_parameters: The explainability parameters
        :type explainability_parameters: Optional[Dict]
        :param fairness_parameters: The fairness parameters
        :type fairness_parameters: Optional[Dict]
        :param drift_v2_parameters: The drift_v2 parameters
        :type drift_v2_parameters: Optional[Dict]
        """
        archive_data = {}

        # 0. See if verbose logging is enabled?
        verbose = kwargs.get("verbose", False)
        from ibm_metrics_plugin.common.utils.metrics_logger import \
            MetricsLogger
        MetricsLogger.set_log_level(
            logging.INFO if verbose else logging.WARNING)
        MetricsLogger.enable_json_logs(verbose)

        # 1. Compute Training Stats
        self.__compute_training_stats(
            fairness_parameters=fairness_parameters, **kwargs)

        # 2. Compute fairness related configuration
        if self.enable_fairness:
            from ibm_watson_openscale.utils.indirect_bias_processor import \
                IndirectBiasProcessor
            fairness_configuration = IndirectBiasProcessor().configure(
                config_json=self.training_stats,
                common_params=self.common_parameters,
                training_data_df=self.training_data,
                parameters=fairness_parameters)
            self.training_stats["fairness_configuration"] = fairness_configuration
            archive_data["fairness_statistics.json"] = dumps(
                fairness_configuration, indent=4)
            print("Fairness Statistics generated.")

        # Compute Common Configuration
        common_configuration_json = {}
        common_configuration_json["common_configuration"] = self.training_stats.get(
            "common_configuration")
        common_configuration_json["notebook_version"] = self.training_stats.get(
            "notebook_version")

        archive_data["common_configuration.json"] = dumps(
            common_configuration_json, indent=4)

        # 3. Compute Explain Archive
        if self.enable_explainability:
            self.explain_configuration = self.training_stats.get(
                "explainability_configuration", {})
            archive_data["explainability.tar.gz"] = self.get_explainability_archive(
                parameters=explainability_parameters, **kwargs)
            print("Explain Archive generated.")

        # 4. Compute drift v2 archive
        if self.enable_drift_v2:
            archive_data["drift_v2_archive.tar.gz"] = self.get_drift_v2_archive(
                parameters=drift_v2_parameters, **kwargs)
            print("Drift v2 Archive generated.")

        # 5. Compute Drift archive
        if self.enable_drift:
            drift_parameters = kwargs.get("drift_parameters", {})
            archive_data["drift_archive.tar.gz"] = self.get_drift_archive(
                parameters=drift_parameters)
            print("Drift Archive generated.")

        # Write the package locally
        display_link = kwargs.get("display_link", False)
        self.__write_package_to_local(
            archive_data=archive_data, display_link=display_link)

    def create_drift_configuration_package(self, drift_v2_parameters: Dict, **kwargs):
        """Create the drift configuration package for an unstructured subscription in IBM Watson OpenScale

        :param drift_v2_parameters: The drift_v2 parameters
        :type drift_v2_parameters: Dict
        """
        from ibm_metrics_plugin.metrics.drift_v2.impl.drift_metric_evaluator import \
            DriftMetricsEvaluator
        from ibm_metrics_plugin.metrics.drift_v2.utils.drift_utils import \
            serialise_as_json

        metrics_config = self.__get_drift_metrics_config(drift_v2_parameters)

        if not drift_v2_parameters.get("max_samples"):
            self.training_data = self.__score_data(
                data=self.training_data, **kwargs)
            data = self.training_data.copy()
        else:
            from ibm_metrics_plugin.common.utils.python_utils import \
                stratified_sample
            data = stratified_sample(
                data=self.training_data,
                column=self.label_column,
                max_samples=drift_v2_parameters.get("max_samples"))
            data = self.__score_data(data=data, **kwargs)

        try:
            import torch as _
            from ibm_metrics_plugin.common.utils.embeddings_utils import \
                compute_embeddings
            self.training_data = compute_embeddings(
                configuration=metrics_config, data=self.training_data)

        except ModuleNotFoundError as me:
            if ("embeddings_utils" not in str(me)) and ("torch" not in str(me)):
                raise me

            # Warn the user to use latest metrics plugin
            warnings.warn(
                "Please install correct version of ibm-metrics-plugin[\"notebook\"] to compute embeddings.")

            drift_v2_config = metrics_config["configuration"]["drift_v2"]["metrics_configuration"]
            advanced_controls = drift_v2_config.get(
                "advanced_controls", {})
            new_drift_v2_config = {
                **drift_v2_config,
                "advanced_controls": {
                    **advanced_controls,
                    "enable_embedding_drift": False
                }
            }
            metrics_config["configuration"]["drift_v2"]["metrics_configuration"] = new_drift_v2_config

        evaluator = DriftMetricsEvaluator()
        drift_data_set, _ = run_in_event_loop(evaluator.fit(configuration=metrics_config,
                                                            data_frame=data,
                                                            feature_importance=[],
                                                            most_important_features=[]))

        data = serialise_as_json(drift_data_set)

        # Write the package locally
        display_link = kwargs.get("display_link", False)
        self.__write_package_to_local(
            archive_data=data, display_link=display_link)


class ConfigurationUtilityLLM():

    def __init__(self, training_data: pd.DataFrame, common_parameters: dict,
                 scoring_fn: callable = None, embeddings_fn: callable = None,
                 **kwargs):
        check_package_exists()
        validate_pandas_dataframe(training_data, "training_data", True)
        validate_type(common_parameters, "common_parameters", dict, True)

        self.scoring_fn = scoring_fn
        self.embeddings_fn = embeddings_fn
        self.training_data = training_data
        self.common_parameters = common_parameters

        self.asset_type = self.common_parameters.get("asset_type")
        validate_enum(self.asset_type,
                      "'asset_type' in common_parameters", AssetType, True)

        self.input_data_type = self.common_parameters.get("input_data_type")
        validate_enum(self.input_data_type,
                      "'input_data_type' in common_parameters", InputDataType, True)

        self.problem_type = self.common_parameters.get("problem_type")
        validate_enum(self.problem_type,
                      "'problem_type' in common_parameters", ProblemType, True)

        if not ProblemType(self.problem_type).is_supported(AssetType(self.asset_type)):
            raise ValueError(
                f"Problem type '{self.problem_type}' is not supported for prompt assets.")

        self.prediction_column = self.common_parameters.get(
            "prediction_column", "generated_text")
        self.prompt_variable_columns = self.common_parameters.get(
            "prompt_variable_columns")
        validate_type(self.prompt_variable_columns,
                      "'prompt_variable_columns' in common_parameters", list, True)
        if not self.prompt_variable_columns:
            raise ValueError("Prompt variable columns cannot be empty.")

        self.context_columns = self.common_parameters.get(
            "context_columns", [])
        self.question_column = self.common_parameters.get(
            "question_column")
        if hasattr(ProblemType, "RAG") and (self.problem_type == ProblemType.RAG.value):
            validate_type(self.context_columns,
                          "'context_columns' in common_parameters", list, True)
            validate_type(self.question_column,
                          "'question_column' in common_parameters", str, True)

        self.meta_columns = self.common_parameters.get("meta_columns", None)
        # self.label_column = self.common_parameters.get(
        #     "label_column", "reference_output")
        self.input_token_count_column = self.common_parameters.get(
            "input_token_count_column")
        self.output_token_count_column = self.common_parameters.get(
            "output_token_count_column")
        self.prediction_probability_column = self.common_parameters.get(
            "prediction_probability_column")

        # Convert all boolean values to string.
        mask = self.training_data.applymap(type) != bool
        map_ = {True: "true", False: "false"}

        self.training_data = self.training_data.where(
            mask, self.training_data.replace(map_))

    def __score_data(self, data):
        if self.prediction_column in data:
            # Scoring is already done, no need to score again.
            return data
        if not self.scoring_fn:
            raise Exception(
                "The data must be either scored or a scoring function must be passed")
        schema = {
            "prediction_column": self.prediction_column,
            "input_token_count_column": self.input_token_count_column,
            "prediction_probability_column": self.prediction_probability_column,
            "output_token_count_column": self.output_token_count_column,
            "prompt_variable_columns": self.prompt_variable_columns
        }

        for col in self.prompt_variable_columns:
            if col not in data.columns:
                raise ValueError(
                    f"The prompt variable column '{col}' is not found in training data.")

        print("Scoring data..")
        data = run_in_event_loop(self.scoring_fn(data, schema))
        return data

    def __check_for_embeddings(self) -> bool:
        """
        Check if the embeddings are present in the training data or not

        Returns:
            bool: True, if embeddings are present, False otherwise
        """

        from ibm_metrics_plugin.common.utils.constants import \
            EmbeddingFieldType
        input_embeddings_name = EmbeddingFieldType.INPUT.get_default_embeddings_name()

        if input_embeddings_name not in self.training_data:
            return False

        # If LLMs but not RAG, check for input, output, individual feature embeddings
        output_embeddings_name = EmbeddingFieldType.OUTPUT.get_default_embeddings_name()
        if output_embeddings_name not in self.training_data:
            return False

        for field in self.prompt_variable_columns:
            embeddings_name = EmbeddingFieldType.FEATURE.get_default_embeddings_name(
                field_name=field)

            if embeddings_name not in self.training_data:
                return False

        if hasattr(ProblemType, "RAG") and (self.problem_type == ProblemType.RAG.value):
            # If RAG based LLMs, check for input, output, context, individual feature embeddings
            context_embeddings_name = EmbeddingFieldType.OUTPUT.get_default_embeddings_name()
            if context_embeddings_name not in self.training_data:
                return False

        return True

    def generate_drift_v2_archive_llm(self, drift_v2_parameters, display_link=True):
        from ibm_metrics_plugin.metrics.drift_v2.impl.drift_metric_evaluator import \
            DriftMetricsEvaluator

        self.training_data = self.__score_data(
            data=self.training_data)

        parameters = {**drift_v2_parameters}
        if "archive_creation_flag" not in parameters:
            parameters["archive_creation_flag"] = True
        if "archive_dir_path" not in parameters:
            parameters["archive_dir_path"] = os.getcwd()

        configuration = {
            "configuration": {
                "asset_type": self.asset_type,
                "problem_type": self.problem_type,
                "input_data_type": self.input_data_type,
                "feature_columns": self.prompt_variable_columns,
                "categorical_columns": [],
                "meta_columns": self.meta_columns,
                "context_columns": self.context_columns,
                "prediction_column": self.prediction_column,
                "prediction_probability_column": self.prediction_probability_column,
                "input_token_count_column": self.input_token_count_column,
                "output_token_count_column": self.output_token_count_column,
                "question_column": self.question_column,
                MetricGroupType.DRIFT.value: {
                    "metrics_configuration": {
                        **parameters
                    }
                }
            }
        }

        from ibm_metrics_plugin.common.utils.metadata_utils import \
            compute_metadata_counts

        self.training_data = compute_metadata_counts(
            configuration=configuration, data=self.training_data)

        configuration = self.__check_and_compute_embeddings(configuration)

        evaluator = DriftMetricsEvaluator()
        _, path = run_in_event_loop(evaluator.fit(configuration=configuration,
                                                  data_frame=self.training_data))
        print("Baseline archive created at path: ", path)
        if display_link:
            create_download_link(
                path=path, title="Download Baseline Archive")
        else:
            return path

    def __check_and_compute_embeddings(self, configuration):
        try:
            import torch as _
            from ibm_metrics_plugin.common.utils.embeddings_utils import \
                compute_embeddings

            if not self.__check_for_embeddings():
                self.training_data = compute_embeddings(
                    configuration=configuration, data=self.training_data,
                    embeddings_fn=self.embeddings_fn)

        except ModuleNotFoundError as me:
            if ("embeddings_utils" not in str(me)) and ("torch" not in str(me)):
                raise me

            # Warn the user to use latest metrics plugin
            print(
                "Please install correct version of ibm-metrics-plugin[\"notebook\"] to compute embeddings.")

            # Disable embedding drift
            drift_v2_config = configuration["configuration"]["drift_v2"]["metrics_configuration"]
            advanced_controls = drift_v2_config.get(
                "advanced_controls", {})
            new_drift_v2_config = {
                **drift_v2_config,
                "advanced_controls": {
                    **advanced_controls,
                    "enable_embedding_drift": False
                }
            }
            configuration["configuration"]["drift_v2"]["metrics_configuration"] = new_drift_v2_config
        finally:
            return configuration
