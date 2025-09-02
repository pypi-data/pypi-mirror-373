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


from typing import TYPE_CHECKING, List

from ibm_watson_openscale.supporting_classes.enums import StatusStateType

try:
    from ibm_metrics_plugin.common.utils.python_utils import get
except ImportError:
    pass

if TYPE_CHECKING:
    from ibm_watson_openscale.client import WatsonOpenScaleV2Adapter


class DriftV2MonitorInstance:

    BASELINE_MAX_SAMPLES = 100
    RUNTIME_MIN_SAMPLES = 10

    def __init__(self, client: "WatsonOpenScaleV2Adapter",
                 subscription_id: str,
                 project_id: str = None, space_id: str = None) -> None:
        """
        Initialize the monitor instance object

        Args:
            client (WatsonOpenScaleV2Adapter): The watson openscale client
            subscription_id (str): The subscription id
            project_id (str, optional): The project id. Defaults to None.
            space_id (str, optional): The space id. Defaults to None.
        """
        self.client = client
        self.subscription_id = subscription_id
        self.project_id = project_id
        self.space_id = space_id

        self.entity = None
        self.id = None

        self.__initialize()

    def __initialize(self):
        monitor_instances = self.client.monitor_instances.list(target_target_id=self.subscription_id,
                                                               target_target_type="subscription",
                                                               monitor_definition_id="drift_v2",
                                                               project_id=self.project_id,
                                                               space_id=self.space_id
                                                               ).result.monitor_instances
        if len(monitor_instances):
            self.entity = monitor_instances[0].entity.to_dict()
            self.id = monitor_instances[0].metadata.id

    @property
    def baseline_max_samples(self) -> int:
        """
        Returns baseline max samples, as specified in the monitor instance.
        If not found, defaults to `~DriftV2MonitorInstance.BASELINE_MAX_SAMPLES`

        Returns:
            int: The baseline max samples
        """
        result = get(self.entity, "parameters.baseline_max_samples")
        if result is None:
            result = self.BASELINE_MAX_SAMPLES
        return result

    @property
    def runtime_min_samples(self) -> int:
        """
        Returns min samples for runtime evaluation, as specified in the monitor instance.
        If not found, defaults to `~DriftV2MonitorInstance.RUNTIME_MIN_SAMPLES`

        Returns:
            int: The runtime min samples
        """
        result = get(self.entity, "parameters.min_samples")
        if result is None:
            result = self.RUNTIME_MIN_SAMPLES
        return result

    @property
    def runtime_max_samples(self) -> int:
        """
        Returns max samples for runtime evaluation, as specified in the monitor instance.

        Returns:
            int: The runtime max samples
        """
        return get(self.entity, "parameters.max_samples")

    @property
    def is_configured(self) -> bool:
        """
        Returns if the monitor instance has already been configured or not

        Returns:
            bool: True, if configured else, False
        """
        return (self.id is not None) and (self.entity is not None)

    @property
    def thresholds(self) -> List | None:
        """
        Returns the monitor instance thresholds

        Returns:
            List | None: The monitor instance thresholds
        """
        return get(self.entity, "thresholds")

    @property
    def status_state(self) -> str:
        """
        Returns the monitor instance state

        Returns:
            str: The monitor instance state
        """
        return get(self.entity, "status.state")

    @property
    def is_error_state(self) -> bool:
        """
        Returns true if monitor is in error state, false otherwise

        Returns:
            bool: true if monitor is in error state, false otherwise
        """
        return self.status_state == StatusStateType.ERROR

    @property
    def advanced_controls(self) -> dict:
        return get(self.entity, "parameters.advanced_controls")
