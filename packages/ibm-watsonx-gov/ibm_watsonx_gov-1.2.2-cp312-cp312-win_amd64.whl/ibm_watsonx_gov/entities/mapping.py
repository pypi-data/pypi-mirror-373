# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from typing import Annotated, List

from pydantic import BaseModel, Field


class MappingItem(BaseModel):
    """
    A mapping item is a single definition of how to extract a value from a span or trace and what key to use for the metric computation.
    """
    key: Annotated[str, Field(
        default="input_text", description="The name of the key to use for the metric computation.")]

    is_root_span: Annotated[bool, Field(
        default=False, description="If the span to search for information is the root span in the trace.")]

    span_name: Annotated[str | None, Field(
        default=None, description="The name of the span to extract from the spans.")]

    attribute_name: Annotated[str, Field(
        default="input", description="The name of the attribute to extract from the span. The following values are shorthand: \n"
        "1. 'input' : 'traceloop.entity.input' \n"
        "2. 'output' : 'traceloop.entity.output' \n"
        "3. 'conversation_id': 'traceloop.association.properties.thread_id'"
    )]

    json_path: Annotated[str | None, Field(
        default=None, description="The JSON path to use to extract the value from the span attribute. If not provided, the complete attribute value will be used.")]

    include_children: Annotated[bool, Field(
        default=True, description="If true, the children of the span will be included in searching for the attribute value.")]


class Mapping(BaseModel):
    """
    A mapping is a collection of mapping items.
    """

    items: Annotated[List[MappingItem], Field(
        description="The list of mapping items.")]
