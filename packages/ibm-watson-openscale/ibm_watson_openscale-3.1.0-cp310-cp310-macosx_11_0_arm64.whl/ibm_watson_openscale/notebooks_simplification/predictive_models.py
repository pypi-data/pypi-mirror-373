# coding: utf-8

# Copyright 2025 IBM All Rights Reserved.
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
import os
import random
import time
import uuid

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson_machine_learning import APIClient as WMLAPIClient

from ibm_watson_openscale import APIClient as WosAPIClient
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
    Asset,
    AssetDeploymentRequest,
    AssetPropertiesRequest,
    COSTrainingDataReferenceConnection,
    COSTrainingDataReferenceLocation,
    DatabaseConfigurationRequest,
    LocationSchemaName,
    PrimaryStorageCredentialsLong,
    SparkStruct,
    Target,
    TrainingDataReference,
    WMLCredentialsCloud,
)
from ibm_watson_openscale.supporting_classes.enums import (
    AssetTypes,
    DatabaseType,
    DataSetTypes,
    DeploymentTypes,
    InputDataType,
    ProblemType,
    ServiceTypes,
    TargetTypes,
    StatusStateType,
)
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord


class PredictiveModelDeploymentManager:
    """
    Handles model deployment and monitoring setup using Watson Machine Learning and Watson OpenScale.
    """

    # Class-level default constants
    DEFAULT_MONITOR_NEW_VERSION = False
    DEFAULT_PROBLEM_TYPE = "binary"
    DEFAULT_INPUT_DATA_TYPE = "structured"
    DEFAULT_MODEL_NAME = "Scikit German Risk Model WML V1"
    DEFAULT_DEPLOYMENT_NAME = "Scikit German Risk Deployment WML V1"
    DEFAULT_ASSET_NAME = "Scikit German Risk Model WML V1"
    DEFAULT_SERVICE_PROVIDER_NAME = "Watson Machine Learning V1"
    DEFAULT_SERVICE_PROVIDER_DESCRIPTION = "Added by tutorial WOS notebook."
    DEFAULT_OPERATIONAL_SPACE_ID = "production"
    DEFAULT_WOS_SERVICE_INSTANCE_ID = None
    DEFAULT_WOS_SERVICE_URL = None
    DEFAULT_SOFTWARE_SPEC_NAME = "runtime-24.1-py3.11"
    DEFAULT_MODEL_TYPE = "scikit-learn_1.3"

    def __init__(self, config):
        self.config = config
        self.monitor_new_version = config.get(
            "monitor_new_version", self.DEFAULT_MONITOR_NEW_VERSION
        )
        self.problem_type = config.get("problem_type", self.DEFAULT_PROBLEM_TYPE)
        self.input_data_type = config.get(
            "input_data_type", self.DEFAULT_INPUT_DATA_TYPE
        )
        self.model_name = config.get("model_name", self.DEFAULT_MODEL_NAME)
        self.deployment_name = config.get(
            "deployment_name", self.DEFAULT_DEPLOYMENT_NAME
        )
        self.asset_name = config.get("asset_name", self.DEFAULT_ASSET_NAME)
        self.service_provider_name = config.get(
            "service_provider_name", self.DEFAULT_SERVICE_PROVIDER_NAME
        )
        self.service_provider_description = config.get(
            "service_provider_description", self.DEFAULT_SERVICE_PROVIDER_DESCRIPTION
        )
        self.operational_space_id = config.get(
            "operational_space_id", self.DEFAULT_OPERATIONAL_SPACE_ID
        )
        self.service_instance_id = config.get(
            "wos_service_instance_id", self.DEFAULT_WOS_SERVICE_INSTANCE_ID
        )
        self.service_url = config.get("wos_service_url", self.DEFAULT_WOS_SERVICE_URL)
        self.software_spec_name = config.get(
            "software_spec_name", self.DEFAULT_SOFTWARE_SPEC_NAME
        )
        self.model_type = config.get("model_type", self.DEFAULT_MODEL_TYPE)
        self.wml_client = None
        self.wos_client = None
        self.scoring_data_fields = None
        self.scoring_data_values = None

    def deploy_and_monitor(self):
        self._validate_inputs()
        self._initialize_wml_client()
        deployment_uid, model_uid = self._publish_and_deploy_model()
        self._score_model(
            deployment_uid,
            self.scoring_data_values,
            self.scoring_data_fields,
            num_records_to_score=3,
        )
        self._initialize_wos_client()
        subscription_id, data_mart_id, payload_data_set_id = (
            self._setup_openscale_monitoring(model_uid, deployment_uid)
        )
        num_records_to_score = 200  # 200 is the min needed data to enable some monitors
        predictions, scoring_payload = self._score_model(
            deployment_uid,
            self.scoring_data_values,
            self.scoring_data_fields,
            num_records_to_score=num_records_to_score,
        )

        expected_num_records = num_records_to_score  # scored 200 expected 200
        self._verify_payload_logging(
            payload_data_set_id,
            expected_num_records,
            predictions,
            scoring_payload,
        )
        self._configure_monitors(subscription_id, data_mart_id, payload_data_set_id)

    def _validate_inputs(self):
        validate_inputs(config_dict=self.config)
        self.scoring_data_fields, self.scoring_data_values = (
            load_and_validate_scoring_data(self.config.get("scoring_data_file"))
        )

    def _initialize_wml_client(self):
        wml_credentials = {
            "url": self.config.get("wml_url"),
            "apikey": self.config.get("cloud_api_key"),
        }
        self.wml_client = WMLAPIClient(wml_credentials)
        self.wml_client.set.default_space(self.config.get("wml_space_id"))
        print(
            f"Connection to WML established. WML version = {self.wml_client.version}"
        )

    def _publish_and_deploy_model(self):

        deployment_uid, model_uid = find_or_delete_existing_deployment(
            self.wml_client,
            self.deployment_name,
            self.monitor_new_version,
        )

        # If deployment was deleted or not found, create a new one
        if self.monitor_new_version or deployment_uid is None:
            training_data_references = create_cos_connection_and_prepare_data_ref(
                self.wml_client, self.config
            )
            model_uid = publish_model_from_config(
                self.wml_client,
                self.config,
                training_data_references,
                self.model_name,
                self.software_spec_name,
                self.model_type,
            )
            deployment_uid = deploy_model_to_wml(
                self.wml_client, model_uid, self.deployment_name
            )

        return deployment_uid, model_uid

    def _score_model(
        self,
        deployment_uid,
        scoring_data_values,
        scoring_data_fields,
        num_records_to_score,
    ):
        values = [
            random.choice(scoring_data_values) for _ in range(num_records_to_score)
        ]
        scoring_payload = {
            "input_data": [{"fields": scoring_data_fields, "values": values}]
        }
        try:
            predictions = self.wml_client.deployments.score(
                deployment_uid, scoring_payload
            )
            print("Scoring completed successfully.")
        except Exception as e:
            print(f"Model scoring failed: {e}")
            raise
        return predictions, scoring_payload

    def _initialize_wos_client(self):
        authenticator = IAMAuthenticator(apikey=self.config.get("cloud_api_key"))
        self.wos_client = WosAPIClient(
            authenticator=authenticator,
            service_instance_id=self.service_instance_id,
            service_url=self.service_url,
        )
        print(
            f"Connection to OpenScale established. WOS version = {self.wos_client.version}"
        )

    def _setup_openscale_monitoring(self, model_uid, deployment_uid):
        data_mart_id = get_or_create_data_mart(self.wos_client, self.config)
        service_provider_id = configure_service_provider(
            wos_client=self.wos_client,
            config=self.config,
            service_provider_name=self.service_provider_name,
            service_provider_description=self.service_provider_description,
            operational_space_id=self.operational_space_id,
            monitor_new_version=self.monitor_new_version,
        )
        subscription_id = configure_subscription(
            wos_client=self.wos_client,
            model_uid=model_uid,
            config=self.config,
            deployment_uid=deployment_uid,
            data_mart_id=data_mart_id,
            service_provider_id=service_provider_id,
            monitor_new_version=self.monitor_new_version,
            problem_type=self.problem_type,
            input_data_type=self.input_data_type,
            deployment_name=self.deployment_name,
        )
        payload_data_set_id = get_payload_data_set_id(self.wos_client, subscription_id)

        return subscription_id, data_mart_id, payload_data_set_id

    def _check_if_monitors_are_required(self):
        return any(
            [
                self.config.get("driftv2_params"),
                self.config.get("explainability_params"),
                self.config.get("quality_monitor_params"),
                self.config.get("fairness_monitor_params"),
            ]
        )

    def _configure_monitors(self, subscription_id, data_mart_id, payload_data_set_id):

        monitors_are_required = self._check_if_monitors_are_required()
        if not monitors_are_required:
            print("OpenScale configuration setup completed successfully.")
            return

        monitor_instances = (
            self.wos_client.monitor_instances.list().result.monitor_instances
        )
        configured_monitors = [
            m.entity.monitor_definition_id
            for m in monitor_instances
            if m.entity.target.target_id == subscription_id
        ]
        print(f"Configured monitors: {configured_monitors}")

        if "quality" not in configured_monitors and self.config.get(
            "quality_monitor_params"
        ):
            self._setup_quality_monitor(subscription_id, data_mart_id)

        if "fairness" not in configured_monitors and self.config.get(
            "fairness_monitor_params"
        ):
            self._setup_fairness_monitor(subscription_id, data_mart_id)

        if "drift_v2" not in configured_monitors and self.config.get("driftv2_params"):
            self._setup_drift_monitor(subscription_id, data_mart_id)

        if "explainability" not in configured_monitors and self.config.get(
            "explainability_params"
        ):
            self._setup_explainability_monitor(
                subscription_id, data_mart_id, payload_data_set_id
            )
        print("OpenScale configuration and monitor setup completed successfully.")

    def _setup_quality_monitor(self, subscription_id, data_mart_id):
        print("Creating quality monitor")
        monitor_details, monitor_id = create_monitor(
            self.wos_client,
            data_mart_id,
            subscription_id,
            monitor="quality",
            parameters=self.config.get("quality_monitor_params"),
            thresholds=self.config.get("quality_monitor_thr"),
        )
        feedback_dataset = self.wos_client.data_sets.list(
            type=DataSetTypes.FEEDBACK,
            target_target_id=subscription_id,
            target_target_type=TargetTypes.SUBSCRIPTION,
        ).result
        feedback_dataset_id = feedback_dataset.data_sets[0].metadata.id
        with open(self.config.get("feedback_data_file")) as f:
            feedback_data = json.load(f)
        self.wos_client.data_sets.store_records(
            feedback_dataset_id,
            request_body=feedback_data,
            background_mode=False,
        )
        self.wos_client.data_sets.get_records_count(data_set_id=feedback_dataset_id)
        run_monitor_and_show_metrics(self.wos_client, monitor_id, wait_seconds=15)

    def _setup_fairness_monitor(self, subscription_id, data_mart_id):
        print("Creating fairness monitor")
        monitor_details, monitor_id = create_monitor(
            self.wos_client,
            data_mart_id,
            subscription_id,
            monitor="fairness",
            parameters=self.config.get("fairness_monitor_params"),
            thresholds=self.config.get("fairness_monitor_thr"),
        )
        run_monitor_and_show_metrics(self.wos_client, monitor_id, wait_seconds=15)

    def _setup_drift_monitor(self, subscription_id, data_mart_id):
        print("Creating drift_v2 monitor")
        monitor_details, monitor_id = create_monitor(
            self.wos_client,
            data_mart_id,
            subscription_id,
            monitor="drift_v2",
            parameters=self.config.get("driftv2_params"),
            thresholds=None,
        )
        time.sleep(20)
        try: 
            run_monitor_and_show_metrics(self.wos_client, monitor_id, wait_seconds=15)
        except Exception as e:
            print(f"Instance monitor run failed trying again: {e}")
            time.sleep(30)
            run_monitor_and_show_metrics(self.wos_client, monitor_id, wait_seconds=15)

    def _setup_explainability_monitor(
        self, subscription_id, data_mart_id, payload_data_set_id
    ):
        print("Creating explainability monitor")
        monitor_details, monitor_id = create_monitor(
            self.wos_client,
            data_mart_id=data_mart_id,
            subscription_id=subscription_id,
            monitor="explainability",
            parameters=self.config.get("explainability_params"),
            thresholds=None,
        )
        pl_records_resp = self.wos_client.data_sets.get_list_of_records(
            data_set_id=payload_data_set_id, limit=1, offset=0
        ).result
        scoring_ids = [pl_records_resp["records"][0]["entity"]["values"]["scoring_id"]]
        explanation_types = ["lime", "contrastive"]
        result = self.wos_client.monitor_instances.explanation_tasks(
            scoring_ids=scoring_ids,
            explanation_types=explanation_types,
            subscription_id=subscription_id,
        ).result
        print(result)

    def _verify_payload_logging(
        self, payload_data_set_id, expected_num_records, predictions, scoring_payload
    ):
        verify_payload_logging(
            self.wos_client,
            payload_data_set_id,
            expected_num_records,
            predictions,
            scoring_payload,
        )


