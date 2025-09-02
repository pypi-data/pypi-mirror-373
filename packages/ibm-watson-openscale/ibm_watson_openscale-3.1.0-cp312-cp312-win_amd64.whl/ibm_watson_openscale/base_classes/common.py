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

import platform
import uuid

from ibm_watson_openscale.version import __version__

USER_AGENT_HEADER = 'User-Agent'
SDK_NAME = 'watson-openscale-python-sdk'
user_header = {}


def set_header(header):
    global user_header
    user_header = header

def get_system_info():
    """
    Constructs the system properties
    """
    return '{0} {1} {2}'.format(
        platform.system(),  # OS
        platform.release(),  # OS version
        platform.python_version())  # Python version


def get_user_agent():
    """
    Returns the user agent
    """
    return USER_AGENT


USER_AGENT = '{0}-{1} {2}'.format(SDK_NAME, __version__, get_system_info())


def get_sdk_headers(**kwargs):
    """
    Returns a dict of custom headers
    """

    headers = {}
    headers[USER_AGENT_HEADER] = get_user_agent()
    for key in user_header:
        headers[key] = user_header[key]
        
    if len(kwargs['operation_id']):
        headers.setdefault('origin', kwargs['operation_id'])
    headers.setdefault('x-global-transaction-id', str(uuid.uuid4()))

    return headers
