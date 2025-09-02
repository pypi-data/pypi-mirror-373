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

from ibm_watson_openscale.utils.client_errors import AuthorizationError
import requests, datetime

class UsageClient:
    def __init__(self, wos_client):
        self.wos_client = wos_client

    def check_plan_usage_and_get_limit(self, is_paid_plan = False, is_llm = False):
        """
        Check if user is within the usage limit
        Raises:
            Exception: Raises exception if user is not within the usage limit
        """

        usage_service_url = "{0}/v2/usage".format(self.wos_client.service_url)

        token = self.wos_client.authenticator.token_manager.get_token()
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }

        limit = 1000
        response = requests.get(usage_service_url, headers=iam_headers)
        if response.ok:
            resources_resp = response.json().get("resources")
            for resource in resources_resp:
                if resource["name"] == "total_evaluations":
                    if all(element in resource.keys() for element in ["name", "usage", "limit"]):
                        if resource["usage"] >= resource["limit"]:
                            raise AuthorizationError(
                                "The number of allowed evaluations for the current plan are exhausted for the user account. Please upgrade the plan to continue.")
                if is_paid_plan and is_llm:
                    if resource["name"] == "llm_evaluation_records":
                        limit = resource["limit"]
                else:
                    if resource["name"] == "evaluation_records":
                        limit = resource["limit"]
        return limit


    def update_plan_usage(self, amount = 1):
        """
        Updates wos plan usage
        Arguments:
            wos_client : watson openscale client
        """
        usage_service_url = "{0}/v2/usage/total_evaluations".format(
            self.wos_client.service_url)

        token = self.wos_client.authenticator.token_manager.get_token()
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }

        current_time = datetime.datetime.now()
        payload = {
            "amount": amount,
            "timestamp": str(current_time),
            "type": "relative"
        }

        response = requests.post(
            url=usage_service_url, json=payload, headers=iam_headers)

        if not response.ok:
            print("Usage limit not updated")