def verify_payload_logging(
    wos_client,
    payload_data_set_id,
    expected_num_records,
    predictions,
    scoring_payload,
    sleep_seconds=10,
):
    time.sleep(sleep_seconds)
    print("Verifying payload logging records...")
    try:
        pl_records_count = wos_client.data_sets.get_records_count(payload_data_set_id)
    except Exception as e:
        print(f"Failed to retrieve payload logging count: {e}")
        raise

    if pl_records_count != expected_num_records:
        print(
            "Payload logging did not happen as expected. Performing explicit logging."
        )
        try:
            wos_client.data_sets.store_records(
                data_set_id=payload_data_set_id,
                request_body=[
                    PayloadRecord(
                        scoring_id=str(uuid.uuid4()),
                        request=scoring_payload,
                        response={
                            "fields": predictions["predictions"][0]["fields"],
                            "values": predictions["predictions"][0]["values"],
                        },
                        response_time=460,
                    )
                ],
            )
            time.sleep(sleep_seconds)
            pl_records_count = wos_client.data_sets.get_records_count(
                payload_data_set_id
            )
        except Exception as e:
            print(f"Explicit payload logging failed: {e}")
            raise

    print(f"Number of records in the payload logging table: {pl_records_count}")


def validate_inputs(config_dict):
    """
    Validates required inputs in the configuration dictionary.
    Only fields with class-level defaults are optional.
    """

    # Required string fields
    required_str_fields = [
        "wml_space_id",
        "cloud_api_key",
        "wml_url",
        "bucket_name",
        "cos_resource_crn",
        "cos_endpoint",
        "label_field",
        "prediction_field",
    ]

    for field in required_str_fields:
        if not isinstance(config_dict.get(field), str):
            raise ValueError(f"Missing or invalid required string field: '{field}'")

    file_keys = ["training_data_file_name", "feedback_data_file", "scoring_data_file"]
    for key in file_keys:
        path = config_dict.get(key)
        if not isinstance(path, str) or not os.path.isfile(path):
            raise ValueError(f"Missing or invalid file path for '{key}'")

    # Required list fields
    required_list_fields = [
        "probability_fields",
        "feature_fields",
    ]
    for field in required_list_fields:
        if not isinstance(config_dict.get(field), list):
            print(f"Warning Missing or invalid  field: '{field}'")

    # Required dict fields
    optional_dict_fields = [
        "quality_monitor_params",
        "fairness_monitor_params",
        "explainability_params",
        "driftv2_params",
    ]
    for field in optional_dict_fields:
        if not isinstance(config_dict.get(field), dict):
            print(f"Warning - Missing or invalid monitor field: '{field}'")

    # Required dict fields
    required_dict_fields = [
        "wml_config"
    ]
    for field in required_dict_fields:
        if not isinstance(config_dict.get(field), dict):
            raise ValueError(f"Error - Missing or invalid required field: '{field}'")


