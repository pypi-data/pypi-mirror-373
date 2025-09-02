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

import logging

from ibm_cloud_sdk_core import BaseService
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
    ApplicabilitySelection, IntegratedSystems, MetricThreshold,
    MonitorInstanceSchedule, MonitorMetricRequest, MonitorRuntime,
    ScheduleStartTime, Target, MonitorTagRequest)
from ibm_watson_openscale.supporting_classes.enums import (
    MetricThresholdTypes, TargetTypes)
from ibm_watson_openscale.utils.utils import validate_type


class SetupCustomMonitor:
    def __init__(self, ai_client: BaseService, service_url: str) -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        self.service_url = service_url
        self.results = {}
        self.config = {}
        logging.info("SetupCustomMonitor instance initialized.")

    def setup_configuration(self, config, function_code):
        try:
            from ibm_watsonx_ai import APIClient
        except Exception as e:
            logging.error(f"ibm_watsonx_ai package is not available, Please install the latest version ")
            raise e
        logging.basicConfig(level=logging.INFO)
        CLOUD_API_KEY = config.get('CLOUD_API_KEY')
        is_cpd = "CPD_INFO" in config
        if is_cpd:
            cpd_info = config.get("CPD_INFO")
            if not cpd_info:
                raise ValueError("Missing 'CPD_INFO' in configuration.")
            cpd_url = cpd_info.get("CPD_URL") if cpd_info.get("CPD_URL") else config.get("OPENSCALE_API_URL")
            cpd_password = cpd_info.get("API_KEY") if cpd_info.get("API_KEY") else config.get("CLOUD_API_KEY")
            cpd_username = cpd_info.get("USERNAME")
            cpd_version = cpd_info.get("VERSION")

            fields = {
                "CPD_URL": cpd_url,
                "USERNAME": cpd_username,
                "API_KEY": cpd_password,
                "VERSION": cpd_version
            }

            missing_fields = [name for name, value in fields.items() if not value]

            if missing_fields:
                raise ValueError(f"Missing required CPD configuration fields: {', '.join(missing_fields)}")

            from urllib.parse import urlparse
            if not urlparse(cpd_url).scheme:
                raise ValueError("Invalid CPD_URL: Must be a valid URL.")
            cpd_config = {
                "token_info": {
                    "url": "{}/icp4d-api/v1/authorize".format(cpd_url),
                    "headers": {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    "payload": {
                        "username": cpd_username,
                        "api_key": cpd_password,
                    },
                    "method": "post"
                }
            }

        defaults = {
            "DEPLOYMENT_NAME": "Custom Metrics Provider Deployment",
            "PYTHON_FUNCTION_NAME": "Custom Metrics Provider Function",
            "WML_URL": "https://us-south.ml.cloud.ibm.com",
            "IAM_URL": "https://iam.cloud.ibm.com/oidc/token",
            "CUSTOM_METRICS_PROVIDER_NAME": "Custom Metrics Provider",
            "CUSTOM_MONITOR_NAME": "Sample Model Performance",
            "OPENSCALE_API_URL": "https://api.aiopenscale.cloud.ibm.com",
            "DATAMART_ID": "00000000-0000-0000-0000-000000000000",
            "CUSTOM_METRICS_WAIT_TIME": 60,
            "DEPLOYMENT_TYPE": "wml_online",
            "RUNTIME_ENV": "runtime-24.1-py3.11",
            "ENABLE_SCHEDULE": False,
            "SCHEDULE" : {
                "repeat_interval": 1,
                "repeat_type": "hour",
                "delay_unit": "minute",
                "delay_time": 5
            },
            "DELETE_CUSTOM_MONITOR": True,
            "DELETE_CUSTOM_MONITOR_INSTANCE": True,
            "INPUT_DATA_TYPES": ["structured","unstructured_text","unstructured_image"],
            "ALGORITHM_TYPES": ["binary", "regression", "multiclass", "question_answering", "summarization",
                                 "retrieval_augmented_generation", "classification", "generation", "extraction"],
            "TAGS": [
                        {
                            "name": "region",
                            "TAG_DESCRIPTION": "customer geographical region"
                        }
                    ],
            "CUSTOM_METRICS_PROVIDER_CREDENTIALS" : {
                "auth_type":"bearer"
            },
            "token_info": {
                "url":  "https://iam.cloud.ibm.com/identity/token",
                "headers": { "Content-type": "application/x-www-form-urlencoded" },
                "payload": "grant_type=urn:ibm:params:oauth:grant-type:apikey&response_type=cloud_iam&apikey="+ CLOUD_API_KEY,
                "method": "POST"
             }
        }
        config = {**defaults, **config}
        if is_cpd:
            creds = config.setdefault("CUSTOM_METRICS_PROVIDER_CREDENTIALS", {})
            token_info = creds.setdefault("token_info", cpd_config.get("token_info", {}))
            config["WML_URL"] = config["OPENSCALE_API_URL"]
            token_info.setdefault("url", f"{config['OPENSCALE_API_URL']}/icp4d-api/v1/authorize")
            payload = token_info.setdefault("payload", {})
            payload.setdefault("api_key", config.get("CLOUD_API_KEY"))
        else:
            if "token_info" not in config.get("CUSTOM_METRICS_PROVIDER_CREDENTIALS", {}):
                config["CUSTOM_METRICS_PROVIDER_CREDENTIALS"]["token_info"] = config["token_info"]
        if config.get("DEPLOYMENT_NAME") and config.get("SUBSCRIPTION_ID"):
            config["DEPLOYMENT_NAME_PREFIX"] = config.get("DEPLOYMENT_NAME") + config.get("SUBSCRIPTION_ID")
        else:
            config["DEPLOYMENT_NAME_PREFIX"] = config.get("DEPLOYMENT_NAME")
        try:
            self.config  = config
            if 'SPACE_ID' not in config or not config['SPACE_ID']:
                raise ValueError("'SPACE_ID' is missing in the configuration")
            print("Initialising  Watson Machine Learning (WML) client.")
            if is_cpd:
                print("Initilising CPD WML")
                credentials = {
                    "url": cpd_url,
                    "username": cpd_username,
                    "apikey": cpd_password,
                    "instance_id": "openshift",
                    "version": cpd_version
                }

                wml_client = APIClient(credentials)
            else:
                print("Initilising Cloud WML")
                wml_client = APIClient({
                    "url": config["WML_URL"],
                    "apikey": config["CLOUD_API_KEY"]
                })

            wml_client.set.default_space(config['SPACE_ID'])
            print(f"Default space set to {config['SPACE_ID']}")

            # Deployment Cleanup
            print(f"Cleaning up existing deployment {config['DEPLOYMENT_NAME']}.")
            self._cleanup_existing_deployment(
                wml_client, config["DEPLOYMENT_NAME_PREFIX"])

            # Function Creation
            print("Creating custom function.")
            function_id = self._create_function(
                wml_client, config, function_code)

            # Deployment
            self.deployment_id, scoring_url = self._deploy_function(
                wml_client, config, function_id)

            print(f"Deployed Custom Metrics Provider: {scoring_url}")
            # Integrated System Cleanup
            print("Setting up an Integration System for Custom Metrics Provider")
            integrated_system_id = self._setup_integrated_system(config, scoring_url)
            print(integrated_system_id)

            # create_custom_monitor
            print("Creating custom monitor.")
            custom_monitor_id = self._create_custom_monitor(config)
            result = self._associate_integrated_system(integrated_system_id, custom_monitor_id)

            # _create_monitor_instance
            print("Creating monitor instance.")
            monitor_instance_id = self._create_monitor_instance(config, custom_monitor_id, integrated_system_id)
            print(monitor_instance_id)

            logging.info("Custom monitor setup completed successfully")
            return self.results

        except Exception as e:
            logging.error(f"Setup failed: {str(e)}")
            raise e

    def _cleanup_existing_deployment(self, wml_client, deployment_name):
        deployment_type = self.config.get("DEPLOYMENT_TYPE","wml_online").lower()

        if deployment_type == "wml_online":
            try:
                print(f"Performing wml_online deployment Cleanup for: {deployment_name}")
                deployments = wml_client.deployments.get_details()
                for deployment in deployments["resources"]:
                    if deployment["metadata"]["name"] == deployment_name:
                        deployment_id = deployment["metadata"]["id"]
                        print(f"Deleting wml_online deployment: {deployment_id} ")
                        wml_client.deployments.delete(deployment_id)
                        asset_id = deployment["entity"].get("asset", {}).get("id")
                        if asset_id:
                            print(f"Deleting associated asset: {asset_id}")
                            wml_client.repository.delete(asset_id)
            except Exception as e:
                print(f"Error during wml_online deployment clenaup {deployment_name} : {e}")

        elif deployment_type == "wml_batch":
            try:
                print(f"Performing Batch deployment Cleanup for: {deployment_name}")
                deployments = wml_client.deployments.get_details()
                for deployment in deployments["resources"]:
                    if deployment["metadata"]["name"] == deployment_name or deployment["metadata"]["name"] == deployment_name + '_WRAPPER':
                        deployment_id = deployment["metadata"]["id"]
                        print(f"Deleting Batch deployment: {deployment_id} ")
                        wml_client.deployments.delete(deployment_id)
                        asset_id = deployment["entity"].get("asset", {}).get("id")
                        if asset_id:
                            print(f"Deleting associated asset: {asset_id}")
                            wml_client.repository.delete(asset_id)
            except Exception as e:
                print(f"Error during Batch deployment clenaup {deployment_name} : {e}")


    def _create_function(self, wml_client, config, code):
        deployment_type = self.config.get("DEPLOYMENT_TYPE","wml_online").lower()
        software_spec_id = wml_client.software_specifications.get_id_by_name(
                config['RUNTIME_ENV'])
        try:
            function_props = {
                wml_client.repository.FunctionMetaNames.NAME: config['PYTHON_FUNCTION_NAME'],
                wml_client.repository.FunctionMetaNames.SOFTWARE_SPEC_ID: software_spec_id
            }
            function_artifact = wml_client.repository.store_function(
                meta_props=function_props, function=code)
            function_id = wml_client.repository.get_function_id(function_artifact)
            self.results["function_id"] = function_id
            return function_id
        except Exception as e:
            print(f"Error during create function of deployment type {deployment_type} : {e}")

    def _deploy_function(self, wml_client, config, function_id):
        deployment_type = self.config.get("DEPLOYMENT_TYPE","wml_online").lower()
        try:
            self.hardware_spec_id = wml_client.hardware_specifications.get_id_by_name('M')
            if deployment_type == "wml_online":
                print(f"Deploy function as ONLINE : {config['DEPLOYMENT_NAME']}")
                deploy_meta = {
                    wml_client.deployments.ConfigurationMetaNames.NAME: config["DEPLOYMENT_NAME_PREFIX"],
                    wml_client.deployments.ConfigurationMetaNames.ONLINE: {},
                    wml_client.deployments.ConfigurationMetaNames.HARDWARE_SPEC: {"id": self.hardware_spec_id}
                }
            elif deployment_type == "wml_batch":
                print(f"Deploy function as BATCH : {config['DEPLOYMENT_NAME']}")
                deploy_meta = {
                    wml_client.deployments.ConfigurationMetaNames.NAME: config["DEPLOYMENT_NAME_PREFIX"],
                    wml_client.deployments.ConfigurationMetaNames.BATCH: {},
                    wml_client.deployments.ConfigurationMetaNames.HARDWARE_SPEC: { "name": "S", "num_nodes": 1}
                    }
            deployment = wml_client.deployments.create(function_id, meta_props=deploy_meta)
            deployment_id = wml_client.deployments.get_uid(deployment)
            deployment_details = wml_client.deployments.get_details(deployment_id)
            created_at = deployment_details['metadata']['created_at']
            current_date = created_at.split("T")[0] if "T" in created_at else ""
            if deployment_type == "wml_online":
                scoring_url = wml_client.deployments.get_scoring_href(deployment)
                scoring_url += f"?version={current_date}"
            elif deployment_type == "wml_batch":
                scoring_url = config['WML_URL'] + '/ml/v4/deployment_jobs?version='+current_date
            self.results.update({"deployment_id": deployment_id, "scoring_url": scoring_url})
            return deployment_id, scoring_url
        except Exception as e:
            print(f"Error during Deploy function of deployment type {deployment_type} : {e}")

    def _setup_integrated_system(self, config, scoring_url):
        # Cleanup existing systems
        systems = IntegratedSystems(self._ai_client).list().result.integrated_systems
        for system in systems:
            if system.entity.name == config['CUSTOM_METRICS_PROVIDER_NAME']:
                IntegratedSystems(self._ai_client).delete(
                    integrated_system_id=system.metadata.id)

        # Create new integrated system
        system = self._ai_client.integrated_systems.add(
            name=config['CUSTOM_METRICS_PROVIDER_NAME'],
            description="Custom metrics provider system",
            type="custom_metrics_provider",
            credentials=config['CUSTOM_METRICS_PROVIDER_CREDENTIALS'],
            connection={
                "display_name": config['CUSTOM_METRICS_PROVIDER_NAME'],
                "endpoint": scoring_url
            }
        ).result
        self.results["integrated_system_id"] = system.metadata.id
        return system.metadata.id


    def _create_custom_monitor(self, config):
        is_schedule = "SCHEDULE" in config
        if is_schedule:
            schedule_info = config["SCHEDULE"]
            REPEAT_INTERVAL = schedule_info.get("repeat_interval")
            REPEAT_TYPE = schedule_info.get("repeat_type")
            delay_unit = schedule_info.get("delay_unit")
            delay_time = schedule_info.get("delay_time")
        # Step 1: Check if monitor already exists
        existing_monitors = self._ai_client.monitor_definitions.list().result.monitor_definitions
        for monitor in existing_monitors:
            if monitor.entity.name == config['CUSTOM_MONITOR_NAME']:
                if config.get('DELETE_CUSTOM_MONITOR', False):
                    print(f"Deleting existing monitor: {monitor.entity.name}")
                    self._ai_client.monitor_definitions.delete(monitor.metadata.id,background_mode=False)
                else:
                    print(f"Reusing existing monitor: {monitor.entity.name}")
                    self.results["custom_monitor_id"] = monitor.metadata.id
                    return monitor.metadata.id

        # Step 2: Set applicability
        problem_type_selection = ApplicabilitySelection(problem_type=config['ALGORITHM_TYPES'])
        input_data_type_selection = ApplicabilitySelection(input_data_type=config['INPUT_DATA_TYPES'])
        # Step 3: Dynamically build metric definitions
        metrics = []
        for metric_cfg in config.get('MONITOR_METRICS', []):
            metric_name = metric_cfg.get('name')
            thresholds = []
            threshold_cfg = metric_cfg.get('thresholds', {})

            for threshold_type, value in threshold_cfg.items():
                if threshold_type.lower() == 'lower_limit':
                    thresholds.append(MetricThreshold(
                        type=MetricThresholdTypes.LOWER_LIMIT,
                        default=value
                    ))
                elif threshold_type.lower() == 'upper_limit':
                    thresholds.append(MetricThreshold(
                        type=MetricThresholdTypes.UPPER_LIMIT,
                        default=value
                    ))
                else:
                    print(f"Warning: Unknown threshold type '{threshold_type}' for metric '{metric_name}'")

            metrics.append(MonitorMetricRequest(
                name=metric_name,
                applies_to=problem_type_selection,
                thresholds=thresholds
            ))

        # Step 4: Dynamically build tag definitions
        tags = []
        tag_configurations = config.get('TAGS', [])
        for tag in tag_configurations:
            name = tag.get('name')
            description = tag.get('TAG_DESCRIPTION')
            # Validate if both name and description exist
            if name and description:
                tags.append(MonitorTagRequest(name=name, description=description))
            else:
                print(f"Invalid tag configuration: {tag}")


        # Step 5: Optional scheduling
        if config['ENABLE_SCHEDULE']:
            schedule = MonitorInstanceSchedule(
                repeat_interval=REPEAT_INTERVAL,
                repeat_unit=REPEAT_TYPE,
                start_time=ScheduleStartTime(
                    type="relative", delay_unit=delay_unit, delay=delay_time)
            )
            monitor_runtime = MonitorRuntime(type="custom_metrics_provider")
        else:
            schedule = None
            monitor_runtime = None

        # Step 6: Create the monitor
        monitor_def = self._ai_client.monitor_definitions.add(
            name=config['CUSTOM_MONITOR_NAME'],
            metrics=metrics,
            tags=tags,
            schedule=schedule,
            applies_to=input_data_type_selection,
            monitor_runtime=monitor_runtime,
            background_mode=False
        ).result

        # Step 7: Save and return monitor ID
        monitor_id = monitor_def.metadata.id
        self.results["custom_monitor_id"] = monitor_id
        print(f"Custom monitor created with ID: {monitor_id}")
        return monitor_id


    def _create_monitor_instance(self,config, custom_monitor_id, integrated_system_id):
        deployment_type = self.config.get("DEPLOYMENT_TYPE","wml_online").lower()
        existing_instances = self._ai_client.monitor_instances.list().result.monitor_instances
        monitor_instance_id = None
        try:
            for instance in existing_instances:
                if instance.entity.monitor_definition_id == custom_monitor_id:
                    monitor_instance_id = instance.metadata.id

                    if config.get("DELETE_CUSTOM_MONITOR_INSTANCE", False):
                        print(f"Deleting existing monitor instance: {monitor_instance_id}")
                        self._ai_client.monitor_instances.delete(monitor_instance_id,background_mode=False)
                        monitor_instance_id = None
                        break  # Proceed to create a new one

                    else:
                        print(f"Updating existing monitor instance: {monitor_instance_id}")
                        if deployment_type == "wml_online":
                            patch_payload = [
                                {
                                    "op": "replace",
                                    "path": "/parameters",
                                    "value": {
                                        "custom_metrics_provider_id": integrated_system_id,
                                        "custom_metrics_wait_time": config["CUSTOM_METRICS_WAIT_TIME"],
                                        "enable_custom_metric_runs": True
                                    }
                                }
                            ]
                        elif deployment_type == "wml_batch":
                            custom_metrics_wait_time = config.get("custom_metrics_wait_time", 120)
                            patch_payload = [
                                {
                                "op": "replace",
                                "path": "/parameters",
                                "value": {
                                    "custom_metrics_provider_id": integrated_system_id,
                                    "custom_metrics_provider_type": "wml_batch",
                                    "custom_metrics_wait_time":  config["CUSTOM_METRICS_WAIT_TIME"],
                                    "space_id": config['SPACE_ID'],
                                    "deployment_id": self.deployment_id,
                                    "hardware_spec_id": self.hardware_spec_id
                                }
                                }
                            ]
                        self._ai_client.monitor_instances.update(
                            monitor_instance_id,
                            patch_payload,
                            update_metadata_only=True
                        )
                        self.results["custom_monitor_instance_id"] = monitor_instance_id
                        return monitor_instance_id

            # No instance found or it was deleted — create a new one
            print(f"Creating new monitor instance for monitor definition: {custom_monitor_id}")
            target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id=config["SUBSCRIPTION_ID"]
            )
            if deployment_type == "wml_online":
                parameters = {
                    "custom_metrics_provider_id": integrated_system_id,
                    "custom_metrics_wait_time": config["CUSTOM_METRICS_WAIT_TIME"],
                    "enable_custom_metric_runs": True
                }
            elif deployment_type == "wml_batch":
                parameters = {
                    "custom_metrics_provider_id": integrated_system_id,
                    "custom_metrics_provider_type": "wml_batch",
                    "custom_metrics_wait_time": config["CUSTOM_METRICS_WAIT_TIME"],
                    "space_id": config['SPACE_ID'],
                    "deployment_id": self.deployment_id,
                    "hardware_spec_id": self.hardware_spec_id
                }
            instance = self._ai_client.monitor_instances.create(
                data_mart_id=config["DATAMART_ID"],
                background_mode=False,
                monitor_definition_id=custom_monitor_id,
                target=target,
                parameters=parameters
            ).result

            monitor_instance_id = instance.metadata.id
            print(f"Monitor instance created: {monitor_instance_id}")
            self.results["custom_monitor_instance_id"] = monitor_instance_id
            return monitor_instance_id
        except Exception as e:
            print(f"Error creating monitor instance : {e}")

    def _associate_integrated_system(self, integrated_system_id, custom_monitor_id):
        response = self._ai_client.integrated_systems.update(integrated_system_id, [{
            "op": "add",
            "path": "/parameters",
            "value": {"monitor_definition_ids": [custom_monitor_id]}
        }])
        result = response.result
        return result

    def get_results(self):
        return self.results

    def get_config(self):
        return self.config
    def get_monitor_instance_config(self,config):
        target  = config.get("SUBSCRIPTION_ID")
        monitor_name = config.get("CUSTOM_MONITOR_NAME","Sample Model Performance")
        existing_monitors = self._ai_client.monitor_definitions.list().result.monitor_definitions
        for monitor in existing_monitors:
            if monitor.entity.name == monitor_name:
                monitor_definition_id = monitor.metadata.id
        print(f"Monitor instance details picking for Subscription: {target} ,monitor definition: {monitor_definition_id} ")
        result  = self._ai_client.monitor_instances.list(target_target_id=target,
                                                         monitor_definition_id=monitor_definition_id).result.to_dict()
        return result

    def get_custom_monitor_configuration(self,config):
        result = {}
        monitor_instance = self.get_results()

        if monitor_instance:
           result = monitor_instance
        else:
            res = self.get_monitor_instance_config(config=config)
            monitor_instances = res.get("monitor_instances") if res else None
            if monitor_instances and isinstance(monitor_instances, list) and monitor_instances and isinstance(monitor_instances[0], dict):
                instance = monitor_instances[0]
                metadata = instance.get("metadata", {})
                entity = instance.get("entity", {})
                parameters = entity.get("parameters", {})

                result["custom_monitor_instance_id"] = metadata.get("id")
                result["monitor_definition_id"] = entity.get("monitor_definition_id")
                result["integrated_system_id"] = parameters.get("custom_metrics_provider_id")
                result["deployment_id"] = parameters.get("deployment_id")
                result["hardware_spec_id"] = parameters.get("hardware_spec_id")
                result["space_id"] = parameters.get("space_id")
                result["custom_metrics_provider_type"] = parameters.get("custom_metrics_provider_type")
                result["custom_metrics_wait_time"] = parameters.get("custom_metrics_wait_time")
            else:
                print("Monitor instance config is missing or improperly structured.")
        return result

