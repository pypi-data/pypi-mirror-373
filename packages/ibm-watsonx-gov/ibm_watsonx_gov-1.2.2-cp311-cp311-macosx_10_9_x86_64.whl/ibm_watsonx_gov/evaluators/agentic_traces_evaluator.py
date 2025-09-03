# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from datetime import timedelta
from typing import Annotated, Dict, Optional

from pydantic import Field

from ibm_watsonx_gov.entities.agentic_app import AgenticApp
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import AgentMetricResult
from ibm_watsonx_gov.entities.mapping import Mapping
from ibm_watsonx_gov.evaluators.base_evaluator import BaseEvaluator
from ibm_watsonx_gov.evaluators.impl.evaluate_metrics_impl import \
    _evaluate_metrics
from ibm_watsonx_gov.traces.span_util import flatten_attributes
from ibm_watsonx_gov.traces.trace_utils import TraceUtils


class AgenticTracesEvaluator(BaseEvaluator):
    """
    The class to evaluate agentic applications based on the traces generated.
    """
    agentic_app: Annotated[Optional[AgenticApp], Field(
        title="Agentic application configuration details", description="The agentic application configuration details.", default=None)]

    def compute_metrics(self, spans: list[dict], mapping: Mapping, **kwargs) -> list[AgentMetricResult]:
        """
        Computes the agentic metrics based on the spans/traces provided as a list.

        Args:
            spans (list[AgentMetricResult]): The spans on which the metrics need to be computed
            mapping (Mapping): The various mappings for finding the metric inputs.

        Returns:
            list[AgentMetricResult]: The computed metric results
        """
        span_trees = TraceUtils.build_span_trees(
            spans=spans, agentic_app=self.agentic_app)
        metrics_result = []
        for span_tree in span_trees:
            # Process only the spans that are associated with the agent application
            attrs = flatten_attributes(span_tree.span.attributes)
            if not attrs.get("traceloop.span.kind") == "workflow":
                continue

            data = span_tree.get_values(mapping)

            mr = self.compute_interaction_level_metrics(data, **kwargs)
            metrics_result.extend(mr)

        return metrics_result

    def compute_interaction_level_metrics(self, data: Dict, **kwargs) -> list[AgentMetricResult]:
        metric_results = []

        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time is None or end_time is None:
            raise Exception("start_time and/or end_time are missing.")

        interaction_id = data.get("interaction_id")
        conversation_id = data.get("conversation_id")

        if interaction_id is None or conversation_id is None:
            raise Exception(
                "interaction_id and/or conversation_id are missing.")

        duration: timedelta = (end_time - start_time)
        duration = duration.total_seconds()

        metric_results.append(AgentMetricResult(name="duration",
                                                value=duration,
                                                group=MetricGroup.PERFORMANCE,
                                                applies_to="interaction",
                                                interaction_id=interaction_id,
                                                conversation_id=conversation_id))

        if not self.agentic_app:
            return metric_results

        metric_result = _evaluate_metrics(configuration=self.agentic_app.metrics_configuration.configuration,
                                          data=data,
                                          metrics=self.agentic_app.metrics_configuration.metrics,
                                          metric_groups=self.agentic_app.metrics_configuration.metric_groups,
                                          api_client=kwargs.get("api_client")).to_dict()
        for mr in metric_result:
            node_result = {
                "applies_to": "interaction",
                "interaction_id": interaction_id,
                "conversation_id": conversation_id,
                **mr
            }

            metric_results.append(AgentMetricResult(**node_result))

        return metric_results
