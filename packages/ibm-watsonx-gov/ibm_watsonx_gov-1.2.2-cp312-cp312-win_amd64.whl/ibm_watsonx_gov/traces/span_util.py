# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json
from typing import Any, Dict

from jsonpath_ng import parse

from ibm_watsonx_gov.entities.agentic_app import AgenticApp
from ibm_watsonx_gov.traces.span_node import SpanNode

try:
    from google.protobuf.json_format import ParseDict
    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
        ExportTraceServiceRequest,
    )
    from opentelemetry.proto.common.v1.common_pb2 import KeyValue
except Exception:
    pass


def get_attributes(attributes, keys: list[str] = []) -> dict[str, Any]:
    """
    Get the attribute value for the given keys from a list of attributes.
    """
    attrs = {}
    for attr in attributes:
        key = attr.key
        val = get_attribute_value(attr)
        if keys:
            if key in keys:
                attrs[key] = val
        else:
            attrs[key] = val

    return attrs


def get_span_nodes_from_json(span_json: str, agentic_app: AgenticApp | None = None) -> dict[str, SpanNode]:
    """
    Convert a JSON string containing a list of spans into a dictionary of SpanNode objects, keyed by span_id.
    """
    span_nodes: dict[str, SpanNode] = {}
    span_msg = ParseDict(span_json, ExportTraceServiceRequest())
    for resource_span in span_msg.resource_spans:
        attrs = get_attributes(
            resource_span.resource.attributes, ["service.name", "wxgov.config.agentic_app"])
        service_name = attrs.get("service.name")
        if agentic_app is None:
            agentic_app = attrs.get("wxgov.config.agentic_app")

            if agentic_app:
                agentic_app = AgenticApp.model_validate_json(agentic_app)
        for scope_span in resource_span.scope_spans:
            for span in scope_span.spans:
                node = SpanNode(service_name=service_name,
                                agentic_app=agentic_app,
                                span=span)
                span_nodes[span.span_id] = node
    return span_nodes


def get_attribute_value(attribute: KeyValue) -> Any:
    """
    Get the attribute value

    Args:
        attribute (KeyValue): The attribute

    Returns:
        Any: The value from the attribute
    """
    if attribute.value.HasField("int_value"):
        return int(attribute.value.int_value)

    if attribute.value.HasField("double_value"):
        return float(attribute.value.double_value)

    if attribute.value.HasField("bool_value"):
        return bool(attribute.value.bool_value)

    if attribute.value.HasField("string_value"):
        try:
            return json.loads(attribute.value.string_value)
        except json.JSONDecodeError:
            return attribute.value.string_value

    return


def flatten_attributes(attributes, lower_case: bool = True) -> Dict[str, Any]:
    """
    Flatten OpenTelemetry span attributes into a simple key-value dictionary.

    Args:
        attributes (list[KeyValue]): List of attributes
        lower_case (bool, optional): Should the result contain the keys in lower case. Defaults to True.

    Returns:
        Dict[str, Any]: The flattened dictionary of key values from attributes
    """
    flattened = {}

    attr: KeyValue
    for attr in attributes:
        value = get_attribute_value(attr)
        key = str(attr.key).lower() if lower_case else attr.key
        flattened[key] = value
    return flattened


def extract_value_from_jsonpath(jsonpath_expr: str, json_data: str | Dict[str, Any]) -> Any | None:
    """
    Extract the value from a JSON path expression.

    Args:
        jsonpath_expr (str): The JSON path expression.
        json_data (str | Dict[str, Any]): The JSON data.

    Raises:
        ValueError: If more than one values found for the expression

    Returns:
        Any | None: The extracted value, if found. Else, None.
    """

    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    jsonpath_expr = parse(jsonpath_expr)
    result = [match.value for match in jsonpath_expr.find(json_data)]
    if len(result) > 1:
        # TODO process only the first item. Log a warning..
        raise ValueError(
            f"Multiple values found for JSON path expression: {jsonpath_expr}")

    if len(result) == 0:
        return None

    if isinstance(result[0], str):
        try:
            result[0] = json.loads(result[0])
            return result[0]
        except Exception:
            pass
    return result[0]
