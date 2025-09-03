# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Generator, List

from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.entities.agentic_app import (AgenticApp,
                                                  MetricsConfiguration, Node)
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import AgentMetricResult
from ibm_watsonx_gov.entities.foundation_model import FoundationModelInfo
from ibm_watsonx_gov.evaluators.impl.evaluate_metrics_impl import \
    _evaluate_metrics
from ibm_watsonx_gov.traces.span_node import SpanNode
from ibm_watsonx_gov.traces.span_util import (get_attributes,
                                              get_span_nodes_from_json)
from ibm_watsonx_gov.utils.python_utils import add_if_unique

try:
    from opentelemetry.proto.trace.v1.trace_pb2 import Span
except:
    pass

TARGETED_USAGE_TRACE_NAMES = [
    # openAI
    "openai.embeddings",
    "ChatOpenAI.chat",
    "OpenAI.completion",
    # IBM
    "ChatWatsonx.chat",
    "WatsonxLLM.completion",
    # Azure
    "AzureChatOpenAI.chat",
    "AzureOpenAI.completion",
    # AWS
    "ChatBedrock.chat",
    "ChatBedrockConverse.chat",
    # Google
    "ChatVertexAI.chat",
    "VertexAI.completion",
    # Anthropic
    "ChatAnthropic.chat",
    "ChatAnthropicMessages.chat",
    # TODO: Add attributes for other frameworks as well.
]
ONE_M = 1000000
COST_METADATA = {  # Costs per 1M tokens
    # ref: https://platform.openai.com/docs/pricing
    "gpt-4": {"input": 30.0, "output": 60.0},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "chatgpt-4o-latest": {"input": 5.0, "output": 15.0},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "text-embedding-ada-002": {"input": 0.10, "output": 0.0},

    # ref: https://docs.anthropic.com/en/docs/about-claude/models/overview#model-pricing
    "claude-opus-4-0": {"input": 15.0, "output": 75.0},
    "claude-opus-4-20250514": {"input": 15.0, "output": 75.0},
    "anthropic.claude-opus-4-20250514-v1:0": {"input": 15.0, "output": 75.0},
    "claude-opus-4@20250514": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-0": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "anthropic.claude-sonnet-4-20250514-v1:0": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4@20250514": {"input": 3.0, "output": 15.0},
    "claude-3-7-sonnet-latest": {"input": 3.0, "output": 15.0},
    "claude-3-7-sonnet-20250219": {"input": 3.0, "output": 15.0},
    "anthropic.claude-3-7-sonnet-20250219-v1:0": {"input": 3.0, "output": 15.0},
    "claude-3-7-sonnet@20250219": {"input": 3.0, "output": 15.0},
    "claude-3-5-sonnet-latest": {"input": 3.0, "output": 15.0},
    "claude-3-5-sonnet-20241022": {"input": 3.0, "output": 15.0},
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {"input": 3.0, "output": 15.0},
    "claude-3-5-sonnet-v2@20241022": {"input": 3.0, "output": 15.0},
    "claude-3-5-haiku-latest": {"input": 0.80, "output": 4.0},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.0},
    "anthropic.claude-3-5-haiku-20241022-v1:0": {"input": 0.80, "output": 4.0},
    "claude-3-5-haiku@20241022": {"input": 0.80, "output": 4.0},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.25, "output": 1.25},
    "claude-3-haiku@20240307": {"input": 0.25, "output": 1.25},

    # ref: https://cloud.google.com/vertex-ai/generative-ai/pricing
    "gemini-2.5-pro": {"input": 1.25, "output": 10.0},
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    "gemini-2.5-flash-lite": {"input": 0.1, "output": 0.4},
    "gemini-2.0-flash-001": {"input": 0.15, "output": 0.6},
    "gemini-2.0-flash-lite-001": {"input": 0.075, "output": 0.3},

    # ref: https://mistral.ai/pricing#api-pricing
    # ref: https://aws.amazon.com/bedrock/pricing
    # ref: https://cloud.google.com/vertex-ai/generative-ai/pricing
    "pixtral-large-latest": {"input": 2.0, "output": 6.0},
    "mistral.pixtral-large-2502-v1:0": {"input": 2.0, "output": 6.0},
    "mistral-large-latest": {"input": 2.0, "output": 6.0},
    "mistral.mistral-large-2407-v1:0": {"input": 2.0, "output": 6.0},
    "mistralai/mistral-large-2411@001": {"input": 2.0, "output": 6.0},
    "mistral.mistral-large-2402-v1:0": {"input": 4.0, "output": 12.0},
    "mistral-medium-latest": {"input": 0.4, "output": 2.0},
    "mistral-small-latest": {"input": 0.1, "output": 0.3},
    "mistralai/mistral-small-2503@001": {"input": 0.1, "output": 0.3},
    "mistral.mistral-small-2402-v1:0": {"input": 1.0, "output": 3.0},
    "open-mistral-7b": {"input": 0.25, "output": 0.25},
    "mistral.mistral-7b-instruct-v0:2": {"input": 0.15, "output": 0.2},
    "open-mixtral-8x7b": {"input": 0.7, "output": 0.7},
    "mistral.mixtral-8x7b-instruct-v0:1": {"input": 0.45, "output": 0.7},

    # ref: https://aws.amazon.com/bedrock/pricing
    "command-r": {"input": 0.5, "output": 1.5},
    "cohere.command-r-v1:0": {"input": 0.5, "output": 1.5},
    "command-r-plus": {"input": 3.0, "output": 15},
    "cohere.command-r-plus-v1:0": {"input": 3.0, "output": 15},
    "command-light": {"input": 0.3, "output": 0.6},
    "cohere.command-light-text-v14": {"input": 0.3, "output": 0.6},
    "command": {"input": 1.0, "output": 2.0},
    "cohere.command-text-v14": {"input": 1.0, "output": 2.0},

    # ref: https://www.ai21.com/pricing
    # ref: https://aws.amazon.com/bedrock/pricing
    # ref: https://cloud.google.com/vertex-ai/generative-ai/pricing
    "jamba-large": {"input": 2.0, "output": 8.0},
    "ai21.jamba-1-5-large-v1:0": {"input": 2.0, "output": 8.0},
    "ai21/jamba-1.5-large@001": {"input": 2.0, "output": 8.0},
    "jamba-mini": {"input": 0.2, "output": 0.4},
    "ai21.jamba-1-5-mini-v1:0": {"input": 0.2, "output": 0.4},
    "ai21/jamba-1.5-mini@001": {"input": 0.2, "output": 0.4},

    # ref: https://www.ibm.com/products/watsonx-ai/pricing
    "ibm/granite-vision-3-2-2b": {"input": 0.10, "output": 0.10},
    "ibm/granite-3-2b-instruct": {"input": 0.10, "output": 0.10},
    "ibm/granite-guardian-3-8b": {"input": 0.20, "output": 0.20},
    "ibm/granite-8b-japanese": {"input": 0.60, "output": 0.60},
    "meta-llama/llama-3-2-11b-vision-instruct": {"input": 0.35, "output": 0.35},
    "meta-llama/llama-3-2-1b-instruct": {"input": 0.1, "output": 0.1},
    "meta-llama/llama-3-2-3b-instruct": {"input": 0.15, "output": 0.15},
    "meta-llama/llama-3-2-90b-vision-instruct": {"input": 2.0, "output": 2.0},
    "meta-llama/llama-3-3-70b-instruct": {"input": 0.71, "output": 0.71},
    "meta-llama/llama-3-405b-instruct": {"input": 5.0, "output": 16.0},
    "meta-llama/llama-guard-3-11b-vision": {"input": 0.35, "output": 0.35},
    "mistralai/mistral-small-3-1-24b-instruct-2503": {"input": 0.1, "output": 0.3},
    "mistralai/mistral-medium-2505": {"input": 3.0, "output": 10.0},
    "core42/jais-13b-chat": {"input": 1.8, "output": 1.8},
    "sdaia/allam-1-13b-instruct": {"input": 1.8, "output": 1.8},
    "meta-llama/llama-4-maverick-17b-128e-instruct-fp": {"input": 0.35, "output": 1.4},
    "ibm/granite-embedding-107m-multilingual": {"input": 0.10, "output": 0.10},
    "ibm/granite-embedding-278m-multilingual": {"input": 0.10, "output": 0.10},
    "ibm/slate-125m-english-rtrvr": {"input": 0.10, "output": 0.10},
    "ibm/slate-125m-english-rtrvr-v2": {"input": 0.10, "output": 0.10},
    "ibm/slate-30m-english-rtrvr": {"input": 0.10, "output": 0.10},
    "ibm/slate-30m-english-rtrvr-v2": {"input": 0.10, "output": 0.10},
    "intfloat/multilingual-e5-large": {"input": 0.10, "output": 0.10},
    "sentence-transformers/all-minilm-l12-v2": {"input": 0.10, "output": 0.10},
    "sentence-transformers/all-minilm-l6-v2": {"input": 0.10, "output": 0.10},
}


