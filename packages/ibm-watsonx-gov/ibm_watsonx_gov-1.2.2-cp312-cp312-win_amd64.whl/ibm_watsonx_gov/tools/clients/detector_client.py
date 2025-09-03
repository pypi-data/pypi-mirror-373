# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json

import requests

import  ibm_watsonx_gov.tools.utils.environment as env
from ibm_watsonx_gov.tools.utils.tool_utils import get_headers
from ibm_watsonx_gov.utils.url_mapping import WATSONX_REGION_URLS


#Detector URLs
DETECTIONS_URL = "{}/ml/v1/text/detection?version=2023-10-25"
DETECTIONS_GENRATE_URL = "{}/ml/v1/text/detection/generated?version=2023-10-25"
DETECTIONS_CONTEXT_URL = "{}/ml/v1/text/detection/context?version=2023-10-25"
DETECTIONS_CHAT_URL = "{}/ml/v1/text/detection/chat?version=2023-10-25"


#Detector names
PII = "pii"
HAP = "hap"
GRANITE_GUADIAN = "granite_guardian"
TOPIC_RELEVANCE = "topic_relevance"
PROMPT_SAFETY_RISK = "prompt_safety_risk"


def get_base_url():
    is_cpd = env.get_is_cpd()

    if is_cpd:
        base_url = env.get_base_url()
    else:
        if env.get_wxai_url():
            base_url =  env.get_wxai_url()
        elif env.get_watsonx_region():
            region = env.get_watsonx_region()
            base_url = WATSONX_REGION_URLS.get(region).wml_url
        else:
            raise Exception(f"Environment variable 'WATSONX_REGION' and 'WXAI_URL' is missing.")
        
    return base_url


def get_base_payload(detector_name: str, detector_params: dict = {}):
    return {
        "detectors": {
            detector_name: detector_params
        }
    }


def get_payload(base_payload:dict, detector_payload:dict):
    return {**base_payload,**detector_payload}
    


def call_detections(url: str, payload: dict):
    #Set headers
    headers = get_headers()
    headers["x-governance-instance-id"] = env.get_service_instance_id()

    #Call the detections api
    response = requests.post(url=url, headers=headers, json=payload)
    response_status = response.status_code
    if response_status != 200:
        response = response.text if not isinstance(
            response, str) else response
        raise Exception(f"""Error while calling the detections endpoint. Details: status {response_status}
                        {str(json.loads(str(response)))}""")
    else:
        return json.loads(response.text)
