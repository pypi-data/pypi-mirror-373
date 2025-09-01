#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCK SDK Configuration.
Handles global client setup, authentication, and SDK-level settings.
"""
from __future__ import annotations
import os
import threading
from typing import Optional, TYPE_CHECKING, Any, Dict
from ratelimit import limits, sleep_and_retry

from .model import ComputeConfig # Changed from BaseProgram
from .exceptions import RCKAPIError, RCKConfigurationError

if TYPE_CHECKING:
    from .rck_client import RCKClient

_client: Optional[RCKClient] = None
_config: Optional[Dict[str, Any]] = None # Store as dict
_sdk_settings = {
    "limiter": None,
    "concurrency_semaphore": None,
    "default_timeout": 60.0
}

def configure(
    api_key: Optional[str] = None,
    base_url: str = "https://rck-aehhddpisa.us-west-1.fcapp.run",
    rate_limit_calls: int = 15,
    rate_limit_period: int = 60,
    max_concurrent_requests: int = 5,
    default_timeout: float = 60.0,
):
    """
    Configures the SDK globally. This should be called once at the start of your application.
    """
    global _client, _config, _sdk_settings
    from .rck_client import RCKClient

    final_api_key = api_key or os.getenv("RCK_API_KEY")
    if not final_api_key:
        from .exceptions import RCKConfigurationError
        raise RCKConfigurationError("API key not provided. Pass it to configure() or set RCK_API_KEY env var.")

    if "rck-aehhddpisa" in base_url and not base_url.startswith("https://"):
        print(f"Warning: Using an insecure base URL ('{base_url}'). HTTPS is recommended.")

    _config = {"api_key": final_api_key, "base_url": base_url}

    _sdk_settings["limiter"] = limits(calls=rate_limit_calls, period=rate_limit_period)
    _sdk_settings["concurrency_semaphore"] = threading.Semaphore(max_concurrent_requests)
    _sdk_settings["default_timeout"] = default_timeout

    _client = RCKClient(config=_config, sdk_settings=_sdk_settings)

def get_client() -> RCKClient:
    """Gets the singleton RCKClient instance."""
    if _client is None:
        from .exceptions import RCKConfigurationError
        raise RCKConfigurationError("Please call rck_sdk.configure(api_key=...) to initialize the client first.")
    return _client

def get_sdk_settings() -> dict:
    """Gets the SDK-specific settings like limiter and semaphore."""
    if _config is None:
        from .exceptions import RCKConfigurationError
        raise RCKConfigurationError("Please call rck_sdk.configure(api_key=...) to initialize the client first.")
    return _sdk_settings

# The set_config function has been removed to simplify the configuration model.
# All compute parameters should be passed via `config_overrides` in API calls.