def load_and_validate_scoring_data(scoring_data_file):
    min_num_records_to_score = 200
    try:
        with open(scoring_data_file, "r") as scoring_file:
            scoring_data = json.load(scoring_file)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in scoring data file: {e}")

    fields = scoring_data.get("fields")
    values = scoring_data.get("values")
    if not fields or not values:
        raise ValueError("Scoring data must contain 'fields' and 'values'.")

    # Validate there are enough records
    if len(values) < min_num_records_to_score:
        raise ValueError(
            f"Scoring data contains only {len(values)} records, "
            f"but {min_num_records_to_score} are required."
        )
    return fields, values


def publish_model_from_config(
    wml_client,
    config,
    training_data_references,
    model_name,
    software_spec_name,
    model_type,
):
    """
    Publishes a model to IBM Watson Machine Learning using config dictionary.

    All WML-specific settings should live under config['wml_config'].
    """
    if wml_client is None:
        raise RuntimeError("WML client is not initialized.")

    wml_config = config.get("wml_config", {})
    if not wml_config:
        raise ValueError("Missing 'wml_config' section in config.")
    print("Storing model...")
    # Extract WML settings
    model_object = wml_config.get("model_object")
    training_data = wml_config.get("training_data_df")
    pipeline = wml_config.get("pipeline")
    label_field = config.get("label_field")
    model_type = wml_config.get("model_type", model_type)

    # Determine required inputs based on model_object type
    if model_type.startswith("mllib") or model_type.startswith("spark"):
        if model_object is None:
            raise ValueError("'model_object' must be provided for Spark models.")
        if training_data is None:
            raise ValueError(
                "'training_data_df' must be provided as a Spark DataFrame for Spark models."
            )
        if pipeline is None:
            raise ValueError("'pipeline' must be provided for Spark models.")

    elif model_type.startswith("scikit-learn") or model_type.startswith("xgboost"):
        if model_object is None:
            raise ValueError(
                "'model_object' must be provided for sklearn/xgboost models."
            )
        if not isinstance(training_data, tuple) or len(training_data) != 2:
            raise ValueError(
                "'training_data_df' must be a tuple (X, y) for sklearn/xgboost models."
            )

    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    # Resolve software spec
    software_spec_uid = wml_client.software_specifications.get_uid_by_name(
        software_spec_name
    )

    model_props = {
        wml_client._models.ConfigurationMetaNames.NAME: model_name,
        wml_client._models.ConfigurationMetaNames.TYPE: model_type,
        wml_client._models.ConfigurationMetaNames.SOFTWARE_SPEC_UID: software_spec_uid,
        wml_client._models.ConfigurationMetaNames.TRAINING_DATA_REFERENCES: training_data_references,
        wml_client._models.ConfigurationMetaNames.LABEL_FIELD: label_field,
    }

    try:
        if model_type.startswith("mllib") or model_type.startswith("spark"):
            published_model_details = wml_client.repository.store_model(
                model=model_object,
                training_data=training_data,
                pipeline=pipeline,
                meta_props=model_props,
            )

        else:  # sklearn or xgboost
            x, y = training_data
            published_model_details = wml_client.repository.store_model(
                model=model_object,
                training_data=x,
                training_target=y,
                meta_props=model_props,
            )
        model_uid = wml_client.repository.get_model_id(published_model_details)
        print(f"Storing model completed successfully; model uid = {model_uid}")

        return model_uid

    except Exception as e:
        print(f"Failed to publish model '{model_name}': {e}")
        raise


