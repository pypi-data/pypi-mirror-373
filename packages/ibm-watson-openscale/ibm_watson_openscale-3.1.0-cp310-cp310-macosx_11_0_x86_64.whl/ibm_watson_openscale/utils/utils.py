# coding: utf-8

# Copyright 2020, 2024 IBM All Rights Reserved.
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
import os
import sys
import time
import datetime
from typing import TYPE_CHECKING, Callable, List, Union

import pandas as pd
import pkg_resources
import requests
from ibm_cloud_sdk_core.api_exception import *
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.utils.client_errors import (ApiRequestFailure,
                                                      AuthorizationError,
                                                      ClientError,
                                                      IncorrectValue,
                                                      MissingValue,
                                                      UnexpectedType,
                                                      MultipleValuesExistError)
from ibm_watson_openscale.utils.constants import RESOURCES_URL_MAPPING

if TYPE_CHECKING:
    from ibm_watson_openscale.subscriptions import Subscriptions


def validate_type(el, el_name, expected_type, mandatory=True, subclass=False):
    if el_name is None:
        raise MissingValue(u'el_name')

    if type(el_name) is not str:
        raise UnexpectedType(u'el_name', str, type(el_name))

    if expected_type is None:
        raise MissingValue(u'expected_type')

    if type(expected_type) is not type and type(expected_type) is not list:
        raise UnexpectedType(
            'expected_type', 'type or list', type(expected_type))

    if type(mandatory) is not bool:
        raise UnexpectedType(u'mandatory', bool, type(mandatory))

    if type(subclass) is not bool:
        raise UnexpectedType(u'subclass', bool, type(subclass))

    if mandatory and el is None:
        raise MissingValue(el_name)
    elif el is None:
        return

    validation_func = isinstance

    if subclass is True:
        def validation_func(x, y): return issubclass(x.__class__, y)

    if type(expected_type) is list:
        try:
            next((x for x in expected_type if validation_func(el, x)))
            return True
        except StopIteration:
            return False
    else:
        if not validation_func(el, expected_type):
            raise UnexpectedType(el_name, expected_type, type(el))


def validate_enum(el, el_name, enum_class, mandatory=True):
    if mandatory and el is None:
        raise MissingValue(el_name)
    elif el is None:
        return

    validate_type(el, el_name, str, mandatory)

    acceptable_values = [enum.value for enum in enum_class]

    if el is not None and el not in acceptable_values:
        reason = "Expected one of '" + \
            ", ".join(acceptable_values) + "', Found: '" + el + "'."
        raise IncorrectValue(value_name=el_name, reason=reason)


def is_ipython():
    # checks if the code is run in the notebook
    try:
        get_ipython
        return True
    except Exception:
        return False


def get_instance_guid(authenticator, is_cp4d: bool = False, service_url: str = None):
    import json

    import requests

    instance_guid = None

    if is_cp4d:
        instance_guid = "00000000-0000-0000-0000-000000000000"
    else:
        token = authenticator.token_manager.get_token() if isinstance(
            authenticator, IAMAuthenticator) else authenticator.bearer_token
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }
        clean_service_url = service_url.rstrip("/")
        if clean_service_url not in RESOURCES_URL_MAPPING:
            raise KeyError(
                f"Unsupported service_url: '{service_url}'. "
                f"Expected one of: {list(RESOURCES_URL_MAPPING.keys())}"
            )

        resources_url = RESOURCES_URL_MAPPING[clean_service_url]

        resources_response = requests.get(resources_url, headers=iam_headers)

        if resources_response.status_code == 401:
            raise AuthorizationError("Expired token provided.")

        # Go through all the pages until next_url is null
        resources = json.loads(resources_response.text)["resources"]
        next_url = json.loads(resources_response.text)['next_url']
        reached_end = False
        while not reached_end:
            if next_url == None:
                reached_end = True
                break
            resources_response = requests.get(
                "https://resource-controller.cloud.ibm.com" + next_url, headers=iam_headers)
            resources.extend(json.loads(resources_response.text)['resources'])
            next_url = json.loads(resources_response.text).get("next_url")

        for resource in resources:
            # Resource ID is fixed for any service on public cloud
            # checking with OpenScale's resource ID
            if resource["resource_id"] == "2ad019f3-0fd6-4c25-966d-f3952481a870":
                if instance_guid is not None:
                   raise MultipleValuesExistError("Multiple service instance id exists. Provide the instance id with which you want to work with.")
                instance_guid = resource["guid"]

    if instance_guid is None:
        raise MissingValue(instance_guid, reason='Instance ID not found')

    if instance_guid is None:
        raise MissingValue(value_name='instance_guid', reason='Instance ID not found')

    return instance_guid


