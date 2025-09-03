# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Literal

import pandas as pd
from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import AggregateMetricResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.detectors_provider import DetectorsProvider
from ibm_watsonx_gov.providers.tool_call_metric_provider import \
    ToolCallMetricProvider
from ibm_watsonx_gov.utils.python_utils import run_in_event_loop
from ibm_watsonx_gov.utils.validation_util import validate_tool_calls
from pydantic import Field

TOOL_CALL_ACCURACY = "tool_call_accuracy"
FUNCTION_CALL = "function_call"


class ToolCallAccuracyMetric(GenAIMetric):
    """
    ToolCallAccuracyMetric checks whether the tool call in the LLM response is 
    syntactically correct and semantically meaningful, given the user's query and 
    the available tool definitions.

    The ToolCallAccuracyMetric can be computed using the below methods:
    
    1. syntactic (default)
    2. granite_guardian

    Examples:
        1. Create ToolCallAccuracyMetric by passing the basic configuration.
            .. code-block:: python

                config = GenAIConfiguration(tools = [get_weather,fetch_stock_price])
                evaluator = MetricsEvaluator(configuration=config)
                df = pd.read_csv("")

                metrics = [ToolCallAccuracyMetric()]
                result = evaluator.evaluate(data=df, metrics=metrics)

        2. Create ToolCallAccuracyMetric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="upper_limit", value=0.8)
                metric = ToolCallAccuracyMetric(threshold=threshold)

        3. Create ToolCallAccuracyMetric by passing custom tool calls field in configuration.
            .. code-block:: python

                test_data = {"input_text": "What's the latest on Tesla today?", 
                "tools_used":[{"name": "get_weather", "args": {"location": "Tesla"}, "id": "0724", "type": "tool_call"}]}

                config = GenAIConfiguration(tools = [get_weather,fetch_stock_price],
                                            tool_calls_field="tools_used")
                evaluator = MetricsEvaluator(configuration=config)
                metrics = [ToolCallAccuracyMetric()]
                result = evaluator.evaluate(data=test_data, metrics=metrics)

        4. Create ToolCallAccuracyMetric by passing a list of dictionary items as tools field in configuration.
            .. code-block:: python
            
                available_tools = [{"type":"function","function":{"name":"f1_name","description":"f1_description.","parameters":{"parameter1":{"description":"parameter_description","type":"parameter_type","default":"default_value"}}}}]
                config = GenAIConfiguration(tools = available_tools,
                                            tool_calls_field="tools_used")
                evaluator = MetricsEvaluator(configuration=config)
                df = pd.read_csv("")

                metrics = [ToolCallAccuracyMetric()]
                result = evaluator.evaluate(data=df, metrics=metrics)
    """

    name: Annotated[Literal["tool_call_accuracy"], Field(title="Metric Name",
                                                         description="The name of metric.",
                                                         default=TOOL_CALL_ACCURACY)]

    tasks: Annotated[list[TaskType], Field(title="Task Type",
                                           description="The generative task type.",
                                           default=[TaskType.RAG])]
    group: Annotated[MetricGroup, Field(
        default=MetricGroup.TOOL_CALL_QUALITY, frozen=True)]

    method: Annotated[Literal["syntactic", "granite_guardian"], Field(title="Computation Method",
                                                                      description="The method used to compute the metric.",
                                                                      default="syntactic")]
    thresholds: Annotated[list[MetricThreshold], Field(title="Metric threshold",
                                                       description="Value that defines the violation limit for the metric",
                                                       default=[MetricThreshold(
                                                           type="upper_limit", value=0.7)]
                                                       )]

    async def evaluate_async(
        self,
        data: pd.DataFrame,
        configuration: GenAIConfiguration | AgenticAIConfiguration,
        **kwargs
    ) -> list[AggregateMetricResult]:

        data_cols = data.columns.to_list()
        validate_tool_calls(data_cols, configuration)

        if self.method == "granite_guardian":
            kwargs["detector_params"] = {
                "risk_name": FUNCTION_CALL, "threshold": 0.001}
            tool_call_provider = DetectorsProvider(configuration=configuration,
                                                   metric_name=self.name,
                                                   metric_method=self.method,
                                                   metric_group=self.group,
                                                   thresholds=self.thresholds,
                                                   **kwargs)
            metric_result = await tool_call_provider.evaluate_async(data=data)
        elif self.method == "syntactic":
            tool_call_provider = ToolCallMetricProvider(
                configuration=configuration, metric=self)

            # Compute the metrics
            metric_result = await tool_call_provider.compute_metrics(data)
        return metric_result

    def evaluate(self, data: pd.DataFrame | dict,
                 configuration: GenAIConfiguration | AgenticAIConfiguration,
                 **kwargs):
        """
        Evaluate the data for ToolCallAccuracyMetric
        Args:
            data (pd.DataFrame | dict): Data to be evaluated
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metrics configuration
            **kwargs: Additional keyword arguments

        Returns:
            AggregateMetricResult: The computed metrics
        """
        # If ran in sync mode, block until it is done
        return run_in_event_loop(
            self.evaluate_async,
            data=data,
            configuration=configuration,
            **kwargs,
        )
