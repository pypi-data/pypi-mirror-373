# coding: utf-8

# Copyright 2020 IBM All Rights Reserved.
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

"""
File containing constants used throughout the Watson OpenScale Python V2 SDK.
"""

DEFAULT_SERVICE_URL = "https://api.aiopenscale.cloud.ibm.com/openscale"
LITE_PLAN = "lite"

DRIFT_DEPRECATION_MESSAGE = "Drift Monitor has been deprecated in favor of Drift v2. This feature will be remove in a future release of IBM Watson OpenScale."

RESOURCES_URL_MAPPING = {
    # YS1DEV
    "https://aiopenscale-dev.us-south.containers.appdomain.cloud/openscale": "https://resource-controller.test.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale-dev.us-south.containers.appdomain.cloud": "https://resource-controller.test.cloud.ibm.com/v2/resource_instances",
    
    # MCSPDEV
    "https://wgov-mcspdev-cb280cfedc2eb812b74cc2bb9994d3dc-0000.us-south.containers.appdomain.cloud/openscale": "https://resource-controller.test.cloud.ibm.com/v2/resource_instances",
    "https://wgov-mcspdev-cb280cfedc2eb812b74cc2bb9994d3dc-0000.us-south.containers.appdomain.cloud": "https://resource-controller.test.cloud.ibm.com/v2/resource_instances",
    
    # YPQA
    "https://api.aiopenscale.test.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale.test.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale.test.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://api.aiopenscale.test.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    
    # MCSPQA
    "https://api.mcspqa.wxgov.test.saas.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://mcspqa.wxgov.test.saas.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://mcspqa.wxgov.test.saas.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://api.mcspqa.wxgov.test.saas.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    
    # YPCR
    "https://aios-yp-cr.us-south.containers.appdomain.cloud": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aios-yp-cr.us-south.containers.appdomain.cloud/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    
    # YPPROD
    "https://api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    
    # FRPROD
    "https://eu-de.api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-de.api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-de.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-de.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    
    # MCSPSYDPROD
    "https://au-syd.api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://au-syd.api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://au-syd.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://au-syd.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    
    # MCSPTORPROD
    "https://ca-tor.api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://ca-tor.api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://ca-tor.api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://ca-tor.api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    
    # MCSPTOKPROD
    "https://jp-tok.api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://jp-tok.api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://jp-tok.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://jp-tok.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",

    # MCSPLONPROD
    "https://eu-gb.api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-gb.api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-gb.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-gb.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances"
}

# Monitor names
MODEL_HEALTH = "MODEL_HEALTH"

# Operational space
PRODUCTION = "production"
PRE_PRODUCTION = "pre_production"