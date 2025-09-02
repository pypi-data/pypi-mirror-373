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

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import ModelRiskManagement as BaseModelRiskManagement, IntegratedSystemMetricsArray, IntegratedMetric, PromptSetupRequestMonitors, PostRiskEvaluationsResponse, DetailedResponse
from ibm_cloud_sdk_core import BaseService, DetailedResponse
from .utils import *
from typing import TextIO
from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator, IAMAuthenticator
from typing import Tuple

if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DetailedResponse


MRM_RISK_EVALUATIONS_HREF_PATTERN = '/v2/monitoring_services/mrm/monitor_instances/{}/risk_evaluations'

class ModelRiskManagement(BaseModelRiskManagement):
    """Manage model risk management monitoring for asset."""

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def evaluate_risk(self,
        monitor_instance_id: str,
        test_data_set_name: str = None,
        test_data_path: str = None,
        publish_metrics: str = None,
        publish_lineage: str = None,
        publish_fact: str = None,
        includes_model_output: str = None,
        delimiter: str = None,
        evaluation_tests: str = None,
        content_type = "text/csv",
        project_id = None,
        space_id = None,
        body = None,
        background_mode: bool = True,
        **kwargs
        ) -> 'DetailedResponse':
        """
        Uploads the test data and triggers a monitor run for risk evaluation.

        :param str monitor_instance_id: The monitor instance ID.
        :param str test_data_path : (optional) Path to test data
        :param str body : (optional) Path to mapping json file
        :param str content_type: (optional) The type of the input. A character
               encoding can be specified by including a `charset` parameter. For example,
               'text/csv;charset=utf-8'.
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :param str test_data_set_name: (optional) The name of the test CSV file
               being uploaded.
        :param str publish_metrics: (optional) Flag to decide whether to send
               evaluated metrics to OpenPages.
        :param str publish_lineage: (optional) Flag to decide whether a lineage
               event should be published to an integrated system.
        :param str publish_fact: (optional) Flag to decide whether Fact metadata
               should be published to an integrated system.
        :param str includes_model_output: (optional) Boolean flag to indicate
               whether the data being uploaded contains scored output or not.
        :param str evaluation_tests: (optional) Comma separated list of monitor
               tests to run.
        :param str delimiter: (optional) The delimiter to be used for CSV/Dynamic
               CSV files.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `PostRiskEvaluationsResponse` result
        """

        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        def get_response(response):
            if background_mode:
                return response
            else:
                def check_state() -> dict:
                    details = self.get_risk_evaluation(monitor_instance_id = monitor_instance_id, project_id = project_id, space_id = space_id)
                    return details.result.entity.status.state.lower()

                def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                    details = self.get_risk_evaluation(monitor_instance_id = monitor_instance_id, project_id = project_id, space_id = space_id)
                    state = details.result.entity.status.state.lower()

                    if state in [StatusStateType.FINISHED]:
                        return "Successfully finished evaluating risk", None, details
                    else:
                        return "Risk evaluation failed with status: {}".format(state), \
                            'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                    details.result.entity.status.failure.errors]), details

                timeout = kwargs.get("timeout", 300)
                return print_synchronous_run(
                    'Waiting for risk evaluation of MRM monitor {}'.format(monitor_instance_id),
                    check_state,
                    get_result=get_result,
                    success_states=[StatusStateType.FINISHED],
                    failure_states = [StatusStateType.FAILURE, StatusStateType.FAILED, StatusStateType.ERROR,
                          StatusStateType.CANCELLED, StatusStateType.CANCELED, StatusStateType.UPLOAD_ERROR],
                    timeout=timeout
                )

        test_data_content = None
        if test_data_path is not None and isinstance(test_data_path,str):
            test_data_content = open(test_data_path, 'rb')
        elif test_data_path is not None and content_type == 'text/csv':
            test_data_content = bytearray(test_data_path.to_csv(index=False), 'utf-8')

        if content_type == "multipart/form-data":
            files = [
                ("data", ('data.txt', test_data_content))
            ]

            mapping_data_content = None
            if body:
                mapping_data_content = open(body, 'rb')
                files.append(("body", ('body.txt', mapping_data_content)))

            url = MRM_RISK_EVALUATIONS_HREF_PATTERN.format(monitor_instance_id)
            params = {
                "test_data_set_name": test_data_set_name,
                "publish_metrics": publish_metrics,
                "publish_lineage": publish_lineage,
                "publish_fact": publish_fact,
                "includes_model_output": includes_model_output,
                "evaluation_tests": evaluation_tests,
                "project_id": project_id,
                "space_id":space_id,
                "delimiter": delimiter
            }
            try:
                request = self.watson_open_scale.prepare_request(method='POST',
                                            url=url,
                                            headers=self.__get_headers(self._ai_client),
                                            params=params,
                                            files=files)

                response = self.watson_open_scale.send(request)
                if hasattr(PostRiskEvaluationsResponse, 'from_dict'):
                    response.result = PostRiskEvaluationsResponse.from_dict(response.result)
                return get_response(response)
            except Exception as e:
                raise Exception(e)
            finally:
                if test_data_content:
                    test_data_content.close()
                if mapping_data_content:
                    mapping_data_content.close()

        response = self.mrm_risk_evaluations(
        monitor_instance_id = monitor_instance_id,
        unknown_base_type =  test_data_content,
        content_type = content_type,
        test_data_set_name =  test_data_set_name,
        publish_metrics = publish_metrics,
        publish_lineage = publish_lineage,
        publish_fact = publish_fact,
        includes_model_output = includes_model_output,
        delimiter = delimiter,
        evaluation_tests = evaluation_tests,
        project_id = project_id,
        space_id = space_id,
        **kwargs)

        return get_response(response)

    def get_risk_evaluation(self,
        monitor_instance_id: str,
        project_id: str = None,
        space_id: str = None,
        **kwargs) -> 'DetailedResponse':
        """
        Returns the status of the risk evaluation.

        :param str monitor_instance_id: The monitor instance ID.
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `RiskEvaluationResponse` result
        """
        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        response = self.mrm_get_risk_evaluation(
        monitor_instance_id = monitor_instance_id,
        project_id = project_id,
        space_id = space_id,
        **kwargs)

        return response

    def cancel_risk_evaluation(self,
        monitor_instance_id: str,
        cancel_run: str = None,
        project_id: str = None,
        space_id: str = None,
        **kwargs
        ) -> 'DetailedResponse':
        """
        Cancels the risk evaluations run.

        :param str monitor_instance_id: The monitor instance ID.
        :param str cancel_run: (optional)
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `RiskEvaluationResponse` result
        """
        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        response = self.mrm_put_risk_evaluation(
        monitor_instance_id = monitor_instance_id,
        cancel_run = cancel_run,
        project_id = project_id,
        space_id = space_id,
        **kwargs)

        return response

    def update_notification_preferences(self,
        monitor_instance_id: str,
        notification_enabled: bool,
        notification_frequency: str,
        notification_emails: List[str],
        project_id: str = None,
        space_id: str = None,
        **kwargs) -> 'DetailedResponse':
        """
        Sets the users email notification preference in the MRM monitor instance of a given model subscription.

        :param str monitor_instance_id: The monitor instance ID.
        :param bool notification_enabled: (optional)
        :param str notification_frequency: (optional)
        :param List[str] notification_emails: (optional)
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `RiskNotificationPreferencesResponse` result
        """
        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        response = self.mrm_update_notification_preferences(monitor_instance_id = monitor_instance_id,
        notification_enabled = notification_enabled,
        notification_frequency = notification_frequency,
        notification_emails = notification_emails,
        project_id = project_id,
        space_id = space_id,
        **kwargs)

        return response

    def get_notification_preferences(self,
         monitor_instance_id: str,
         project_id: str = None,
         space_id: str = None,
        **kwargs) -> 'DetailedResponse':
        """
        Gets the users email notification preferences for a given model subscription.

        Gets the users email notification preferences for a given model subscription.

        :param str monitor_instance_id: The monitor instance ID.
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `RiskNotificationPreferencesResponse` result
        """
        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)

        response = self.mrm_get_notification_preferences(monitor_instance_id = monitor_instance_id,
                                                         project_id = project_id,
                                                         space_id = space_id,
                                                         **kwargs)

        return response

    def publish_metrics(self,
        monitor_instance_id: str,
        monitoring_run_id: str,
        metrics_info: dict = None,
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':

        """
        Publishes the chosen metrics to the integrated system reference.

        :param str monitor_instance_id: The monitor instance ID.
        :param str monitoring_run_id: The monitoring run ID.
        :param List[IntegratedSystemMetricsArray] metrics: (optional)
        :param bool send_report: (optional)
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """
        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)
        validate_type(monitoring_run_id, 'monitoring_run_id', str, True)

        metrics_array = []
        send_report = get(metrics_info, "send_report")
        metrics_list = get(metrics_info, "metrics")
        for metrics in metrics_list:
            type = get(metrics, "type")
            measures = get(metrics, "measures")
            integrated_metrics_list = []
            integrated_metrics = get(metrics, "integrated_metrics")
            if integrated_metrics != None:
                for integrated_metric in integrated_metrics:
                    integrated_system_type = get(integrated_metric, "integrated_system_type")
                    mapped_metrics = get(integrated_metric, "mapped_metrics")
                    integrated_metric_obj = IntegratedMetric(
                        integrated_system_type = integrated_system_type,
                        mapped_metrics = mapped_metrics
                    )
                    integrated_metrics_list.append(integrated_metric_obj)

            metrics_array_object = IntegratedSystemMetricsArray(
                type = type,
                measures = measures,
                integrated_metrics = integrated_metrics_list
            )
        metrics_array.append(metrics_array_object)

        response = self.mrm_publish_metrics(
        monitor_instance_id = monitor_instance_id,
        monitoring_run_id = monitoring_run_id,
        metrics = metrics_array,
        send_report = send_report,
        project_id = project_id,
        space_id = space_id,
        **kwargs
        )

        return response

    def get_risk_evaluation_status_list(self,
        project_id: str = None,
        space_id: str = None,
        data_mart_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Returns the risk evaluation status of all subscriptions in a given service instance.

        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :param str data_mart_id: (optional) The data mart ID.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MrmGetRiskEvaluationStatusEntity` result
        """
        response = self.mrm_get_all_sub_risk_evaluation_status(self,
            project_id = project_id,
            space_id = space_id,
            data_mart_id = data_mart_id,
            **kwargs
        )

        return response

    def get_risk_evaluation_status(self,
        subscription_id: str,
        project_id = None,
        space_id = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Gets risk evaluation status for the given subscription.

        :param str subscription_id: The subscription ID.
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """
        response = self.mrm_get_risk_evaluation_status(
            subscription_id = subscription_id,
            project_id = project_id,
            space_id = space_id,
            **kwargs
        )

        return response

    def update_risk_evaluation_status(self,
        subscription_id: str,
        state: str = None,
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Updates the risk evaluation status for the given subscription.

        :param str subscription_id: The subscription ID.
        :param str state: (optional)
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """
        validate_type(subscription_id, 'subscription_id', str, True)
    
        response = self.mrm_update_risk_evaluation_status(
            subscription_id = subscription_id,
            state = state,
            project_id = project_id,
            space_id = space_id,
            **kwargs
        )

        return response

    def mrm_download_pdf_report(self,
        monitor_instance_id: str,
        monitoring_run_id: str,
        file_name: str = None,
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> 'None':
        """
        Returns the risk evaluation report in a PDF format.

        :param str monitor_instance_id: The monitor instance ID.
        :param str monitoring_run_id: The monitoring run ID.
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :return: None
        """
        validate_type(monitor_instance_id, 'monitor_instance_id', str, True)
        validate_type(monitoring_run_id, 'monitoring_run_id', str, True)

        if file_name == None:
            file_name = "mrm_evaluation_report.pdf"

        response = self.mrm_download_report(
            monitor_instance_id = monitor_instance_id,
            monitoring_run_id = monitoring_run_id,
            project_id = project_id,
            space_id = space_id,
            **kwargs
        )

        if response.status_code != 200:
            print("Failed downloading report - Status : " + str(response.status_code))
        else:
            try:
                with open(file_name, "xb") as file:
                    file.write(response.result.content)
                    print("MRM evaluation report " + file_name + " download successfully !")
            except IOError as e:
                print("Could not create file:" + file_name, ". Please specify another file name and try again..")
                print("I/O error({0}): {1}".format(e.errno, e.strerror))

    def execute_prompt_setup(self,
        prompt_template_asset_id: str,
        label_column: str,
        operational_space_id: str,
        problem_type: str,
        input_data_type: str,
        data_input_locale: List[str] = ['en'],
        generated_output_locale: List[str] = ['en'],
        project_id: str = None,
        space_id: str = None,
        deployment_id : str = None,
        classification_type: str = None,
        context_fields: List[str] = None,
        question_field: str = None,
        supporting_monitors : dict = {},
        background_mode: bool = True,
        **kwargs
    ) -> 'DetailedResponse':

        """
        Performs the setup activities in Openscale for a given prompt template asset.
        
        Note: This method will be deprecated in the next release and be replaced by wos_client.wos.execute_prompt_setup() method"

        :param str prompt_template_asset_id: The GUID of the prompt template asset.
        :param str label_column: The name of the column containing the
               ground truth or actual labels.
        :param str operational_space_id: The rank of the environment in
               which the monitoring is happening. Accepted values are `development`,
               `pre_production`, `production`.
        :param str problem_type: The task type to monitor for the given
               prompt template asset.
        :param str input_data_type:  The input data type.
        :param List[str] data_input_locale: The list containing the locale codes for the input language. eg: ['en'] or ['ja'] Note: Input and output locale should be same.
        :param List[str] generated_output_locale: The list containing the locale codes for the output language. eg: ['en'] or ['ja']
        :param str classification_type: (optional) The classification type
               `binary`/`multiclass` applicable only for `classification` problem (task)
               type.
        :param List[str] context_fields: (optional) The list of prompt variables
               containing the context. Applicable only for Retrieval-Augmented Generation
               problem type.
        :param str question_field: (optional) The prompt variable containing the
               question. Applicable only for Retrieval-Augmented Generation problem type.
        :param dict supporting_monitors: (optional)
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :param str deployment_id: (optional) The GUID of the deployment.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `PromptSetupResponse` result
        """
        
        print("=================================================================")
        print("This method will be deprecated in the next release and be replaced by wos_client.wos.execute_prompt_setup() method")        
        print("=================================================================")
        
        validate_type(prompt_template_asset_id, 'prompt_template_asset_id', str, True)
        monitors = LLLMMonitors(supporting_monitors)

        response = super().mrm_start_prompt_setup(
            prompt_template_asset_id = prompt_template_asset_id,
            project_id = project_id,
            space_id = space_id,
            deployment_id = deployment_id,
            label_column = label_column,
            operational_space_id = operational_space_id,
            problem_type = problem_type,
            classification_type = classification_type,
            input_data_type = input_data_type,
            data_input_locale = data_input_locale,
            generated_output_locale = generated_output_locale,
            context_fields = context_fields,
            question_field = question_field,
            monitors = monitors,
            **kwargs)

        if background_mode:
            return response
        else:
            prompt_template_asset_id = response.result.prompt_template_asset_id
            project_id = response.result.project_id

            def check_state() -> dict:
                details = self.get_prompt_setup(prompt_template_asset_id=prompt_template_asset_id, project_id=project_id, space_id=space_id, deployment_id = deployment_id,show_deprecated_msg=False)
                return details.result.status.state.lower()

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get_prompt_setup(prompt_template_asset_id=prompt_template_asset_id, project_id=project_id, space_id=space_id, deployment_id = deployment_id,show_deprecated_msg=False)
                state = details.result.status.state.lower()

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished setting up prompt template subscription", None, details
                else:
                    return "Adding prompt template subscription failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.status.failure.errors]), details
            timeout = kwargs.get("timeout", 300)
            return print_synchronous_run(
                'Waiting for end of adding prompt setup {}'.format(prompt_template_asset_id),
                check_state,
                get_result=get_result,
                timeout=timeout
            )

    def get_prompt_setup(self,
        prompt_template_asset_id: str,
        project_id: str = None,
        space_id: str = None,
        deployment_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Gets the status of the prompt setup for the given prompt template asset.
        
        Note: This method will be deprecated in the next release and be replaced by wos_client.wos.get_prompt_setup() method

        :param str prompt_template_asset_id: The GUID of the prompt template asset.
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :param str deployment_id: (optional) The GUID of the deployment.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `PromptSetupResponse` result
        """
        if kwargs.get("show_deprecated_msg",True):
            print("=================================================================")
            print("This method will be deprecated in the next release and be replaced by wos_client.wos.get_prompt_setup() method")        
            print("=================================================================")
        
        validate_type(prompt_template_asset_id, 'prompt_template_asset_id', str, True)

        response =  super().mrm_get_prompt_setup(
        prompt_template_asset_id = prompt_template_asset_id,
        project_id = project_id,
        space_id = space_id,
        deployment_id = deployment_id,
        **kwargs)

        return response

    def __get_headers(self,client):
        token = client.authenticator.token_manager.get_token() if (
            isinstance(client.authenticator, IAMAuthenticator) or 
            isinstance(client.authenticator, CloudPakForDataAuthenticator) or 
            isinstance(client.authenticator, MCSPV2Authenticator)
        ) else client.authenticator.bearer_token

        iam_headers = {
            "Authorization": "Bearer %s" % token
        }
        return iam_headers

class LLLMMonitors(PromptSetupRequestMonitors):

    def __init__(self, monitors = {}) -> None:
        self.monitors = monitors

    def to_dict(self):
        return self.monitors
