# coding: utf-8

# Copyright 2020,2025 IBM All Rights Reserved.
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

import inspect
import json
import tarfile
from typing import Any, BinaryIO, Tuple

from ibm_cloud_sdk_core import BaseService
from ibm_watson_openscale.base_classes.tables import Table
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
    DataSource, DataSourceConnection, DataSourceStatus, DriftService,
    DriftV2Service, ExplainabilityService, ExplanationTasks)
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import \
    Instances as BaseInstances
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
    IntegratedSystems, IntegratedSystemsListEnums, JsonPatchOperation,
    Measurements, Metrics, Runs, Target, get_sdk_headers)
from ibm_watson_openscale.mrm_monitoring import MrmMonitoring
from ibm_watson_openscale.supporting_classes.enums import (FairnessMetrics,
                                                           TargetTypes)

from .mrm import ModelRiskManagement
from .utils import *

if TYPE_CHECKING:
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import (
        DetailedResponse, MetricThresholdOverride, MonitorInstanceSchedule,
        Target)

    from .client import WatsonOpenScaleV2Adapter

_DEFAULT_LIST_LENGTH = 50


class MonitorInstances(BaseInstances):
    """
    Manages Monitor Instances.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        self.runs = Runs(self._ai_client)
        self.measurements = Measurements(ai_client)
        self.explanation = ExplanationTasks(ai_client)
        self.explanation_service = ExplainabilityService(ai_client)
        self.drift = DriftService(ai_client)
        self.drift_v2 = DriftV2Service(ai_client)
        self.mrm_monitoring = MrmMonitoring(ai_client)
        self.mrm = ModelRiskManagement(ai_client)
        super().__init__(watson_open_scale=self._ai_client)

    ################################################
    #    Hidden methods from base monitor class    #
    ################################################
    @property
    def get_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def add(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.create() instead")

    @property
    def update_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def delete_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def list_instances(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def add_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.create() instead")

    @property
    def run_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    #################################################
    #    Overridden methods for monitor instances   #
    #################################################

    def run(
            self,
            monitor_instance_id: str,
            triggered_by: str = "user",
            parameters: dict = None,
            business_metric_context=None,
            project_id: str = None,
            space_id: str = None,
            background_mode: bool = True,
            **kwargs) -> Any:
        """
        Trigger monitoring run.
        :param str monitor_instance_id: Unique monitor instance ID.
        :param str triggered_by: (optional) An identifier representing the source
               that triggered the run request (optional). One of: event, scheduler, user,
               webhook.
        :param dict parameters: (optional) Monitoring
               parameters consistent with the `parameters_schema` from the monitor
               definition.
        :param MonitoringRunBusinessMetricContext business_metric_context:
               (optional) Properties defining the business metric context in the triggered
               run of AI metric calculation.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRun` result

        A way you may use me:

        >>> monitor_instance_run_info = client.monitor_instances.run(
                background_mode=False,
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
             )
        """
        # runs = Runs(watson_open_scale=self._ai_client)
        response = self.runs.add(monitor_instance_id=monitor_instance_id, triggered_by=triggered_by,
                                 parameters=parameters, business_metric_context=business_metric_context,
                                 project_id=project_id, space_id=space_id)

        run_id = response.result.metadata.id

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get_run_details(
                    monitor_instance_id=monitor_instance_id, monitoring_run_id=run_id, project_id=project_id, space_id=space_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get_run_details(
                    monitor_instance_id=monitor_instance_id, monitoring_run_id=run_id, project_id=project_id, space_id=space_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished run", None, details
                else:
                    return "Run failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details
            timeout = kwargs.get("timeout", 300)
            return print_synchronous_run(
                'Waiting for end of monitoring run {}'.format(run_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED],
                timeout=timeout
            )

    def list(self,
             data_mart_id: str = None,
             monitor_definition_id: str = None,
             target_target_id: str = None,
             project_id: str = None,
             space_id: str = None,
             target_target_type: str = None) -> 'DetailedResponse':
        """
        List monitor instances.

        :param str data_mart_id: (optional) comma-separated list of IDs.
        :param str monitor_definition_id: (optional) comma-separated list of IDs.
        :param str target_target_id: (optional) comma-separated list of IDs.
        :param str target_target_type: (optional) comma-separated list of types.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceCollection` result

        A way you may use me:

        >>> monitor_instances_info = client.monitor_instances.list(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
             )
        """
        response = super().list(data_mart_id=data_mart_id,
                                monitor_definition_id=monitor_definition_id,
                                target_target_id=target_target_id,
                                target_target_type=target_target_type,
                                project_id=project_id,
                                space_id=space_id)
        return response

    def show(self, limit: int = 10,
             data_mart_id: str = None,
             monitor_definition_id: str = None,
             target_target_id: str = None,
             target_target_type: str = None,
             project_id: str = None,
             space_id: str = None
             ) -> None:
        """
        Show monitor instances. By default 10 records will be shown.

        :param limit: Maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :param str data_mart_id: (optional) comma-separated list of IDs.
        :param str monitor_definition_id: (optional) comma-separated list of IDs.
        :param str target_target_id: (optional) comma-separated list of IDs.
        :param str target_target_type: (optional) comma-separated list of types.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: None

        A way you might use me is:

        >>> client.monitor_instances.show()
        >>> client.monitor_instances.show(limit=20)
        >>> client.monitor_instances.show(20)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list(data_mart_id=data_mart_id, monitor_definition_id=monitor_definition_id,
                             target_target_id=target_target_id, target_target_type=target_target_type,
                             project_id=project_id, space_id=space_id)

        records = [[instances.entity.data_mart_id,
                    instances.entity.status.state,
                    instances.entity.target.target_id,
                    instances.entity.target.target_type,
                    instances.entity.monitor_definition_id,
                    instances.metadata.created_at,
                    instances.metadata.id]
                   for instances in response.result.monitor_instances]
        columns = ['data_mart_id', 'status', 'target_id', 'target_type', 'monitor_definition_id',
                   'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Monitor instances"
        )

    def show_metrics(self, monitor_instance_id: str, limit: int = 10,
                     project_id: str = None,
                     space_id: str = None,
                     start: str = None,
                     end: str = None
                     ):
        """
        Show metrics for monitor instance.

        :param monitor_instance_id: ID of the monitor instance.
        :type monitor_instance_id: str
        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :param str start: start time on which all metrics we need to pick(optional)
        :param str end: end time on which all metrics we need to pick(optional)
        :type limit: int
        :return: None

        A way you might use me is:

        >>> client.monitor_instances.show_metrics(monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5')
        """
        from datetime import datetime, timedelta
        start_time = start if start is not None else datetime.now() - timedelta(days=7)
        end_time = end if end is not None else datetime.now()

        # runs = Runs(watson_open_scale=self._ai_client)
        response = self.runs.list(
            monitor_instance_id=monitor_instance_id, project_id=project_id, space_id=space_id)

        records = []
        measurements = Measurements(watson_open_scale=self._ai_client)
        for run_id in [run.metadata.id for run in response.result.runs]:
            response = measurements.list(
                monitor_instance_id=monitor_instance_id,
                start=start_time,
                end=end_time,
                run_id=run_id,
                project_id=project_id,
                space_id=space_id
            )

            records.extend([[measurement.entity.timestamp,
                             metric.id,
                             measurement.metadata.id,
                             metric.value,
                             metric.lower_limit,
                             metric.upper_limit,
                             ['{}:{}'.format(tag.id, tag.value)
                              for tag in value.tags],
                             measurement.entity.monitor_definition_id,
                             measurement.entity.monitor_instance_id,
                             measurement.entity.run_id,
                             measurement.entity.target.target_type,
                             measurement.entity.target.target_id]
                            for measurement in response.result.measurements for value in measurement.entity.values for
                            metric in
                            value.metrics])

        columns = ['ts',
                   'id',
                   'measurement_id',
                   'value',
                   'lower_limit',
                   'upper_limit',
                   'tags',
                   'monitor_definition_id',
                   'monitor_instance_id',
                   'run_id',
                   'target_type',
                   'target_id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="{} Monitor Runs Metrics from: {}  till: {}".format(
                monitor_instance_id, start_time, end_time)
        )

    def create(self,
               monitor_definition_id: str,
               target: 'Target',
               parameters: 'dict',
               data_mart_id: str = None,
               thresholds: 'List[MetricThresholdOverride]' = None,
               schedule: 'MonitorInstanceSchedule' = None,
               managed_by: str = None,
               training_data_stats: dict = None,
               background_mode: bool = True,
               skip_scheduler: bool = None,
               project_id: str = None,
               space_id: str = None,
               **kwargs) -> Union['DetailedResponse', Optional[dict]]:
        """
        Create monitor instance.

        :param str data_mart_id:
        :param str monitor_definition_id:
        :param Target target:
        :param dict parameters: (optional) Monitoring
               parameters consistent with the `parameters_schema` from the monitor
               definition.
        :param list[MetricThresholdOverride] thresholds: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param str managed_by: (optional)
        :param training_data_stats: Training statistic json generated using training stats notebook (https://github.com/IBM-Watson/aios-data-distribution/blob/master/training_statistics_notebook.ipynb)
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result

        A way you might use me is:

        >>> from ibm_watson_openscale import *
        >>> target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
             )
        >>> parameters = {
                min_feedback_data_size=50
            }
        >>> thresholds = [
                MetricThresholdOverride(
                    metric_id=client.monitor_definitions.MONITORS.QUALITY.METRIC.ACCURACY,
                    type=MetricThresholdTypes.LOWER_LIMIT,
                    value=0.7
                )
             ]
        >>> monitor_instances_info = client.monitor_instances.create(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                background_mode=False,
                monitor_definition_id=client.monitor_definitions.MONITORS.QUALITY.ID,
                target=target,
                parameters=parameters,
                thresholds=thresholds
             )
        """

        if parameters == None:
            raise Exception("Error : parameters cannot be None")
        if training_data_stats is None:

            # SKIP the schedule creation if monitor is Explain and subscription type is online -- https://github.ibm.com/aiopenscale/tracker/issues/25266
            if self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID == monitor_definition_id:
                self.__validate_fairness_params(parameters)

            # Skip creation of schedule for online subscription
            global_explanation = get(parameters, "global_explanation.enabled")
            if monitor_definition_id == self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID and not self.__is_batch_subscription(target.target_id, self._ai_client,
                                                                                                                                            project_id=project_id, space_id=space_id):
                if not global_explanation:
                    if skip_scheduler == False:
                        print(
                            "Warning : Monitor is Explain, subscription type is online and global_explanation is not enabled, so skip_scheduler is re assigned as True !")
                    skip_scheduler = True
            response = super().add(data_mart_id=data_mart_id, monitor_definition_id=monitor_definition_id,
                                   target=target, parameters=parameters, thresholds=thresholds,
                                   schedule=schedule, managed_by=managed_by, skip_scheduler=skip_scheduler,
                                   project_id=project_id, space_id=space_id)
            monitor_instance_id = response.result.metadata.id
            return self.__check_for_finished_status(background_mode, monitor_instance_id, response=response, project_id=project_id, space_id=space_id)
        else:
            if len(training_data_stats) == 0:
                raise Exception(
                    "training_data_stats is empty. Please re-generate and use it")
            return self.__create_monitor_from_training_stats(data_mart_id, training_data_stats, kwargs, background_mode,
                                                             project_id=project_id, space_id=space_id)

    def delete(self,
               monitor_instance_id: str,
               background_mode: bool = True, force: bool = False,
               project_id: str = None,
               space_id: str = None,
               **kwargs
               ) -> Union['DetailedResponse', Optional[dict]]:
        """
        Delete monitor instance.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you might use me is:

        >>> ai_client_v2.monitor_instances.delete(
                background_mode=False,
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
             )
        """
        response = super().delete(monitor_instance_id=monitor_instance_id, force=force)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list(project_id=project_id, space_id=space_id)
                if monitor_instance_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list(project_id=project_id, space_id=space_id)
                if monitor_instance_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting monitor instance", None, response
                else:
                    # TODO: Need to show the reason.
                    return "Delete monitor instance failed", 'Reason: None', response
            timeout = kwargs.get("timeout", 300)
            return print_synchronous_run(
                'Waiting for end of deleting monitor instance {}'.format(
                    monitor_instance_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED],
                timeout=timeout
            )

    def get(self, monitor_instance_id: str,
            project_id: str = None,
            space_id: str = None
            ) -> 'DetailedResponse':
        """
        Get monitor instance details.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result

        A way you might use me is:

        >>> monitor_instance_info = client.monitor_instances.get(
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
             )
        """
        response = super().get(monitor_instance_id=monitor_instance_id,
                               project_id=project_id, space_id=space_id)
        return response

    def update(self,
               monitor_instance_id: str,
               patch_document: List['PatchDocument'],
               update_metadata_only: bool = None) -> 'DetailedResponse':
        """
        Update monitor instance.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param List[PatchDocument] patch_document:
        :param bool update_metadata_only: (optional) Flag that allows to control if
               the underlaying actions related to the monitor reconfiguration should be
               triggered.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result
        """
        response = super().update(monitor_instance_id=monitor_instance_id, patch_document=patch_document,
                                  update_metadata_only=update_metadata_only)
        return response

    def _verify_table(self, data_set_id: str = None) -> None:
        """
        Verify if particular dataset/table exists and is loaded with any data.

        :param data_set_id: ID of the data set to check
        """
        validate_type(data_set_id, 'data_set_id', str, True)
        if self._ai_client.data_sets.get_records_count(data_set_id=data_set_id) == 0:
            raise MissingPayload(
                self.__class__.__name__, '{} data set table is empty.'.format(data_set_id))

    def get_metrics_count(self, monitor_instance_id: str, start: 'datetime', end: 'datetime',
                          interval: str = None, filter: str = None, group: str = None,
                          project_id=None, space_id=None):
        """
        Get the count of the metrics.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param datetime start: Calculations **inclusive**, internally floored to
               achieve full interval. If interval is vulnerable to time zone, the
               calculated value depends on a backend db engine: PostgreSQL respects time
               zone and DB2 use UTC time. Calculated value is returned in response.
        :param datetime end: Calculations **exclusive**, internally ceiled to
               achieve full interval. If interval is vulnerable to time zone, the
               calculated value depends on a backend db engine: PostgreSQL respects time
               zone and DB2 use UTC time. Calculated value is returned in response.
        :param str agg: Comma delimited function list constructed from metric name
               and function, e.g. `agg=metric_name:count,:last` that defines aggregations.
        :param str interval: (optional) Time unit in which metrics are grouped and
               aggregated, interval by interval.
        :param str filter: (optional) Filter expression can consist of any metric
               tag or a common column of string type followed by filter name and
               optionally a value, all delimited by colon. Supported filters are: `in`,
               `eq`, `null` and `exists`. Sample filters are:
               `filter=region:in:[us,pl],segment:eq:sales` or
               `filter=region:null,segment:exists`.
        :param str group: (optional) Comma delimited list constructed from metric
               tags, e.g. `group=region,segment` to group metrics before aggregations.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartGetMonitorInstanceMetrics` result

        A way you might use me is:

        >>> metrics_count = client.monitor_instances.get_metrics_count(
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                start=start_time,
                end=end_time,
             )
        """
        metrics = Metrics(self._ai_client)
        response = metrics.list(monitor_instance_id=monitor_instance_id, start=start, end=end,
                                agg='count', interval=interval, filter=filter, group=group,
                                project_id=project_id, space_id=space_id)
        return response

    def get_metrics(self, monitor_instance_id: str, start: 'datetime', end: 'datetime',
                    agg: str = 'last', interval: str = None, filter: str = None, group: str = None,
                    project_id=None, space_id=None):
        """
        Get all the generated metrics between start and end date for specific monitor instance id

        :param str monitor_instance_id: Unique monitor instance ID.
        :param datetime start: Calculations **inclusive**, internally floored to
               achieve full interval. If interval is vulnerable to time zone, the
               calculated value depends on a backend db engine: PostgreSQL respects time
               zone and DB2 use UTC time. Calculated value is returned in response.
        :param datetime end: Calculations **exclusive**, internally ceiled to
               achieve full interval. If interval is vulnerable to time zone, the
               calculated value depends on a backend db engine: PostgreSQL respects time
               zone and DB2 use UTC time. Calculated value is returned in response.
        :param str agg: Comma delimited function list constructed from metric name
               and function, e.g. `agg=metric_name:count,:last` that defines aggregations.
        :param str interval: (optional) Time unit in which metrics are grouped and
               aggregated, interval by interval.
        :param str filter: (optional) Filter expression can consist of any metric
               tag or a common column of string type followed by filter name and
               optionally a value, all delimited by colon. Supported filters are: `in`,
               `eq`, `null` and `exists`. Sample filters are:
               `filter=region:in:[us,pl],segment:eq:sales` or
               `filter=region:null,segment:exists`.
        :param str group: (optional) Comma delimited list constructed from metric
               tags, e.g. `group=region,segment` to group metrics before aggregations.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartGetMonitorInstanceMetrics` result

        A way you might use me is:

        >>> metrics_count = client.monitor_instances.get_metrics_count(
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                start=start_time,
                end=end_time,
             )
        """
        metrics = Metrics(self._ai_client)
        response = metrics.list(monitor_instance_id=monitor_instance_id, start=start, end=end,
                                agg=agg, interval=interval, filter=filter, group=group,
                                project_id=project_id, space_id=space_id)
        return response

    def upload_drift_model(self, model_path: str, data_mart_id: str, subscription_id: str,
                           archive_name: str = "user_drift.tar.gz", enable_data_drift: bool = True,
                           enable_model_drift: bool = True, project_id=None, space_id=None) -> 'DetailedResponse':
        """
        Upload a Drift model to be able to compute Drift monitor.

        :param str model_path: (required) path to the drift model
        :param str data_mart_id: (required) data_mart ID
        :param str subscription_id: (required) subscription ID
        :param str archive_name: (optional) Archive name to use while storing tarball in datamart
        :param str enable_data_drift: (optional) If data drift is expected to be enabled for this subscription.
            If set to True, archive is verified to contain a valid data constraints json file.
        :param str enable_model_drift: (optional) If model drift is expected to be enabled for this subscription.
            If set to True, archive is verified to contain a valid drift model pickle file.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.

        A way you might use me is:

        >>> client.monitor_instances.upload_drift_model(
                model_path='drift_models/drift_detection_model.tar.gz',
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                subscription_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
             )
        """

        drift_model = open(model_path, mode="rb").read()

        response = self.drift.drift_archive_post(data_mart_id, subscription_id, drift_model, archive_name=archive_name,
                                                 enable_data_drift=enable_data_drift, enable_model_drift=enable_model_drift,
                                                 project_id=project_id, space_id=space_id)

        return response

    def download_drift_model(self, monitor_instance_id: str) -> "DetailedResponse":
        """
        Downloads the model.

        :param str monitor_instance_id: (required) The Drift monitor instance ID.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.

        A way you might use me is:

        >>> client.monitor_instances.download_drift_model(
            monitor_instance_id="0a9a4b85-f2bb-46de-850b-f033d7d37d9a"
            )
        """

        response = self.drift.drift_archive_get(monitor_instance_id)

        return response

    def download_drift_model_metadata(self, monitor_instance_id: str) -> "DetailedResponse":
        """
        Downloads the model metadata.

        :param str monitor_instance_id: (required) The Drift monitor instance ID.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.

        A way you might use me is:

        >>> client.monitor_instances.download_drift_model_metadata(
            monitor_instance_id="0a9a4b85-f2bb-46de-850b-f033d7d37d9a"
            )
        """

        response = self.drift.drift_archive_head(monitor_instance_id)
        return response

    def list_runs(self,
                  monitor_instance_id: str, start: str = None, limit: int = None,
                  project_id=None, space_id=None):
        """
        List monitoring runs.

        List monitoring runs.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param str start: (optional) The page token indicating where to start
               paging from.
        :param int limit: (optional) The limit of the number of items to return,
               for example limit=50. If not specified a default of 100 will be  used.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRunCollection` result
        """

        # runs = Runs(watson_open_scale=self._ai_client)
        return self.runs.list(monitor_instance_id=monitor_instance_id, start=start, limit=limit,
                              project_id=project_id, space_id=space_id)

    def get_run_details(self, monitor_instance_id: str, monitoring_run_id: str, project_id=None, space_id=None, **kwargs):
        """
        Get monitoring run details.
        :param str monitor_instance_id: Unique monitor instance ID.
        :param str monitoring_run_id: Unique monitoring run ID.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRun` result
        """
        # runs = Runs(watson_open_scale=self._ai_client)
        return self.runs.get(monitor_instance_id=monitor_instance_id, monitoring_run_id=monitoring_run_id, project_id=project_id, space_id=space_id)

    def explanation_tasks(self, scoring_ids: List[str], input_rows: List[dict] = None, explanation_types: List[str] = None, subscription_id=None,
                          project_id=None, space_id=None, **kwargs):
        """
        Compute explanations.

        Submit tasks for computing explanation of predictions.

        :param List[str] scoring_ids: IDs of the scoring transaction.
        :param List[dict] input_rows: (optional) List of scoring transactions.
        :param List[str] explanation_types: (optional) Types of explanations to
               generate.
        :param str subscription_id: (optional) Unique subscription ID.               
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `PostExplanationTaskResponse` result
        """

        return self.explanation.add(scoring_ids=scoring_ids, input_rows=input_rows, explanation_types=explanation_types, subscription_id=subscription_id,
                                    project_id=project_id, space_id=space_id, **kwargs)

    def get_explanation_tasks(self, explanation_task_id: str, subscription_id=None, project_id=None, space_id=None, **kwargs):
        """
        Get explanation.

        Get explanation for the given explanation task id.

        :param str explanation_task_id: ID of the explanation task.
        :param str subscription_id: Unique subscription ID.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `GetExplanationTaskResponse` result
        """

        return self.explanation.get(explanation_task_id=explanation_task_id, subscription_id=subscription_id, project_id=project_id, space_id=space_id, **kwargs)

    def get_all_explaination_tasks(self, offset=None, limit=None, subscription_id=None, scoring_id=None, status=None,
                                   project_id=None, space_id=None, **kwargs):
        """
        List all explanations.

        List of all the computed explanations.

        :param str subscription_id: Unique subscription ID.
        :param int offset: (optional) offset of the explanations to return.
        :param int limit: (optional) Maximum number of explanations to return.
        :param str scoring_id: (optional) ID of the scoring transaction.
        :param str status: (optional) Status of the explanation task.
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `GetExplanationTasksResponse` result
        """

        return self.explanation.list(offset=offset, limit=limit, subscription_id=subscription_id, scoring_id=scoring_id, status=status,
                                     project_id=project_id, space_id=space_id, **kwargs)

    def get_measurement_details(self, monitor_instance_id: str, measurement_id: str, project_id=None, space_id=None, **kwargs):
        """
        Get Measurement details.
        Get Measurement info for the given measurement and monitor  instance id.
        :param str monitor_instance_id: ID of the monitor instance.
        :param str measurement_id: ID of the measurement.
        :param dict headers: A `dict` containing the request headers
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorMeasurementResponse` result
        """
        return self.measurements.get(monitor_instance_id=monitor_instance_id, measurement_id=measurement_id,
                                     project_id=project_id, space_id=space_id, **kwargs)

    # private method to check for finished state
    def __check_for_finished_status(self, background_mode, monitor_instance_id, response, project_id=None, space_id=None):
        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get(
                    monitor_instance_id=monitor_instance_id, project_id=project_id, space_id=space_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get(
                    monitor_instance_id=monitor_instance_id, project_id=project_id, space_id=space_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.ACTIVE]:
                    return "Monitor instance successfully created", None, details
                else:
                    return "Monitor instance creation failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details

            return print_synchronous_run(
                'Waiting for end of monitor instance creation {}'.format(
                    monitor_instance_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE],
            )

    # private method to create monitors from training stats
    def __create_monitor_from_training_stats(self, data_mart_id, training_stats_info, params, background_mode,
                                             project_id=None,
                                             space_id=None):
        subscription_id = params.get("subscription_id")

        validate_type(data_mart_id, 'data_mart_id', str, True)
        validate_type(subscription_id, 'subscription_id', str, True)

        responses = {}
        if 'fairness_configuration' in training_stats_info:
            target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id=subscription_id
            )
            parameters = training_stats_info["fairness_configuration"]["parameters"]
            self.__validate_fairness_params(parameters)
            parameters["model_type"] = training_stats_info['common_configuration']['problem_type']
            thresholds = training_stats_info["fairness_configuration"]["thresholds"]
            print("Creating fairness monitor")
            response = super().add(
                data_mart_id=data_mart_id,
                background_mode=False,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID,
                target=target,
                parameters=parameters,
                thresholds=thresholds,
                project_id=project_id,
                space_id=space_id)

            mon_resp = self.__check_for_finished_status(
                background_mode, response.result.metadata.id, response=response, project_id=project_id, space_id=space_id)
            responses[self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID] = mon_resp.result.to_dict()

        if 'explainability_configuration' in training_stats_info:
            target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id=subscription_id
            )
            parameters = {
                "enabled": True,
                "training_statistics": training_stats_info["explainability_configuration"]
            }
            print("Creating Explain monitor")

            # SKIP the schedule creation for Explain monitor -- https://github.ibm.com/aiopenscale/tracker/issues/25266
            skip_scheduler = True
            # Don't skip if it is a batch subscription or if global explanation is enabled
            global_explanation = get(
                training_stats_info, "explainability_configuration.parameters.global_explanation.enabled")
            if self.__is_batch_subscription(subscription_id, self._ai_client, project_id=project_id, space_id=space_id) or global_explanation:
                skip_scheduler = None

            response = super().add(
                data_mart_id=data_mart_id,
                background_mode=False,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID,
                target=target,
                parameters=parameters,
                skip_scheduler=skip_scheduler,
                project_id=project_id,
                space_id=space_id
            )

            mon_resp = self.__check_for_finished_status(
                background_mode, response.result.metadata.id, response=response, project_id=project_id, space_id=space_id)
            responses[self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID] = mon_resp.result.to_dict()

            return responses

    def add_measurements(self,
                         monitor_instance_id: str, monitor_measurement_request: List['MonitorMeasurementRequest'],
                         project_id=None, space_id=None, **kwargs):
        """
        Publish measurement data to OpenScale.

        Publish measurement data to OpenScale for a specific monitor instance.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param List[MonitorMeasurementRequest] monitor_measurement_request:
        :param str project_id: Id of the Project context in which governance operation is happening (optional)
        :param str space_id: Id of the Space context in which governance operation is happening (optional)
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        return self.measurements.add(monitor_instance_id=monitor_instance_id, monitor_measurement_request=monitor_measurement_request,
                                     project_id=project_id, space_id=space_id, **kwargs)

    def upload_explainability_archive(self, subscription_id: str, archive: BinaryIO, **kwargs):
        """
        Upload explainability archives.

        API to upload explainability archives such as the Perturbations scoring response
        archive. The api can also be used to update the archive.

        :param str subscription_id: Unique subscription ID.
        :param BinaryIO archive: explanation Archive
        :rtype: DetailedResponse
        """

        return self.explanation_service.explainability_archive_post(subscription_id=subscription_id, body=archive, **kwargs)

    def get_explainability_archive(self, subscription_id: str, **kwargs):
        """
        Retrieves the Explainability archives.

        API to retrieve the Explainability archives.

        :param str subscription_id: Unique subscription ID.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        return self.explanation_service.explainability_archive_get(subscription_id=subscription_id, **kwargs)

    def __is_batch_subscription(self, subscription_id, ai_client, project_id=None, space_id=None):
        return ai_client.subscriptions.get(subscription_id, project_id=project_id, space_id=space_id).result.entity.deployment.deployment_type == 'batch'

    def __sanitize_parameters_for_drift_v2_batch(self, parameters):
        """
        Updates the handling of the Drift V2 batch parameter to accommodate the SDK format,
        with the input list internally converted to a dictionary to maintain compatibility 
        with the Service side format.

        Example:
            Service side format:
                "most_important_features": {
                    "fields": ["A", "B", "C", "D"]
                }

            SDK format:
                "most_important_features": ["A", "B", "C", "D"]
        """
        for key in ("most_important_features", "important_input_metadata_columns"):
            value = parameters.get(key, [])
            if not isinstance(value, dict):
                parameters[key] = {"fields": value}
                
        return parameters

    def enable_monitor_using_training_data(self, datamart_id, subscription_id, monitors_config, drifted_transaction_table={}, explain_queue_table={}, explain_results_table={},
                                           project_id=None, space_id=None):
        """
            Enable configured monitors and learn stats online

            :param str datamart_id: Datamart id in which we want to to create this subscription.
            :param str subscription_id: subscription id
            :param dict monitors_config: configuration params for monitors
                Format for the monitors_config is as follows
                monitors_config = {
                    "fairness_configuration": {
                        "enabled": True,
                        "parameters": {
                        },
                        "thresholds": [
                        ]
                    },
                    "quality_configuration": {
                            "enabled": True,
                            "parameters" : {
                            },
                            "thresholds" : []
                    },
                    "explainability_configuration":{
                            "enabled": True,
                            "parameters" : {
                                "enable_online_learning": True
                            }
                    },
                    "drift_configuration": {
                            "enabled": True,
                            "parameters" : {
                            "train_drift_model": True
                            }
                        },
                    "drift_v2_configuration": {
                            "enabled": True,
                            "parameters" : {
                                "train_archive": True,
                                "features": {
                                    "fields": [
                                        "A",
                                        "B"
                                    ],
                                    "importances": {
                                        "A": 0.6642,
                                        "B": 0.0003,
                                    }
                                },
                                "most_important_features": {
                                    "fields": ["A"]
                                }
                                "advanced_controls": {
                                    "enable_drift_v2_batch": True
                                }
                            }
                        }
                }
            :param dict drifted_transaction_table: Dictionary containing drifted transaction table connection information. Required if drift is to be configured
                Format for the drifted transaction table is as follows
                drifted_transaction_table = {
                    "data": {
                        "auto_create": False,
                        "database": "SAMPLE",
                        "schema": "KP",
                        "table": "DRIFTED_TRANSACTION_TABLE"
                    },
                    "parameters":{
                        "partition_column": "WOS_PARTITION_COLUMN",
                        "num_partitions": 12
                    }
                }
            :param dict explain_queue_table: Dictionary containing explanation queue table connection information. Required if explanation is to be configured.
                Format for the explain_queue_table is same as drifted transaction table
            :param dict explain_results_table: Dictionary containing explanation results table connection information. Required if explanation is to be configured.
                Format for the explain_results_table is same as drifted transaction table
            :param str project_id: Id of the Project context in which governance operation is happening (optional)
            :param str space_id: Id of the Space context in which governance operation is happening (optional)
            :return: list containing monitor instance ids
            :rtype: list
        """

        validate_type(datamart_id, 'data_mart_id', str, True)
        validate_type(subscription_id, 'subscription_id', str, True)

        # Verify subscription is in “active” state
        subscription = self._ai_client.subscriptions.get(
            subscription_id, project_id=project_id, space_id=space_id).result.to_dict()
        if get(subscription, "entity.status.state") != "active":
            raise Exception(
                "Subscription is not in active state. Make sure subscription was created successfully")

        # Verify subscription is batch
        if get(subscription, "entity.analytics_engine.type") != "spark":
            raise Exception(
                "Enabling monitors with training data is only available for batch subscription.")

        # Load monitors_config
        monitor_instance_ids = {}
        enable_fairness = monitors_config["fairness_configuration"]["enabled"]
        enable_quality = monitors_config["quality_configuration"]["enabled"]
        enable_explainability = monitors_config["explainability_configuration"]["enabled"]
        enable_drift = monitors_config["drift_configuration"]["enabled"]
        enable_drift_v2 = get(
            monitors_config, "drift_v2_configuration.enabled", False)
        target = self.__get_target_obj(subscription_id)
        data_sources = get(subscription, "entity.data_sources", [])

        if enable_explainability or enable_drift:
            if len(data_sources) == 0:
                raise Exception(
                    "Data sources not found for creating explain tables")
        db_integrated_system_id = get(
            data_sources[0], "connection.integrated_system_id")
        source_type = get(data_sources[0], "connection.type")

        if enable_explainability:
            print("Enabling Explainability....")

            scoring_endpoint = get(
                subscription, "entity.deployment.scoring_endpoint")
            if not get(scoring_endpoint, "url"):
                raise Exception(
                    "Missing Scoring url : Scoring url is mandatory for the subscription to enable explainability")

            # Patch Data Sources
            explain_queue_data_source = self.__get_data_source(
                explain_queue_table, db_integrated_system_id, "explain_queue", source_type)
            explain_result_data_source = self.__get_data_source(
                explain_results_table, db_integrated_system_id, "explain_result", source_type)
            data_source_patch_document = [
                JsonPatchOperation(
                    op=OperationTypes.ADD, path="/data_sources/-", value=explain_queue_data_source),
                JsonPatchOperation(
                    op=OperationTypes.ADD, path="/data_sources/-", value=explain_result_data_source)
            ]
            self._ai_client.subscriptions.update(
                subscription_id=subscription_id, patch_document=data_source_patch_document)
            # Enable Explainability
            parameters = monitors_config["explainability_configuration"]["parameters"]
            monitor_instance_details = self.create(
                data_mart_id=datamart_id,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID,
                target=target,
                parameters=parameters).result
            explain_mon_id = monitor_instance_details.metadata.id
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID] = explain_mon_id

        if enable_fairness:
            print("Enabling fairness....")
            parameters = monitors_config["fairness_configuration"]["parameters"]
            thresholds = monitors_config["fairness_configuration"]["thresholds"]
            monitor_instance_details = self.create(
                data_mart_id=datamart_id,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID,
                target=target,
                parameters=parameters,
                thresholds=thresholds).result
            fairness_id = monitor_instance_details.metadata.id
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID] = fairness_id

        if enable_quality:
            print("Enabling Quality....")
            parameters = monitors_config["quality_configuration"]["parameters"]
            thresholds = monitors_config["quality_configuration"]["thresholds"]
            monitor_instance_details = self.create(
                data_mart_id=datamart_id,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.QUALITY.ID,
                target=target,
                parameters=parameters,
                thresholds=thresholds).result
            quality_id = monitor_instance_details.metadata.id
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.QUALITY.ID] = quality_id

        if enable_drift:
            print("Enabling Drift....")
            # Patch Data Sources
            drift_data_source = self.__get_data_source(
                drifted_transaction_table, db_integrated_system_id, "drift", source_type)
            data_source_patch_document = [
                JsonPatchOperation(
                    op=OperationTypes.ADD, path="/data_sources/-", value=drift_data_source)
            ]
            self._ai_client.subscriptions.update(
                subscription_id=subscription_id, patch_document=data_source_patch_document)
            # Enable Drift
            parameters = monitors_config["drift_configuration"]["parameters"]
            drift_monitor_details = self.create(
                data_mart_id=datamart_id,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.DRIFT.ID,
                target=target,
                parameters=parameters
            ).result
            drift_mon_id = drift_monitor_details.metadata.id
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.DRIFT.ID] = drift_mon_id

        if enable_drift_v2:
            print("Enabling Drift V2....")
            parameters = self.__sanitize_parameters_for_drift_v2_batch(monitors_config["drift_v2_configuration"]["parameters"])
            drift_v2_monitor_details = self.create(
                data_mart_id=datamart_id,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.DRIFT_V2.ID,
                target=target,
                parameters=parameters
            ).result
            drift_v2_mon_id = drift_v2_monitor_details.metadata.id
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.DRIFT_V2.ID] = drift_v2_mon_id

        return monitor_instance_ids

    def enable_monitors(self, datamart_id, service_provider_id, subscription_id, configuration_archive, drifted_transaction_table={}, explain_queue_table={}, explain_results_table={},
                        project_id=None, space_id=None):
        """
            Enable configured monitors using configuration archive file

            :param str datamart_id: Datamart id in which we want to to create this subscription.
            :param str service_provider_id: Service Provider id.            
            :param str configuration_archive: Path to the configuration archive.
            :param dict drifted_transaction_table: Dictionary containing drifted transaction table connection information. Required if drift is to be configured    
                Format for the drifted transaction table is as follows
                    drifted_transaction_table = {
                        "data": {
                            "auto_create": True,
                            "database": "SAMPLE",
                            "schema": "KP",
                            "table": "drifted_transactions_table_new"
                        }
                    }
            :param dict explain_queue_table: Dictionary containing explanation queue table connection information. Required if explanation is to be configured.
                Format for the explain_queue_table is same as drifted transaction table
            :param dict explain_results_table: Dictionary containing explanation results table connection information. Required if explanation is to be configured.
                Format for the explain_results_table is same as drifted transaction table
            :param str project_id: Id of the Project context in which governance operation is happening (optional)
            :param str space_id: Id of the Space context in which governance operation is happening (optional)
            :return: list containing monitor instance ids
            :rtype: list

        """

        validate_type(datamart_id, 'data_mart_id', str, True)
        validate_type(service_provider_id, 'service_provider_id', str, True)
        validate_type(subscription_id, 'subscription_id', str, True)
        # validate_type(configuration_archive, 'configuration_archive', str, True)

        common_config = self.__get_common_configuration(configuration_archive)
        common_configuration = get(common_config, 'common_configuration')

        enable_fairness = get(common_configuration, "enable_fairness", False)
        enable_explainability = get(
            common_configuration, "enable_explainability", False)
        enable_quality = get(common_configuration, "enable_quality", False)
        enable_drift = get(common_configuration, "enable_drift", False)
        enable_drift_v2 = get(common_configuration, "enable_drift_v2", False)

        monitor_instance_ids = {}

        subscription = self._ai_client.subscriptions.get(
            subscription_id, project_id=project_id, space_id=space_id).result.to_dict()

        if get(subscription, "entity.status.state") != "active":
            raise Exception(
                "Subscription is not in active state. Make sure subscription was created successfully")

        subscription_name = get(subscription, "entity.asset.name")
        data_sources = get(subscription, "entity.data_sources", [])
        # Validate individual monitor required information
        fairness_config = None
        if enable_fairness:
            fairness_config = self.__get_fairness_configuration(
                configuration_archive)

        explain_statistics = None
        if enable_explainability:
            self.__validate_table_info(explain_results_table)
            self.__validate_table_info(explain_queue_table)
            if len(data_sources) == 0:
                raise Exception(
                    "Data sources not found for creating explain tables")

            with tarfile.open(configuration_archive, 'r:gz') as tar:
                if "explainability.tar.gz" not in tar.getnames():
                    if "explainability_statistics.json" not in tar.getnames() and "explainability_perturbations.tar.gz" not in tar.getnames():
                        raise Exception(
                            "explainability.tar.gz file is missing in archive file")
                    else:
                        if "explainability_statistics.json" not in tar.getnames():
                            raise Exception(
                                "explainability_statistics.json file is missing in archive file")
                        else:
                            explain_statistics = self.__get_explainability_statistics(
                                configuration_archive)

                        if "explainability_perturbations.tar.gz" not in tar.getnames():
                            raise Exception(
                                "explainability_perturbations.tar.gz file is missing in archive file")

        if enable_drift:
            self.__validate_table_info(drifted_transaction_table)
            if len(data_sources) == 0:
                raise Exception(
                    "Data sources not found for creating drift tables")

            with tarfile.open(configuration_archive, 'r:gz') as tar:
                if "drift_archive.tar.gz" not in tar.getnames():
                    raise Exception(
                        "drift_archive.tar.gz file is missing in archive file")

                tar_file = tar.extractfile("drift_archive.tar.gz")

                with open("drift.tar.gz", 'wb') as outfile:
                    outfile.write(tar_file.read())

                # Upload drift monitor
                self._ai_client.monitor_instances.upload_drift_model(
                    model_path="drift.tar.gz",
                    data_mart_id=datamart_id,
                    subscription_id=subscription_id,
                    project_id=project_id,
                    space_id=space_id
                ).result

        if enable_drift_v2:
            # Read the drift_v2 archive file
            with tarfile.open(configuration_archive, 'r:gz') as tar:
                if "drift_v2_archive.tar.gz" not in tar.getnames():
                    raise Exception(
                        "drift_v2_archive.tar.gz file is missing in archive file")

                tar_file = tar.extractfile("drift_v2_archive.tar.gz")

                with open("drift_v2.tar.gz", 'wb') as outfile:
                    outfile.write(tar_file.read())

                # Upload the archive file to the subscription
                self._ai_client.monitor_instances.upload_drift_v2_archive(
                    archive_path="drift_v2.tar.gz",
                    subscription_id=subscription_id
                ).result

        if enable_fairness:
            print("Enabling fairness....")
            fairness_id = self.__create_fairness_monitor(
                datamart_id, subscription_id, fairness_config, project_id=project_id, space_id=space_id)
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID] = fairness_id

        if enable_quality:
            print("Enabling Quality....")
            quality_id = self.__create_quality_monitor(
                datamart_id, subscription_id, project_id=project_id, space_id=space_id)
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.QUALITY.ID] = quality_id

        if enable_drift:
            print("Enabling Drift....")
            drift_mon_id = self.__create_drift_monitor(
                datamart_id, subscription_id, configuration_archive, common_configuration, drifted_transaction_table, data_sources,
                project_id=project_id, space_id=space_id)
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.DRIFT.ID] = drift_mon_id

        if enable_drift_v2:
            print("Enabling Drift V2....")
            drift_v2_mon_id = self.__create_drift_v2_monitor(
                datamart_id=datamart_id, subscription_id=subscription_id)
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.DRIFT_V2.ID] = drift_v2_mon_id

        if enable_explainability:

            print("Enabling Explainability....")

            explain_mon_id = self.__create_explain_monitor(
                datamart_id, subscription_id, explain_statistics, explain_queue_table, explain_results_table, data_sources, configuration_archive,
                project_id=project_id, space_id=space_id)
            monitor_instance_ids[self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID] = explain_mon_id

        return monitor_instance_ids

    def get_drift_v2_archive_metadata(self, subscription_id: str, archive_id: str = None, **kwargs
                                      ) -> 'DetailedResponse':
        """
        Get drift archive metadata for a given subscription.

        :param str subscription_id: The id of the subscription.
        :param str archive_id: (optional) The id of the archive for which the metadata needs to be downloaded. 
           It will download the metadata for the latest baseline archive by default..
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        return self.drift_v2.download_drift_v2_archive_metadata(subscription_id=subscription_id, archive_id=archive_id, **kwargs)

    def upload_drift_v2_archive(self, subscription_id: str, archive_path: str, archive_name: str = None, **kwargs) -> 'DetailedResponse':
        """
        Upload drift_v2 archive for a given subscription.

        This API is used to upload the drift_v2 archive necessary to configure the Drift
        v2 monitor.

        :param str subscription_id: The id of the subscription.
        :param archive_path: The path of the archive being uploaded 
        :param str archive_name: (optional) The name of the archive being uploaded.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if archive_path is None:
            raise ValueError('archive_path must be provided')

        body = open(archive_path, mode="rb").read()

        return self.drift_v2.upload_drift_v2_archive(subscription_id=subscription_id, body=body, archive_name=archive_name, **kwargs)

    def download_drift_v2_archive(self, subscription_id: str, archive_id: str = None, **kwargs) -> 'DetailedResponse':
        """
        Get drift v2 archive for a given subscription.

        This API is used to download the drift_v2 Archives.

        :param str subscription_id: The id of the subscription.
        :param str archive_id: (optional) The id of the archive to be downloaded.
               It will download the latest baseline archive by default.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """
        return self.drift_v2.download_drift_v2_archive(subscription_id=subscription_id, archive_id=archive_id, **kwargs)

    def __validate_table_info(self, table_info):

        validate_type(get(table_info, "data.auto_create"),
                      'auto_create', bool, True)
        validate_type(get(table_info, "data.database"), 'database', str, True)
        validate_type(get(table_info, "data.table"), 'table', str, True)

    def __get_common_configuration(self, configuration_archive):
        common_config = None
        with tarfile.open(configuration_archive, 'r:gz') as tar:
            if "common_configuration.json" not in tar.getnames():
                raise Exception(
                    "common_configuration.json file is missing in archive file")

            json_content = tar.extractfile('common_configuration.json')
            data = json_content.read().decode()
            common_config = json.loads(data)

        return common_config

    def __get_fairness_configuration(self, configuration_archive):
        fairness_config = None
        with tarfile.open(configuration_archive, 'r:gz') as tar:
            if "fairness_statistics.json" not in tar.getnames():
                raise Exception(
                    "fairness_statistics.json file is missing in archive file")

            json_content = tar.extractfile('fairness_statistics.json')
            data = json_content.read().decode()
            fairness_config = json.loads(data)

        return fairness_config

    def __get_explainability_statistics(self, configuration_archive):
        explain_stats = None
        with tarfile.open(configuration_archive, 'r:gz') as tar:
            json_content = tar.extractfile('explainability_statistics.json')
            data = json_content.read().decode()
            explain_stats = json.loads(data)

        return explain_stats

    def __get_target_obj(self, subscription_id):
        return Target(
            target_type=TargetTypes.SUBSCRIPTION,
            target_id=subscription_id
        )

    def __create_fairness_monitor(self, datamart_id, subscription_id, configuration, project_id=None, space_id=None):

        target = self.__get_target_obj(subscription_id)
        parameters = get(configuration, "parameters")
        thresholds = get(configuration, "thresholds")

        monitor_instance_details = self.create(
            data_mart_id=datamart_id,
            monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID,
            target=target,
            parameters=parameters,
            thresholds=thresholds,
            project_id=project_id,
            space_id=space_id).result

        return monitor_instance_details.metadata.id

    def __create_explain_monitor(self, datamart_id, subscription_id, explain_statistics, explain_queue_table, explain_results_table, data_sources, configuration_archive,
                                 project_id=None, space_id=None):

        # Upload explainability tar
        archive_file = "explainability.tar.gz"
        with tarfile.open(configuration_archive, 'r:gz') as tar:
            if "explainability.tar.gz" not in tar.getnames() and "explainability_perturbations.tar.gz" in tar.getnames():
                archive_file = "explainability_perturbations.tar.gz"

            tar_file = tar.extractfile(archive_file)
            with open(archive_file, 'wb') as outfile:
                outfile.write(tar_file.read())

        with open(archive_file, mode="rb") as explainability_tar:
            self._ai_client.monitor_instances.upload_explainability_archive(
                subscription_id=subscription_id, archive=explainability_tar, project_id=project_id, space_id=space_id)

        explain_integrated_system_id = get(
            data_sources[0], "connection.integrated_system_id")
        source_type = get(data_sources[0], "connection.type")

        parameters = {}
        if "parameters" in explain_queue_table:
            parameters = get(explain_queue_table, "parameters", {})

        explain_queue_table['parameters'] = parameters
        explain_queue_data_source = self.__get_data_source(
            explain_queue_table, explain_integrated_system_id, "explain_queue", source_type)

        additional_perturbation_param = {
            "perturbations_file": archive_file}
        explain_result_data_source = self.__get_data_source(
            explain_results_table, explain_integrated_system_id, "explain_result", source_type, additional_params=additional_perturbation_param)
        # Patch subscription with additional source
        data_source_patch_document = [
            JsonPatchOperation(
                op=OperationTypes.ADD, path="/data_sources/-", value=explain_queue_data_source),
            JsonPatchOperation(
                op=OperationTypes.ADD, path="/data_sources/-", value=explain_result_data_source)
        ]
        self._ai_client.subscriptions.update(
            subscription_id=subscription_id, patch_document=data_source_patch_document)

        target = self.__get_target_obj(subscription_id)
        parameters = {}
        if explain_statistics:
            parameters["training_statistics"] = explain_statistics

        explainability_parameters = self.__get_explainability_parameters(
            archive_file)
        if explainability_parameters:
            parameters.update(explainability_parameters)

        monitor_instance_details = self.create(
            data_mart_id=datamart_id,
            monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID,
            target=target,
            parameters=parameters,
            project_id=project_id,
            space_id=space_id
        ).result

        return monitor_instance_details.metadata.id

    def __get_explainability_parameters(self, explain_archive):
        explain_params = None

        with tarfile.open(explain_archive, "r:gz") as tar:
            if "configuration.json" in tar.getnames():
                json_content = tar.extractfile("configuration.json")
                data = json_content.read().decode()
                explain_params = json.loads(data).get("parameters")

        return explain_params

    def __create_quality_monitor(self, datamart_id, subscription_id, project_id=None, space_id=None):

        target = self.__get_target_obj(subscription_id)
        parameters = {
            "min_feedback_data_size": 100
        }
        thresholds = [{
            "metric_id": "area_under_roc",
            "type": "lower_limit",
            "value": 0.8
        }]
        monitor_instance_details = self.create(
            data_mart_id=datamart_id,
            monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.QUALITY.ID,
            target=target,
            parameters=parameters,
            thresholds=thresholds,
            project_id=project_id,
            space_id=space_id).result

        return monitor_instance_details.metadata.id

    def __create_drift_monitor(self, datamart_id, subscription_id, configuration_archive, common_configuration, drifted_transaction_table, data_sources,
                               project_id=None, space_id=None):

        drift_integrated_system_id = get(
            data_sources[0], "connection.integrated_system_id")
        source_type = get(data_sources[0], "connection.type")

        drift_data_source = self.__get_data_source(
            drifted_transaction_table, drift_integrated_system_id, "drift", source_type)
        data_source_patch_document = [
            JsonPatchOperation(op=OperationTypes.ADD,
                               path="/data_sources/-", value=drift_data_source)
        ]
        self._ai_client.subscriptions.update(
            subscription_id=subscription_id, patch_document=data_source_patch_document)

        # Enable the monitor
        target = self.__get_target_obj(subscription_id)
        parameters = {
            # "min_samples": 1000,
            "min_samples": 200,
            "drift_threshold": 0.05,
            "train_drift_model": False
        }

        drift_monitor_details = self.create(
            data_mart_id=datamart_id,
            monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.DRIFT.ID,
            target=target,
            # parameters=get(common_configuration,"drift_parameters",{})
            parameters=parameters,
            project_id=project_id,
            space_id=space_id
        ).result

        return drift_monitor_details.metadata.id

    def __create_drift_v2_monitor(self, datamart_id, subscription_id):
        """
        Enable the drift v2 monitor instance

        Args:
            datamart_id (str): Datamart ID
            subscription_id (str): Subscription ID

        Returns:
            str: Monitor instance id
        """

        target = self.__get_target_obj(subscription_id)
        parameters = {
            "train_archive": False,
            "min_samples": 200
        }
        monitor_instance_details = self.create(
            data_mart_id=datamart_id,
            monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.DRIFT_V2.ID,
            target=target,
            parameters=parameters).result

        return monitor_instance_details.metadata.id

    def __get_data_source(self, table_info, integrated_system_id, table_type, source_type, additional_params=None):

        auto_create = get(table_info, "data.auto_create", False)
        status = DataSourceStatus(state="new")

        parameters = None
        if "parameters" in table_info:
            parameters = get(table_info, "parameters")
        if additional_params is not None:
            if parameters is None:
                parameters = {}
            parameters.update(additional_params)

        data_source = DataSource(
            type=table_type,
            database_name=get(table_info, "data.database"),
            schema_name=get(table_info, "data.database") if source_type == IntegratedSystemsListEnums.Type.HIVE.value else get(
                table_info, "data.schema"),
            table_name=get(table_info, "data.table"),
            auto_create=auto_create,
            status=status,
            connection=DataSourceConnection(
                type=source_type,
                integrated_system_id=integrated_system_id
            ),
            parameters=parameters
        )
        return data_source.to_dict()

    def __create_db2_hive_integrated_system(self, subscription_name, table_info, project_id=None, space_id=None):
        connection_type = get(table_info, "type")
        hive_db2_connection = get(table_info, "connection")
        hive_db2_credentials = get(table_info, "credentials")
        if hive_db2_credentials is None:
            hive_db2_credentials = {}
        if connection_type == IntegratedSystemsListEnums.Type.HIVE.value:
            hive_db2_connection["location_type"] = "metastore"
        elif connection_type == IntegratedSystemsListEnums.Type.JDBC.value:
            hive_db2_connection["location_type"] = IntegratedSystemsListEnums.Type.JDBC.value
            hive_db2_credentials["jdbc_url"] = get(
                table_info, "connection.jdbc_url")
        hive_db2_connection_details = IntegratedSystems(self._ai_client).add(
            name=subscription_name + " - DB Info",
            description="",
            type=connection_type,
            credentials=hive_db2_credentials,
            connection=hive_db2_connection,
            project_id=project_id,
            space_id=space_id
        ).result
        hive_db2_connection_id = hive_db2_connection_details.metadata.id
        print("Hive/Db2 Integrated system {} created".format(hive_db2_connection_id))
        return hive_db2_connection_id

    def __delete_integrated_sytems(self, ids):
        print("Cleaning up integration systems")
        for id in ids:
            if id is not None:
                print("Deleting {}".format(id))
                IntegratedSystems(self._ai_client).delete(id)

    def __validate_fairness_params(self, params):
        features = get(params, "features")
        supported_metrics = [
            metric_name.value for metric_name in FairnessMetrics]
        un_supported_metrics = []
        for feature in features:
            metric_ids = get(feature, "metric_ids")
            if metric_ids is not None:
                for metric_id in metric_ids:
                    if metric_id not in supported_metrics:
                        if metric_id not in un_supported_metrics:
                            un_supported_metrics.append(metric_id)

        if len(un_supported_metrics) > 0:
            raise Exception("Metric ids {} are invalid. Please use the FairnessMetrics enum class for the correct metric ids".format(
                un_supported_metrics))

    def list_measurements(self,
                          monitor_instance_id: str,
                          start: datetime,
                          end: datetime,
                          project_id: str = None,
                          space_id: str = None,
                          run_id: str = None,
                          filter: str = None,
                          limit: int = None,
                          offset: int = None,
                          **kwargs):
        """
                Listing the measurements for particular start and end time or run_id.

                :param str monitor_instance_id: Unique monitor instance ID.
                :param datetime start: Beginning of the time range.
                :param datetime end: End of the time range.
                :param str project_id: (optional) The GUID of the project.
                :param str space_id: (optional) The GUID of the space.
                :param str run_id: (optional) Comma delimited list of measurement run_id.
                :param str filter: (optional) Filter expression can consist of any metric
                       tag or a common column of a string type followed by filter name and
                       optionally a value, all delimited by colon. Supported filters are: `in`,
                       `eq`, `null` and `exists`. Sample filters are:
                       `filter=region:in:[us,pl],segment:eq:sales` or
                       `filter=region:null,segment:exists`.
                :param int limit: (optional) Maximum number of measurements returned.
                :param int offset: (optional) Offset of measurements returned.
                :param dict headers: A `dict` containing the request headers
                :return: A `DetailedResponse` containing the result, headers and HTTP status code.
                :rtype: DetailedResponse with `MonitorMeasurementResponseCollection` result
        """
        metrics_response = self.measurements.list(monitor_instance_id=monitor_instance_id,
                                                  start=start,
                                                  end=end,
                                                  project_id=project_id,
                                                  space_id=space_id,
                                                  run_id=run_id,
                                                  filter=filter,
                                                  limit=limit,
                                                  offset=offset,
                                                  **kwargs)
        return metrics_response

    # Adding below function to modify schedule duration for any monitors.
    def modify_schedule(self, monitor_instance_id: str, repeat_interval: int, repeat_type: str):
        """
               Update monitor schedule.

               :param str monitor_instance_id: Unique monitor instance ID.
               :param int repeat_interval: Duration for an interval.
               :param str repeat_type: Duration type for interval ['minute', 'hour', 'day', 'week', 'month', 'year'].

        """
        payload = [
            {
                "op": "replace",
                "path": "/schedule",
                "value": {
                    "repeat_interval": repeat_interval,
                    # ['minute', 'hour', 'day', 'week', 'month', 'year'],
                    "repeat_type": repeat_type
                }
            }
        ]
        return self.update(monitor_instance_id=monitor_instance_id, patch_document=payload, update_metadata_only=True)
