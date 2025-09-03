# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import  ibm_watsonx_gov.tools.clients.detector_client as dc

from typing import Annotated, List, Optional, Type
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr




class HAPInput(BaseModel):
    """
        Model that can be used for setting input args for HAPDetectorTool
    """
    input: Annotated[str,
                     Field(..., description="Detect HAP for the given input")]
    threshold: Annotated[Optional[float], Field(
        0.8, description="Threshold for hap detection in the input, values range from 0.0 to 1.0")]


class HAPConfig(BaseModel):
    """
        Model that can be used for setting threshold for HAPDetectorTool
    """
    threshold: Annotated[Optional[float], Field(
        0.8, description="Threshold for hap detection in the input, values range from 0.0 to 1.0")]


class HAPDetectorTool(BaseTool):
    """
    Tool to detect Hate, Abuse and Profanity content in input string

    Examples:
        Basic usage
            .. code-block:: python

                hap_detector_tool = HAPDetectorTool()
                hap_detector_tool.invoke({"input":"<USER_INPUT>"})
    """
    name: str = "hap_detector"
    description: str = "Tool to detect Hate, Abuse and Profanity content in the input string"
    args_schema: Type[BaseModel] = HAPInput

    _url: any = PrivateAttr()
    _threshold: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config = HAPConfig(**kwargs)
        self._threshold = config.threshold
        self._url = dc.DETECTIONS_URL.format(dc.get_base_url())
        self._base_payload = dc.get_base_payload(dc.HAP,detector_params= {
                                                                            "threshold": 0.0
                                                                        })

    # Define HAP Tool
    def _run(self,
             input: str,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:
        """
        Detects Hate, Abuse and Profanity content in the input string

        Sample Response:
            {
              'detections': [{'start': 0,
                'end': 46,
                'text': '<USER_INPUT>',
                'detection_type': 'hap',
                'detection': 'has_HAP',
                'score': 0.9495730400085448,
                }],
              'is_hap_detected': True
            }
        """

        threshold = kwargs.get("threshold",self._threshold)
        # By default threshold is 0.0 and score is compared with the default/user provided threshold
       
        payload = dc.get_payload(self._base_payload,detector_payload={
                                                                        "input":input
                                                                     })
        response = dc.call_detections(self._url, payload)
        

        #Add boolean to response
        response["is_hap_detected"] = False
        for detection in response.get("detections"):
            if detection.get("score") > threshold:
                response["is_hap_detected"] = True
                break

        return response
    
    async def _arun(self,
                    input: str,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    **kwargs) -> List[str]:
        
        return self._run(input , kwargs)