def deploy_model_to_wml(wml_client, model_uid, deployment_name):
    """
    Deploys the model and returns the deployment UID and deployment metadata.
    """
    print("Deploying model...")
    deployment_details = wml_client.deployments.create(
        model_uid,
        meta_props={
            wml_client.deployments.ConfigurationMetaNames.NAME: deployment_name,
            wml_client.deployments.ConfigurationMetaNames.ONLINE: {},
        },
    )

    deployment_uid = wml_client.deployments.get_uid(deployment_details)
    print(f"Deploying model completed successfully; deployment uid = {deployment_uid}")
    return deployment_uid


def create_cos_connection_and_prepare_data_ref(wml_client, config):
    """
    Creates a COS connection and prepares the training data reference for model publishing.
    Returns the training data reference list.
    """
    datasource_type = wml_client.connections.get_datasource_type_uid_by_name(
        "bluemixcloudobjectstorage"
    )

    conn_meta_props = {
        wml_client.connections.ConfigurationMetaNames.NAME: "Connection My COS",
        wml_client.connections.ConfigurationMetaNames.DATASOURCE_TYPE: datasource_type,
        wml_client.connections.ConfigurationMetaNames.DESCRIPTION: "Connection to my COS",
        wml_client.connections.ConfigurationMetaNames.PROPERTIES: {
            "bucket": config["bucket_name"],
            "api_key": config["cloud_api_key"],
            "resource_instance_id": config["cos_resource_crn"],
            "iam_url": "https://iam.ng.bluemix.net/oidc/token",
            "url": config["cos_endpoint"],
        },
    }

    conn_details = wml_client.connections.create(meta_props=conn_meta_props)
    connection_id = wml_client.connections.get_uid(conn_details)

    training_data_references = [
        {
            "id": "German Credit Risk",
            "type": "connection_asset",
            "connection": {
                "id": connection_id,
                "href": f"/v2/connections/{connection_id}?space_id={config['wml_space_id']}",
            },
            "location": {
                "bucket": config["bucket_name"],
                "file_name": config["training_data_file_name"],
            },
        }
    ]
    return training_data_references


