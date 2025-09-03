# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from collections import defaultdict
from typing import List

import pandas as pd

from ibm_watsonx_gov.entities.ai_experiment import Node

AI_SERVICE_QUALITY = "ai_service_quality"

class AIExperimentUtils:
    """ Class for AI experiment related utility methods """

    @classmethod
    def construct_result_attachment_payload(cls, evaluation_results: dict, nodes: List[Node] = None):
        """
        Constructs payload for result attachment from experiment run's result
        Args:
            - evaluation_results: The dict of metrics from evaluators and custom.
        
        Returns: The payload for result attachment and total number of records processed
        """
        attachment_payload = {}
        node_name_to_id_map = {}
        if nodes is not None:
            node_name_to_id_map = {node.name: node.id for node in nodes}
        
        if not evaluation_results:
            raise ValueError("Evaluation result is empty or missing.")

        total_records = 0
        agent_evaluation_result = {
            "evaluation_result": {}
        }
        node_level_results = []
        node_name_to_node_object = {}

        # Separating agent level and node level metrics using the applies_to field in the result.
        for monitor_name, metric_results in evaluation_results.items():
            # If result for some monitor is empty, skipping it
            if not metric_results:
                continue
            agent_level_metrics = []
            node_level_metrics = defaultdict(list)

            for metric_result in metric_results:
                result_applies_to = metric_result.get(
                    "applies_to", "conversation")
                metric_id = metric_result.get("name", "")
                metric_result["id"] = metric_id
                metric_result["name"] = metric_id.capitalize().replace(
                    "_", " ")
                # If thresholds exist, add them to the run result
                thresholds = metric_result.pop("thresholds", [])
                if thresholds:
                    for threshold in thresholds:
                        metric_result[threshold.get(
                            "type")] = threshold.get("value")

                if result_applies_to == "node":
                    node_name = metric_result.pop("node_name", "")
                    if node_name and result_applies_to == "node":
                        node_level_metrics[node_name].append(metric_result)

                # agentic_result_components ["conversation", "interaction"]
                else:
                    if total_records == 0:
                        total_records = metric_result.get("count")
                    metric_id = f"{result_applies_to}_{metric_id}"
                    metric_result["id"] = metric_id
                    metric_result["name"] = metric_id.capitalize().replace(
                        "_", " ")
                    agent_level_metrics.append(metric_result)

            # Constructing the agent level metrics result
            agent_evaluation_result["evaluation_result"][monitor_name] = {
                "metric_groups": cls.get_result_with_metric_groups(agent_level_metrics)
            }

            # Constructing the node level metrics result
            for node_name, metrics in node_level_metrics.items():
                metric_groups_result = cls.get_result_with_metric_groups(
                    metrics)

                if node_name not in node_name_to_node_object:
                    node_obj = {
                        "type": "tool",
                        "id": node_name_to_id_map.get(node_name, node_name),
                        "name": node_name,
                        "evaluation_result": {}
                    }

                    node_obj["evaluation_result"][monitor_name] = {
                        "metric_groups": metric_groups_result
                    }
                    node_name_to_node_object[node_name] = node_obj
                    node_level_results.append(node_obj)

                else:
                    node_obj = node_name_to_node_object[node_name]
                    node_obj["evaluation_result"][monitor_name] = {
                        "metric_groups": metric_groups_result
                    }

        attachment_payload = {
            "ai_application": agent_evaluation_result,
            "nodes": node_level_results
        }

        return attachment_payload, total_records

    @classmethod
    def get_result_with_metric_groups(cls, metrics: list) -> list:
        """
        Organises the result based on metric groups
        Args:
            - metrics: The list of metrics
        
        Returns: The list containing metric groups and corresponding metrics for each group
        """
        metric_groups_map = defaultdict(list)
        for metric in metrics:
            metric_group = metric.pop("group", "Other metrics").capitalize().replace("_", " ")
            metric_groups_map[metric_group].append(metric)
        
        metric_groups_result = [
            {"name": group_name, "metrics": group_metrics} for group_name, group_metrics in metric_groups_map.items()]
        
        return metric_groups_result
