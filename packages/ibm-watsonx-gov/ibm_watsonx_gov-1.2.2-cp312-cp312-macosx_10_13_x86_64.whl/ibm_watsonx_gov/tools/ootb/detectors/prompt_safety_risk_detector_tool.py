# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json
import ibm_watsonx_gov.tools.clients.detector_client as dc
from typing import Annotated, List, Optional, Type
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr


class PromptSafetyRiskInput(BaseModel):
    """
        Model that can be used for setting input args for PromptSafetyRiskTool
    """
    input: Annotated[str,
                     Field(..., description="Detect PromptSafetyRisk for the given input")]
    threshold: Annotated[Optional[float], Field(
        default=0.8, description="Threshold for prompt safety risk detection in the input, values range from 0.0 to 1.0")]
    system_prompt: Annotated[str,
                             Field(..., description="System prompt to configure the chatbot's behavior.")]
    enable_two_level_detection: Annotated[Optional[bool], Field(
        default=True, description="Enable or disable two level detection")]


class PromptSafetyRiskConfig(BaseModel):
    """
        Model that can be used for setting threshold for PromptSafetyRiskTool
    """
    threshold: Annotated[Optional[float], Field(
        default=0.8, description="Threshold for prompt safety risk detection in the input, values range from 0.0 to 1.0")]
    enable_two_level_detection: Annotated[Optional[bool], Field(
        default=False, description="Enable or disable two level detection")]


class PromptSafetyRiskDetectorTool(BaseTool):
    """
    Prompt Safety Risk tool measures the intent of jailbreak and/or prompt injection in the input sent to the LLM.

    Examples:
        Basic usage
            .. code-block:: python

                prompt_safety_detector_tool = PromptSafetyRiskTool()
                prompt_safety_detector_tool.invoke({"input":"<USER_INPUT>", "system_prompt":"<SYSTEM_PROMPT>"})
    """

    name: str = "prompt_safety_risk_detector"
    description: str = "Tool that detects off topic and prompt injection attempts in user input"
    args_schema: Type[BaseModel] = PromptSafetyRiskInput

    _threshold: any = PrivateAttr()
    _system_prompt: any = PrivateAttr()
    _url: any = PrivateAttr()
    _enable_two_level_detection: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config = PromptSafetyRiskConfig(**kwargs)
        self._threshold = config.threshold
        self._enable_two_level_detection = config.enable_two_level_detection
        self._url = dc.DETECTIONS_URL.format(dc.get_base_url())

    def _run(self,
             input: str,
             system_prompt:str,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:
        
        """
        Sample Response:
            {'detections': [{'start': 0,
                            'end': 36,
                            'text': '<USER_INPUT>',
                            'detection_type': 'topic_relevance',
                            'detection': 'off-topic',
                            'score': 0.9422797560691832}],
            'is_prompt_safety_risk_detected': True}
        """
        
        threshold = threshold = kwargs.get("threshold",self._threshold)
        enable_two_level_detection = kwargs.get("enable_two_level_detection",self._enable_two_level_detection)

        # Default or user provided threshold and enable_two_level_detection is passed to the endpoint
        detector_params = {
            "system_prompt": system_prompt,
            "enable_two_level_detection": enable_two_level_detection,
            "threshold": 0.0
        }

        base_payload = dc.get_base_payload(dc.PROMPT_SAFETY_RISK,detector_params)

        # payload = get_payload(
        #     self.detector_name, input, detector_params=detector_params)
        payload = dc.get_payload(base_payload,detector_payload={
                                                                        "input":input
                                                                     })
        response = dc.call_detections(self._url, payload)
        

        if len(response.get("detections")) > 0 and response.get("detections")[0].get("score") > threshold:
            response["is_prompt_safety_risk_detected"] = True
        else:
            response["is_prompt_safety_risk_detected"] = False
        return response
