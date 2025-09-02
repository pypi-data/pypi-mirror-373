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

import requests
from typing import Tuple

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import PromptSetupRequestMonitors, PostRiskEvaluationsResponse, DetailedResponse

from ibm_cloud_sdk_core import BaseService
from ibm_watson_openscale.supporting_classes.enums import TargetTypes, StatusStateType

from ibm_watson_openscale.utils.utils import *
from ibm_watson_openscale.utils.client_errors import *

class WOS():
    """
    Manages Utility methods at the Watson OpenScale level.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter', service_url: str) -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)        
        self._ai_client = ai_client  
        self.service_url = service_url
        
    
    def get_instance_mapping(self, project_id: str = None, space_id: str  = None):
        
        """
        Get all instance mappings specified by the parameters filtered by either of project_id or space_id
        
        Note: This operation is applicable only for Cloud Pack for Data env

        :param str project_id: (optional) Project id with which mapping has to be done
        :param str space_id: (optional) Space id with which mapping has to be done
        :rtype: dict

        A way you might use me is:

        >>> from ibm_watson_openscale import *
        >>> client.wos.get_instance_mapping(                
                project_id=project_id                
             )
        """
        
        if self._ai_client.is_cp4d is not True:
            raise AuthorizationError("This operation is allowed only on CP4D environment")
                
        if project_id == None and space_id == None:
            raise ParameterError("Provide value for either project_id or space_id")
        
        if project_id is not None and space_id is not None:
            raise ParameterError("Provide value for project_id or space_id but not both")
        
        url = '{0}/openscale/v2/instance_mappings'.format(self.service_url)        
        if project_id is not None:
            url = '{0}?project_id={1}'.format(url, project_id)
        
        if space_id is not None:
            url = '{0}?space_id={1}'.format(url, space_id)        
            
        headers = {
            'Accept': 'application/json',
            'Authorization': "Bearer {}".format(self._ai_client.authenticator.token_manager.get_token())
        }
        
        response =  requests.get(url, headers=headers,verify=False)
        return response.json()
            
    def add_instance_mapping(self, service_instance_id: str = None, project_id: str = None, space_id: str  = None):
        
        """
        Create instance mapping between OpenScale service instance and with either space or project.
        
        Note: This operation is applicable only for Cloud Pack for Data env

        :param str service_instance_id: Service instance id.
        :param str project_id: (optional) Project id with which mapping has to be done
        :param str space_id: (optional) Space id with which mapping has to be done
        :rtype: dict

        A way you might use me is:

        >>> from ibm_watson_openscale import *
        >>> client.wos.add_instance_mapping(                
                service_instance_id=service_instance_id,
                project_id=project_id                
             )
        """
        if self._ai_client.is_cp4d is not True:
            raise AuthorizationError("This operation is allowed only on CP4D environment")
        
        validate_type(service_instance_id, 'service_instance_id', str, True)
        
        if project_id == None and space_id == None:
            raise ParameterError("Provide value for either project_id or space_id")
        
        if project_id is not None and space_id is not None:
            raise ParameterError("Provide value for project_id or space_id but not both")
        

        # Check if mapping already exists
        existing_mappings = self.get_instance_mapping(project_id=project_id,space_id=space_id)
        
        # Check if any mappings exist for given project or space
        if existing_mappings.get("instance_mappings"):
            print("Instance mapping already exists. Skipping creation.")
            return existing_mappings
        

        target = {
            "target_type" : TargetTypes.PROJECT if project_id is not None else TargetTypes.SPACE,
            "target_id": project_id if project_id is not None else space_id
        }

        url = '{}/openscale/v2/instance_mappings'.format(self.service_url)
        headers = {
            'Content-type': 'application/json',
            'Authorization': "Bearer {}".format(self._ai_client.authenticator.token_manager.get_token())
        }                 
        payload = {
            "service_instance_id": service_instance_id,
            "target": target
        }
        
        response = requests.post(url, json=payload, headers=headers, verify=False)   
        
        if response.status_code!=201:
            raise ApiRequestFailure("Failed to create instance mapping. Error {}".format(response.text),response)  
        
        return response.json()
    
    def execute_prompt_setup(self,
        prompt_template_asset_id: str,
        project_id: str = None,
        space_id: str = None,
        deployment_id : str = None,
        label_column: str = None,
        operational_space_id: str = None,
        problem_type: str = None,
        classification_type: str = None,
        input_data_type: str = None,
        data_input_locale: List[str] = ['en'],
        generated_output_locale: List[str] = ['en'],
        context_fields: List[str] = None,
        question_field: str = None,
        supporting_monitors : dict = {},
        background_mode: bool = True,
        **kwargs
    ) -> 'DetailedResponse':

        """
        Performs the setup activities in Openscale for a given prompt template asset.

        :param str prompt_template_asset_id: The GUID of the prompt template asset.
        :param str label_column: (optional) The name of the column containing the
               ground truth or actual labels.
        :param str operational_space_id: (optional) The rank of the environment in
               which the monitoring is happening. Accepted values are `development`,
               `pre_production`, `production`.
        :param str problem_type: (optional) The task type to monitor for the given
               prompt template asset.
        :param str classification_type: (optional) The classification type
               `binary`/`multiclass` applicable only for `classification` problem (task)
               type.
        :param str input_data_type: (optional) The input data type.
        :param List[str] data_input_locale: The list containing the locale codes for the input language. eg: ['en'] or ['ja'] Note: Input and output locale should be same.
        :param List[str] generated_output_locale: The list containing the locale codes for the output language. eg: ['en'] or ['ja']
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

        validate_type(prompt_template_asset_id, 'prompt_template_asset_id', str, True)
        monitors = LLMMonitors(supporting_monitors)

        response = self._ai_client.monitor_instances.mrm.mrm_start_prompt_setup(
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
                details = self.get_prompt_setup(prompt_template_asset_id=prompt_template_asset_id, project_id=project_id, space_id=space_id, deployment_id = deployment_id)
                return details.result.status.state.lower()

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get_prompt_setup(prompt_template_asset_id=prompt_template_asset_id, project_id=project_id, space_id=space_id, deployment_id = deployment_id)
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

        :param str prompt_template_asset_id: The GUID of the prompt template asset.
        :param str project_id: (optional) The GUID of the project.
        :param str space_id: (optional) The GUID of the space.
        :param str deployment_id: (optional) The GUID of the deployment.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `PromptSetupResponse` result
        """
        validate_type(prompt_template_asset_id, 'prompt_template_asset_id', str, True)

        response =  self._ai_client.monitor_instances.mrm.mrm_get_prompt_setup(
            prompt_template_asset_id = prompt_template_asset_id,
            project_id = project_id,
            space_id = space_id,
            deployment_id = deployment_id,
            **kwargs )

        return response
    
class LLMMonitors(PromptSetupRequestMonitors):

        def __init__(self, monitors = {}) -> None:
            self.monitors = monitors
    
        def to_dict(self):
            return self.monitors

        