def find_or_delete_existing_deployment(
    wml_client, deployment_name, monitor_new_version
):
    """
    Searches for a deployment by name in the provided deployments metadata dictionary.
    If a matching deployment is found:
      - If `monitor_new_version` is True, deletes the deployment and returns its ID and model ID.
      - If `monitor_new_version` is False, returns the existing deployment and model IDs.
    If no matching deployment is found, returns (None, None).
    """
    deployments_list = wml_client.deployments.get_details()

    if not isinstance(deployments_list, dict):
        raise TypeError("deployments_list must be a dictionary.")

    if "resources" not in deployments_list:
        raise ValueError("Invalid deployments_list format: missing 'resources' key.")

    if not isinstance(deployment_name, str):
        raise TypeError("deployment_name must be a string.")

    try:
        for deployment in deployments_list["resources"]:
            model_id = deployment.get("entity", {}).get("asset", {}).get("id")
            deployment_id = deployment.get("metadata", {}).get("id")
            name = deployment.get("metadata", {}).get("name")

            if name == deployment_name:
                if monitor_new_version:
                    print(f"Deleting deployment id: {deployment_id}")
                    wml_client.deployments.delete(deployment_id)
                    print(
                        f"Deleted deployment_id: {deployment_id}, model_id: {model_id}"
                    )
                    return deployment_id, model_id
                else:
                    print(
                        f"Found existing model deployment with name '{deployment_name}', "
                        f"deployment ID: {deployment_id}, and model ID: {model_id}."
                    )

                    return deployment_id, model_id

        return None, None

    except Exception as e:
        print(f"An error occurred while checking or deleting the deployment: {e}")
        return None, None


def get_or_create_data_mart(wos_client, config):
    try:
        wos_client.data_marts.show()
        data_marts = wos_client.data_marts.list().result.data_marts

        if data_marts:
            print(f"Using existing datamart {data_marts[0].metadata.id}")
            return data_marts[0].metadata.id

        db_credentials = config.get("db_credentials")
        schema_name = config.get("schema_name")

        if db_credentials:
            if not schema_name:
                raise ValueError(
                    "schema_name must be provided with external DB credentials."
                )
            print("Setting up external datamart")
            result = wos_client.data_marts.add(
                background_mode=False,
                name="WOS Data Mart",
                description="Data Mart created by WOS tutorial notebook",
                database_configuration=DatabaseConfigurationRequest(
                    database_type=DatabaseType.POSTGRESQL,
                    credentials=PrimaryStorageCredentialsLong(
                        hostname=db_credentials["hostname"],
                        username=db_credentials["username"],
                        password=db_credentials["password"],
                        db=db_credentials["database"],
                        port=db_credentials["port"],
                        ssl=True,
                        sslmode=db_credentials["sslmode"],
                        certificate_base64=db_credentials["certificate_base64"],
                    ),
                    location=LocationSchemaName(schema_name=schema_name),
                ),
            ).result
        else:
            print("Setting up internal datamart")
            result = wos_client.data_marts.add(
                background_mode=False,
                name="WOS Data Mart",
                description="Data Mart created by WOS tutorial notebook",
                internal_database=True,
            ).result

        return result.metadata.id

    except Exception as e:
        print(f"Error in data mart setup: {e}")
        raise


