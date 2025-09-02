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


import uuid
from typing import Iterator, List, Tuple

import pandas as pd

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import \
    PatchDocument
from ibm_watson_openscale.supporting_classes.payload_record import \
    PayloadRecord


def get_payload_record(data: pd.DataFrame, input_columns: List[str], output_columns: List[str], meta_columns: List[str] = []) -> Tuple[PayloadRecord, int]:
    """
    Create a PayloadRecord out of pandas dataframe

    Args:
        data (pd.DataFrame): The input data
        input_columns (List[str]): The input columns that go in request
        output_columns (List[str]): The output columns that go in response
        meta_columns (List[str], optional): The meta columns that go in request.meta. Defaults to [].

    Returns:
        Tuple[PayloadRecord, int]: Tuple of PayloadRecord, and the count of records
    """
    scoring_id = str(uuid.uuid4())
    from ibm_metrics_plugin.common.utils.python_utils import get_python_types
    request = {
        "fields": input_columns,
        "values": get_python_types(data[input_columns].to_dict("split")["data"])
    }
    if len(meta_columns):
        request["meta"] = {
            "fields": meta_columns,
            "values": get_python_types(data[meta_columns].to_dict("split")["data"])
        }

    response = {
        "fields": output_columns,
        "values": get_python_types(data[output_columns].to_dict("split")["data"])
    }

    return PayloadRecord(request=request, response=response, scoring_id=scoring_id), len(data)


def get_patch_operation(data: pd.DataFrame, embeddings_columns: List[str], record_id_column: str) -> Tuple[List, List]:
    """
    Get patch operation payload for storing embeddings

    Args:
        data (pd.DataFrame): The input data
        embeddings_columns (List[str]): The list of columns for embeddings
        record_id_column (str): The record id column

    Returns:
        Tuple[List, List]: The embedding annotation patch payload and the embedding column status patch payload
    """
    annotation_patch_documents = []
    embeddings_status_documents = []
    from ibm_metrics_plugin.common.utils.python_utils import get_python_types

    for _, row in data.iterrows():
        for column in embeddings_columns:
            annotation_patch_document = PatchDocument(op="add",
                                                      path=f"/records/{row[record_id_column]}/annotations/{column}",
                                                      value=get_python_types(row[column]))
            annotation_patch_documents.append(annotation_patch_document)

        embeddings_status_documents.append(PatchDocument(
            op="replace", path=f"/records/{row[record_id_column]}/values/wos_embeddings_status__", value="active"))

    return annotation_patch_documents, embeddings_status_documents


def patch_payload_splitter(configuration: dict, data: pd.DataFrame) -> Iterator:
    """
    Splits the patch payload so that each request is about 600KBs

    Args:
        configuration (dict): The configuration dictionary
        data (pd.DataFrame): The input data

    Yields:
        Iterator: Iterator for patch payloads
    """
    chunk_size = 600*1024
    current_chunk = []
    current_sum = 0

    embeddings_columns = []

    import ibm_metrics_plugin.common.utils.configuration_utils as ConfigurationFn
    from ibm_metrics_plugin.common.utils.constants import (EmbeddingFieldType,
                                                           ProblemType)
    problem_type = ConfigurationFn.get_problem_type(configuration)
    feature_columns = ConfigurationFn.get_feature_columns(configuration)
    record_id_column = ConfigurationFn.get_record_id_column(configuration)

    embeddings_columns = [EmbeddingFieldType.FEATURE.get_default_embeddings_name(
        col) for col in feature_columns]
    embeddings_columns.append(
        EmbeddingFieldType.INPUT.get_default_embeddings_name())
    embeddings_columns.append(
        EmbeddingFieldType.OUTPUT.get_default_embeddings_name())
    if problem_type is ProblemType.RAG:
        embeddings_columns.append(
            EmbeddingFieldType.CONTEXT.get_default_embeddings_name())

    for _, row in data[embeddings_columns + [record_id_column]].iterrows():
        length = row.memory_usage(index=False, deep=True)
        if current_sum + length > chunk_size:
            yield get_patch_operation(pd.DataFrame(current_chunk), embeddings_columns, record_id_column)
            current_chunk = []
            current_sum = 0

            if length > chunk_size:
                yield get_patch_operation(pd.DataFrame([row.to_dict()], embeddings_columns, record_id_column))
                continue

        current_chunk.append(row.to_dict())
        current_sum += length

    if len(current_chunk):
        yield get_patch_operation(pd.DataFrame(current_chunk), embeddings_columns, record_id_column)


def request_payload_splitter(data: pd.DataFrame, input_columns: List[str],
                             output_columns: List[str], meta_columns: List[str] = []) -> Iterator[PayloadRecord]:
    """
    Splits the input data so that each request is about 900KBs each

    Args:
        data (pd.DataFrame): The input data
        input_columns (List[str]): The input columns
        output_columns (List[str]): The output columns
        meta_columns (List[str], optional): The meta columns. Defaults to [].

    Yields:
        Iterator[PayloadRecord]: Iterator for payload record
    """
    chunk_size = 900*1024
    current_chunk = []
    current_sum = 0

    for _, row in data[input_columns + output_columns + meta_columns].iterrows():
        length = row.memory_usage(index=False, deep=True)
        if current_sum + length > chunk_size:
            yield get_payload_record(pd.DataFrame(current_chunk), input_columns, output_columns, meta_columns)
            current_chunk = []
            current_sum = 0

            if length > chunk_size:
                yield get_payload_record(pd.DataFrame([row.to_dict()], input_columns, output_columns, meta_columns))
                continue

        current_chunk.append(row.to_dict())
        current_sum += length

    if len(current_chunk):
        yield get_payload_record(pd.DataFrame(current_chunk), input_columns, output_columns, meta_columns)
