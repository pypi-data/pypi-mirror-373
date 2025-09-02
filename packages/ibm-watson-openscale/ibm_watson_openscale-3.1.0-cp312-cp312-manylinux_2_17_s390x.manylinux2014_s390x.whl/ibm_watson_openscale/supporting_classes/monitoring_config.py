# coding: utf-8

# Copyright 2021 IBM All Rights Reserved.
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

from ibm_watson_openscale.supporting_classes.feature import Feature


class MonitoringConfig:
    def __init__(self, monitor_name, min_records):
        self.monitor_name = monitor_name
        self.min_records = min_records

    def get(self):
        pass


class QualityMonitoringConfig(MonitoringConfig):

    def __init__(self, threshold=None, min_records=100, max_records=None, config_dict=None):
        MonitoringConfig.__init__(self, "Quality", min_records)
        self.threshold = threshold
        self.max_records = max_records
        if config_dict is not None:
            self.load(config_dict)

    def get(self):
        return json.dumps({k: self.__dict__[k] for k in ["min_records", "max_records", "threshold"]},
                          default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def load(self, config):
        self.min_records = config["min_records"]
        self.max_records = config["max_records"]
        self.threshold = config["threshold"]


class DriftMonitoringConfig(MonitoringConfig):

    def __init__(self, threshold=0.1, min_records=100, model_path=None, config_dict=None):
        MonitoringConfig.__init__(self, "Drift", min_records)
        self.threshold = threshold
        self.model_path = model_path
        self.max_records = None
        self.enable_model_drift = True
        self.enable_data_drift = True
        if config_dict is not None:
            self.load(config_dict)

    def get(self):
        return json.dumps(
            {k: self.__dict__[k] for k in ["min_records", "threshold", "model_path", "model_path", "enable_model_drift","enable_data_drift"]},
            default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def load(self, config):
        self.min_records = config["min_records"]
        if "threshold" in config:
            self.threshold = config["threshold"]
        if "model_path" in config:
            self.model_path = config["model_path"]
        if "max_records" in config:
            self.max_records = config["max_records"]
        if "enable_model_drift" in config:
            self.enable_model_drift = config["enable_model_drift"]
        if "enable_data_drift" in config:
            self.enable_data_drift = config["enable_data_drift"]


class FairnessMonitoringConfig(MonitoringConfig):

    def __init__(self, threshold=None, min_records=100, features=None, favorable_classes=None, unfavorable_classes=None, config_dict=None):
        MonitoringConfig.__init__(self, "Fairness", min_records)
        self.threshold = threshold
        self.features = features
        self.favorable_classes = favorable_classes
        self.unfavorable_classes = unfavorable_classes
        self.max_records = None
        if config_dict is not None:
            self.load(config_dict)

    def get(self):
        return json.dumps(
            {k: self.__dict__[k] for k in ["min_records", "features", "unfavorable_classes", "favorable_classes", "max_records", "threshold"]},
            default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def load(self, config):
        self.favorable_classes = config["favorable_classes"]
        self.unfavorable_classes = config["unfavorable_classes"]
        self.min_records = config["min_records"]
        if "max_records" in config:
            self.max_records = config["max_records"]
        if "threshold" in config:
            self.threshold = config["threshold"]
        self.features = []
        for mf in config["features"]:
            self.features.append(
                Feature(name=mf["name"], majority=mf["majority"], minority=mf["minority"], threshold=mf["threshold"]))


class DriftV2MonitoringConfig(MonitoringConfig):
    def __init__(self, min_records=100, config_dict=None):
        MonitoringConfig.__init__(self, "Drift_v2", min_records)
        self.max_records = None
        self.fields = None
        self.importance = None
        self.train_archive = False
        self.thresholds = None
        if config_dict is not None:
            self.load(config_dict)

    def get(self):
        return json.dumps(
            {k: self.__dict__[k] for k in
             ["min_records", "max_records", "train_archive", "fields", "importance", "thresholds"]},
            default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def load(self, config):
        self.min_records = config["min_records"]
        self.fields = config["fields"]
        self.importance = config["importance"]
        if "max_records" in config:
            self.max_records = config["max_records"]
        if "train_archive" in config:
            self.train_archive = config["train_archive"]
        if "thresholds" in config:
            self.thresholds = config["thresholds"]


class ConfigSummary:

    def __init__(self, *configs: MonitoringConfig):
        self.fairness = None
        self.drift = None
        self.quality = None
        self.drift_v2 = None
        self._set_individual_configs(*configs)

    def _set_individual_configs(self, *configs: MonitoringConfig):

        for config in configs:
            if config is not None:
                if config.monitor_name == "Fairness":
                    self.fairness = config
                elif config.monitor_name == "Drift":
                    self.drift = config
                elif config.monitor_name == "Quality":
                    self.quality = config
                elif config.monitor_name == "Drift_v2":
                    self.drift_v2 = config

    def get(self):
        return json.dumps({k: self.__dict__[k] for k in self.__dict__.keys()}, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
