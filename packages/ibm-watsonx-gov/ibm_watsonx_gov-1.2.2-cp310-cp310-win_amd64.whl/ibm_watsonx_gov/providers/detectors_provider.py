# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import asyncio
import json

import aiohttp
import pandas as pd

from ibm_watsonx_gov.clients.usage_client import validate_usage_client
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.entities.base_classes import Error
from ibm_watsonx_gov.entities.enums import (EvaluationProvider,
                                            GraniteGuardianRisks, MetricGroup)
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.tool_call_metric_provider import \
    ToolCallMetricProvider
from ibm_watsonx_gov.utils.python_utils import (run_in_event_loop,
                                                transform_str_to_list)

ACCURACY_METRICS = ["answer_relevance", "context_relevance",
                    "faithfulness", "topic_relevance", "tool_call_accuracy"]


class DetectorsProvider():
    # Status codes for BAD_GATEWAY, SERVICE_UNAVAILABLE and GATEWAY_TIMEOUT
    RETRY_AFTER_STATUS_CODES = [502, 503, 504]
    RETRY_COUNT = 3
    BACK_OFF_FACTOR = 1

    def __init__(
        self,
        configuration: GenAIConfiguration,
        metric_name: str,
        metric_method: str,
        metric_group: MetricGroup = None,
        thresholds: list[MetricThreshold] = [],
        **kwargs,
    ) -> None:
        if not kwargs.get("api_client"):
            raise ValueError(
                f"IBM WatsonX Governance SDK must be initialized to compute {metric_name} using {metric_method}. Please initialize the client to proceed, or remove this metric from the evaluation.")
        base = self.__get_base_url(metric_name)
        self.base_url = base.format(
            self.get_detector_url(kwargs.get("api_client")))
        self.configuration: GenAIConfiguration = configuration
        self.configuration_: dict[str, any] = {}
        self.metric_name = metric_name
        self.metric_method = metric_method
        self.metric_group = metric_group
        self.service_instance_id = self.get_service_instance_id(
            kwargs.get("api_client"))
        self.thresholds = thresholds
        self.detector_params = kwargs.get("detector_params", None)
        validate_usage_client(kwargs.get("usage_client"))

    def evaluate(self, data: pd.DataFrame) -> AggregateMetricResult:
        return run_in_event_loop(
            self.evaluate_async,
            data=data
        )

    async def evaluate_async(self, data: pd.DataFrame) -> AggregateMetricResult:
        """
        Entry point method to compute the configured detectors-based metrics.
        Args:
            data: Input test data
        """
        try:
            json_payloads, record_ids = self.__pre_process_data(data=data)
            result = await self.__compute_metric(json_payloads)
            aggregated_result = self.__post_process(result, record_ids)
            return aggregated_result

        except Exception as e:
            raise Exception(
                f"Error while computing metrics: {self.metric_name}. Reason: {str(e)}")

    def __pre_process_data(self, data: pd.DataFrame):
        """
        Creates payload for each row in the test data.
        """
        # read data based on the metric.
        input_content = data[self.configuration.input_fields[0]].to_list()
        output_content, context_content, tool_calls_content, tools_catalog_content = None, None, None, None

        if self.metric_name in ["answer_relevance", "faithfulness"]:
            output_content = data[self.configuration.output_fields[0]].to_list(
            )

        if self.metric_name in ["context_relevance", "faithfulness"]:
            if len(self.configuration.context_fields) > 1:
                context_content = data[self.configuration.context_fields].values.tolist(
                )
            elif len(self.configuration.context_fields) == 1:
                context_content = data[self.configuration.context_fields[0]].apply(
                    transform_str_to_list)

        if self.metric_name == "tool_call_accuracy":
            # Get the tools catalog i.e., a list of available tools
            tools_catalog_content = self.get_tools_catalog_content()
            # Get the tool calls list
            tool_calls_content = self.get_tool_calls_content(data)

        payloads_json = self.__get_json_payloads(
            input_content, output_content, context_content, tools_catalog_content, tool_calls_content)
        record_ids = data[self.configuration.record_id_field].to_list()
        return payloads_json, record_ids

    async def send_with_retries(self, payload, session: aiohttp.ClientSession):
        """
        Asynchronously calls the detections API with retries and returns the responses.
        Returns an error if all retries fail or an exception is caught.
        """
        for attempt in range(self.RETRY_COUNT):
            try:
                async with session.post(
                    url=self.base_url,
                    headers=self.__get_headers(),
                    data=payload,
                    ssl=self.verify
                ) as response:

                    response_status = response.status
                    response_text = await response.text()

                    if response_status == 200:
                        return json.loads(response_text)

                    elif response_status in self.RETRY_AFTER_STATUS_CODES and attempt < self.RETRY_COUNT - 1:
                        await asyncio.sleep(self.BACK_OFF_FACTOR * (2 ** attempt))
                        continue  # retry
                    else:
                        return {
                            "error": Error(
                                code=str(response_status),
                                message_en=str(json.loads(response_text))
                            )
                        }

            except Exception as e:
                return {
                    "error": Error(
                        code="REQUEST_FAILED",
                        message_en=str(e)
                    )
                }

    async def __compute_metric(self, api_payloads: list):
        async with aiohttp.ClientSession() as session:
            tasks = [self.send_with_retries(payload, session)
                     for payload in api_payloads]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        return responses

    def __post_process(self, results: list, record_ids: list) -> AggregateMetricResult:
        """
        Process the responses and aggregate the results.
        """
        record_level_metrics: list[RecordMetricResult] = []
        values = []
        errors = []
        for result, record_id in zip(results, record_ids):
            record_data = {
                "name": self.metric_name,
                "method": self.metric_method,
                "provider": EvaluationProvider.DETECTORS.value,
                "group": self.metric_group,
                "record_id": record_id,
                "thresholds": self.thresholds,
            }

            if "error" in result:
                record_level_metrics.append(RecordMetricResult(
                    **record_data,
                    value=None,
                    errors=[Error(code=result["error"].code,
                                  message_en=str(result["error"].message_en))]
                ))
                errors.append(Error(code=result["error"].code,
                                    message_en=str(result["error"].message_en)))
            else:
                value = 0
                if len(result["detections"]) > 0:
                    score = result["detections"][0]["score"]
                    value = round(
                        1 - score if self.metric_name in ACCURACY_METRICS else score, 4)
                record_level_metrics.append(RecordMetricResult(
                    **record_data,
                    value=value
                ))
                values.append(value)

        # creating AggregateMetricResult
        if values:
            mean_val = round(sum(values) / len(values), 4)
            min_val = min(values)
            max_val = max(values)
            value = mean_val
            error_info = {}
        else:
            mean_val = min_val = max_val = None
            value = "Error"
            error_info = {"errors": errors}
        aggregated_result = AggregateMetricResult(
            name=self.metric_name,
            method=self.metric_method,
            group=self.metric_group,
            provider=EvaluationProvider.DETECTORS.value,
            value=value,
            total_records=len(results),
            record_level_metrics=record_level_metrics,
            min=min_val,
            max=max_val,
            mean=mean_val,
            thresholds=self.thresholds,
            **error_info
        )

        # return the aggregated result
        return aggregated_result

    def __get_json_payloads(self, input_contents: list, output_contents: list | None, context_contents: list | None, tools_catalog_content: list | None, tool_calls_content: list | None) -> list:
        # Method to create the request payload.
        json_payloads = []
        metric_name = self.set_metric_name(self.metric_name)

        if self.metric_name == "answer_relevance":
            for (input, output) in zip(input_contents, output_contents):
                payload_json = {
                    "detectors": {
                        metric_name: self.detector_params or {}
                    },
                    "prompt": input,
                    "generated_text": output
                }
                json_payloads.append(json.dumps(payload_json))

        elif self.metric_name == "context_relevance":
            for (input, context) in zip(input_contents, context_contents):
                payload_json = {
                    "detectors": {
                        metric_name: self.detector_params or {}
                    },
                    "input": input,
                    "context_type": "docs",
                    "context": context
                }
                json_payloads.append(json.dumps(payload_json))

        elif self.metric_name == "faithfulness":
            for (output, context) in zip(output_contents, context_contents):
                payload_json = {
                    "detectors": {
                        metric_name: self.detector_params or {}
                    },
                    "input": output,
                    "context_type": "docs",
                    "context": context
                }
                json_payloads.append(json.dumps(payload_json))

        elif self.metric_name == "tool_call_accuracy":
            for (input, tool_call) in zip(input_contents, tool_calls_content):
                payload_json = {
                    "detectors": {
                        metric_name: self.detector_params or {}
                    },
                    "messages": [{"content": input, "role": "user"},
                                 {"tool_calls": tool_call, "role": "assistant"}],
                    "tools": tools_catalog_content
                }
                json_payloads.append(json.dumps(payload_json))
        else:
            for input in input_contents:
                payload_json = {
                    "detectors": {
                        metric_name: self.detector_params or {}
                    },
                    "input": input
                }
                json_payloads.append(json.dumps(payload_json))
        return json_payloads

    def __get_headers(self):
        # Method to create request headers
        headers = {}
        headers["Content-Type"] = "application/json"
        headers["Authorization"] = f"Bearer {self.wos_client.authenticator.token_manager.get_token()}"
        headers["x-governance-instance-id"] = self.service_instance_id
        return headers

    def get_detector_url(self, api_client):
        """
        Sets the wos_client and returns the service url
        """
        self.wos_client = api_client.wos_client
        self.verify = not api_client.credentials.disable_ssl
        if api_client.credentials.version:
            return api_client.credentials.url
        else:
            from ibm_watsonx_gov.utils.url_mapping import WOS_URL_MAPPING
            urls = WOS_URL_MAPPING.get(api_client.credentials.url)
            return urls.wml_url

    def get_service_instance_id(self, api_client):
        """
        Sets the wos_client and returns the service instance id
        """

        self.wos_client = api_client.wos_client
        return self.wos_client.service_instance_id

    def set_metric_name(self, metric_name):
        """
        Sets metric name as 'granite guardian' for Granite Guardian risks
        """
        metric_name = "granite_guardian" if metric_name in GraniteGuardianRisks.values() else metric_name
        return metric_name

    def __get_base_url(self, metric_name):
        """
        Returns the inference proxy end-point to be invoked based on the metric.
        """
        if metric_name == "answer_relevance":
            return "{}/ml/v1/text/detection/generated?version=2023-10-25"
        elif metric_name in ["context_relevance", "faithfulness"]:
            return "{}/ml/v1/text/detection/context?version=2023-10-25"
        elif metric_name == "tool_call_accuracy":
            return "{}/ml/v1/text/detection/chat?version=2023-10-25"
        else:
            return "{}/ml/v1/text/detection?version=2023-10-25"

    def get_tool_calls_content(self, data):
        tool_calls_content = []
        if self.configuration.tool_calls_field:
            data[self.configuration.tool_calls_field] = data[self.configuration.tool_calls_field].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x)
            for _, row in data.iterrows():
                tool_calls = ToolCallMetricProvider.extract_tool_calls_from_response(
                    row[self.configuration.tool_calls_field])
                for tc in tool_calls:
                    if isinstance(tc["function"]["arguments"], str):
                        tc["function"]["arguments"] = json.loads(
                            tc["function"]["arguments"])
                tool_calls_content.append(tool_calls)

        return tool_calls_content

    def get_tools_catalog_content(self):
        # Get the specification of tools used in the application
        # in proper format if it is a list of Callable
        if isinstance(self.configuration.tools, list) and all(callable(item) for item in self.configuration.tools):
            tools_catalog_content = ToolCallMetricProvider.get_tools_list_schema(
                self.configuration.tools)
            # converting the model to a json object
            tools_catalog_content = [
                tool_spec.model_dump() for tool_spec in tools_catalog_content]
        else:
            tools_catalog_content = self.configuration.tools
        return tools_catalog_content
        return tools_catalog_content
