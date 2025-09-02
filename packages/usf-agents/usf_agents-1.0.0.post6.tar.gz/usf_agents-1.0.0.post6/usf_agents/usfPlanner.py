import aiohttp
import json
from typing import Dict, List, Any, Optional


def _debug_log(message: str, data: Any = None, config: Dict[str, Any] = None):
    """
    Debug logging function that outputs detailed information when debug mode is enabled
    
    Args:
        message: Debug message to log
        data: Optional data to include in the log
        config: Configuration object to check for debug mode
    """
    if config and config.get('debug'):
        print(f"\n{'='*60}")
        print(f"DEBUG: {message}")
        print(f"{'='*60}")
        if data is not None:
            if isinstance(data, dict) or isinstance(data, list):
                print(json.dumps(data, indent=2, default=str))
            else:
                print(str(data))
        print(f"{'='*60}\n")


def _sanitize_tools_for_openai(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert internal tool dicts (that may include non-serializable metadata like x_exec)
    into OpenAI-compatible tool objects suitable for JSON serialization.
    Keeps only {'type':'function','function': {'name','description','parameters'}}.
    """
    cleaned: List[Dict[str, Any]] = []
    for t in tools or []:
        if not isinstance(t, dict):
            continue
        fn = (t.get('function') or {})
        cleaned.append({
            'type': t.get('type', 'function'),
            'function': {
                'name': fn.get('name'),
                'description': fn.get('description', ''),
                'parameters': fn.get('parameters') or {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        })
    return cleaned


async def plan_with_usf(messages: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Plan using USF Agent SDK Plan API
    
    Args:
        messages: Array of message objects in OpenAI format
        config: Configuration object with api_key, tools, provider, model, introduction, knowledge_cutoff
        
    Returns:
        Planning result with plan, tool_choice, agent_status
    """
    # Validate input parameters
    if not messages or not isinstance(messages, list):
        raise Exception('Planning Error: Messages must be an array')

    if not config or not isinstance(config, dict):
        raise Exception('Planning Error: Configuration object is required')

    if not config.get('api_key'):
        raise Exception('Planning Error: API key is required')

    try:
        # Prepare request payload for Plan API
        request_body = {
            'messages': messages,
            'tools': _sanitize_tools_for_openai(config.get('tools', [])),
            'model': config.get('model', 'usf-mini')
        }

        # Optional provider routing
        provider = (config.get('provider') or '').strip() if isinstance(config.get('provider'), str) else config.get('provider')
        if provider:
            allowed_providers = {'openrouter', 'openai', 'claude', 'huggingface-inference', 'groq'}
            if not isinstance(provider, str):
                raise Exception('Planning Error: provider must be a string')
            if provider not in allowed_providers:
                raise Exception(f"Planning Error: Invalid provider '{provider}'. Allowed providers: {', '.join(sorted(allowed_providers))}")
            request_body['provider'] = provider

        # Add optional parameters if provided
        if config.get('introduction'):
            request_body['introduction'] = config['introduction']
        if config.get('knowledge_cutoff'):
            request_body['knowledge_cutoff'] = config['knowledge_cutoff']
        if config.get('backstory'):
            request_body['backstory'] = config['backstory']
        if config.get('goal'):
            request_body['goal'] = config['goal']

        # Debug logging
        _debug_log("Planning API Call", {
            'url': 'https://api.us.inc/usf/v1/usf-agent/plan',
            'method': 'POST',
            'headers': {
                'apiKey': f'{config["api_key"][:10]}...{config["api_key"][-4:]}',
                'Content-Type': 'application/json'
            },
            'payload': request_body
        }, config)

        # Make API call to USF Agent Plan API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.us.inc/usf/v1/usf-agent/plan',
                    headers={
                        'apiKey': config['api_key'],
                        'Content-Type': 'application/json'
                    },
                    json=request_body
                ) as response:
                    if not response.ok:
                        # Try to get response body for better error details
                        try:
                            error_body = await response.json()
                            _debug_log("Planning API Error Details", {
                                'status': response.status,
                                'reason': response.reason,
                                'error_body': error_body,
                                'request_body_sent': request_body
                            }, config)
                        except:
                            error_body = None
                        
                        status_text = response.reason or 'Unknown error'
                        error_message = f'Planning API call failed: {response.status} {status_text}'
                        
                        if error_body:
                            error_message += f'. Server response: {error_body}'
                        
                        if response.status == 401:
                            error_message += '. Please check your API key.'
                        elif response.status == 403:
                            error_message += '. Access forbidden. Please check your API key permissions.'
                        elif response.status == 404:
                            error_message += '. API endpoint not found.'
                        elif response.status == 429:
                            error_message += '. Rate limit exceeded. Please wait before making more requests.'
                        elif response.status >= 500:
                            error_message += '. Server error. Please try again later.'
                        
                        raise Exception(error_message)

                    try:
                        data = await response.json()
                        _debug_log("Planning API Success", {
                            'response_status': response.status,
                            'has_choices': bool(data.get('choices')),
                            'choice_count': len(data.get('choices', [])),
                            'response_data': data
                        }, config)
                    except Exception as error:
                        _debug_log("Planning JSON Parse Error", {
                            'error': str(error),
                            'response_status': response.status
                        }, config)
                        raise Exception('Planning Response Error: Invalid JSON response from USF Agent API')

        except aiohttp.ClientError as error:
            raise Exception(f'Planning Network Error: Cannot connect to USF Agent API. Please check your internet connection.')
        except Exception as error:
            if 'Planning' in str(error):
                raise error
            raise Exception(f'Planning Network Error: {str(error)}')

        # Check for API error response
        if data.get('status') == 0:
            msg = str(data.get('message') or '')
            # Normalize duplicate/invalid sequencing into a clear error
            if 'already exists' in msg.lower():
                raise Exception(f"Sequencing Error: {msg}. You attempted to call the Plan API while a previous plan is still active for this thread. Append tool results for the prior tool_calls or start a new thread.")
            raise Exception(f'Planning API Error: {msg}')

        if not data.get('choices') or not data['choices'][0] or not data['choices'][0].get('message'):
            raise Exception('Planning Response Error: Invalid response format from USF Agent API')

        message = data['choices'][0]['message']
        
        return {
            'plan': message.get('plan') or message.get('content') or '',
            'final_decision': message.get('final_decision') or '',
            'tool_choice': message.get('tool_choice'),
            'agent_status': message.get('agent_status') or 'preparing_final_response',
            'content': message.get('content') or '',
            'type': message.get('type') or 'agent_plan'
        }
    except Exception as error:
        # Re-throw errors with proper context
        if 'Planning' in str(error):
            raise error
        raise Exception(f'Planning Error: {str(error)}')


