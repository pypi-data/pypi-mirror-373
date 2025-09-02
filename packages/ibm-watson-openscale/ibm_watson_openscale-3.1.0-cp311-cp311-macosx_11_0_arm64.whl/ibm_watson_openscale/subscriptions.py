# coding: utf-8

# Copyright 2020,2021 IBM All Rights Reserved.
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


from typing import Tuple
import uuid

from ibm_cloud_sdk_core import BaseService
from ibm_watson_openscale.base_classes.tables import Table
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Asset, AssetPropertiesRequest, \
    AssetDeploymentRequest, RiskEvaluationStatus
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import SparkStruct, IntegratedSystems,IntegratedSystemsListEnums,AnalyticsEngine,JsonPatchOperation, DataSourceStatus, DataSource, DataSourceConnection
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Subscriptions as BaseSubscriptions
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import SchemaUtility
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import ScoringEndpointRequest, ScoringEndpointCredentialsAzureScoringEndpointCredentials
from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.supporting_classes import Target

from .utils import *
import time
from datetime import datetime

import json
import tarfile
import copy
import requests

if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DetailedResponse

_DEFAULT_LIST_LENGTH = 50


# TODO: Add parameters validation in every method
class Subscriptions(BaseSubscriptions):
    """
    Manages Subscription instance.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def show(self, limit: Optional[int] = 10,
             data_mart_id: str = None,
            service_provider_id: str = None,
            asset_asset_id: str = None,
            asset_asset_type: str = None,
            deployment_deployment_id: str = None,
            deployment_deployment_type: str = None,
            integration_reference_integrated_system_id: str = None,
            integration_reference_external_id: str = None,
            risk_evaluation_status_state: str = None,
            service_provider_operational_space_id: str = None,
            pre_production_reference_id: str = None,
            project_id: str = None,
            space_id: str = None,
            **kwargs) -> None:
        """
        Show service providers. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :param str data_mart_id: (optional) comma-separated list of IDs.
        :param str service_provider_id: (optional) comma-separated list of IDs.
        :param str asset_asset_id: (optional) comma-separated list of IDs.
        :param str asset_asset_type: (optional) comma-separated list of types.
        :param str deployment_deployment_id: (optional) comma-separated list of
               IDs.
        :param str deployment_deployment_type: (optional) comma-separated list of
               types.
        :param str integration_reference_integrated_system_id: (optional)
               comma-separated list of IDs.
        :param str integration_reference_external_id: (optional) comma-separated
               list of IDs.
        :param str risk_evaluation_status_state: (optional) comma-separated list of
               states.
        :param str service_provider_operational_space_id: (optional)
               comma-separated list of operational space ids (property of service provider
               object).
        :param str pre_production_reference_id: (optional) comma-separated list of
               IDs.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)

        A way you might use me is:

        >>> client.subscriptions.show()
        >>> client.subscriptions.show(limit=20)
        >>> client.subscriptions.show(limit=None)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list(data_mart_id = data_mart_id,
            service_provider_id = service_provider_id,
            asset_asset_id = asset_asset_id,
            asset_asset_type = asset_asset_type,
            deployment_deployment_id = deployment_deployment_id,
            deployment_deployment_type = deployment_deployment_type,
            integration_reference_integrated_system_id = integration_reference_integrated_system_id,
            integration_reference_external_id = integration_reference_external_id,
            risk_evaluation_status_state = risk_evaluation_status_state,
            service_provider_operational_space_id = service_provider_operational_space_id,
            pre_production_reference_id = pre_production_reference_id,
            project_id = project_id,
            space_id = space_id,
            **kwargs)

        records = [[subscription.entity.asset.asset_id,
                    subscription.entity.asset.asset_type,
                    subscription.entity.asset.name,
                    subscription.entity.data_mart_id,
                    subscription.entity.deployment.deployment_id,
                    subscription.entity.deployment.name,
                    subscription.entity.service_provider_id,
                    subscription.entity.status.state,
                    subscription.metadata.created_at,
                    subscription.metadata.id
                    ] for subscription in response.result.subscriptions]
        columns = ['asset_id', 'asset_type', 'asset_name', 'data_mart_id', 'deployment_id', 'deployment_name',
                   'service_provider_id', 'status', 'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Subscriptions"
        )

    def add(self,
            data_mart_id: str,
            service_provider_id: str,
            asset: 'Asset',
            deployment: 'AssetDeploymentRequest',
            asset_properties: 'AssetPropertiesRequest' = None,
            risk_evaluation_status: 'RiskEvaluationStatus' = None,
            analytics_engine: 'AnalyticsEngine' = None,
            data_sources: List['DataSource'] = None,
            training_data_stats: dict = None,
            project_id: str = None,
            space_id: str = None,
            background_mode: bool = True,
            **kwargs) -> Union['DetailedResponse', Optional[dict]]:
        """
        Add a subscription to the model deployment.

        :param str data_mart_id: ID of the data_mart (required)
        :param str service_provider_id: ID of the service_provider (required)
        :param Asset asset: an Asset object with asset's information (required)
        :param AssetDeploymentRequest deployment: an AssetDeploymentRequest object with deployment's information (required)
        :param AssetPropertiesRequest asset_properties: (optional) Additional asset
               properties (subject of discovery if not provided when creating the
               subscription).
        :param RiskEvaluationStatus risk_evaluation_status: (optional)
        :param AnalyticsEngine analytics_engine: (optional)
        :param List[DataSource] data_sources: (optional)
        :param training_data_stats: Training statistic json generated using training stats notebook (https://github.com/IBM/watson-openscale-samples/blob/main/training%20statistics/training_statistics_notebook.ipynb)
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `SubscriptionResponse` result

        A way you may use me:

        >>> from ibm_watson_openscale import *
        >>> added_subscription_info = client.subscriptions.add(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                service_provider_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                asset=Asset(...),
                deployment=AssetDeploymentRequest(...),
                asset_properties=AssetPropertiesRequest(...),
             )
        """
        validate_type(data_mart_id, 'data_mart_id', str, True)
        validate_type(service_provider_id, 'service_provider_id', str, True)
        
        if self._ai_client.check_entitlements is True and self._ai_client.plan_name == constants.LITE_PLAN:
            total_subscriptions = self.list(project_id = project_id, space_id = space_id).result.subscriptions
            if len(total_subscriptions) >= 5:
                raise Exception("You are not allowed to create more than 5 subscriptions for lite plan.")
        
        if asset_properties is None and training_data_stats is None:
            raise Exception("Either asset_properties or training_data_stats has to be passed")
     
        ### If "other" data type is present in output or input schema then remove it from subscription before saving it.
        ### https://github.ibm.com/aiopenscale/tracker/issues/19160
        if asset_properties is not None:
            asset_props = asset_properties.to_dict()
            if 'input_data_schema' in asset_props:
                input_schema = asset_props['input_data_schema']
                if input_schema is not None:
                    has_other_data_type = self._has_other_datatype(input_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.input_data_schema = None    
            if 'output_data_schema' in asset_props:    
                output_schema = asset_props['output_data_schema']
                if output_schema is not None:
                    has_other_data_type = self._has_other_datatype(output_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.output_data_schema = None
            if 'training_data_schema' in asset_props:    
                training_schema = asset_props['training_data_schema']
                if training_schema is not None:
                    has_other_data_type = self._has_other_datatype(training_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.training_data_schema = None 
                        
        if training_data_stats is None:
            response = super().add(data_mart_id=data_mart_id, service_provider_id=service_provider_id, asset=asset,
                                   deployment=deployment, asset_properties=asset_properties,
                                   risk_evaluation_status=risk_evaluation_status, 
                                   analytics_engine=analytics_engine,
                                   data_sources=data_sources,
                                   project_id = project_id,
                                   space_id = space_id)
        else:
            #Create subscription using data available in training stats
            if len(training_data_stats) == 0:
                raise Exception("training_data_stats is empty. Please re-generate and use it")
            response = self.__create_subscription_from_training_stats(data_mart_id, service_provider_id, training_data_stats, kwargs,background_mode,
                                                                      project_id = project_id,
                                                                      space_id = space_id)

        subscription_id = response.result.metadata.id

        self.__create_default_monitors(subscription_id, data_mart_id, service_provider_id)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get(subscription_id=subscription_id, project_id = project_id, space_id = space_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get(subscription_id=subscription_id, project_id = project_id, space_id = space_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.ACTIVE]:
                    return "Successfully finished adding subscription", None, details
                else:
                    return "Add subscription failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details
            timeout = kwargs.get("timeout", 300)
            return print_synchronous_run(
                'Waiting for end of adding subscription {}'.format(subscription_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE],
                timeout=timeout
            )

    def delete(self,
               subscription_id: str,
               force: bool = None,
               project_id: str = None,
               space_id: str = None,
               background_mode: bool = True,
               **kwargs) -> Union['DetailedResponse', Optional[dict]]:
        """
        Delete subscription.

        :param str subscription_id: Unique subscription ID.
        :param bool force: (optional) force hard delete.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you may use me:

        >>> client.subscriptions.delete(
                background_mode=False,
                subscription_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                force=True
             )
        """
        response = super().delete(subscription_id=subscription_id, force=force, project_id = project_id, space_id = space_id)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list(project_id = project_id, space_id = space_id)
                if subscription_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list(project_id = project_id, space_id = space_id)
                if subscription_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting subscription", None, response
                else:
                    return "Delete subscription failed", 'Reason: None', response  # TODO: Need to show the reason.
            timeout = kwargs.get("timeout", 300)
            return print_synchronous_run(
                'Waiting for end of deleting subscription {}'.format(subscription_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED],
                timeout=timeout
            )
            
    def _has_other_datatype(self, fields):
        for field in fields:
            type = field['type']
            if type == 'other':
                return True
        return False   
    
    # Private method to create subscription using training stats data
    def __create_subscription_from_training_stats(self, data_mart_id, service_provider_id, training_stats_info, params,background_mode,
                                                  project_id = None, space_id = None):
        
        deployment_id = params.get("deployment_id")

        # Required in case of headless subscription
        deployment_name = params.get("deployment_name")
        deployment_space_id = params.get("deployment_space_id")
        model_type = training_stats_info['common_configuration']['problem_type']
        problem_type = None
        if model_type=="binary":
            problem_type = ProblemType.BINARY_CLASSIFICATION
        elif model_type=="multiclass":
            problem_type = ProblemType.MULTICLASS_CLASSIFICATION
        elif model_type=="regression":
            problem_type = ProblemType.REGRESSION    
        
        
        prediction_column = params.get("prediction_field")
        probability_columns = params.get("probability_fields")
        predicted_target_column = params.get("predicted_target_field")
        prediction_names = params.get("prediction_names")
        transaction_id_field = params.get("transaction_id_field")
        input_token_count_field = params.get("input_token_count_field")
        output_token_count_field = params.get("output_token_count_field")
        
        #validate_type(deployment_id, 'deployment_id', str, True)
        validate_type(prediction_column, 'prediction_field', str, True)
        #validate_type(predicted_target_column, 'predicted_target_field', str, True)
        
        if deployment_id is None and deployment_name is None :
            raise Exception("Please provide deployment_id if you have deployment information or else provide deployment_name in case you want to create headless subscription")
            
        model_asset_details_from_deployment = {}
        deployment_found = False
        if deployment_id is not None and deployment_space_id is not None:
            model_asset_details_from_deployment=self._ai_client.service_providers.get_deployment_asset(data_mart_id=data_mart_id,service_provider_id=service_provider_id,deployment_id=deployment_id,deployment_space_id=deployment_space_id)
            if model_asset_details_from_deployment['metadata']['guid']== deployment_id:
                deployment_found = True
            if not deployment_found :
                raise Exception("Deployment with id {} could not be found in deployment space {}. Please check again".format(deployment_id, deployment_space_id))    
        elif deployment_id is not None and deployment_space_id is None:
            #For non-WML model, pick the right deployment from list
            model_asset_details_from_deployment=self._ai_client.service_providers.list_assets(data_mart_id=data_mart_id,service_provider_id=service_provider_id).result    
            models = model_asset_details_from_deployment['resources']
            for model in models:
                if model['metadata']['guid']== deployment_id:
                    model_asset_details_from_deployment = model
                    deployment_found = True
                    break;
            if not deployment_found :
                raise Exception("Deployment with id {} could not be found. Please check again".format(deployment_id))
        elif deployment_id is None and deployment_space_id is not None:     
            raise Exception("Please provide deployment_id for space {}".format(deployment_space_id))
        else:
            print("Creating headless subscription as both deployment id and deployment space id are null")              
            
        input_data_schema = training_stats_info["common_configuration"]["input_data_schema"]
        fields = []
        label_column = training_stats_info["common_configuration"]["label_column"]
        # remove label column entry from input data schema
        for field in input_data_schema["fields"]:
            if field["name"] == label_column:
                continue
            fields.append(field)
        
        required_input_data_schema = {
            "type": "struct",
            "fields": fields
        }
        training_data_schema = None
        output_data_schema = None  # To store output_data_schema form training_stats_info

        if deployment_name is not None and not deployment_found:
            model_asset_id = str(uuid.uuid4())  
            model_name = deployment_name   
            model_url = "https://dummyModelUrl"
            deployment_asset_id = str(uuid.uuid4()) 
            deployment_name = deployment_name 
            scoring_endpoint = "https://dummyScoringUrl"
        else:
            if not deployment_found:
                raise Exception("Deployment with id {} not found".format(deployment_id))    
            model_asset_id = model_asset_details_from_deployment["entity"]["asset"]["asset_id"] 
            model_name = model_asset_details_from_deployment["entity"]["asset"]["name"]   
            model_url = model_asset_details_from_deployment["entity"]["asset"]["url"]
            deployment_asset_id =  model_asset_details_from_deployment['metadata']['guid']
            deployment_name = model_asset_details_from_deployment['entity']['name']
            scoring_endpoint = model_asset_details_from_deployment['entity']['scoring_endpoint']['url']
        
        if model_asset_details_from_deployment is not None and len(model_asset_details_from_deployment)>0:     
            if "training_data_schema" in model_asset_details_from_deployment["entity"]["asset_properties"]:
                training_data_schema = SparkStruct.from_dict(model_asset_details_from_deployment["entity"]["asset_properties"]["training_data_schema"])

        # This line is added to check whether training_data_schema is available in training_stats_info
        if "training_data_schema" in training_stats_info["common_configuration"]:
            training_data_schema = SparkStruct.from_dict(training_stats_info["common_configuration"]["training_data_schema"])

        # This line is added to check whether output_data_schema is available in training_stats_info
        if "output_data_schema" in training_stats_info["common_configuration"]:
            output_data_schema = SparkStruct.from_dict(training_stats_info["common_configuration"]["output_data_schema"])
            
        return super().add(
                data_mart_id=data_mart_id,
                service_provider_id=service_provider_id,
                asset=Asset(
                    asset_id=model_asset_id,
                    name=model_name,
                    url=model_url,
                    asset_type=AssetTypes.MODEL,
                    input_data_type=InputDataType.STRUCTURED,
                    problem_type=problem_type
                ),
                deployment=AssetDeploymentRequest(
                    deployment_id=deployment_asset_id,
                    name=deployment_name,
                    deployment_type= DeploymentTypes.ONLINE,
                    url=scoring_endpoint
                ),
                asset_properties=AssetPropertiesRequest(
                    transaction_id_field = transaction_id_field,
                    label_column=label_column,
                    probability_fields=probability_columns,
                    prediction_field=prediction_column,
                    predicted_target_field=predicted_target_column,
                    prediction_names=prediction_names,
                    feature_fields = training_stats_info["common_configuration"]["feature_fields"],
                    categorical_fields = training_stats_info["common_configuration"]["categorical_fields"],
                    input_data_schema = SparkStruct.from_dict(required_input_data_schema),
                    training_data_schema=training_data_schema,
                    output_data_schema=output_data_schema,
                    input_token_count_field = input_token_count_field,
                    output_token_count_field = output_token_count_field,
                ),
                project_id = project_id,
                space_id = space_id,
                background_mode=background_mode
            )
        
    def create_feedback_table(self,
        subscription_id: str,
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Create a table for feedback dataset type.

        :param str subscription_id: Unique subscription ID.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataSetResponse` result
        """
        dataset_type = "feedback"
        payload = {}
        
        return super().tables(subscription_id=subscription_id, dataset_type=dataset_type, unknown_base_type=payload,
                              project_id=project_id, space_id=space_id, **kwargs)

    def poll_subscription_status(self, subscription_id, message, ids, delay, project_id = None, space_id = None):
        subscription_status = None
        print(message)
        while subscription_status not in ("active", "error"):
            subscriprion = self.get(subscription_id, project_id = project_id, space_id = space_id).result.to_dict()
            subscription_status = get(subscriprion, "entity.status.state")
            if subscription_status not in ("active", "error"):
                print(datetime.now().strftime("%H:%M:%S"), subscription_status)
                time.sleep(delay)
        if subscription_status == "error":
            failure = get(subscriprion, "entity.status.failure")
            if failure == None:
                print("No failure information available")
            else:
                trace = get(failure, "trace")
                print("Trace: {}".format("" if not trace else trace))
                errors = get(failure, "errors")
                if errors != None and len(errors) != 0:
                    error = errors[0]
                    error_code = get(error, "code")
                    print("Error code: {}".format("" if not error_code else error_code))
                    error_message = get(error, "message")
                    print("Error message: {}".format("" if not error_message else error_message))
            print("Deleting subscription and related integrated systems ..")
            self.__delete_integrated_sytems(ids, project_id = project_id, space_id = space_id)
            self.delete(subscription_id, project_id = project_id, space_id = space_id)
            raise Exception("Subscription in error state !")

    def create_subscription_using_training_data(self, subscription_name, datamart_id, service_provider_id, model_info, sample_csv, spark_credentials, data_warehouse_connection, payload_table, feedback_table, scored_training_data_table, managed_by,
                                                project_id = None, space_id = None,
                                                background_mode: bool = True):
        """
            Create batch subscription using model_info.

            :param str subscription_name: Name of this subscription.
            :param str datamart_id: Datamart id in which we want to to create this subscription.
            :param str service_provider_id: Service Provider id.
            :param dict model_info: Information about the model which needs the subscription.
                Format for model_info
                model_info = {
                    "model_type": "binary",
                    "label_column": "Risk",
                    "prediction": "predicted_label",
                    "probability": "probability",
                    "feature_columns": [list of categorical columns]/None,
                    "categorical_columns": [list of categorical columns]/None,
                    "scoring": {
                        "url": "url":"scoring url", # This is required if explainability needs to be enabled,
                        "token": "token for scoring", # This is mandatory for Azure ML studio Model
                    }
                }
            :param csv sample_csv: Sample csv file
            :param dict spark_credentials: Dictionary containing spark connection information.
                Format for spark_credentials
                spark_credentials = {
                    "connection": {
                        "endpoint": <SPARK_ENDPOINT>,
                        "location_type": <LOCATION_TYPE>,
                        "display_name": <DISPLAY_NAME>,
                        "instance_id": <INSTANCE_ID>,
                        "volume": <VOLUME>
                    },
                    "credentials": {
                        "username": <USERNAME>,
                        "apikey": <APIKEY>
                    }
                }
            :param dict data_warehouse_connection: Dictionary containing data warehouse (DB connection) information.
                Format for the DB connection
                dataware_house_connection = {
                    "type": "jdbc",
                    "connection": {
                        "jdbc_driver": "com.ibm.db2.jcc.DB2Driver",
                        "use_ssl": False,
                        "certificate": None,
                        "jdbc_url": "jdbc:db2://<HOST>:50000/SAMPLE"
                    },
                    "credentials": {
                         "username": "<USERNAME>",
                        "password": "<PASSWORD>"
                    }
                }
            :param dict payload_table: Dictionary containing payload table connection information.
                Format for the payload table
                payload_table = {
                    "data": {
                        "auto_create": True,
                        "database": "SAMPLE",
                        "schema": "KP",
                        "table": "PAYLOAD_TABLE"
                    },
                    "parameters":{
                        "partition_column": "WOS_PARTITION_COLUMN",
                        "num_partitions": 12
                    }
                }
            :param dict feedback_table: Dictionary containing feedback table connection information.
            :param dict scored_training_data_table: Dictionary scored trainin data table.
                Format for scored_training_data_table
                scored_training_data_table = {
                    "data": {
                        "auto_create": False,
                        "database": "SAMPLE",
                        "schema": "KP",
                        "table": "SCORED_TRAINING_DATA_TABLE"
                    },
                    "parameters":{
                        "partition_column": "WOS_PARTITION_COLUMN",
                        "num_partitions": 12
                    }
                }
            :param str managed_by: To identify whether the subscription is online or batch. It should be either `system` for online subscription or `self` for batch subscripion.
            :param str project_id: Id of the Project context in which governance operation is happening (optional)
            :param str space_id: Id of the Space context in which governance operation is happening (optional)
        """
        if (managed_by == "self"):
            validate_type(datamart_id, 'data_mart_id', str, True)
            validate_type(service_provider_id, 'service_provider_id', str, True)
            validate_type(model_info, 'model_info', dict, True)
            validate_type(spark_credentials, 'spark_credentials', dict, True)
            validate_type(payload_table, 'payload_table', dict, True)
            validate_type(feedback_table, 'feedback_table', dict, True)
            validate_type(scored_training_data_table, 'scored_training_data_table', dict, True)

            self.__validate_data_warehouse_connetion(data_warehouse_connection)
            provider = self._ai_client.service_providers.get(service_provider_id, project_id=project_id, space_id=space_id).result
            
            # Take feature and catogerical field from user if provided.
            user_feature_fields = get(model_info,"feature_columns")
            user_categorical_field = get(model_info,"categorical_columns")

            label_column = get(model_info,"label_column")
            prediction_field = get(model_info,"prediction")
            probability_field = get(model_info,"probability")
            transaction_id_field = get(model_info,"transaction_id_field")
            prediction_names = get(model_info,"prediction_names")
            input_token_count_field = get(model_info,"input_token_count_field")
            output_token_count_field = get(model_info,"output_token_count_field")

            feature_fields = []
            categorical_fields = []

            # Get feature fields if provided by user
            isUserFeatureFields = False
            if (user_feature_fields != None and len(user_feature_fields) != 0):

                # Validate if prediction or probability field is added in feature columns"
                if ((label_column in user_feature_fields) or (prediction_field in user_feature_fields) or (label_column in user_feature_fields)):
                    raise Exception("Bad Input: Prediction, probability or label column is/are added as feature column(s).")

                feature_fields = user_feature_fields
                isUserFeatureFields = True

            # Get catogerical fields if provided by user
            isUserCategoricalFields = False
            if (user_categorical_field != None and len(user_categorical_field) != 0):

                # Validate if prediction or probability field is added in categorical columns"
                if ((label_column in user_categorical_field) or (prediction_field in user_categorical_field) or (label_column in user_categorical_field)):
                    raise Exception("Bad Input: Prediction, probability or label column is/are added as categorical column(s).")

                # Validate if categorical fields is subset of feature fields
                if (isUserFeatureFields and (not(set(user_categorical_field).issubset(set(user_feature_fields))))):
                    raise Exception("Bad Input: One or more categorical columns are not found in feature columns.")

                categorical_fields = user_categorical_field
                isUserCategoricalFields = True

            # Validate scoring details provided by user
            scoring = get(model_info,"scoring")
            scoring_url = None
            endpoint_credentials = None

            provider = self._ai_client.service_providers.get(service_provider_id, project_id=project_id, space_id=space_id).result
            if provider.entity.service_type != ServiceTypes.CUSTOM_MACHINE_LEARNING:
                if not scoring:
                    raise Exception("[Error] Missing scoring details : scoring details are mandatory to create subscription")
                if not get(scoring,"url"):
                    raise Exception("[Error] Missing scoring url : scoring url is mandatory to create subscription")
                if get(scoring,"token"):
                    endpoint_credentials = ScoringEndpointCredentialsAzureScoringEndpointCredentials(token=get(scoring,"token"))
                else:
                    if provider.entity.service_type == ServiceTypes.AZURE_MACHINE_LEARNING:
                        raise Exception("[Error] Missing Token : Token is mandatory to create subscription for Azure ML studio model")

            if scoring:
                scoring_url = get(scoring,"url")
                if not scoring_url:
                    print("[Warning] Missing scoring url : scoring url is mandatory if explain needs to be enabled")
            else:
                print("[Warning] Missing scoring details : scoring details are not provided")

            # Call config/datamart service API with CSV as payload to infer schema
            schemaUtil = SchemaUtility(self._ai_client)
            csv = open(sample_csv, 'rb')
            responseSchema = schemaUtil.spark_schemas_post(csv).result
            self.__validate_response_schema(responseSchema)

            input_fields = []
            output_fields = []
            training_fields = []

            fields = responseSchema.fields
            field_names = []
            for field in fields:
                field_names.append(field["name"])
                if (field['name'] == label_column):
                    field["metadata"]["modeling_role"] = "target"
                    training_fields.append(field)
                elif (field["name"] == prediction_field):
                    field["metadata"]["modeling_role"] = "prediction"
                    output_fields.append(field)
                elif (not(field["name"] == probability_field)):
                    field["metadata"]["modeling_role"] = "feature"

                    # If user provided feature columns
                    if isUserFeatureFields and field["name"] in feature_fields:
                        input_fields.append(field)
                        output_fields.append(field)
                        training_fields.append(field)
                    elif(not isUserFeatureFields):
                        feature_fields.append(field['name'])
                        input_fields.append(field)
                        output_fields.append(field)
                        training_fields.append(field)

                    # If user provided categorical columns
                    if (isUserCategoricalFields and field["name"] in categorical_fields):
                        field["metadata"]["measure"] = "discrete"
                    elif(not isUserCategoricalFields):
                        if field["name"] in feature_fields and field['type'] == "string":
                            categorical_fields.append(field['name'])
                            field["metadata"]["measure"] = "discrete"

            if (isUserFeatureFields):
                if (not(set(user_feature_fields).issubset(set(field_names)))):
                    raise Exception("Bad Input: One or more feature field provided are not present in the input csv")

            if (isUserCategoricalFields):
                if (not(set(user_categorical_field).issubset(set(field_names)))):
                    raise Exception("Bad Input: One or more catogerical field provided are not present in the input csv")

            problem_type = get(model_info,"model_type")
            if (problem_type != ProblemType.REGRESSION):
                probability =  {
                    "name": probability_field,
                    "type": {
                        "type": "array",
                        "elementType": "double",
                        "containsNull": True
                    },
                    "nullable": True,
                    "metadata": {
                        "modeling_role": "probability"
                    }
                }
                output_fields.append(probability)

            spark_engine_id = None
            db_integrated_system_id = None
            try:
                print("Creating integrated system for Spark")
                spark_engine_id = self.__create_spark_integrated_system(subscription_name, spark_credentials, project_id=project_id, space_id=space_id)
                print("Creating integrated system for Hive/DB2")
                db_integrated_system_id = self.__create_db2_hive_integrated_system(subscription_name,data_warehouse_connection,
                                                                                   project_id = project_id, space_id=space_id)

                # Set asset details
                asset = Asset(
                    asset_id=str(uuid.uuid4()),
                    url="",
                    name=subscription_name,
                    asset_type=AssetTypes.MODEL,
                    input_data_type=InputDataType.STRUCTURED,
                    problem_type=problem_type
                )

                # Set deployment details
                asset_deployment = AssetDeploymentRequest(
                    deployment_id=str(uuid.uuid4()),
                    name=subscription_name,
                    description="This is {}".format(subscription_name),
                    deployment_type="batch",
                    scoring_endpoint = ScoringEndpointRequest(url=scoring_url, credentials=endpoint_credentials)
                )

                # Define input, output and training data schema
                input_data_schema = {"fields" : input_fields, "type" : responseSchema.type}
                output_data_schema = {"fields" : output_fields, "type" : responseSchema.type}
                training_data_scheme = {"fields" : training_fields, "type" : responseSchema.type}

                asset_properties_request = AssetPropertiesRequest(
                    transaction_id_field=transaction_id_field,
                    label_column = label_column,
                    probability_fields = None if not probability_field else [probability_field],
                    prediction_field = prediction_field,
                    prediction_names = prediction_names,
                    feature_fields = feature_fields,
                    categorical_fields = categorical_fields,
                    input_token_count_field = input_token_count_field,
                    output_token_count_field = output_token_count_field
                )
                analytics_engine = AnalyticsEngine(
                    type = "spark",
                    integrated_system_id = spark_engine_id,
                    parameters = get(spark_credentials,"spark_settings",{})
                )

                subscription_details = self.add(
                    data_mart_id = datamart_id,
                    service_provider_id = service_provider_id,
                    asset = asset,
                    deployment = asset_deployment,
                    asset_properties = asset_properties_request,
                    analytics_engine = analytics_engine,
                    project_id = project_id,
                    space_id = space_id,
                    background_mode = True
                    ).result
            except Exception as e:
                # Delete all the integrated systems created for this failed subscription
                print("Creation of subscription failed")
                print(e)
                ids = [spark_engine_id, db_integrated_system_id]
                self.__delete_integrated_sytems(ids, project_id = project_id, space_id = space_id)
                raise e

            subscription_id = subscription_details.metadata.id
            schemas_patch_document=[
                    JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/training_data_schema', value=training_data_scheme),
                    JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/input_data_schema', value=input_data_schema),
                    JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/output_data_schema', value=output_data_schema)
                ]

            ids = [spark_engine_id, db_integrated_system_id]
            message = "Updating schemas ..."
            self.poll_subscription_status(subscription_id, message, ids, 3, project_id = project_id, space_id = space_id)
            self._ai_client.subscriptions.update(subscription_id=subscription_id, patch_document=schemas_patch_document,
                                                 project_id = project_id, space_id = space_id)
            print("Schemas update completed.")

            # Add selected tables as data sources
            data_sources = []
            source_type = get(data_warehouse_connection,"type")
            if len(payload_table) > 0 and get(payload_table,"data.table",None) is not None:
                data_sources.append(self.__get_data_source(payload_table, db_integrated_system_id, "payload", source_type))
            if len(feedback_table) > 0 and get(feedback_table,"data.table",None) is not None:
                data_sources.append(self.__get_data_source(feedback_table, db_integrated_system_id, "feedback", source_type))
            if len(scored_training_data_table) > 0 and get(scored_training_data_table, "data.table",None) is not None:
                scored_training_data_table["data"]["state"] = "active"
                data_sources.append(self.__get_data_source(scored_training_data_table, db_integrated_system_id, "training", source_type))

            message = "Updating data-sources ..."
            self.poll_subscription_status(subscription_id, message, ids, 1, project_id=project_id, space_id=space_id)

            # Patch datasources
            if len(data_sources) > 0:
                data_sources_patch_document=[
                    JsonPatchOperation(op=OperationTypes.ADD, path="/data_sources", value=data_sources)
                ]
                self._ai_client.subscriptions.update(subscription_id=subscription_id, patch_document=data_sources_patch_document,
                                                     project_id = project_id, space_id = space_id)
                print("Data-sources update complete.")

            print("Subscription is created. Id is : {}".format(subscription_id))

            if not background_mode:
                message = "Waiting for subscription to be in active state ..."
                self.poll_subscription_status(subscription_id, message, ids, 15, project_id=project_id, space_id=space_id)
                print("Subscription is now in active state.")
            else:
                print("Subscription is being activated, please wait for state to be active before using it further.")

            return subscription_id

        elif (managed_by == "system"):
            raise Exception("Currently not supporting online subscription")
        else:
            raise Exception("The possible values for `managed_by` are either `system` for online subscription or `self` for batch subscripion")
    
    def create_subscription(self, subscription_name: str, datamart_id, service_provider_id, configuration_archive, spark_credentials, data_warehouse_connection, payload_table: dict = {}, feedback_table: dict = {} , model_info: dict = {}, background_mode: bool = True,
                            project_id = None, space_id = None, **kwargs):
        """
            Create batch subscription
            
            :param str subscription_name: Name of the subscription.
            :param str datamart_id: Datamart id in which we want to to create this subscription.
            :param str service_provider_id: Service Provider id.
            
            :param str configuration_archive: Path to the configuration archive file.
            :param dict spark_credentials: Dictionary containing spark connection information.
                Format for Remote Spark on hadoop 
                spark_credentials =  {
                    "connection":{
                        "endpoint": "<SPARK_ENDPOINT>",
                        "location_type": "custom"
                    },
                    "credentials": {
                        "username": "<USERNAME>",
                        "password": "<PASSWORD>"
                    },
                    "spark_settings": {
                        "max_num_executors": <MAX_EXECUTOR_COUNT>,
                        "min_num_executors": <MIN_EXECUTOR_COUNT>,
                        "executor_cores": <EXECUTOR_CORE>,
                        "executor_memory": <EXECUTOR_MEMORY>,
                        "driver_cores": <NUM_OF_DRIVER_CORES>,
                        "driver_memory": <DRIVER_MEMORY>
                    }                    
                }
                Format for IAE Spark
                spark_credentials = {
                "connection": {
                    "display_name": "<IAE_INSTANCE_DISPLAYNAME>",
                    "endpoint": "<IAE_JOB_ENDPOINT>",
                    "location_type": "cpd_iae",
                    "volume": "<VOLUME_NAME>"
                },
                "credentials": {
                    "username": "<USERNAME>",
                    "apikey": "<APIKEY>"
                },
                "spark_setting": {
                    #Look at remote spark settings
                }
            }
            :param dict data_warehouse_connection: Dictionary containing data warehouse (DB connection) information.  
                Format for the DB connection
                dataware_house_connection = {
                    "type": "jdbc",
                    "connection": {
                        "jdbc_driver": "com.ibm.db2.jcc.DB2Driver",
                        "use_ssl": False,
                        "certificate": None,
                        "jdbc_url": "jdbc:db2://<HOST>:50000/SAMPLE"        
                    },
                    "credentials": {
                         "username": "<USERNAME>",
                        "password": "<PASSWORD>"
                    }
                }
                
            :param dict payload_table: Dictionary containing payload table connection information.
                Format for the payload table 
                payload_table = {
                    "data": {
                        "auto_create": True,
                        "database": "SAMPLE",
                        "schema": "KP",
                        "table": "PAYLOAD_GERMAN_CREDIT_DATA_NEW"
                    },
                    "parameters":{
                        "partition_column": "WOS_PARTITION_COLUMN",
                        "num_partitions": 12
                    }
                }
            :param dict feedback_table: Dictionary containing feedback table connection information.
                Format for the feedback_table is same as payload table
            :param dict model_info: Information about the model which needs the subscription.
                Format for model_info
                model_info = {
                    "model_type": "binary",
                    "label_column": "Risk",
                    "prediction": "predicted_label",
                    "probability": "probability",
                    "feature_columns": [list of categorical columns]/None,
                    "categorical_columns": [list of categorical columns]/None,
                    "scoring": {
                        "url": "url":"scoring url", # This is required if explainability needs to be enabled,
                        "token": "token for scoring", # This is mandatory for Azure ML studio Model
                    }
                }
            :param str project_id: Id of the Project context in which governance operation is happening (optional)
            :param str space_id: Id of the Space context in which governance operation is happening (optional)
            :return: subscription id
            :rtype: str
        
        """    
        
        validate_type(subscription_name, 'subscription_name', str, True)
        validate_type(datamart_id, 'data_mart_id', str, True)
        validate_type(service_provider_id, 'service_provider_id', str, True)
        #validate_type(configuration_archive, 'configuration_archive', str, True)
        validate_type(spark_credentials, 'spark_credentials', dict, True)
        validate_type(data_warehouse_connection, 'data_warehouse_connection', dict, True)
        validate_type(payload_table, 'payload_table', dict, False)
        validate_type(feedback_table, 'feedback_table', dict, False)
        validate_type(model_info, 'model_info', dict, False)
        
        self.__validate_data_warehouse_connetion(data_warehouse_connection)
        
        self.__validate_table_info(payload_table)
        if feedback_table != None and len(feedback_table) > 0 :
            self.__validate_table_info(feedback_table)

        scoring_url = None
        endpoint_credentials = None
        scoring = get(model_info,"scoring")
        if scoring:
            scoring_url = get(scoring,"url")
            if not scoring_url:
                print("[Warning] Missing scoring url : There is no scoring url provided")
            if get(scoring,"token"):
                endpoint_credentials = ScoringEndpointCredentialsAzureScoringEndpointCredentials(token=get(scoring,"token"))
            else:
                provider = self._ai_client.service_providers.get(service_provider_id, project_id=project_id, space_id=space_id).result
                if provider.entity.service_type == ServiceTypes.AZURE_MACHINE_LEARNING:
                    print("[Warning] Missing Token : There is no token provided for Azure ML studio model")

        #TODO validate parameters
        spark_engine_id = None
        db_integrated_system_id = None
        try:
            print("Creating integrated system for Spark")
            spark_engine_id = self.__create_spark_integrated_system(subscription_name, spark_credentials, project_id=project_id, space_id=space_id)
            
            print("Creating integrated system for Hive/DB2")            
            db_integrated_system_id = self.__create_db2_hive_integrated_system(subscription_name,data_warehouse_connection,
                                                                               project_id=project_id, space_id=space_id)
            
            common_config = self.__get_common_configuration(configuration_archive)
            common_configuration = get(common_config,'common_configuration')
            model_type = get(common_configuration,"model_type")
            if model_type == None:
                model_type = get(common_configuration,"problem_type")
            
            # Set asset details
            asset = Asset(
                asset_id=str(uuid.uuid4()),
                url="",
                name=subscription_name,
                asset_type=AssetTypes.MODEL,
                input_data_type=InputDataType.STRUCTURED,
                problem_type=model_type
            )
            
            # Set deployment details
            asset_deployment = AssetDeploymentRequest(
                deployment_id=str(uuid.uuid4()),
                name=subscription_name,
                description="This is {}".format(subscription_name),
                deployment_type="batch",
                scoring_endpoint = None if not scoring else ScoringEndpointRequest(url=scoring_url, credentials=endpoint_credentials)
            )

            probability_field = None
            if model_type != ProblemType.REGRESSION:
                probability_field = get(common_configuration,"probability_fields")
                if not probability_field:
                    probability_field = [get(common_configuration,"probability")]

            asset_properties_request = AssetPropertiesRequest(
                transaction_id_field=get(common_configuration,"transaction_id_field"),
                label_column=get(common_configuration,"label_column"),
                probability_fields=probability_field,
                prediction_field=get(common_configuration,"prediction"),
                prediction_names = get(common_configuration,"prediction_names"),
                feature_fields=get(common_configuration,"feature_columns"),
                categorical_fields=get(common_configuration,"categorical_columns"),
                input_token_count_field=get(common_configuration,"input_token_count_field"),
                output_token_count_field=get(common_configuration,"output_token_count_field")
            )    
            
            analytics_engine = AnalyticsEngine(
                type="spark",
                integrated_system_id=spark_engine_id,
                parameters = get(spark_credentials,"spark_settings",{})
            )  
            
            subscription_details = self.add(
                data_mart_id=datamart_id,
                service_provider_id=service_provider_id,
                asset=asset,
                deployment=asset_deployment,
                asset_properties=asset_properties_request,                
                analytics_engine=analytics_engine,
                project_id=project_id,
                space_id=space_id,
                background_mode = True
                ).result
                
        except Exception as e:
            #Delete all the integrated systems created for this failed subscription
            print("Creation of subscription failed")
            print(e)
            #ids = [spark_engine_id, payload_integrated_system_id,feedback_integrated_system_id,training_integrated_system_id]
            ids = [spark_engine_id, db_integrated_system_id]            
            self.__delete_integrated_sytems(ids, project_id = project_id, space_id = space_id)
            raise e
        
        subscription_id = subscription_details.metadata.id
        schemas_patch_document=[
                JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/training_data_schema', value=common_configuration["training_data_schema"]),
                JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/input_data_schema', value=common_configuration["input_data_schema"]),
                JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/output_data_schema', value=common_configuration["output_data_schema"])
            ]

        ids = [spark_engine_id, db_integrated_system_id]
        message = "Updating schemas ..."
        self.poll_subscription_status(subscription_id, message, ids, 3, project_id=project_id, space_id=space_id)
        self._ai_client.subscriptions.update(subscription_id=subscription_id, patch_document=schemas_patch_document,
                                             project_id = project_id, space_id = space_id)
        print("Schemas update completed.")

         # Add selected tables as data sources
        data_sources = []
        source_type = get(data_warehouse_connection,"type")
        if len(payload_table) > 0 and get(payload_table,"data.table",None) is not None:
            data_sources.append(self.__get_data_source(payload_table, db_integrated_system_id, "payload", source_type))
            
        if feedback_table != None and len(feedback_table) > 0 and get(feedback_table,"data.table",None) is not None:
            data_sources.append(self.__get_data_source(feedback_table, db_integrated_system_id, "feedback", source_type))

        message = "Updating data-sources ..."
        self.poll_subscription_status(subscription_id, message, ids, 1, project_id=project_id, space_id=space_id)

        #patch datasources
        if len(data_sources) > 0:
            data_sources_patch_document=[
                 JsonPatchOperation(op=OperationTypes.ADD, path="/data_sources", value=data_sources)
            ]        
            self._ai_client.subscriptions.update(subscription_id=subscription_id, patch_document=data_sources_patch_document,
                                                 project_id = project_id, space_id = space_id)
            print("Data-sources update complete.")
        
        print("Subscription is created. Id is : {}".format(subscription_id))

        if not background_mode:
            message = "Waiting for subscription to be in active state ..."
            self.poll_subscription_status(subscription_id, message, ids, 15, project_id=project_id, space_id=space_id)
            print("Subscription is now in active state.")
        else:
            print("Subscription is being activated, please wait for state to be active before using it further.")

        return subscription_id


    def __create_spark_integrated_system(self, subscription_name, spark_credentials, project_id = None, space_id = None):
        """
        Format of spark_credentials

        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        # Remote Spark example
        spark_credentials =  {
            "connection":{
                "endpoint": "http://wimps1.fyre.ibm.com:5000",
                "location_type": "custom"
            },
            "credentials": {
                "username": "<USERNAME>",
                "password": "<PASSWORD>"
            },
            "spark_settings": {
                "max_num_executors": 1,
                "min_num_executors": 1,
                "executor_cores": 1,
                "executor_memory": 2,
                "driver_cores": 1,
                "driver_memory": 2
            }
        }

        # IAE Spark example
        spark_credentials = {
            "connection": {
                "display_name": "<IAE_DISPLAY_NAME>",
                "endpoint": "<IAE_JOB_ENDPOINT>",
                "location_type": "cpd_iae",
                "volume": "<VOLUME_NAME>"
            },
            "credentials": {
                "username": "admin",
                "apikey": "<APIKEY>"
            },
            "spark_setting": {
                "max_num_executors": 1,
                "min_num_executors": 1,
                "executor_cores": 1,
                "executor_memory": 2,
                "driver_cores": 1,
                "driver_memory": 2
            }
        }

        """
        
        spark_engine_details = IntegratedSystems(self._ai_client).add(
                name=subscription_name + " - Spark Engine",
                description = " ",
                type=IntegratedSystemsListEnums.Type.SPARK.value,
                credentials= get(spark_credentials,"credentials"),
                connection=get(spark_credentials,"connection"),
                project_id=project_id,
                space_id=space_id
            ).result
            
        
        spark_engine_id = spark_engine_details.metadata.id
        
        print("Integrated system {} created ".format(spark_engine_id))
        
        return spark_engine_id
       
            
    def __create_db2_hive_integrated_system(self, subscription_name, table_info, project_id = None, space_id = None):
        #system_types = list(set([get(payload_table,"type"),get(feedback_table,"type"),get(scored_training_data_table,"type")]))
        #if len(system_types)==1: #All are of same type
        connection_type = get(table_info,"type")
        hive_db2_connection = get(table_info,"connection")
        hive_db2_credentials = get(table_info,"credentials")
        if hive_db2_credentials is None:
            hive_db2_credentials = {}
            
        if connection_type==IntegratedSystemsListEnums.Type.HIVE.value:
            hive_db2_connection["location_type"] = "metastore"
        
        elif connection_type==IntegratedSystemsListEnums.Type.JDBC.value:
            hive_db2_connection["location_type"] =  IntegratedSystemsListEnums.Type.JDBC.value            
            hive_db2_credentials["jdbc_url"] = get(table_info,"connection.jdbc_url")
            
        hive_db2_connection_details = IntegratedSystems(self._ai_client).add(
                name=subscription_name + " - DB Info",
                description = "",
                type=connection_type,
                credentials=hive_db2_credentials,
                connection=hive_db2_connection,
                project_id=project_id,
                space_id=space_id
            ).result
        
                
        hive_db2_connection_id=hive_db2_connection_details.metadata.id
        print("Hive/Db2 Integrated system {} created".format(hive_db2_connection_id))
        
        return hive_db2_connection_id
    
    def __delete_integrated_sytems(self, ids, project_id = None, space_id = None):
        print("Cleaning up integration systems")
        for id in ids:
            if id is not None:
                print("Deleting {}".format(id))
                IntegratedSystems(self._ai_client).delete(id, project_id=project_id, space_id=space_id)
                
    def __get_common_configuration(self, configuration_archive):
        common_config = None
        with tarfile.open(configuration_archive, 'r:gz') as tar:
            if "common_configuration.json" not in tar.getnames():
                raise Exception("common_configuration.json file is missing in archive file")
            
            json_content = tar.extractfile('common_configuration.json')
            data = json_content.read().decode()
            common_config = json.loads(data)  
                 
        return common_config    
    
    def __validate_data_warehouse_connetion(self, connection_info):
        validate_type(get(connection_info,"type"), 'type', str, True)

        type = get(connection_info,"type")
        if type=="jdbc":
            
            validate_type(get(connection_info,"connection.use_ssl"), 'use_ssl', bool, False)
            validate_type(get(connection_info,"connection.jdbc_driver"), 'jdbc_driver', str, True)
            validate_type(get(connection_info,"connection.jdbc_url"), 'jdbc_url', str, True)
            
            validate_type(get(connection_info,"credentials.username"), 'username', str, True)
            validate_type(get(connection_info,"credentials.password"), 'password', str, True)
         
        else:
            validate_type(get(connection_info,"connection.metastore_url"), 'metastore_url', str, True)
            kerberos_enabled = get(connection_info,"connection.kerberos_enabled",None)
            if kerberos_enabled is not None:
                 validate_type(get(connection_info,"connection.kerberos_enabled"), 'kerberos_enabled', bool, True)
                 if kerberos_enabled:
                     validate_type(get(connection_info,"credentials.kerberos_principal"), 'kerberos_principal', str, True)
                     delegation_token_urn = get(connection_info,"credentials.delegation_token_urn")
                     delegation_token_endpoint = get(connection_info,"credentials.delegation_token_endpoint")
                     if delegation_token_urn is None and delegation_token_endpoint is None:
                         raise Exception("Either delegation_token_urn or delegation_token_endpoint value is required when connecting to Kerberos Hive")
                         
                     
    def __validate_table_info(self, table_info):  
          
        validate_type(get(table_info,"data.auto_create"), 'auto_create', bool, True)
        validate_type(get(table_info,"data.database"), 'database', str, True)
        validate_type(get(table_info,"data.table"), 'table', str, True)

    def __validate_response_schema(self, schema):
        try:
            if not schema:
                raise Exception("spark_schema response is empty or none")
            if schema.type != "struct":
                raise Exception("The returned schema type is not struct.")
            if len(schema.fields) == 0:
                raise Exception("There are no fields in the returned schema.")
        except Exception as e:
            print("Schema validation failed.")
            raise e

    def __get_data_source(self, table_info, integrated_system_id,table_type,source_type):
        auto_create = get(table_info,"data.auto_create",False)
        state = get(table_info,"data.state","new")
        status = DataSourceStatus(state=state)
        parameters = None
        if "parameters" in table_info:
            parameters = get(table_info,"parameters")
        data_source = DataSource(
            type=table_type, 
            database_name=get(table_info,"data.database"), 
            schema_name=get(table_info,"data.database") if source_type==IntegratedSystemsListEnums.Type.HIVE.value else get(table_info,"data.schema"),
            table_name=get(table_info,"data.table"), 
            auto_create = auto_create,
            status = status,
            connection=DataSourceConnection(
                type=source_type, 
                integrated_system_id=integrated_system_id
            ),
            parameters = parameters
        )
        return data_source.to_dict()

    def __create_default_monitors(self, subscription_id, data_mart_id, service_provider_id, project_id = None, space_id = None):
        target = Target(
            target_type=TargetTypes.SUBSCRIPTION,
            target_id=subscription_id
        )

        provider = self._ai_client.service_providers.get(service_provider_id, project_id=project_id, space_id=space_id).result
        operational_space_id = provider.entity.operational_space_id

        if operational_space_id == constants.PRODUCTION:
            #Create Model Health Monittor
            if hasattr(self._ai_client.monitor_definitions.MONITORS, constants.MODEL_HEALTH):
                self.__create_monitor(data_mart_id, target, self._ai_client.monitor_definitions.MONITORS.MODEL_HEALTH.ID)
                
        # Create performance monitor for any type of subscription    
        self.__create_monitor(data_mart_id, target, self._ai_client.monitor_definitions.MONITORS.PERFORMANCE.ID)        

    def __create_monitor(self, data_mart_id, target, monitor_definition_id, parameters = {}):
        monitor_instances_info = self._ai_client.monitor_instances.create(monitor_definition_id=monitor_definition_id,
                                target = target,
                                parameters = parameters,
                                data_mart_id = data_mart_id,
                                managed_by = "user"
                                )
        monitor_instance_id = monitor_instances_info.result.metadata.id