def check_service_provider(
    wos_client, service_provider_name, wml_space_id, operational_space_id
):
    try:
        service_provider_id = None
        service_providers = wos_client.service_providers.list().result.service_providers
        print("Configuring service provider")

        for service_provider in service_providers:
            service_provider_type = getattr(
                service_provider.entity, "service_type", None
            )
            service_provider_space_id = getattr(
                service_provider.entity, "deployment_space_id", None
            )

            service_provider_operational_space_id = getattr(
                service_provider.entity, "operational_space_id", None
            )
            service_provider_instance_name = getattr(
                service_provider.entity, "name", None
            )
            if (
                (service_provider_space_id == wml_space_id)
                and (service_provider_type == ServiceTypes.WATSON_MACHINE_LEARNING)
                and (service_provider_operational_space_id == operational_space_id)
                and (service_provider_instance_name == service_provider_name)
            ):
                service_provider_id = getattr(service_provider.metadata, "id", None)
                print(
                    f"Found existing WML service provider '{service_provider_name}' with ID: {service_provider_id} for the space id {service_provider_space_id}"
                )
                return service_provider_id
        return service_provider_id

    except Exception as e:
        print(f"Error in service provider configuration: {e}")
        raise


def delete_service_provider(wos_client, service_provider_id):
    try:
        print(f"Deleting service provider with ID: {service_provider_id}")
        wos_client.service_providers.delete(service_provider_id)
        time.sleep(30)
    except Exception as e:
        raise RuntimeError("Error occurred while deleting service provider")


def configure_service_provider(
    wos_client,
    config,
    service_provider_name,
    service_provider_description,
    operational_space_id,
    monitor_new_version,
):
    try:
        wml_space_id = config.get("wml_space_id")
        service_provider_id = check_service_provider(
            wos_client, service_provider_name, wml_space_id, operational_space_id
        )

        # Case 1: Force recreate (monitor_new_version=True)
        if monitor_new_version:
            if service_provider_id:
                delete_service_provider(
                    wos_client=wos_client, service_provider_id=service_provider_id
                )
            print("Adding new service provider")
            return add_new_service_provider(
                wos_client=wos_client,
                config=config,
                service_provider_name=service_provider_name,
                service_provider_description=service_provider_description,
                operational_space_id=operational_space_id,
            )

        # Case 2: Reuse existing provider
        if service_provider_id:
            return service_provider_id

        # Case 3: No existing provider, create new
        print("Adding new service provider")
        return add_new_service_provider(
            wos_client=wos_client,
            config=config,
            service_provider_name=service_provider_name,
            service_provider_description=service_provider_description,
            operational_space_id=operational_space_id,
        )

    except Exception as e:
        print(f"Error in service provider configuration: {e}")
        raise


def add_new_service_provider(
    wos_client,
    config,
    service_provider_name,
    service_provider_description,
    operational_space_id,
):
    """
    Adds a new Watson Machine Learning (WML) service provider to Watson OpenScale (WOS).
    """
    try:
        added_service_provider_result = wos_client.service_providers.add(
            name=service_provider_name,
            description=service_provider_description,
            service_type=ServiceTypes.WATSON_MACHINE_LEARNING,
            deployment_space_id=config.get("wml_space_id"),
            operational_space_id=operational_space_id,
            credentials=WMLCredentialsCloud(
                apikey=config.get("cloud_api_key"),
                url=config.get("wml_url"),
                instance_id=None,
            ),
            background_mode=False,
        ).result

        service_provider_id = added_service_provider_result.metadata.id
        print(
            f"Added new service provider successfully; Service provider ID {service_provider_id}"
        )
        return service_provider_id

    except Exception as e:
        print(f"An error occurred while adding the service provider: {e}")
        raise


def check_existing_subscription(wos_client, model_uid, deployment_uid):
    """
    Checks if a subscription exists for the given model and deployment.
    """
    try:

        subscriptions = wos_client.subscriptions.list().result.subscriptions
        subscription_id = None
        sub_status = None

        for subscription in subscriptions:
            sub_model_id = getattr(subscription.entity.asset, "asset_id", None)
            sub_deployment_id = getattr(
                subscription.entity.deployment, "deployment_id", None
            )
            sub_status = getattr(subscription.entity.status, "state", None)

            if sub_model_id == model_uid and sub_deployment_id == deployment_uid:
                subscription_id = getattr(subscription.metadata, "id", None)
                print(
                    f"Found existing subscription {subscription_id} for model UID {model_uid} "
                    f"and deployment UID {deployment_uid} with status '{sub_status}'. "
                )
                return subscription_id, sub_status

        return subscription_id, sub_status
    except Exception as e:
        print(f"Failed to obtain subscription data  {e}")
        raise


