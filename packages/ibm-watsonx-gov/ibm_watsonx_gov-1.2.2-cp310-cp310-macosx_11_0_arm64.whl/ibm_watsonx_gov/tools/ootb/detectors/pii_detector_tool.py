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


class PIIInput(BaseModel):
    """
        Model that can be used for setting input args for PIIDetectorTool
    """
    input: Annotated[str,
                     Field(..., description="Detect PII for the given input")]


class PIIDetectorTool(BaseTool):
    """
    Tool to detect PII content in input string

    Examples:
        Basic usage
            .. code-block:: python

                pii_detector_tool = PIIDetectorTool()
                pii_detector_tool.invoke({"input":"<USER_INPUT>"})
    """
    name: str = "pii_detector"
    description: str = "Tool that detects Personally Identifiable Information(PII) information in the input string."
    args_schema: Type[BaseModel] = PIIInput
    _url: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._url = dc.DETECTIONS_URL.format(dc.get_base_url())
        self._base_payload = dc.get_base_payload(dc.PII)

    # Define PII Tool
    def _run(self,
             input: str,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:
        
        """
        Sample Response:
            {'detections': [{'start': 15,
                            'end': 30,
                            'text': 'johndoe@abc.com',
                            'detection_type': 'pii',
                            'detection': 'EmailAddress',
                            'score': 0.8}],
            'is_pii_detected': True}
        """
       
        payload = dc.get_payload(self._base_payload,detector_payload={
                                                                        "input":input
                                                                     })
        response = dc.call_detections(self._url, payload)
        

        if response.get("detections") == []:
            # No PII information detected
            response["is_pii_detected"] = False
        else:
            response["is_pii_detected"] = True

        return response
    
    async def _arun(self,
                    input: str,
                    run_manager: Optional[CallbackManagerForToolRun] = None,
                    **kwargs) -> List[str]:
        
        return self._run(input , kwargs)
