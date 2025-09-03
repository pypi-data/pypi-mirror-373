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


class TopicRelevanceDetectorInput(BaseModel):
    """
        Model that can be used for setting input args for TopicRelevanceDetectorTool
    """
    input: Annotated[str,
                     Field(..., description="Detect topic relevance for the given input")]
    threshold: Annotated[Optional[float], Field(
        default=0.8, description="Threshold for off-topic detection in the input, values range from 0.0 to 1.0")]
    system_prompt: Annotated[str,
                             Field(..., description="System prompt to configure the chatbot's behavior.")]


class TopicRelevanceDetectorConfig(BaseModel):
    """
        Model that can be used for setting threshold for TopicRelevanceDetectorTool
    """
    threshold: Annotated[Optional[float], Field(
        default=0.8, description="Threshold for off-topic detection in the input, values range from 0.0 to 1.0")]


class TopicRelevanceDetectorTool(BaseTool):
    """
    Tool that analyzes whether the user input is relevant to the topic defined in the system prompt and measures the degree of alignment.

    Examples:
        Basic usage
            .. code-block:: python

                topic_relevance_detector = TopicRelevanceDetectorTool()
                topic_relevance_detector.invoke({"input":"<USER_INPUT>", "system_prompt":"<SYSTEM_PROMPT>"})
    """

    name: str = "topic_relevance_detector"
    description: str = "Tool that analyzes whether the user input is relevant to the topic defined in the system prompt and measures the degree of alignment."
    args_schema: Type[BaseModel] = TopicRelevanceDetectorInput

    _threshold: any = PrivateAttr()
    _system_prompt: any = PrivateAttr()
    _url: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        config = TopicRelevanceDetectorConfig(**kwargs)
        self._threshold = config.threshold
        self._url = dc.DETECTIONS_URL.format(dc.get_base_url())

    def _run(self,
             input: str,
             system_prompt,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:
        """
        Sample Response:
            {'detections': [{'start': 0,
                            'end': 35,
                            'text': '<USER_INPUT>',
                            'detection_type': 'topic_relevance',
                            'detection': 'off-topic',
                            'score': 0.847662091255188}],
            'is_topic_relevant': False}
        """

        threshold = kwargs.get("threshold",self._threshold)
        # By default threshold is 0.0 and score is compared with the default/user provided threshold
        detector_params = {
            "system_prompt": system_prompt,
            "threshold": 0.0
        }

        base_payload = dc.get_base_payload(dc.TOPIC_RELEVANCE,detector_params)
        payload = dc.get_payload(base_payload,detector_payload={
                                                                        "input":input
                                                                     })
        response = dc.call_detections(self._url, payload)
        
        
        #Propogate boolean values
        if len(response.get("detections")) > 0 and response.get("detections")[0].get("score") > threshold:
            response["is_topic_relevant"] = False
        else:
            response["is_topic_relevant"] = True
        return response