def check_if_cp4d(service_url: str,verify: bool = True):
    """
    Returns True if the URL provided belongs to a CP4D environment.
    :service_url: The service URL for Watson OpenScale.
    """
    is_cp4d = None

    # Calling the fairness heartbeat API to check for environment details
    url = "{}/v2/fairness/heartbeat".format(service_url)

    payload = {}
    headers = {
        "Accept": "application/json"
    }

    response = requests.request(
        "GET", url, headers=headers, data=payload, verify=verify)

    if response.status_code == 404:
        # This means that the V2 changes are not yet available and this can happen only in CP4D environments
        # Hence, marking is_cp4d as True
        is_cp4d = True
    else:
        if response.ok is False:
            # Heartbeat call failed
            raise ClientError("Heartbeat call to check for environment details failed with status code {}. Error: {}".format(
                response.status_code, response.text))
        else:
            response_json = json.loads(response.text)
            is_cp4d = not response_json["is_cloud"] if "is_cloud" in response_json else False

    return is_cp4d


def get_asset_property(subscription: 'Subscriptions' = None, asset_property: str = None):
    validate_type(asset_property, 'asset_property', str, True)
    validate_type(subscription, 'subscription', Subscriptions, True)
    asset_properties = subscription.get()['entity']['asset_properties']

    if asset_property in asset_properties:
        return asset_properties[asset_property]
    else:
        return None


def decode_hdf5(encoded_val):
    import base64
    import os
    import uuid

    import h5py

    filename = 'tmp_payload_' + str(uuid.uuid4()) + '.hdf5'

    try:
        with open(filename, 'wb') as f:
            f.write(base64.decodebytes(bytes(encoded_val, 'utf-8')))

        with h5py.File(filename, 'r') as content:
            return content['data'].value.tolist()
    finally:
        try:
            os.remove(filename)
        except:
            pass


