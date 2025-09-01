#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core RCK API Client.
Handles HTTP requests, rate limiting, concurrency, and response parsing.
"""
import requests
import json
import logging
from typing import Any, Optional, Dict

from .model import RCKConfig, BaseProgram
from .exceptions import RCKAPIError
from ratelimit import sleep_and_retry

logger = logging.getLogger(__name__)

class RCKResponse:
    """Represents a response from the RCK API."""
    def __init__(self, output: Any, raw_response: Dict[str, Any]):
        self.output = output
        self.raw = raw_response
        self.success = "error" not in raw_response

class RCKClient:
    def __init__(self, config: Dict[str, Any], sdk_settings: Dict[str, Any]):
        self.config = config
        self.sdk_settings = sdk_settings
        self.semaphore = self.sdk_settings["concurrency_semaphore"]
        limiter = self.sdk_settings["limiter"]
        self.unified_compute = sleep_and_retry(limiter(self._unified_compute_impl))

    def _unified_compute_impl(self, request_model: UnifiedAPIRequest, timeout: Optional[float] = None) -> RCKResponse:
        """Executes any RCK program with concurrency control."""
        request_timeout = timeout if timeout is not None else self.sdk_settings["default_timeout"]

        payload = request_model.model_dump(by_alias=True, exclude_none=True)

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.config["api_key"]  # Use new Authorization header
        }
        
        logger.debug(f"Acquiring semaphore... (available: {getattr(self.semaphore, '_value', 'N/A')})")
        with self.semaphore:
            logger.debug("Semaphore acquired. Sending POST to /calculs...")
            try:
                resp = requests.post(
                    f"{self.config['base_url']}/calculs", 
                    json=payload, 
                    headers=headers, 
                    timeout=request_timeout
                )
                logger.debug(f"Received response: Status={resp.status_code}, Body='{resp.text}'")

                try:
                    data = resp.json()
                except json.JSONDecodeError:
                    raise RCKAPIError(f"Failed to decode JSON response: {resp.text}", resp.status_code, resp.text)

                if resp.status_code >= 400:
                    raise RCKAPIError(
                        data.get("details", f"API call failed with status {resp.status_code}"),
                        resp.status_code,
                        data
                    )
                
                output = data.get("output")
                return RCKResponse(output, data)

            except requests.exceptions.RequestException as e:
                raise RCKAPIError(f"Network request error: {e}") from e
            finally:
                logger.debug("Semaphore released.")
