"""
This module provides utility functions for extracting system, user,
and assistant messages from various input formats.
"""

import logging
from urllib.parse import urlparse

from monocle_apptrace.instrumentation.common.utils import Option, try_option

DATA_INPUT_KEY = "data.input"

logger = logging.getLogger(__name__)
def extract_messages(args):
    """Extract system and user messages"""
    try:
        messages = []
        if args and isinstance(args, tuple) and len(args) > 0:
            if hasattr(args[0], "messages") and isinstance(args[0].messages, list):
                for msg in args[0].messages:
                    if hasattr(msg, 'content') and hasattr(msg, 'type'):
                        messages.append({msg.type: msg.content})
        return [str(d) for d in messages]
    except Exception as e:
        logger.warning("Warning: Error occurred in extract_messages: %s", str(e))
        return []


def extract_assistant_message(response):
    try:
        if isinstance(response, str):
            return [response]
        if hasattr(response, "content"):
            return [response.content]
        if hasattr(response, "message") and hasattr(response.message, "content"):
            return [response.message.content]
    except Exception as e:
        logger.warning("Warning: Error occurred in extract_assistant_message: %s", str(e))
        return []


def extract_provider_name(instance):
    provider_url: Option[str] = try_option(getattr, instance.client._client.base_url, 'host')
    if provider_url.is_none():
        provider_url = try_option(getattr, instance, 'api_base').and_then(lambda url: urlparse(url).hostname)

    return provider_url.unwrap_or(None)


# to be validated for non-langchain
def extract_inference_endpoint(instance):
    inference_endpoint: Option[str] = try_option(getattr, instance.client._client, 'base_url').map(str)
    if inference_endpoint.is_none():
        inference_endpoint = try_option(getattr, instance.client.meta, 'endpoint_url').map(str)

    if inference_endpoint.is_none():#for mistral API
        inference_endpoint = try_option(getattr, instance._client.sdk_configuration, 'server_url').map(str)    

    return inference_endpoint.unwrap_or(extract_provider_name(instance))