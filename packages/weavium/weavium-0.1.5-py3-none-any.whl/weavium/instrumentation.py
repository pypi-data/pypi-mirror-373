import json
import logging
from typing import Any, Dict, List, Optional, Union

try:
    import boto3
    import botocore.client
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from .client import WeaviumClient, LLMMessage

logger = logging.getLogger(__name__)


class Boto3InstrumentationError(Exception):
    """Exception raised when boto3 instrumentation fails."""
    pass


def instrument_bedrock(
    bedrock_client, 
    weavium_client: WeaviumClient = None, 
    callback=None, 
    skip_on_error: bool = False, 
    inject_only: bool = True
) -> None:
    """
    Instrument a bedrock client to automatically inject invoke model data into Weavium.
    
    Args:
        bedrock_client: The boto3 bedrock client to instrument
        weavium_client [optional]: The Weavium client instance to use for injection. If not provided, a default client will be created, which requires the WEAVIUM_API_KEY environment variable to be set.
        callback [optional]: An additional callback function to be called before the weavium injection.
        skip_on_error [optional]: If True, errors will be logged but not raised. If False (default), errors will be raised.
        inject_only [optional]: If True (default), only injection is performed. If False, raises an error as this mode is not yet supported.
    Raises:
        Boto3InstrumentationError: If boto3 is not available
        NotImplementedError: If inject_only is set to False (not yet supported)
    """
    if not inject_only:
        error_msg = "inject_only=False is not yet supported"
        if skip_on_error:
            logger.error(f"[Weavium] {error_msg}")
            return
        else:
            raise NotImplementedError(error_msg)
    
    if not weavium_client:
        weavium_client = WeaviumClient()
    
    if not BOTO3_AVAILABLE:
        raise Boto3InstrumentationError(
            "boto3 is not available. Install it with: pip install boto3"
        )
    
    def inject_body_hook(params, **kwargs):
        """Event handler for bedrock invoke model calls."""
        logger.info("[Weavium] InvokeModel hook started.")
        
        try: 
            if callback:
                callback(params, **kwargs)
        except Exception as e:
            error_msg = f"Error in bedrock instrumentation callback: {e}"
            logger.error(error_msg)
            if not skip_on_error:
                raise
        
        try:
            if not isinstance(params, dict):
                error_msg = "[Weavium] Invalid params format - expected dict, skipping injection"
                logger.warning(error_msg)
                if not skip_on_error:
                    raise ValueError("Invalid params format - expected dict")
                return
                
            body = params.get('body')
            url_path = params.get('url_path', '')
            
            if not body:
                error_msg = "[Weavium] No body found in request parameters, skipping injection"
                logger.warning(error_msg)
                if not skip_on_error:
                    raise ValueError("No body found in request parameters")
                return
                
            try:
                if isinstance(body, bytes):
                    body_str = body.decode('utf-8')
                elif isinstance(body, str):
                    body_str = body
                else:
                    error_msg = f"[Weavium] Unsupported body type: {type(body)}, skipping injection"
                    logger.warning(error_msg)
                    if not skip_on_error:
                        raise ValueError(f"Unsupported body type: {type(body)}")
                    return
                    
                body_data = json.loads(body_str)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                error_msg = f"[Weavium] Failed to parse request body: {e}, skipping injection"
                logger.warning(error_msg)
                if not skip_on_error:
                    raise
                return
            
            # Extract model ID from URL path
            model_id = ''
            if url_path and '/model/' in url_path:
                try:
                    model_id = url_path.split('/model/')[1].split('/')[0]
                    # URL decode the model ID
                    import urllib.parse
                    model_id = urllib.parse.unquote(model_id)
                except (IndexError, AttributeError):
                    pass
            
            api_params = {
                'modelId': model_id,
                'body': body_data
            }
            
            messages = _extract_messages_from_bedrock_request(api_params)
            if not messages:
                error_msg = "[Weavium] No valid messages extracted from request, skipping injection"
                logger.warning(error_msg)
                if not skip_on_error:
                    raise ValueError("No valid messages extracted from request")
                return
                
            for msg in messages:
                if not hasattr(msg, 'role') or not hasattr(msg, 'content'):
                    error_msg = "[Weavium] Invalid message structure detected, skipping injection"
                    logger.warning(error_msg)
                    if not skip_on_error:
                        raise ValueError("Invalid message structure detected")
                    return
                if not isinstance(msg.role, str) or not isinstance(msg.content, str):
                    error_msg = "[Weavium] Invalid message types detected, skipping injection"
                    logger.warning(error_msg)
                    if not skip_on_error:
                        raise ValueError("Invalid message types detected")
                    return
                    
            result = weavium_client.inject(messages=messages)
            logger.info(f"Successfully injected {len(messages)} messages to Weavium dataset: {result.dataset_id}")
                
        except Exception as e:
            error_msg = f"Error in bedrock instrumentation handler: {e}"
            logger.error(error_msg)
            if not skip_on_error:
                raise
    
    # Register both before and after call handlers
    bedrock_client.meta.events.register(
        "before-call.bedrock-runtime.InvokeModel",
        inject_body_hook
    )
    
    logger.info("[Weavium] Bedrock client instrumented.")


def _extract_messages_from_bedrock_request(api_params: Dict[str, Any]) -> List[LLMMessage]:
    """
    Extract messages from bedrock invoke model request parameters.
    
    Args:
        api_params: The API parameters from the bedrock invoke_model call
        
    Returns:
        List of LLMMessage objects extracted from the request
    """
    messages = []
    
    try:
        body_data = api_params.get('body')
        
        if isinstance(body_data, (bytes, str)):
            if isinstance(body_data, bytes):
                body_data = body_data.decode('utf-8')
            body_data = json.loads(body_data)
        
        try:
            if 'system' in body_data:
                messages.append(LLMMessage(role="system", content=body_data['system']))
            
            if 'messages' in body_data:
                for msg in body_data['messages']:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    
                    # Handle multipart content
                    if isinstance(content, list):
                        text_parts = []
                        for part in content:
                            if isinstance(part, dict):
                                if part.get('type') == 'text':
                                    text_parts.append(part.get('text', ''))
                                elif 'text' in part:
                                    text_parts.append(part.get('text', ''))
                        content = ' '.join(text_parts)
                    
                    if content:
                        messages.append(LLMMessage(role=role, content=content))
                        
            if messages:
                return messages
        except Exception:
            pass
        
        # Format 2: Simple prompt format
        try:
            if 'prompt' in body_data:
                messages.append(LLMMessage(role="user", content=body_data['prompt']))
                return messages
        except Exception:
            pass
        
        # Format 3: Amazon Titan format
        try:
            if 'inputText' in body_data:
                messages.append(LLMMessage(role="user", content=body_data['inputText']))
                return messages
        except Exception:
            pass
        
        # Format 4: Cohere format
        try:
            if 'chat_history' in body_data:
                for msg in body_data['chat_history']:
                    role = "user" if msg.get('role', '').upper() == 'USER' else "assistant"
                    content = msg.get('message', '')
                    if content:
                        messages.append(LLMMessage(role=role, content=content))
                        
            if 'message' in body_data:
                messages.append(LLMMessage(role="user", content=body_data['message']))
                
            if messages:
                return messages
        except Exception:
            pass
        
        # Format 5: Generic messages format
        try:
            if 'messages' in body_data:
                for msg in body_data['messages']:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if content:
                        messages.append(LLMMessage(role=role, content=content))
                        
            if messages:
                return messages
        except Exception:
            pass
    
    except Exception as e:
        logger.error(f"Error extracting messages from bedrock request: {e}")
    
    return messages