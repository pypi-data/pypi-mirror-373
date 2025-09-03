# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json

import  ibm_watsonx_gov.tools.clients.detector_client as dc

from typing import Annotated, List, Optional, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr


class JailBreakInput(BaseModel):
    """
        Model that can be used for setting input args for JailBreakDetectorTool
    """
    input: Annotated[str,
                     Field(..., description="Detect JailBreak for the given input")]
    threshold: Annotated[Optional[float], Field(
        0.8, description="Threshold for detecting jailbreak in the input, values range from 0.0 to 1.0")]


class JailBreakConfig(BaseModel):
    """
        Model that can be used for setting threshold for JailBreakDetectorTool
    """
    threshold: Annotated[Optional[float], Field(
        0.8, description="Threshold for detecting jailbreak in the input, values range from 0.0 to 1.0")]


class JailBreakDetectorTool(BaseTool):
    """
    Tool to detect deliberate circumvention of AI systems built-in safeguards or ethical guidelines.
    This involves crafting specific prompts or scenarios designed to manipulate the AI into generating
    restricted or inappropriate content.

    Examples:
        Basic usage
            .. code-block:: python

                jailbreak_detector_tool = JailBreakDetectorTool()
                jailbreak_detector_tool.invoke({"input":"<USER_INPUT>"})
    """

    name: str = "jailbreak_detector"
    description: str = """Tool that detects deliberate circumvention of AI systems built-in safeguards or ethical guidelines.
                        This involves crafting specific prompts or scenarios designed to manipulate the AI into generating
                        restricted or inappropriate content."""
    args_schema: Type[BaseModel] = JailBreakInput

    _url: any = PrivateAttr()
    _threshold: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config = JailBreakConfig(**kwargs)
        self._threshold = config.threshold
        self._url = dc.DETECTIONS_URL.format(dc.get_base_url())
        self._base_payload = dc.get_base_payload(dc.GRANITE_GUADIAN,detector_params= {
                                                                            "risk_name": "jailbreak",
                                                                            "threshold": 0.0
                                                                        })

    # Define JailBreak Tool
    def _run(self,
             input: str,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:
        """
         Sample Response:
            {'detections': [{'start': 0,
                            'end': 26,
                            'text': '<USER_INPUT>',
                            'detection_type': 'risk',
                            'detection': 'Yes',
                            'score': 0.9688562154769896}],
             'is_jailbreak_detected': True}
        """
        threshold = kwargs.get("threshold",self._threshold)
        payload = dc.get_payload(self._base_payload,detector_payload={
                                                                        "input":input
                                                                     })
        response = dc.call_detections(self._url, payload)

        if response.get("detections")[0].get("score") > threshold:
            response["is_jailbreak_detected"] = True
        else:
            response["is_jailbreak_detected"] = False
        return response
    
    async def _arun(self,
                    input: str,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    **kwargs) -> List[str]:
        
        return self._run(input , kwargs)
