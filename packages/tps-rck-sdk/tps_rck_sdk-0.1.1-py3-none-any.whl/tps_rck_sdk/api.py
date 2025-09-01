#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCK SDK High-Level API.
Provides simplified, user-friendly functions for common RCK operations.
"""
import base64
import json
import re
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError

from .config import get_client
from .exceptions import RCKAPIError
from .model import (APIConfig, APIExample, APIInput, APIPipeline, APIProgram,
                    AttractorInputBase, AttractorOutputBase, ComputeConfig,
                    EndpointModel, EngineEnum, UnifiedAPIRequest)

T = TypeVar("T", bound=EndpointModel)
InputT = TypeVar("InputT", bound=AttractorInputBase)
OutputT = TypeVar("OutputT", bound=EndpointModel)


def structured_transform(
    input_text: str,
    output_schema: Type[T],
    function_logic: str,
    custom_logic: Optional[Dict[str, str]] = None,
    resources: Optional[List[Dict[str, str]]] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> T:
    """
    Transforms unstructured text into a structured Pydantic object. (Standard Engine)
    """
    client = get_client()

    # Build config
    cfg_overrides = config_overrides or {}
    cfg_overrides.setdefault("engine", EngineEnum.STANDARD)
    api_config = APIConfig(**cfg_overrides)

    # Build program
    api_input = APIInput(input=input_text, resource=resources)
    output_class_str = output_schema.to_json_schema_str()
    
    pipeline = APIPipeline(
        OutputDataClass=output_class_str,
        FunctionLogic=function_logic,
        CustomLogic=custom_logic,
    )
    program = APIProgram(input=api_input, Pipeline=pipeline)

    request = UnifiedAPIRequest(config=api_config, program=program)
    response = client.unified_compute(request, timeout=timeout)

    if not response.success or response.output is None:
        raise RCKAPIError("API call failed or returned empty output", response_body=response.raw)

    try:
        return output_schema.model_validate(response.output)
    except ValidationError as e:
        raise RCKAPIError(f"Failed to validate API response against schema '{output_schema.__name__}': {e}", response_body=response.output) from e


def learn_from_examples(
    input_model: InputT,
    output_schema: Type[OutputT],
    examples: List[Tuple[InputT, OutputT]],
    config_overrides: Optional[Dict[str, Any]] = None,
    custom_logic: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
) -> OutputT:
    """
    Transforms data by learning from examples. (Attractor Engine)
    """
    client = get_client()

    # Build config
    cfg_overrides = config_overrides or {}
    cfg_overrides.setdefault("engine", EngineEnum.ATTRACTOR)
    api_config = APIConfig(**cfg_overrides)

    # Build program
    api_input = APIInput(input=input_model.model_dump_json())
    
    api_examples = [
        APIExample(
            input=ex_in.model_dump_json(),
            output=ex_out.model_dump_json()
        )
        for ex_in, ex_out in examples
    ]

    pipeline = APIPipeline(Examples=api_examples, CustomLogic=custom_logic)
    program = APIProgram(input=api_input, Pipeline=pipeline)

    request = UnifiedAPIRequest(config=api_config, program=program)
    response = client.unified_compute(request, timeout=timeout)

    if not response.success or response.output is None:
        raise RCKAPIError("API call failed or returned empty output", response_body=response.raw)

    try:
        return output_schema.model_validate(response.output)
    except (ValidationError, json.JSONDecodeError) as e:
        raise RCKAPIError(f"Failed to validate/parse API response for schema '{output_schema.__name__}': {e}", response_body=response.output) from e


def generate_text(
    input_text: str,
    function_logic: str,
    custom_logic: Optional[Dict[str, str]] = None,
    resources: Optional[List[Dict[str, str]]] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> str:
    """
    Generates free-form text. (Pure Engine)
    """
    client = get_client()
    
    cfg_overrides = config_overrides or {}
    cfg_overrides.setdefault("engine", EngineEnum.PURE)
    api_config = APIConfig(**cfg_overrides)

    api_input = APIInput(input=input_text, resource=resources)
    pipeline = APIPipeline(FunctionLogic=function_logic, CustomLogic=custom_logic)
    program = APIProgram(input=api_input, Pipeline=pipeline)

    request = UnifiedAPIRequest(config=api_config, program=program)
    response = client.unified_compute(request, timeout=timeout)
    
    if not response.success or not isinstance(response.output, str):
        raise RCKAPIError(f"API call failed or returned non-string output: {type(response.output)}", response_body=response.raw)

    return response.output

def auto(
    input_text: str,
    function_logic: Optional[str] = None,
    output_schema: Optional[Type[T]] = None,
    examples: Optional[List[Tuple[InputT, OutputT]]] = None,
    composition: Optional[str] = None,
    lighting: Optional[str] = None,
    style: Optional[str] = None,
    custom_logic: Optional[Dict[str, str]] = None,
    resources: Optional[List[Dict[str, str]]] = None,
    timeout: Optional[float] = None,
) -> Union[T, "ImageResponse", str, Dict[str, Any]]:
    """
    Automatically determines the engine to use based on the provided parameters.

    This function calls the RCK API without an explicit `config`, allowing the
    backend's SolverService to choose the best engine and parameters.

    Args:
        input_text: The primary input text.
        function_logic: Natural language instructions for the task.
        output_schema: Optional Pydantic class for structured output.
        examples: Optional list of (input, output) examples for learning.
        composition: Image composition description.
        lighting: Image lighting description.
        style: Image artistic style.
        custom_logic: Optional custom key-value parameters.
        resources: Optional list of associated resources.
        timeout: Optional request timeout in seconds.

    Returns:
        The result, which can be a Pydantic object (if output_schema is provided),
        an ImageResponse, a plain string, or a dictionary.
    """
    client = get_client()

    # Build program
    api_input = APIInput(input=input_text, resource=resources)
    
    pipeline_params = {
        "FunctionLogic": function_logic,
        "CustomLogic": custom_logic,
        "frame_Composition": composition,
        "lighting": lighting,
        "style": style,
    }

    if output_schema:
        pipeline_params["OutputDataClass"] = output_schema.to_json_schema_str()

    if examples:
        pipeline_params["Examples"] = [
            APIExample(
                input=ex_in.model_dump_json(),
                output=ex_out.model_dump_json()
            )
            for ex_in, ex_out in examples
        ]

    pipeline = APIPipeline(**{k: v for k, v in pipeline_params.items() if v is not None})
    program = APIProgram(input=api_input, Pipeline=pipeline)

    # config is None for auto mode
    request = UnifiedAPIRequest(config=None, program=program)
    response = client.unified_compute(request, timeout=timeout)

    if not response.success or response.output is None:
        raise RCKAPIError("API call failed or returned empty output", response_body=response.raw)

    output = response.output

    # Determine output type
    if isinstance(output, str):
        return output
    
    if isinstance(output, list) and all(isinstance(item, str) and "data:image" in item for item in output):
        images = []
        for i, data_url in enumerate(output):
            details = _parse_data_url(data_url, i)
            if details:
                images.append(details)
        return ImageResponse(images=images, count=len(images))
        
    if isinstance(output, dict):
        if output_schema:
            try:
                return output_schema.model_validate(output)
            except ValidationError as e:
                raise RCKAPIError(f"Failed to validate 'auto' response against schema '{output_schema.__name__}': {e}", response_body=output) from e
        return output # Return raw dict if no schema provided

    # Fallback for unexpected types
    return output

class ImageDetails(BaseModel):
    """Details of a single generated image."""
    mimeType: str
    imageData: bytes  # Raw image bytes
    index: int
    size: int
    data_url: str

class ImageResponse(BaseModel):
    """The response structure for an image generation request."""
    images: List[ImageDetails]
    count: int

def _parse_data_url(data_url: str, index: int) -> Optional[ImageDetails]:
    match = re.match(r'^data:(.+?);base64,(.*)$', data_url)
    if not match:
        return None
    
    mime_type, b64_data = match.groups()
    image_data = base64.b64decode(b64_data)
    
    return ImageDetails(
        mimeType=mime_type,
        imageData=image_data,
        index=index,
        size=len(image_data),
        data_url=data_url
    )

def generate_image(
    input_text: str,
    composition: str,
    lighting: str,
    style: str,
    config_overrides: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None,
) -> ImageResponse:
    """
    Generates an image from a structured description. (Image Engine)
    """
    client = get_client()
    
    cfg_overrides = config_overrides or {}
    cfg_overrides.setdefault("engine", EngineEnum.IMAGE)
    api_config = APIConfig(**cfg_overrides)

    api_input = APIInput(input=input_text)
    pipeline = APIPipeline(
        frame_Composition=composition,
        lighting=lighting,
        style=style
    )
    program = APIProgram(input=api_input, Pipeline=pipeline)
    
    request = UnifiedAPIRequest(config=api_config, program=program)
    response = client.unified_compute(request, timeout=timeout)

    if not response.success or not isinstance(response.output, list):
        raise RCKAPIError("API call failed or returned invalid image data", response_body=response.raw)

    images = []
    for i, data_url in enumerate(response.output):
        if isinstance(data_url, str):
            details = _parse_data_url(data_url, i)
            if details:
                images.append(details)
    
    return ImageResponse(images=images, count=len(images))
