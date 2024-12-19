"""
This module provides utility functions for extracting system, user,
and assistant messages from various input formats.
"""

import json
import logging
from urllib.parse import urlparse

from monocle_apptrace.instrumentation.common.utils import (
    Option,
    get_keys_as_tuple,
    get_nested_value,
    try_option,
)

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


def extract_vectorstore_deployment(my_map):
    if isinstance(my_map, dict):
        if '_client_settings' in my_map:
            client = my_map['_client_settings'].__dict__
            host, port = get_keys_as_tuple(client, 'host', 'port')
            if host:
                return f"{host}:{port}" if port else host
        keys_to_check = ['client', '_client']
        host = __get_host_from_map(my_map, keys_to_check)
        if host:
            return host
    else:
        if hasattr(my_map, 'client') and '_endpoint' in my_map.client.__dict__:
            return my_map.client.__dict__['_endpoint']
        host, port = get_keys_as_tuple(my_map.__dict__, 'host', 'port')
        if host:
            return f"{host}:{port}" if port else host
    return None

def __get_host_from_map(my_map, keys_to_check):
    for key in keys_to_check:
        seed_connections = get_nested_value(my_map, [key, 'transport', 'seed_connections'])
        if seed_connections and 'host' in seed_connections[0].__dict__:
            return seed_connections[0].__dict__['host']
    return None

def resolve_from_alias(my_map, alias):
    """Find a alias that is not none from list of aliases"""

    for i in alias:
        if i in my_map.keys():
            return my_map[i]
    return None

def extract_prompt_input(args):
    input_arg_text = args[0]
    if isinstance(input_arg_text, str):
        return input_arg_text
    elif isinstance(input_arg_text, list):
        return', '.join([json.dumps(item) for item in input_arg_text])
    elif isinstance(input_arg_text, dict):
         return  json.dumps(input_arg_text)


def extract_prompt_output(result):
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        return', '.join([json.dumps(item) for item in result])
    elif isinstance(result, dict):
        return  json.dumps(result)
    
def is_root_span(curr_span) -> bool:
    return curr_span.parent is None