async def call_tool_with_usf(messages: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute tool call using USF Agent SDK Tool Call API
    
    Args:
        messages: Array of message objects including the plan response
        config: Configuration object with api_key, tools, tool_choice, provider, model, introduction, knowledge_cutoff
        
    Returns:
        Tool call result with tool_calls array
    """
    # Validate input parameters
    if not messages or not isinstance(messages, list):
        raise Exception('Tool Call Error: Messages must be an array')

    if not config or not isinstance(config, dict):
        raise Exception('Tool Call Error: Configuration object is required')

    if not config.get('api_key'):
        raise Exception('Tool Call Error: API key is required')

    if not config.get('tool_choice'):
        raise Exception('Tool Call Error: tool_choice is required')

    if not config.get('tools') or not isinstance(config['tools'], list):
        raise Exception('Tool Call Error: tools array is required')

    try:
        # Prepare request payload for Tool Call API
        request_body = {
            'messages': messages,
            'tools': _sanitize_tools_for_openai(config['tools']),
            'tool_choice': config['tool_choice'],
            'model': config.get('model', 'usf-mini')
        }

        # Optional provider routing
        provider = (config.get('provider') or '').strip() if isinstance(config.get('provider'), str) else config.get('provider')
        if provider:
            allowed_providers = {'openrouter', 'openai', 'claude', 'huggingface-inference', 'groq'}
            if not isinstance(provider, str):
                raise Exception('Tool Call Error: provider must be a string')
            if provider not in allowed_providers:
                raise Exception(f"Tool Call Error: Invalid provider '{provider}'. Allowed providers: {', '.join(sorted(allowed_providers))}")
            request_body['provider'] = provider

        # Add optional parameters if provided
        if config.get('introduction'):
            request_body['introduction'] = config['introduction']
        if config.get('knowledge_cutoff'):
            request_body['knowledge_cutoff'] = config['knowledge_cutoff']
        if config.get('backstory'):
            request_body['backstory'] = config['backstory']
        if config.get('goal'):
            request_body['goal'] = config['goal']

        # Debug logging
        _debug_log("Tool Call API Call", {
            'url': 'https://api.us.inc/usf/v1/usf-agent/tool-call',
            'method': 'POST',
            'headers': {
                'apiKey': f'{config["api_key"][:10]}...{config["api_key"][-4:]}',
                'Content-Type': 'application/json'
            },
            'payload': request_body
        }, config)

        # Make API call to USF Agent Tool Call API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.us.inc/usf/v1/usf-agent/tool-call',
                    headers={
                        'apiKey': config['api_key'],
                        'Content-Type': 'application/json'
                    },
                    json=request_body
                ) as response:
                    if not response.ok:
                        # Try to get response body for better error details
                        try:
                            error_body = await response.json()
                            _debug_log("Tool Call API Error Details", {
                                'status': response.status,
                                'reason': response.reason,
                                'error_body': error_body,
                                'request_body_sent': request_body
                            }, config)
                        except:
                            error_body = None
                        
                        status_text = response.reason or 'Unknown error'
                        error_message = f'Tool Call API call failed: {response.status} {status_text}'
                        
                        if error_body:
                            error_message += f'. Server response: {error_body}'
                        
                        if response.status == 401:
                            error_message += '. Please check your API key.'
                        elif response.status == 403:
                            error_message += '. Access forbidden. Please check your API key permissions.'
                        elif response.status == 404:
                            error_message += '. API endpoint not found.'
                        elif response.status == 429:
                            error_message += '. Rate limit exceeded. Please wait before making more requests.'
                        elif response.status >= 500:
                            error_message += '. Server error. Please try again later.'
                        
                        raise Exception(error_message)

                    try:
                        data = await response.json()
                        _debug_log("Tool Call API Success", {
                            'response_status': response.status,
                            'has_choices': bool(data.get('choices')),
                            'choice_count': len(data.get('choices', [])),
                            'response_data': data
                        }, config)
                    except Exception as error:
                        _debug_log("Tool Call JSON Parse Error", {
                            'error': str(error),
                            'response_status': response.status
                        }, config)
                        raise Exception('Tool Call Response Error: Invalid JSON response from USF Agent API')

        except aiohttp.ClientError as error:
            raise Exception(f'Tool Call Network Error: Cannot connect to USF Agent API. Please check your internet connection.')
        except Exception as error:
            if 'Tool Call' in str(error):
                raise error
            raise Exception(f'Tool Call Network Error: {str(error)}')

        # Check for API error response
        if data.get('status') == 0:
            msg = str(data.get('message') or '')
            # Normalize duplicate/invalid sequencing into a clear error
            if 'already exists' in msg.lower():
                raise Exception(f"Sequencing Error: {msg}. The Tool Call API must only be called after a plan suggests tools and before re-planning. Ensure correct ordering and provide tool results before the next plan.")
            raise Exception(f'Tool Call API Error: {msg}')

        if not data.get('choices') or not data['choices'][0] or not data['choices'][0].get('message'):
            raise Exception('Tool Call Response Error: Invalid response format from USF Agent API')

        message = data['choices'][0]['message']
        
        if not message.get('tool_calls') or not isinstance(message['tool_calls'], list):
            raise Exception('Tool Call Response Error: No tool_calls found in response')

        return {
            'tool_calls': message['tool_calls'],
            'agent_status': message.get('agent_status') or 'running',
            'type': message.get('type') or 'agent_tool_calls'
        }
    except Exception as error:
        # Re-throw errors with proper context
        if 'Tool Call' in str(error):
            raise error
        raise Exception(f'Tool Call Error: {str(error)}')