def validate_asset_properties(asset_properties, properties_list):
    keys = asset_properties.keys()

    for prop in properties_list:

        # TODO remove hooks for duplicated fields or different names when API is cleaned up
        if type(prop) is list:
            if not any([True for item in prop if item in keys]):
                if 'predicted_target_field' in prop or 'prediction_field' in prop:
                    raise MissingValue('prediction_column',
                                       reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
                elif 'class_probability_fields' in prop or 'prediction_probability_field' in prop or 'probability_fields' in prop:
                    raise MissingValue('class_probability_columns or probability_column',
                                       reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
                else:
                    raise MissingValue(''.join(prop),
                                       reason='Subscription is missing one of listed asset properties. Missing parameter can be specified using subscription.update() method.')
        else:
            if prop not in keys:
                if prop == 'predicted_target_field' or prop == 'prediction_field':
                    raise MissingValue('prediction_column',
                                       reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
                elif prop == 'feature_fields' or prop == 'categorical_fields':
                    raise MissingValue(prop.replace('fields', 'columns'),
                                       reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
                elif prop == 'output_data_schema':
                    raise MissingValue(prop,
                                       reason='Payload should be logged first to have output_data_schema populated.')
                else:
                    raise MissingValue(prop,
                                       reason='Subscription is missing required asset property. Missing parameter can be specified using subscription.update() method.')
            elif prop == 'output_data_schema':
                output_data_schema = asset_properties['output_data_schema']

                if 'probability_fields' in keys and "'modeling_role': 'probability'" not in str(output_data_schema):
                    raise MissingValue(prop,
                                       reason='Column `{}` cannot be found in output_data_schema. Check if this column name is valid. Make sure that payload has been logged to populate schema.'.format(
                                           asset_properties['probability_fields']))
                elif 'prediction_field' in keys and "'modeling_role': 'prediction'" not in str(output_data_schema):
                    raise MissingValue(prop,
                                       reason='Column `{}` cannot be found in output_data_schema. Check if this column name is valid. Make sure that payload has been logged to populate schema.'.format(
                                           asset_properties['prediction_field']))


def print_text_header_h1(title: str) -> None:
    print(u'\n\n' + (u'=' * (len(title) + 2)) + u'\n')
    print(' ' + title + ' ')
    print(u'\n' + (u'=' * (len(title) + 2)) + u'\n\n')


def print_text_header_h2(title: str) -> None:
    print(u'\n\n' + (u'-' * (len(title) + 2)))
    print(' ' + title + ' ')
    print((u'-' * (len(title) + 2)) + u'\n\n')


def print_synchronous_run(title: str, check_state: Callable, run_states: List[str] = None,
                          success_states: List[str] = None,
                          failure_states: List[str] = None, delay: int = 5,
                          get_result: Callable = None,
                          **kwargs) -> Union[None, dict]:
    if success_states is None:
        success_states = [StatusStateType.SUCCESS, StatusStateType.FINISHED, StatusStateType.COMPLETED,
                          StatusStateType.ACTIVE]
    if failure_states is None:
        failure_states = [StatusStateType.FAILURE, StatusStateType.FAILED, StatusStateType.ERROR,
                          StatusStateType.CANCELLED, StatusStateType.CANCELED]

    if get_result is None:
        def tmp_get_result():
            if state in success_states:
                return 'Successfully finished.', None, None
            else:
                return 'Error occurred.', None, None

        get_result = tmp_get_result

    print_text_header_h1(title)

    state = None
    start_time = time.time()
    elapsed_time = 0
    timeout = kwargs.get("timeout", 300)


    while (run_states is not None and state in run_states) or (
            state not in success_states and state not in failure_states):
        time.sleep(delay)

        last_state = state
        state = check_state()

        if state is not None and state != last_state:
            print('\n' + state, end='')
        elif last_state is not None:
            print('.', end='')

        elapsed_time = time.time() - start_time

        if elapsed_time > timeout:
            break

    if elapsed_time > timeout:
        result_title, msg, result = 'Run timed out', 'The run didn\'t finish within {}s.'.format(
            timeout), None
    else:
        result_title, msg, result = get_result()

    print_text_header_h2(result_title)

    if msg is not None:
        print(msg)

    return result


def version():
    try:
        version = pkg_resources.get_distribution(
            "ibm-watson-openscale").version
    except pkg_resources.DistributionNotFound:
        version = u'0.0.1-local'

    return version


def install_package(package, version=None):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import subprocess

        if version is None:
            package_name = package
        else:
            package_name = "{}=={}".format(package, version)

        subprocess.call([sys.executable, '-m', 'pip', 'install', package_name])


def check_package_exists(package: str = "ibm_metrics_plugin"):
    """Checks if a package by the given name exists.

    :param package: The package name, defaults to "ibm_metrics_plugin"
    :type package: str, optional
    :raises Exception: If the package does not exist
    """
    import importlib
    try:
        importlib.import_module(package)
    except ImportError as ie:
        raise Exception(
            f"The '{package}' library is required for this operation. Please install it and retry.") from ie


def install_package_from_pypi(name, version=None, test_pypi=False):
    from setuptools.command import easy_install

    if version is None:
        package_name = name
    else:
        package_name = "{}=={}".format(name, version)

    if test_pypi:
        index_part = ["--index-url", "https://test.pypi.org/simple/"]
    else:
        index_part = ["--index-url", "https://pypi.python.org/simple/"]

    easy_install.main(index_part + [package_name])

    import importlib
    globals()[name] = importlib.import_module(name)


def validate_pandas_dataframe(el, el_name, mandatory):
    import pandas as pd
    if el_name is None:
        raise MissingValue(u'el_name')

    if mandatory:
        if el is None:
            raise MissingValue(el_name)
        elif not isinstance(el, pd.DataFrame):
            raise UnexpectedType(el_name, pd.DataFrame, type(el))
        elif el.empty:
            raise ValueError(f"{el_name} is empty.")

    elif el is None:
        return


def validate_columns_in_dataframe(el: pd.DataFrame, el_name, columns: List[str]):
    missing_columns = [col for col in columns if col not in el]

    if len(missing_columns):
        missing_columns = ", ".join(missing_columns)
        name = el_name or "data frame"
        raise MissingValue(f"{missing_columns} in {name}")

def replace_nulls_in_columns(el: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Replace null values in the specified columns of a DataFrame with an empty string (or any placeholder value).

    Args:
        el (pd.DataFrame): The DataFrame to process.
        columns (List[str]): A list of columns where null values should be ignored.

    Returns:
        pd.DataFrame: A DataFrame with null values in specified columns replaced with a placeholder.
    """
    if el is None or el.empty:
        return pd.DataFrame() 
    
    # Validation for column list 
    if not columns:
        return el
    
    # Replace null values in specified columns with an empty string (or another placeholder if needed)
    el[columns] = el[columns].fillna('')
    return el

def print_text_header_h1(title):
    print(u'\n\n' + (u'=' * (len(title) + 2)) + u'\n')
    print(' ' + title + ' ')
    print(u'\n' + (u'=' * (len(title) + 2)) + u'\n\n')


def print_text_header_h2(title):
    print(u'\n\n' + (u'-' * (len(title) + 2)))
    print(' ' + title + ' ')
    print((u'-' * (len(title) + 2)) + u'\n\n')


def handle_response(expected_status_code, operationName, response, json_response=True):
    if response.status_code == expected_status_code:
        # print(u'Successfully finished {} for url: \'{}\''.format(operationName, response.url))
        # print(u'Response({} {}): {}'.format(response.request.method, response.url, response.text))
        if json_response:
            try:
                return response.json()
            except Exception as e:
                raise ClientError(
                    u'Failure during parsing json response: \'{}\''.format(response.text), e)
        else:
            return response.text
    elif response.status_code == 409:
        raise ApiRequestFailure(
            u'Warning during {}.'.format(operationName), response)
    else:
        raise ApiRequestFailure(
            u'Failure during {}.'.format(operationName), response)


def get(obj: dict, path, default=None):
    """Gets the deep nested value from a dictionary

    Arguments:
        obj {dict} -- Dictionary to retrieve the value from
        path {list|str} -- List or . delimited string of path describing path.

    Keyword Arguments:
        default {mixed} -- default value to return if path does not exist (default: {None})

    Returns:
        mixed -- Value of obj at path
    """
    if isinstance(path, str):
        path = path.split(".")

    new_obj = {
        **obj
    }
    for key in path:
        if not new_obj:
            # for cases where key has null/none value
            return default

        if key in new_obj.keys():
            new_obj = new_obj.get(key)
        else:
            return default
    return new_obj


def convert_directory_to_dataframe(dir_path, **kwargs):
    """
    This method will convert the image directory to a pandas.DataFrame

    Args:
        dir_path (str): Root path of the images.

    Returns:
        pd.DataFrame: Pandas DataFrame containing the image path and labels.
    """
    import pandas as pd

    # Check whether the image directory is valid or not
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path) or not os.listdir(dir_path):
        raise Exception(f"Image path {dir_path} is not valid.")

    image_path_column = kwargs.get("image_path_column") or "image_path_column"
    label_column = kwargs.get("label_column") or "label"
    output_df = pd.DataFrame(columns=[image_path_column, label_column])

    labels = [label for label in os.listdir(
        dir_path) if os.path.isdir(os.path.join(dir_path, label))]
    for label in labels:
        label_path = os.path.join(dir_path, label)

        # Get a list of image files in the subdirectory
        image_files = [f for f in os.listdir(label_path) if os.path.isfile(
            os.path.join(label_path, f))]

        # Raise exception if the image files are empty in the sub directory
        if not image_files:
            raise Exception(
                f"The {label_path} is empty. Please verify whether there are any images present.")

        # Iterate through each image file in the subdirectory
        for image_file in image_files:
            image_path = os.path.join(label_path, image_file)
            output_df = pd.concat([output_df, pd.DataFrame(
                [{image_path_column: image_path, label_column: label}])], ignore_index=True, axis=0)

    return output_df


def validate_image_path(train_data, **kwargs):
    """
    Iterate through the dataframe image_path_column and check any invalid path available.

    Args:
        tr  ain_data (pandas.DataFrame): Dataframe containing the image path column

    Raises:
        Exception: Raises exception if image/path is not valid
    """
    image_path_column = kwargs.get(
        "image_path_column") or "image_path_column"
    for _, row in train_data.iterrows():
        img_path = row[image_path_column]
        if not os.path.exists(img_path):
            raise Exception(f"Image path {img_path} is not valid.")


def create_download_link(path: str, title: str):
    check_package_exists("IPython")
    data = None
    import base64
    with open(path, "rb") as f:
        # read configuration archive from local
        data = f.read()

    format_args = {
        "payload": base64.b64encode(data).decode(),
        "title": title,
        "filename": path
    }

    from IPython.display import HTML, display
    html = '<a download="{filename}" href="data:text/json;base64,{payload}" target="_blank">{title}</a>'
    return display(HTML(html.format(**format_args)))