def configure_subscription(
    wos_client,
    config,
    model_uid,
    deployment_uid,
    data_mart_id,
    service_provider_id,
    monitor_new_version,
    problem_type,
    input_data_type,
    deployment_name,
):
    # Validate inputs
    # subscriptions = wos_client.subscriptions.list().result.subscriptions
    # if not isinstance(subscriptions, list):
    #     raise TypeError("subscriptions must be a list of subscription objects.")
    if not isinstance(model_uid, str):
        raise TypeError("model_uid must be a string.")

    try:
        # Check for existing subscription
        subscription_id, sub_status = check_existing_subscription(
            wos_client=wos_client, model_uid=model_uid, deployment_uid=deployment_uid
        )

        # Case 1: User wants to monitor a new version — delete and recreate
        if monitor_new_version:
            if subscription_id:
                delete_existing_subscription(wos_client, subscription_id)
            new_subscription_id = create_new_subscription(
                wos_client=wos_client,
                config=config,
                model_uid=model_uid,
                deployment_uid=deployment_uid,
                data_mart_id=data_mart_id,
                service_provider_id=service_provider_id,
                problem_type=problem_type,
                input_data_type=input_data_type,
                deployment_name=deployment_name,
            )
            print(
                f"New subscription created successfully with ID: {new_subscription_id}"
            )
            return new_subscription_id

        # Case 2: Reuse existing active subscription
        if subscription_id and sub_status == StatusStateType.ACTIVE:
            print(f"Reusing existing active subscription with ID: {subscription_id}")
            return subscription_id

        # Case 3: Subscription exists but is not active — raise error
        if subscription_id and sub_status != StatusStateType.ACTIVE:
            raise RuntimeError(
                f"Found existing subscription with ID {subscription_id} but status is '{sub_status}'. "
                "Please set monitor_new_version=True to delete and recreate the subscription."
            )

        # Case 4: No subscription exists — create a new one
        new_subscription_id = create_new_subscription(
            wos_client=wos_client,
            config=config,
            model_uid=model_uid,
            deployment_uid=deployment_uid,
            data_mart_id=data_mart_id,
            service_provider_id=service_provider_id,
            problem_type=problem_type,
            input_data_type=input_data_type,
            deployment_name=deployment_name,
        )
        print(f"New subscription created successfully with ID: {new_subscription_id}")
        return new_subscription_id

    except Exception as e:
        print(f"An error occurred while configuring the subscription: {e}")
        raise


def delete_existing_subscription(wos_client, subscription_id):
    """
    Deletes a subscription from Watson OpenScale and logs the result.
    """
    try:
        wos_client.subscriptions.delete(subscription_id)
        print(f"Deleted existing subscription with ID: {subscription_id}")
    except Exception as e:
        print(f"Failed to delete subscription {subscription_id}: {e}")
        raise


def create_new_subscription(
    wos_client,
    config,
    model_uid,
    deployment_uid,
    data_mart_id,
    service_provider_id,
    problem_type,
    input_data_type,
    deployment_name,
):

    if not isinstance(model_uid, str) or not isinstance(deployment_uid, str):
        raise TypeError("model_uid and deployment_uid must be strings.")

    label_field = config.get("label_field")
    probability_fields = config.get("probability_fields")
    prediction_field = config.get("prediction_field")
    feature_fields = config.get("feature_fields")
    categorical_fields = config.get("categorical_fields")

    training_data_file_name = config.get("training_data_file_name")
    bucket_name = config.get("bucket_name")
    cos_resource_crn = config.get("cos_resource_crn")
    cos_endpoint = config.get("cos_endpoint")
    cloud_api_key = config.get("cloud_api_key")
    wml_space_id = config.get("wml_space_id")

    # Mapping dictionaries
    input_data_type_map = {
        "structured": InputDataType.STRUCTURED,
        "unstructured_image": InputDataType.UNSTRUCTURED_IMAGE,
        "unstructured_text": InputDataType.UNSTRUCTURED_TEXT,
        "unstructured_audio": InputDataType.UNSTRUCTURED_AUDIO,
        "unstructured_video": InputDataType.UNSTRUCTURED_VIDEO,
    }

    problem_type_map = {
        "regression": ProblemType.REGRESSION,
        "binary": ProblemType.BINARY_CLASSIFICATION,
        "binary_classification": ProblemType.BINARY_CLASSIFICATION,
        "multiclass": ProblemType.MULTICLASS_CLASSIFICATION,
        "multiclass_classification": ProblemType.MULTICLASS_CLASSIFICATION,
    }

    input_data_type = input_data_type_map[input_data_type]
    problem_type = problem_type_map[problem_type]

    model_asset_details_from_deployment = (
        wos_client.service_providers.get_deployment_asset(
            data_mart_id=data_mart_id,
            service_provider_id=service_provider_id,
            deployment_id=deployment_uid,
            deployment_space_id=wml_space_id,
        )
    )

    try:
        asset = Asset(
            asset_id=model_asset_details_from_deployment["entity"]["asset"]["asset_id"],
            name=model_asset_details_from_deployment["entity"]["asset"]["name"],
            url=model_asset_details_from_deployment["entity"]["asset"]["url"],
            asset_type=AssetTypes.MODEL,
            input_data_type=input_data_type,
            problem_type=problem_type,
        )
        asset_deployment = AssetDeploymentRequest(
            deployment_id=deployment_uid,
            name=deployment_name,
            deployment_type=DeploymentTypes.ONLINE,
            url=model_asset_details_from_deployment["entity"]["asset"]["url"],
        )

        training_data_reference = TrainingDataReference(
            type="cos",
            location=COSTrainingDataReferenceLocation(
                bucket=bucket_name, file_name=training_data_file_name
            ),
            connection=COSTrainingDataReferenceConnection.from_dict(
                {
                    "resource_instance_id": cos_resource_crn,
                    "url": cos_endpoint,
                    "api_key": cloud_api_key,
                    "iam_url": "https://iam.bluemix.net/oidc/token",
                }
            ),
        )

        asset_properties_request = AssetPropertiesRequest(
            label_column=label_field,
            probability_fields=probability_fields,
            prediction_field=prediction_field,
            feature_fields=feature_fields,
            categorical_fields=categorical_fields,
            training_data_reference=training_data_reference,
            training_data_schema=SparkStruct.from_dict(
                model_asset_details_from_deployment["entity"]["asset_properties"][
                    "training_data_schema"
                ]
            ),
        )

        subscription_details = wos_client.subscriptions.add(
            data_mart_id=data_mart_id,
            service_provider_id=service_provider_id,
            asset=asset,
            deployment=asset_deployment,
            asset_properties=asset_properties_request,
            background_mode=False,
        ).result

        subscription_id = subscription_details.metadata.id
        subscription_status = subscription_details.entity.status.state
        if subscription_status != StatusStateType.ACTIVE:
            raise RuntimeError(
                f"New subscription created with ID: {subscription_id} but subscription status {subscription_status}"
            )
        return subscription_id

    except Exception as e:
        print(f"An error occurred while creating the subscription: {e}")
        raise


