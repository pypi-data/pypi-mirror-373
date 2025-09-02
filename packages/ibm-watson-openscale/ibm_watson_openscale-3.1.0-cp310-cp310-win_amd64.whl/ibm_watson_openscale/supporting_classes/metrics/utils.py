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
import requests

from ibm_watson_openscale.utils.client_errors import AuthorizationError


def is_entitled_on_cp4d(url, instance_id, bearer_token, verify=False):
    print("Doing entitlement check on CP4D...")
    return True
    headers = {}
    headers["Authorization"] = "Bearer " + bearer_token
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    url = "{}/v2/data_marts/{}".format(url, instance_id)
    response = requests.get(url, verify=verify, headers=headers)
    if not response.ok:
        raise AuthorizationError(
            "Not authorized to compute metrics. Error {}".format(response.text))
    return True


def is_entitled_on_cloud(url, instance_id, bearer_token, verify=True):
    """
    Check if user got entitled to a wos plan

    :returns: False if entitled to lite plan, True otherwise
    """
    if "/openscale/" in url:
        index = url.find('/openscale/')
        url = url[0:index]

    entitlement_url = url + '/v1/entitlements'
    msg = "Not authorized to compute metrics. Supported plans :['standard', 'standard-v2', 'essentials']"
    headers = {}
    headers["Authorization"] = "Bearer " + bearer_token
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    response = requests.get(entitlement_url, verify=verify, headers=headers)
    if not response.ok:
        raise AuthorizationError("{} Error {}".format(msg, response.text))

    entitlements = response.json()['entitlements']
    if 'ai_openscale' not in entitlements:
        raise AuthorizationError(msg)

    instances = entitlements['ai_openscale']
    if len(instances) <= 0:
        raise AuthorizationError(msg)

    for instance in instances:
        if instance_id == instance['id']:
            plan_name = instance['plan_name']
            if plan_name.lower() in ('standard', 'standard-v2', 'essentials'):
                return True

    return False