class TraceUtils:

    @staticmethod
    def build_span_trees(spans: list[dict], agentic_app: AgenticApp | None = None) -> List[SpanNode]:
        root_spans: list[SpanNode] = []

        span_nodes: dict[str, SpanNode] = {}
        for span in spans:
            span_nodes.update(get_span_nodes_from_json(span, agentic_app))

        # Create tree
        for _, node in span_nodes.items():
            parent_id = node.span.parent_span_id
            if not parent_id:
                root_spans.append(node)  # Root span which will not have parent
            else:
                parent_node = span_nodes.get(parent_id)
                if parent_node:
                    parent_node.add_child(node)
                else:
                    # Orphan span where parent is not found
                    root_spans.append(node)

        return root_spans

    @staticmethod
    def convert_array_value(array_obj: Dict) -> List:
        """Convert OTEL array value to Python list"""
        return [
            item.get("stringValue")
            or int(item.get("intValue", ""))
            or float(item.get("doubleValue", ""))
            or bool(item.get("boolValue", ""))
            for item in array_obj.get("values", [])
        ]

    @staticmethod
    def stream_trace_data(file_path: Path) -> Generator:
        """Generator that yields spans one at a time."""
        with open(file_path) as f:
            for line in f:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse line: {line}\nError: {e}")

    @staticmethod
    def __extract_usage_meta_data(span: Span) -> dict:
        """
        Extract meta data required to calculate usage metrics from spans
        """
        meta_data = {}
        attributes = get_attributes(span.attributes)
        model = attributes.get("gen_ai.request.model")

        if not model:
            return meta_data

        meta_data["cost"] = {
            "model": model,
            "total_prompt_tokens": attributes.get("gen_ai.usage.prompt_tokens", 0),
            "total_completion_tokens": attributes.get(
                "gen_ai.usage.completion_tokens", 0
            ),
            "total_tokens": attributes.get("llm.usage.total_tokens", 0),
        }
        meta_data["input_token_count"] = attributes.get(
            "gen_ai.usage.prompt_tokens", 0)
        meta_data["output_token_count"] = attributes.get(
            "gen_ai.usage.completion_tokens", 0)
        return meta_data

    @staticmethod
    def calculate_cost(usage_data: List[dict]) -> float:
        """Calculate cost for given list of usage."""
        total_cost = 0.0

        for data in usage_data:
            model = data["model"].lower()

            try:
                model_pricing = COST_METADATA[model]
            except KeyError:
                return 0
                # raise ValueError(
                #     f"Pricing not available for {model}")

            # Calculate costs (per 1M tokens)
            input_cost = (data["total_prompt_tokens"] /
                          ONE_M) * model_pricing["input"]
            output_cost = (data["total_completion_tokens"] / ONE_M) * model_pricing[
                "output"
            ]
            total_cost += input_cost + output_cost

        return total_cost

    @staticmethod
    def compute_metrics_from_trace(span_tree: SpanNode, api_client: APIClient = None) -> tuple[list[AgentMetricResult], list[Node], list]:
        metric_results, edges = [], []

        # Add Interaction level metrics
        metric_results.extend(TraceUtils.__compute_interaction_level_metrics(
            span_tree, api_client))

        # Add node level metrics result
        node_metric_results, nodes_list, experiment_run_metadata = TraceUtils.__compute_node_level_metrics(
            span_tree, api_client)
        metric_results.extend(node_metric_results)

        for node in nodes_list:
            if node.name in experiment_run_metadata:
                node.foundation_models = list(
                    experiment_run_metadata[node.name]["foundation_models"])

        return metric_results, nodes_list, edges

    @staticmethod
    def __compute_node_level_metrics(span_tree: SpanNode, api_client: APIClient | None):
        metric_results = []
        trace_metadata = defaultdict(list)
        experiment_run_metadata = defaultdict(lambda: defaultdict(set))
        nodes_list = []
        node_stack = list(span_tree.children)
        child_stack = list()
        node_execution_count = {}
        while node_stack or child_stack:
            is_parent = not child_stack
            node = child_stack.pop() if child_stack else node_stack.pop()
            if is_parent:
                parent_span: Span = node.span
                node_name, metrics_config_from_decorators, code_id, events, execution_order = None, [], "", [], None
                data = {}
                # inputs = get_nested_attribute_values(
                #     [node], "traceloop.entity.input")
                # outputs = get_nested_attribute_values(
                #     [node], "traceloop.entity.output")
            span: Span = node.span

            for attr in span.attributes:
                key = attr.key
                value = attr.value

                if is_parent:
                    if key == "traceloop.entity.name":
                        node_name = value.string_value
                    elif key == "gen_ai.runnable.code_id":
                        code_id = value.string_value
                    elif key == "traceloop.association.properties.langgraph_step":
                        execution_order = int(
                            value.int_value) if value else None
                    elif key in ("traceloop.entity.input", "traceloop.entity.output"):
                        try:
                            content = json.loads(value.string_value)
                            inputs_outputs = content.get(
                                "inputs" if key.endswith("input") else "outputs")
                            if isinstance(inputs_outputs, str):
                                inputs_outputs = json.loads(inputs_outputs)
                            if data:
                                data.update(inputs_outputs)
                            else:
                                data = inputs_outputs
                        except (json.JSONDecodeError, AttributeError) as e:
                            raise Exception(
                                "Unable to parse json string") from e
                if key.startswith("wxgov.config.metrics"):
                    metrics_config_from_decorators.append(
                        json.loads(value.string_value))
            if span.events:
                events.extend(span.events)

            if (not node_name) or (node_name == "__start__"):
                continue

            if span.name in TARGETED_USAGE_TRACE_NAMES:
                # Extract required details to calculate usage metrics from each span
                for k, v in TraceUtils.__extract_usage_meta_data(span).items():
                    trace_metadata[k].append(v)

            for k, v in TraceUtils.__get_run_metadata_from_span(span).items():
                experiment_run_metadata[node_name][k].add(v)

            child_stack.extend(node.children)

            if not child_stack:
                metrics_to_compute, all_metrics_config = TraceUtils.__get_metrics_to_compute(
                    span_tree.get_nodes_configuration(), node_name, metrics_config_from_decorators)

                add_if_unique(Node(name=node_name, func_name=code_id.split(":")[-1] if code_id else node_name, metrics_configurations=all_metrics_config), nodes_list,
                              ["name", "func_name"])

                if node_name in node_execution_count:
                    node_execution_count[node_name] += node_execution_count.get(
                        node_name)
                else:
                    node_execution_count[node_name] = 1

                for mc in metrics_to_compute:
                    metric_result = _evaluate_metrics(configuration=mc.configuration,
                                                      data=data,
                                                      metrics=mc.metrics,
                                                      metric_groups=mc.metric_groups,
                                                      api_client=api_client).to_dict()
                    for mr in metric_result:
                        node_result = {
                            "applies_to": "node",
                            "interaction_id": span_tree.get_interaction_id(),
                            "node_name": node_name,
                            "conversation_id": span_tree.get_conversation_id(),
                            "execution_count": node_execution_count.get(node_name),
                            "execution_order": execution_order,
                            ** mr
                        }

                        metric_results.append(AgentMetricResult(**node_result))

                # Add node latency metric result
                metric_results.append(AgentMetricResult(name="latency",
                                                        value=(int(
                                                            parent_span.end_time_unix_nano) - int(parent_span.start_time_unix_nano))/1e9,
                                                        group=MetricGroup.PERFORMANCE,
                                                        applies_to="node",
                                                        interaction_id=span_tree.get_interaction_id(),
                                                        conversation_id=span_tree.get_conversation_id(),
                                                        node_name=node_name,
                                                        execution_count=node_execution_count.get(
                                                            node_name),
                                                        execution_order=execution_order))

                # Get the node level metrics computed online during graph invocation from events
                metric_results.extend(TraceUtils.__get_metrics_results_from_events(
                    events=events,
                    interaction_id=span_tree.get_interaction_id(),
                    conversation_id=span_tree.get_conversation_id(),
                    node_name=node_name,
                    execution_count=node_execution_count.get(node_name),
                    execution_order=execution_order))

        metric_results.extend(
            TraceUtils.__compute_interaction_metrics_from_trace_metadata(trace_metadata, span_tree.get_interaction_id(), span_tree.get_conversation_id()))

        return metric_results, nodes_list, experiment_run_metadata

    @staticmethod
    def __compute_interaction_level_metrics(span_tree: SpanNode, api_client: APIClient | None) -> list[AgentMetricResult]:
        metric_results = []
        span = span_tree.span
        metric_results.append(AgentMetricResult(name="duration",
                                                value=(int(
                                                    span.end_time_unix_nano) - int(span.start_time_unix_nano))/1000000000,
                                                group=MetricGroup.PERFORMANCE,
                                                applies_to="interaction",
                                                interaction_id=span_tree.get_interaction_id(),
                                                conversation_id=span_tree.get_conversation_id()))

        if not span_tree.agentic_app:
            return metric_results

        data = {}

        attrs = get_attributes(
            span.attributes, ["traceloop.entity.input", "traceloop.entity.output"])
        inputs = attrs.get("traceloop.entity.input", "{}")
        if isinstance(inputs, str):
            inputs = json.loads(inputs).get("inputs", {})
        elif isinstance(inputs, dict):
            inputs = inputs.get("inputs", {})

        if "messages" in inputs:
            for message in reversed(inputs["messages"]):
                if "kwargs" in message and "type" in message["kwargs"] and message["kwargs"]["type"].upper() == "HUMAN":
                    data["input_text"] = message["kwargs"]["content"]
                    break
        else:
            data.update(inputs)

        outputs = attrs.get("traceloop.entity.output", "{}")
        if isinstance(outputs, str):
            outputs = json.loads(outputs).get("outputs", {})
        elif isinstance(outputs, dict):
            outputs = outputs.get("outputs", {})

        if "messages" in outputs:
            # The messages is a list depicting the history of interactions with the agent.
            # It need NOT be the whole list of interactions in the conversation though.
            # We will traverse the list from the end to find the human input of the interaction,
            # and the AI output.

            # If there was no input_text so far, find first human message
            if "input_text" not in data:
                for message in reversed(outputs["messages"]):
                    if "kwargs" in message and "type" in message["kwargs"] and message["kwargs"]["type"].upper() == "HUMAN":
                        data["input_text"] = message["kwargs"]["content"]
                        break

            # Find last AI message
            for message in reversed(outputs["messages"]):
                if "kwargs" in message and "type" in message["kwargs"] and message["kwargs"]["type"].upper() == "AI":
                    data["generated_text"] = message["kwargs"]["content"]
                    break
        else:
            data.update(outputs)

        metric_result = _evaluate_metrics(configuration=span_tree.agentic_app.metrics_configuration.configuration,
                                          data=data,
                                          metrics=span_tree.agentic_app.metrics_configuration.metrics,
                                          metric_groups=span_tree.agentic_app.metrics_configuration.metric_groups,
                                          api_client=api_client).to_dict()
        for mr in metric_result:
            node_result = {
                "applies_to": "interaction",
                "interaction_id": span_tree.get_interaction_id(),
                "conversation_id": span_tree.get_conversation_id(),
                **mr
            }

            metric_results.append(AgentMetricResult(**node_result))

        return metric_results

    @staticmethod
    def __get_metrics_to_compute(nodes_config, node_name, metrics_configurations):
        metrics_to_compute, all_metrics_config = [], []

        if nodes_config.get(node_name):
            metrics_config = nodes_config.get(node_name)
            for mc in metrics_config:
                mc_obj = MetricsConfiguration(configuration=mc.configuration,
                                              metrics=mc.metrics,
                                              metric_groups=mc.metric_groups)
                metrics_to_compute.append(mc_obj)
                all_metrics_config.append(mc_obj)

        for mc in metrics_configurations:
            mc_obj = MetricsConfiguration.model_validate(
                mc.get("metrics_configuration"))

            all_metrics_config.append(mc_obj)
            if mc.get("compute_real_time") == "false":
                metrics_to_compute.append(mc_obj)

        return metrics_to_compute, all_metrics_config

    @staticmethod
    def __get_metrics_results_from_events(events, interaction_id, conversation_id, node_name, execution_count, execution_order):
        results = []
        if not events:
            return results

        for event in events:
            for attr in event.attributes:
                if attr.key == "attr_wxgov.result.metric":
                    val = attr.value.string_value
                    if val:
                        mr = json.loads(val)
                        mr.update({
                            "node_name": node_name,
                            "interaction_id": interaction_id,
                            "conversation_id": conversation_id,
                            "execution_count": execution_count,
                            "execution_order": execution_order
                        })
                        results.append(AgentMetricResult(**mr))

        return results

    @staticmethod
    def __compute_interaction_metrics_from_trace_metadata(trace_metadata: dict, interaction_id: str, conversation_id: str) -> list:
        metrics_result = []

        for metric, data in trace_metadata.items():
            if metric == "cost":
                metric_value = TraceUtils.calculate_cost(data)
            elif metric == "input_token_count":
                metric_value = sum(data)
            elif metric == "output_token_count":
                metric_value = sum(data)
            else:
                continue
            agent_mr = {
                "name": metric,
                "value": metric_value,
                "interaction_id": interaction_id,
                "applies_to": "interaction",
                "conversation_id": conversation_id,
                "group": MetricGroup.USAGE.value
            }

            metrics_result.append(AgentMetricResult(**agent_mr))

        return metrics_result

    @staticmethod
    def __get_run_metadata_from_span(span: Span) -> dict:
        """
        Extract run specific metadata from traces
        1. Foundation model involved in run
        2. Tools involved in run
        """
        metadata = {}
        attributes = get_attributes(span.attributes)
        provider = attributes.get(
            "traceloop.association.properties.ls_provider", attributes.get("gen_ai.system"))
        llm_type = attributes.get("llm.request.type")
        model_name = attributes.get("gen_ai.request.model")

        if model_name:
            metadata["foundation_models"] = FoundationModelInfo(
                model_name=model_name, provider=provider, type=llm_type
            )

        return metadata