def get_payload_data_set_id(wos_client, subscription_id):
    try:
        payload_data_sets = wos_client.data_sets.list(
            type=DataSetTypes.PAYLOAD_LOGGING,
            target_target_id=subscription_id,
            target_target_type=TargetTypes.SUBSCRIPTION,
        ).result.data_sets

        if payload_data_sets:
            print("Payload data set id:", payload_data_sets[0].metadata.id)
            return payload_data_sets[0].metadata.id
        else:
            print("Payload data set not found. Please check subscription status.")
            return None
    except Exception as e:
        print(f"Error retrieving payload data set: {e}")
        raise


def create_monitor(
    wos_client, data_mart_id, subscription_id, monitor, parameters=None, thresholds=None
):
    """
    Creates a monitor instance in Watson OpenScale (WOS) for a given subscription.

    """
    if (
        not isinstance(data_mart_id, str)
        or not isinstance(subscription_id, str)
        or not isinstance(monitor, str)
    ):
        raise TypeError(
            "data_mart_id, subscription_id, and monitor must all be strings."
        )

    monitor_map = {
        "drift_v2": wos_client.monitor_definitions.MONITORS.DRIFT_V2.ID,
        "explainability": wos_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID,
        "drift": wos_client.monitor_definitions.MONITORS.DRIFT.ID,
        "fairness": wos_client.monitor_definitions.MONITORS.FAIRNESS.ID,
        "quality": wos_client.monitor_definitions.MONITORS.QUALITY.ID,
    }

    if monitor not in monitor_map:
        raise ValueError(
            f"Unsupported monitor type '{monitor}'. Supported types are: {', '.join(monitor_map.keys())}"
        )

    try:
        target = Target(target_type=TargetTypes.SUBSCRIPTION, target_id=subscription_id)

        monitor_details = wos_client.monitor_instances.create(
            data_mart_id=data_mart_id,
            background_mode=False,
            monitor_definition_id=monitor_map[monitor],
            target=target,
            parameters=parameters,
            thresholds=thresholds,
        ).result

        monitor_instance_id = monitor_details.metadata.id
        print(f"waiting for {20} sec for system")
        time.sleep(20)

        return monitor_details, monitor_instance_id

    except Exception as e:
        print(f"An error occurred while creating the monitor: {e}")
        raise


def run_monitor_and_show_metrics(wos_client, monitor_instance_id, wait_seconds=5):
    """
    Runs a monitor instance in Watson OpenScale (WOS) and retrieves its metrics after a delay.
    """
    if not isinstance(monitor_instance_id, str):
        raise TypeError("monitor_instance_id must be a string.")
    if not isinstance(wait_seconds, int) or wait_seconds < 0:
        raise ValueError("wait_seconds must be a non-negative integer.")

    try:
        run_details = wos_client.monitor_instances.run(
            monitor_instance_id=monitor_instance_id, background_mode=False
        )
        print("Monitor run details:", run_details)
        print(f"waiting for {wait_seconds}")
        time.sleep(wait_seconds)

        _ = wos_client.monitor_instances.show_metrics(
            monitor_instance_id=monitor_instance_id
        )
        print(f"waiting for {wait_seconds}")
        time.sleep(wait_seconds)
        return run_details

    except Exception as e:
        print(f"An error occurred while running the monitor or retrieving metrics: {e}")
        raise
