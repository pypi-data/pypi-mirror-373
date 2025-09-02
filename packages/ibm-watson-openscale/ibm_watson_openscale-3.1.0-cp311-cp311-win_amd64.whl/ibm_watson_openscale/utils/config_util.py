# coding: utf-8

# Copyright 2022 IBM All Rights Reserved.
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
import tarfile
from collections import Counter
from copy import deepcopy
from io import BytesIO
from json import dumps, loads
from random import sample

import numpy as np
import pandas as pd
from ibm_cloud_sdk_core import BaseService
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator
from ibm_watson_openscale.utils.utils import get, validate_type


class ConfigUtil():

    def __init__(self, ai_client: "WatsonOpenScaleV2Adapter"):
        validate_type(ai_client, "ai_client", BaseService, True)
        self.ai_client = ai_client
        self.scored_perturbations = None
        # authenticator.token_manager
        if type(self.ai_client.authenticator) is BearerTokenAuthenticator:
            self.token = self.ai_client.authenticator.bearer_token
        else:
            self.token = self.ai_client.authenticator.token_manager.get_token()

    def get_explainability_archive(self, config, training_data, parameters, scoring_fn, enable_explainability: bool = True):
        """
        Creates the explainability archive with the required artifacts and return as bytes.
        """
        if not enable_explainability:
            return None

        try:
            __import__("ibm_metrics_plugin.core.metrics_manager",
                       fromlist=["MetricManager"])
        except Exception as e:
            msg = "Unable to find ibm-metrics-plugin library. Please install it and retry."
            raise Exception(msg)

        self.config = config.get("common_configuration")
        self.training_data = training_data
        self.parameters = parameters
        self.probability_column = self.config.get("probability")
        self.prediction_column = self.config.get("prediction")
        self.explain_stats = config.get("explainability_configuration")
        self.scoring_fn = scoring_fn

        if self.parameters and self.parameters.get(
                "global_explanation"):
            # set the defaut global explanation method as lime
            self.global_explanation_method = self.parameters.get(
                "global_explanation").get("explanation_method") or "lime"
        else:
            self.global_explanation_method = None

        from ibm_metrics_plugin.common.utils.constants import ProblemType
        archive_data = {}
        # Add training data statistics
        if self.scoring_fn and self.config.get("problem_type") != ProblemType.REGRESSION.value:
            class_labels_in_config = self.config.get("class_labels")
            class_labels_in_stats = self.explain_stats.get("class_labels")
            if class_labels_in_config:
                if sorted(class_labels_in_config) != sorted(class_labels_in_stats):
                    raise Exception(
                        "The list of class labels {0} in the training statistics and the class labels {1} provided in the input are not equal.".format(class_labels_in_stats, class_labels_in_config))
                self.explain_stats["class_labels"] = self.config.get(
                    "class_labels")
            else:
                self.explain_stats["class_labels"] = self.__get_class_labels(
                    class_labels_in_stats)
        archive_data["training_statistics.json"] = dumps(
            {"training_statistics": self.explain_stats})

        # Add lime scored perturbations
        if self.scoring_fn:
            self.scored_perturbations = self.__get_lime_scored_perturbations()
            archive_data["lime_scored_perturbations.json"] = dumps(
                self.scored_perturbations)

        # Add shap related files
        if self.parameters:
            if self.global_explanation_method == "shap":
                archive_data.update(self.__get_shap_background_data_sets())
            archive_data.update(self.__get_global_explanation(archive_data))
            archive_data["configuration.json"] = dumps(
                {"parameters": self.parameters})

        return self.create_archive_as_bytes(data=archive_data)

    def create_explainability_archive(self, config, training_data, parameters, scoring_fn):
        """
        Creates the explainability archive with the required artifacts and return as a downloadable link from notebook.
        """
        from ibm_wos_utils.joblib.utils.notebook_utils import \
            create_download_link
        archive_bytes = self.get_explainability_archive(config=config,
                                                        training_data=training_data,
                                                        parameters=parameters,
                                                        scoring_fn=scoring_fn)
        return create_download_link(data=archive_bytes, type="explainability")

    def get_global_explanation(self, explainability_archive=None, metrics_result=None):
        """
        Get the global explanation from the given explainability archive or metrics_result.

        Arguments:
            explainability_archive: The explainability archive could be bytes or the path to explainability.tar.gz file.
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
        from ibm_metrics_plugin.common.utils.constants import ProblemType
        from ibm_wos_utils.explainability.utils.perturbations import \
            Perturbations
        problem_type = self.config.get("problem_type")
        lime_parameters = self.parameters.get("lime")
        perturbations_count = lime_parameters.get(
            "perturbations_count") if lime_parameters else 5000
        perturbations = Perturbations(
            training_stats=self.explain_stats, problem_type=problem_type, perturbations_count=perturbations_count)
        perturbs_df = perturbations.generate_perturbations()

        # use score function to score generated perturbations
        predict_probability = self.scoring_fn(perturbs_df)
        if problem_type == ProblemType.REGRESSION.value:
            scored_perturbations = {
                "predictions": predict_probability.tolist()
            }
        else:
            scored_perturbations = {
                "probabilities": predict_probability[0].tolist(),
                "predictions": predict_probability[1].tolist()
            }

        return scored_perturbations

    def __get_shap_background_data(self):
        base_values = self.explain_stats.get("base_values").copy()
        feature_columns = self.explain_stats.get("feature_columns")
        background_df = pd.DataFrame({
            feature_columns[int(k)]: [v] for k, v in base_values.items()})

        # Set dtype for int columns in background_df
        schema = self.config.get(
            "output_data_schema") or self.config.get("input_data_schema")
        if schema:
            features_schema = {f.get("name"): f.get("type")
                               for f in schema.get("fields")}
            for f in feature_columns:
                feature_data_type = features_schema.get(f)
                if feature_data_type:
                    feature_data_type = feature_data_type.lower()
                    if any(i in feature_data_type for i in ["int", "integer", "long"]):
                        background_df[f] = background_df[f].astype(int)

        return background_df

    def __get_training_global_explanation(self, background_data=None):
        from ibm_metrics_plugin.common.utils.constants import (
            ExplainabilityMetricType, MetricGroupType, ProblemType)
        from ibm_metrics_plugin.core.metrics_manager import MetricManager
        if self.global_explanation_method == ExplainabilityMetricType.SHAP.value:
            metrics_config = self.__get_shap_metrics_config()
            metrics_result = MetricManager().evaluate(spark=None,
                                                      configuration=metrics_config,
                                                      data_frame=self.training_data,
                                                      scoring_fn=self.__scoring_fn,
                                                      background_data=background_data)
        else:
            metrics_config = self.__get_lime_metrics_config()
            metrics_result = MetricManager().evaluate(spark=None,
                                                      configuration=metrics_config,
                                                      data_frame=self.training_data,
                                                      scoring_fn=self.__scoring_fn)
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

            local_exps = get_lime_explanations_distribution(
                local_explanations=local_exps, global_explanation=global_explanation)

        # Compute class_labels_count
        if self.config.get("problem_type") != ProblemType.REGRESSION.value:
            label_column = self.config.get("label_column")
            if label_column:
                global_explanation["class_labels_count"] = self.training_data[label_column].value_counts(
                ).to_dict()

        return {"global_explanation": global_explanation,
                "local_explanations": local_exps}

    def __get_shap_metrics_config(self):
        from ibm_metrics_plugin.common.utils.constants import (
            ExplainabilityMetricType, MetricGroupType)
        from ibm_metrics_plugin.metrics.explainability.entity.constants import (
            ShapAggregationMethod, ShapAlgorithm)

        schema = self.config.get(
            "output_data_schema") or self.config.get("input_data_schema")
        if schema:
            features_schema = {f.get("name"): f.get("type")
                               for f in schema.get("fields")}
        else:
            features_schema = {}

        shap_params = deepcopy(self.parameters.get(
            ExplainabilityMetricType.SHAP.value)) or {}

        # Set aggregation methods
        agg_methods = self.parameters["global_explanation"].get(
            "aggregation_methods")
        if agg_methods:
            shap_params["aggregation_methods"] = agg_methods
        else:
            shap_params["aggregation_methods"] = [
                ShapAggregationMethod.MEAN_ABS.value, ShapAggregationMethod.MAX_ABS.value]

        # set algorithm
        algorithm = self.parameters["shap"].get("algorithm")
        if not algorithm:
            shap_params["algorithm"] = ShapAlgorithm.KERNEL.value

        return {
            "configuration": {
                "problem_type": self.config.get("problem_type"),
                "input_data_type": "structured",
                "feature_columns": self.explain_stats.get("feature_columns"),
                "categorical_columns": self.explain_stats.get("categorical_columns"),
                "label_column": self.config.get("label_column"),
                "features_schema": features_schema,
                MetricGroupType.EXPLAINABILITY.value: {
                    "metrics_configuration": {
                        ExplainabilityMetricType.SHAP.value: shap_params
                    }
                }
            }
        }

    def __get_lime_metrics_config(self):
        from ibm_metrics_plugin.common.utils.constants import (
            ExplainabilityMetricType, MetricGroupType)

        schema = self.config.get(
            "output_data_schema") or self.config.get("input_data_schema")
        if schema:
            features_schema = {f.get("name"): f.get("type")
                               for f in schema.get("fields")}
        else:
            features_schema = {}

        lime_params = deepcopy(self.parameters.get(
            ExplainabilityMetricType.LIME.value)) or {"perturbations_count": 5000}
        lime_params["include_input_features"] = True

        metrics_config = {
            "configuration": {
                "problem_type": self.config.get("problem_type"),
                "input_data_type": "structured",
                "feature_columns": self.explain_stats.get("feature_columns"),
                "categorical_columns": self.explain_stats.get("categorical_columns"),
                "label_column": self.config.get("label_column"),
                "features_schema": features_schema,
                "prediction": self.prediction_column,
                "probability": self.probability_column,
                MetricGroupType.EXPLAINABILITY.value: {
                    "metrics_configuration": {
                        ExplainabilityMetricType.LIME.value: lime_params
                    }
                }
            }
        }
        metrics_config["configuration"][MetricGroupType.EXPLAINABILITY.value]["training_statistics"] = self.explain_stats
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

    def __scoring_fn(self, data):
        from ibm_metrics_plugin.common.utils.constants import ProblemType
        resp = self.scoring_fn(data)
        problem_type = self.config.get("problem_type")
        if problem_type == ProblemType.REGRESSION.value:
            return resp.tolist(), None
        else:
            return resp[1].tolist(), resp[0].tolist()

    def __get_shap_background_data_sets(self):
        archive_data = {}
        shap_params = self.parameters.get("shap") or {}
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

            self.parameters["shap"]["background_data_sets"] = background_data_sets
            self.parameters["shap"]["background_data_set"] = background_data_set

        return archive_data

    def __get_global_explanation(self, archive_data):
        archive_data_to_add = {}
        global_exp_params = self.parameters.get("global_explanation") or {}
        shap_params = self.parameters.get("shap") or {}

        # Generate training data global explanation if enabled
        if not self.scoring_fn and bool(global_exp_params.get("enabled")):
            raise Exception(
                "Scoring function is required for configuring global explanation.")

        if self.scoring_fn and bool(global_exp_params.get("enabled")):
            if bool(shap_params.get("enabled")) and self.global_explanation_method == "shap":
                background_data_set = shap_params.get("background_data_set")
                background_data_sets = shap_params.get("background_data_sets")
                background_file_name = next((b.get("file_name") for b in background_data_sets if b.get(
                    "name") == background_data_set), None)
                background_df = pd.read_csv(
                    BytesIO(bytes(archive_data.get(background_file_name), "utf-8")))
                archive_data_to_add["shap_training_data_global_explanation.json"] = dumps(self.__get_training_global_explanation(
                    background_data=background_df))
            else:
                from ibm_metrics_plugin.common.utils.constants import \
                    ProblemType
                problem_type = ProblemType(self.config.get("problem_type"))
                if (problem_type == ProblemType.REGRESSION and self.prediction_column not in self.training_data) \
                        or (problem_type.is_classification and self.probability_column not in self.training_data):
                    predictions, probabilities = self.__scoring_fn(
                        self.training_data)
                    self.training_data[self.prediction_column] = predictions
                    self.training_data[self.probability_column] = probabilities
                archive_data_to_add["lime_training_data_global_explanation.json"] = dumps(
                    self.__get_training_global_explanation())

        return archive_data_to_add

    def __get_class_labels(self, class_labels):
        labels = []
        # Score all the possible predictions and determine the order
        label_column = self.config.get("label_column")
        df = self.training_data.groupby(
            label_column).head(10).reset_index(drop=True)
        labels = self.__get_labels(df)

        if None in labels:
            labels_to_score = list(set(class_labels) - set(labels))
            df = self.training_data[self.training_data[label_column].isin(
                labels_to_score)].groupby(label_column).tail(50).reset_index(drop=True)
            scored_labels = self.__get_labels(df)
            for i in range(len(labels)):
                if labels[i] == None:
                    labels[i] = scored_labels[i]

        if None in labels:
            raise Exception("The records with the class labels {0} in the training data returned a different prediction when scored against the model. The configuration requires atleast one record from training data to return the class labels when scored.".format(
                set(class_labels) - set(labels)))

        return labels

    def __get_labels(self, df):
        probabilities, predictions = self.scoring_fn(df)
        if predictions is None or (len(probabilities) != len(predictions)):
            return

        labels = [None]*len(probabilities[0])
        for probs, pred in zip(probabilities, predictions):
            if probs is None:
                continue
            max_prob = max(probs)
            if Counter(probs)[max_prob] == 1:
                labels[np.argmax(probs)] = pred.item() if type(
                    pred).__module__ == np.__name__ else pred
        return labels

    def create_archive_as_bytes(self, data):
        archive_data = None
        with BytesIO() as archive:
            with tarfile.open(fileobj=archive, mode="w:gz") as tf:
                for filename, filedata in data.items():
                    content = BytesIO(filedata.encode("utf8"))
                    tarinfo = tarfile.TarInfo(filename)
                    tarinfo.size = len(content.getvalue())
                    tf.addfile(
                        tarinfo=tarinfo, fileobj=content)
            archive_data = archive.getvalue()

        return archive_data
