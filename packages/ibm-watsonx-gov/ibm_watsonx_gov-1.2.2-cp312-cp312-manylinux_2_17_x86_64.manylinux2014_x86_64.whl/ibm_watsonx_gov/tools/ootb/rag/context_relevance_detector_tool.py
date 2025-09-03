# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, List, Optional, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

import ibm_watsonx_gov.tools.clients.detector_client as dc


class ContextRelevanceInput(BaseModel):
    """
        Model that can be used for setting input args for context relevance tool
    """
    input: Annotated[str,
                     Field(..., description="The original user input/question.")]
    context: Annotated[str,
                     Field(..., description="The retrieved or provided context to validate")]
    threshold: Annotated[Optional[float], Field(
        0.7, description="Threshold for answer relevance detection, values range from 0.0 to 1.0")]
    
    
class ContextRelevanceConfig(BaseModel):
    """
        Model that can be used for setting config args for context relevance tool
    """
    threshold: Annotated[Optional[float], Field(
        0.7, description="Threshold for answer relevance detection, values range from 0.0 to 1.0")]


class ContextRelevanceDetectorTool(BaseTool):
    """
    Tool to detect answer relevance for given input and response from LLM

    Examples:
        Basic usage
            .. code-block:: python

                context_relevance_detector = class ContextRelevanceDetectorTool(BaseTool)()
                context_relevance_detector.invoke({"input":"<USER_INPUT>","context":"<context retrieved>"})
    """
    name: str = "context_relevance_detector"
    description: str = ("Tool that analyzes whether the user input is relevant to the given context." \
    "It compares the input with the provided context and outputs a boolean along with a relevance score. ")
    args_schema: Type[BaseModel] = ContextRelevanceInput
    _url: any = PrivateAttr()
    _threshold: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config = ContextRelevanceConfig(**kwargs)
        self._threshold = config.threshold
        self._url = dc.DETECTIONS_CONTEXT_URL.format(dc.get_base_url())

    # Define Answer relevace tool
    def _run(self,
             input: str,
             context: str,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:
        """
        Sample Response:
            {
                "detections": [
                    {
                        "detection_type": "risk",
                        "detector_id": "granite_guardian_3_2_5b",
                        "score": 0.03726182132959366
                    }
                ],
                "is_context_relevant":True
            }
        """
        threshold = kwargs.get("threshold",self._threshold)

        #Get payload
        base_payload = dc.get_base_payload(dc.GRANITE_GUADIAN,
                                           detector_params={
                                                                "risk_name": "context_relevance",
                                                                "threshold": 0.0
                                                            })
        cr_payload = {
            "input":input,
            "context_type": "docs",
            "context": [context]
        }

        payload = {**base_payload,**cr_payload}
        detections_response = dc.call_detections(self._url, payload)

        #Remove unwanted properties
        detections = detections_response.get("detections",[])
        for detection in detections:
            detection.pop("detection",None)
        score = detections[0].get("score")

        #Propogate a boolen to get a intutive response
        is_context_relevant = False if score > threshold else True

        detections_response["detections"] = detections
        detections_response["is_context_relevant"] = is_context_relevant
        return detections_response
    
    async def _arun(self,
                    input: str,
                    context: str,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    **kwargs) -> List[str]:
        
        return self._run(input , context, kwargs)
