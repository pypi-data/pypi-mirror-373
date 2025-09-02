# coding: utf-8

# Copyright 2020, 2023 IBM All Rights Reserved.
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

import numpy as np
from ibm_watson_openscale.utils import check_package_exists


class IndirectBiasProcessor:

    '''
    Class to perform following indirect bias related tasks
    - Find co-related attributes
    - Find co-related majority, minority
    - Store the co-relation information in fairness configuration
    '''

    def __init__(self):
        # Check for ibm_metrics_plugin package. It will have ibm_wos_utils as dependency.
        check_package_exists()

    def configure(self, config_json, common_params, training_data_df, parameters):
        if not common_params.get("enable_fairness"):
            return None

        feature_columns = common_params.get("feature_columns")
        label_column = common_params.get("label_column")
        if label_column is None:
            label_column = common_params.get("class_label")

        training_columns = training_data_df.columns.tolist()
        training_columns.remove(label_column)

        non_feature_columns = list(
            set(training_columns) - set(feature_columns))
        if not non_feature_columns:
            return config_json.get("fairness_configuration")

        fairness_attributes_list = [attribute.get(
            "feature") for attribute in parameters.get("fairness_attributes")]

        protected_attributes = []
        for column in non_feature_columns:
            if column in fairness_attributes_list:
                protected_attributes.append(column)

        if not protected_attributes:
            return config_json.get("fairness_configuration")

        return self.get_correlated_attributes(
            training_data=training_data_df,
            fairness_configuration=config_json.get("fairness_configuration"),
            feature_columns=feature_columns,
            label_column=label_column,
            protected_attributes=protected_attributes)

    def get_correlated_attributes(self, training_data, fairness_configuration, feature_columns, protected_attributes, label_column):

        from service.runtime.indirect_bias.utils.co_relations_util import CoRelationsUtil
        from service.runtime.indirect_bias.utils.indirect_bias_util import IndirectBiasUtil
        from service.runtime.indirect_bias.utils.mapping_util import MappingUtil

        for protected_attribute in protected_attributes:
            # Remove other protected attributes so that they won't be considered while finding co_related attributes
            for col in feature_columns:
                if col in protected_attributes and col != protected_attribute:
                    feature_columns.remove(col)
            columns = feature_columns + \
                [protected_attribute, label_column]
            correlated_attributes = CoRelationsUtil.find_co_related_attributes(
                training_data[columns], protected_attribute, label_column)
            feature_details = IndirectBiasUtil.get_feature_details(
                protected_attribute, fairness_configuration["parameters"]["features"])
            # Update is_protected_attribute flag
            feature_details["is_protected_attribute"] = True
            if len(correlated_attributes) > 0:
                majority = feature_details["majority"]
                minority = feature_details["minority"]
                correlated_attributes_list = CoRelationsUtil.get_co_related_attributes_list(
                    correlated_attributes)
                if training_data[protected_attribute].dtype == np.int64 or training_data[protected_attribute].dtype == np.float64:
                    # get mapping for numerical attribute
                    co_related_maj, co_related_min = MappingUtil.get_indirect_majority_minority_for_numerical_attr(
                        training_data, protected_attribute, correlated_attributes_list, majority, minority)
                else:
                    co_related_maj, co_related_min = MappingUtil.get_indirect_majority_minority_for_categorical_attr(
                        training_data, protected_attribute, correlated_attributes_list, majority, minority)
                # Update the correlation information in fairness configuration
                feature_details["correlated_attributes"] = correlated_attributes
                if co_related_maj is not None:
                    feature_details["correlated_majority"] = co_related_maj
                if co_related_min is not None:
                    feature_details["correlated_minority"] = co_related_min
            else:
                feature_details["correlated_attributes"] = []
        fairness_configuration["parameters"]["protected_attributes"] = protected_attributes
        return fairness_configuration

    def get_feature_details(self, feature, fairness_configuration):
        from service.runtime.indirect_bias.utils.indirect_bias_util import IndirectBiasUtil
        return IndirectBiasUtil.get_feature_details(
            feature, fairness_configuration["parameters"]["features"])

    def get_formatted_range(self, values):
        from service.runtime.indirect_bias.utils.indirect_bias_util import IndirectBiasUtil
        return IndirectBiasUtil.get_formatted_range(values)

    def get_correlations_for_maj_min_group(self, correlated_maj_min, maj_min_group):
        from service.runtime.indirect_bias.utils.indirect_bias_util import IndirectBiasUtil
        return IndirectBiasUtil.get_correlations_for_maj_min_group(correlated_maj_min, maj_min_group)
