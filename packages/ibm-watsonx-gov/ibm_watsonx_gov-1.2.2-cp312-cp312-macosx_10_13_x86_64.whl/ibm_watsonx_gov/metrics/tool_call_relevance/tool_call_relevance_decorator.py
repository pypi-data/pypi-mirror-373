# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
from functools import partial
from typing import Callable, Optional

from ibm_watsonx_gov.config.agentic_ai_configuration import \
    AgenticAIConfiguration
from ibm_watsonx_gov.entities.enums import EvaluatorFields
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.metrics.base_metric_decorator import BaseMetricDecorator
from ibm_watsonx_gov.metrics.tool_call_relevance.tool_call_relevance_metric import \
    ToolCallRelevanceMetric
from ibm_watsonx_gov.providers.tool_call_metric_provider import \
    ToolCallMetricProvider
from ibm_watsonx_gov.utils.python_utils import parse_functions_to_openai_schema
from wrapt import decorator


class ToolCallRelevanceDecorator(BaseMetricDecorator):
    def evaluate_tool_call_relevance(self,
                                     func: Optional[Callable] = None,
                                     *,
                                     configuration: Optional[AgenticAIConfiguration] = None,
                                     metrics: list[GenAIMetric] = [
                                         ToolCallRelevanceMetric()
                                     ]
                                     ) -> dict:
        """
        An evaluation decorator for computing tool call relevance metric on an agentic node.
        """
        if func is None:
            return partial(self.evaluate_tool_call_relevance, configuration=configuration, metrics=metrics)

        if not metrics:
            metrics = [ToolCallRelevanceMetric()]

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.validate(func=func, metrics=metrics,
                              valid_metric_types=(ToolCallRelevanceMetric,))

                metric_inputs = [
                    EvaluatorFields.INPUT_FIELDS
                ]
                metric_outputs = [
                    EvaluatorFields.TOOL_CALLS_FIELD, EvaluatorFields.OUTPUT_FIELDS]

                if isinstance(configuration.tools, list) and all(callable(item) for item in configuration.tools):
                    configuration.tools = ToolCallMetricProvider.get_tools_list_schema(
                        configuration.tools)

                original_result = self.compute_helper(func=func, args=args, kwargs=kwargs,
                                                      configuration=configuration,
                                                      metrics=metrics,
                                                      metric_inputs=metric_inputs,
                                                      metric_outputs=metric_outputs)

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating tool call relevance metric on {func.__name__},") from ex

        return wrapper(func)
