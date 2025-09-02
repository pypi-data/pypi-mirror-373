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

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import IntegratedSystems as BaseIntegratedSystems
from .utils import *
from ibm_cloud_sdk_core import BaseService
from ibm_watson_openscale.base_classes.tables import Table

if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DetailedResponse, JsonPatchOperation

_DEFAULT_LIST_LENGTH = 50

class IntegratedSystems(BaseIntegratedSystems):
    """
    Manages Integrated Systems instance.
    """
    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def show(self, limit: Optional[int] = 10,
        type: str = None,
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> None:
        """
        Show integrated systems. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :param str type: (optional) comma-separated list of type for the integrated
               system.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        A way you might use me is:

        >>> client.integrated_systems.show()
        >>> client.integrated_systems.show(limit=20)
        >>> client.integrated_systems.show(limit=None)
        """
        validate_type(limit, 'limit', int, False)

        response = self.list(
            type=type,
            project_id=project_id,
            space_id=space_id,
            **kwargs)

        records = [[integrated_system.entity.name,
                    integrated_system.entity.type,
                    integrated_system.entity.description,
                    integrated_system.metadata.created_at,
                    integrated_system.metadata.id
                    ] for integrated_system in response.result.integrated_systems]
        columns = ['name', 'type', 'description', 'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Integrated Systems"
        )

    def add(self, name: str,
        type: str,
        description: str,
        credentials: dict,
        connection: object = None,
        group_ids: List[str] = None,
        user_ids: List[str] = None,
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Create a new integrated system.

        Create a new integrated system.

        :param str name: The name of the Integrated System.
        :param str type:
        :param str description: The description of the Integrated System.
        :param dict credentials: The credentials for the Integrated System.
        :param object connection: (optional) The additional connection information
               for the Integrated System.
        :param List[str] group_ids: (optional) Access control list of group id of
               Cloud Pak for Data (Only available for open_pages type and OpenScale on
               Cloud Pak for Data >= 4.0.6 with ENABLE_GROUP_AUTH being true).
        :param List[str] user_ids: (optional) Access control list of user id of
               Cloud Pak for Data (Only available for open_pages type and OpenScale on
               Cloud Pak for Data >= 4.0.6 with ENABLE_GROUP_AUTH being true).
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `IntegratedSystemResponse` result
        """

        validate_type(name, 'name', str, True)
        validate_type(type, 'type', str, True)
        validate_type(description, 'description', str, True)
        validate_type(credentials, 'credentials', dict, True)

        response = super().add(
                name = name,
                description = description,
                type = type,
                credentials = credentials,
                connection = connection,
                group_ids = group_ids,
                user_ids = user_ids,
                project_id = project_id,
                space_id = space_id,
                **kwargs
        )

        return response

    def get(self,
        integrated_system_id: str,
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Get a specific integrated system.

        Get a specific integrated system.

        :param str integrated_system_id: Unique integrated system ID.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `IntegratedSystemResponse` result
        """

        validate_type(integrated_system_id, 'integrated_system_id', str, True)

        response = super().get(integrated_system_id = integrated_system_id,
                               project_id = project_id, space_id = space_id, **kwargs)

        return response

    def update(self,
        integrated_system_id: str,
        json_patch_operation: List['JsonPatchOperation'],
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Update an integrated system.

        Update an integrated system.

        :param str integrated_system_id: Unique integrated system ID.
        :param List[JsonPatchOperation] json_patch_operation:
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `IntegratedSystemResponse` result
        """
        validate_type(integrated_system_id, 'integrated_system_id', str, True)

        response = super().update(integrated_system_id = integrated_system_id, json_patch_operation = json_patch_operation,
                                   project_id=project_id, space_id=space_id, **kwargs)

        return response

    def delete(self,
        integrated_system_id: str,
        project_id: str = None,
        space_id: str = None,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Delete an integrated system.

        Delete an integrated system.

        :param str integrated_system_id: Unique integrated system ID.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        validate_type(integrated_system_id, 'integrated_system_id', str, True)

        response = super().delete(integrated_system_id = integrated_system_id,
                                   project_id=project_id, space_id=space_id, **kwargs)

        return response