# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import base64
from datetime import datetime
from typing import Any, Dict

from ibm_watsonx_gov.entities.agentic_app import AgenticApp
from ibm_watsonx_gov.entities.mapping import Mapping, MappingItem
from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger

logger = GovSDKLogger.get_logger(__name__)


class SpanNode:
    """
    Class to represent the structure of a single span and its children.
    """

    def __init__(self, service_name: str, agentic_app: AgenticApp | None, span):
        self.service_name = service_name
        from opentelemetry.proto.trace.v1.trace_pb2 import Span
        self.span: Span = span
        self.agentic_app = agentic_app

        self.children: list['SpanNode'] = []
        self._interaction_id = None
        self._conversation_id = None

    def add_child(self, child: 'SpanNode'):
        self.children.append(child)

    def get_interaction_id(self) -> str:
        """
        Returns the interaction id from this span

        Returns:
            str: The interaction id
        """
        if self._interaction_id is None:
            self._interaction_id = base64.b64encode(
                self.span.trace_id).decode()
        return self._interaction_id

    def get_conversation_id(self) -> str:
        """
        Returns the conversation id from this span

        Returns:
            str: The conversation id
        """
        if self._conversation_id is None:
            thread_id_key = "traceloop.association.properties.thread_id"
            from ibm_watsonx_gov.traces.span_util import get_attributes
            self._conversation_id = get_attributes(self.span.attributes, [
                thread_id_key]).get(thread_id_key) or self.get_interaction_id()
        return self._conversation_id

    def get_nodes_configuration(self) -> dict:
        nodes_config = {}
        if self.agentic_app:
            nodes_config = {
                n.name: n.metrics_configurations for n in self.agentic_app.nodes}
        return nodes_config

    def find_nodes_with_name(self, name: str) -> list["SpanNode"]:
        """
        Depth First Search to find the nodes with span name provided.

        Args:
            name (str): The span name to find

        Returns:
            list[SpanNode]: The list of nodes matching the criteria.
        """
        result = []

        def dfs(node: "SpanNode"):
            if node.span.name.lower().startswith(name.lower()):
                result.append(node)
            for child in node.children:
                dfs(child)

        dfs(self)
        return result

    def __get_mapping_value_helper(self, mapping_item: MappingItem) -> Any | None:
        from ibm_watsonx_gov.traces.span_util import (
            extract_value_from_jsonpath,
            flatten_attributes,
        )

        logger.debug(
            f"Finding mapping {mapping_item.model_dump()} in {self.span.name} with {len(self.children)} children.")

        # Define some short-hand patterns for attribute names
        attribute_patterns = {
            "input": "traceloop.entity.input",
            "output": "traceloop.entity.output",
            "conversation_id": "traceloop.association.properties.thread_id"
        }

        # Get the search pattern
        attr_name_lower = str(mapping_item.attribute_name).lower()
        search_pattern = attribute_patterns.get(
            attr_name_lower, attr_name_lower)

        # Find matching attribute
        attributes = flatten_attributes(self.span.attributes)
        result = attributes.get(search_pattern)

        if result is None:
            logger.debug(f"No value found for {mapping_item.attribute_name}.")
            return

        # Apply JSON path if specified
        if mapping_item.json_path:
            result = extract_value_from_jsonpath(
                mapping_item.json_path, result)

        if mapping_item.key == "tools":
            from rich import inspect
            inspect(result)
        if result is not None:
            return result

        # Could not find result in the span. Let's try the children
        if not mapping_item.include_children:
            return None

        logger.debug(
            f"Checking {len(self.children)} child nodes of {self.span.name}.")

        for child_span_node in self.children:
            result = child_span_node.__get_mapping_value_helper(mapping_item)
            if result is not None:
                return result

        return result

    def get_mapping_value(self, mapping_item: MappingItem) -> Any | None:
        """
        Gets the mapping value specified by a single mapping item from the span.

        Args:
            mapping_item (MappingItem): The mapping item containing the json path etc.

        Raises:
            ValueError: 1. If the mapping item is not correct. 
                        2. When mapping item type is span, and more than one spans OR no spans match the criteria.

        Returns:
            Any | None: If found, the value from the span corresponding to the mapping item provided.
        """

        # Early return if no attribute name specified
        if not mapping_item.attribute_name:
            raise ValueError(
                f"Attribute name is not specified for {mapping_item.key}")

        # Check if the trace is root span. i.e. parent_span_id is empty
        if (mapping_item.is_root_span):
            return self.__get_mapping_value_helper(mapping_item)

        if (mapping_item.span_name is None):
            raise ValueError(
                f"Span name is not specified for {mapping_item.key}")

        nodes = self.find_nodes_with_name(mapping_item.span_name)

        # Throw an error if no span nodes found.
        if len(nodes) == 0:
            message = f"No spans found with names starting with {mapping_item.span_name} prefix."
            raise ValueError(message)

        # TODO : Support multiple occurrences as a node will get executed multiple times.
        if len(nodes) > 1:
            message = f"Found {len(nodes)} spans with {mapping_item.span_name} name."
            # message += f" Expected only one span. Full List : {[node.span.name for node in nodes]}."
            message += " Returning the value for first node. Ignoring the rest."
            logger.warning(message)

        node: SpanNode = nodes[0]
        return node.__get_mapping_value_helper(mapping_item)

    def get_values(self, mapping: Mapping) -> Dict[str, Any]:
        """
        Get the values according to the mapping provided from this span node.

        Args:
            mapping (Mapping): The mapping

        Returns:
            Dict[str, Any]: A single dictionary containing the input/output etc extracted from the trace.
        """
        row = {
            mapping_item.key: self.get_mapping_value(mapping_item)
            for mapping_item in mapping.items
        }

        row["interaction_id"] = self.get_interaction_id()
        row["conversation_id"] = self.get_conversation_id()
        row["start_time"] = datetime.fromtimestamp(
            self.span.start_time_unix_nano / 1e9)
        row["end_time"] = datetime.fromtimestamp(
            self.span.end_time_unix_nano / 1e9)
        return row

    def __repr__(self, level=0):
        indent = "  " * level
        s = f"{indent}- {self.span.name} (span_id={base64.b64encode(self.span.span_id).decode()}, parent_id={base64.b64encode(self.span.parent_span_id).decode() if self.span.parent_span_id else 'None'})\n"
        for child in self.children:
            s += child.__repr__(level + 1)
        return s
