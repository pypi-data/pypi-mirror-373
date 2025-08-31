import openai
import aiohttp
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator, Union


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


def separate_config_parameters(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Separate known configuration parameters from extra OpenAI parameters
    
    Args:
        config: Full configuration object
        
    Returns:
        Object with known_params and extra_params
    """
    # USF-specific parameters that should NOT be passed to OpenAI API
    usf_specific_params = [
        'api_key', 'base_url', 'model', 'temperature', 'stop', 
        'date_time_override', 'backstory', 'goal', 'introduction', 'knowledge_cutoff', 'debug'
    ]
    
    known = {}
    extra = {}
    
    for key, value in config.items():
        if key in usf_specific_params:
            known[key] = value
        else:
            extra[key] = value
    
    return {'known_params': known, 'extra_params': extra}


def validate_date_time_override(override: Optional[Dict[str, Any]]) -> bool:
    """
    Validate date/time override format
    
    Args:
        override: Override object with date, time, timezone
        
    Returns:
        True if valid, false otherwise
    """
    if not override or not isinstance(override, dict):
        return False

    date = override.get('date')
    time = override.get('time')
    timezone = override.get('timezone')

    # All three must be provided
    if not date or not time or not timezone:
        return False

    # Validate date format: MM/DD/YYYY
    date_regex = r'^(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}$'
    if not re.match(date_regex, date):
        return False

    # Validate time format: HH:MM:SS AM/PM
    time_regex = r'^(0[1-9]|1[0-2]):[0-5]\d:[0-5]\d\s(AM|PM)$'
    if not re.match(time_regex, time):
        return False

    # Validate timezone is a non-empty string
    if not isinstance(timezone, str) or timezone.strip() == '':
        return False

    return True


def get_current_date_time_string(override: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate current date and time string in UTC format or with user override
    
    Args:
        override: Optional override object with date, time, timezone
        
    Returns:
        Formatted date/time string
    """
    # Check if override is provided and valid
    if override and override.get('enabled') and validate_date_time_override(override):
        date = override['date']
        time = override['time']
        timezone = override['timezone']
        return f'Current date: {date}, {time} ({timezone} Timezone). You can convert it to other time zones as required.'

    # Default UTC behavior
    now = datetime.utcnow()
    formatted_date = now.strftime('%m/%d/%Y, %I:%M:%S %p')
    
    return f'Current date: {formatted_date} (UTC Timezone). You can convert it to other time zones as required.'


def process_messages_for_final_response(
    messages: List[Dict[str, Any]], 
    date_time_override: Optional[Dict[str, Any]] = None,
    backstory: str = '',
    goal: str = '',
    introduction: str = '',
    knowledge_cutoff: str = ''
) -> List[Dict[str, Any]]:
    """
    Process messages for final response by filtering and reorganizing conversation history
    
    Args:
        messages: Array of message objects from the agent conversation
        date_time_override: Optional date/time override configuration
        backstory: Optional user backstory for system message enhancement
        goal: Optional user goal for system message enhancement
        
    Returns:
        Processed messages ready for final LLM call
    """
    if not messages or not isinstance(messages, list):
        raise Exception('Message Processing Error: Messages must be an array')

    # Extract different types of messages
    original_messages = [msg for msg in messages 
                        if msg.get('role') == 'user' and not msg.get('plan') and not msg.get('tool_calls')]
    
    tool_call_messages = [msg for msg in messages 
                         if msg.get('role') == 'assistant' and msg.get('tool_calls') and isinstance(msg.get('tool_calls'), list)]
    
    tool_response_messages = [msg for msg in messages 
                             if msg.get('role') == 'tool']
    
    # Get only the last planning message
    last_planning_message = None
    for msg in reversed(messages):
        if msg.get('role') == 'assistant' and (msg.get('plan') or msg.get('type') == 'agent_plan'):
            last_planning_message = msg
            break

    # Reconstruct chronological order of tool calls and responses
    tool_interactions = []
    
    # Create pairs of tool calls and their responses
    for tool_call in tool_call_messages:
        tool_interactions.append(tool_call)
        
        # Find corresponding tool responses for this tool call
        if tool_call.get('tool_calls'):
            corresponding_responses = [response for response in tool_response_messages 
                                     if any(call.get('id') == response.get('tool_call_id') 
                                           for call in tool_call['tool_calls'])]
            tool_interactions.extend(corresponding_responses)

    # Create system message with introduction and knowledge_cutoff
    system_content_parts = []
    
    # Add introduction first if provided
    if introduction and introduction.strip():
        system_content_parts.append(introduction.strip())
    
    # Add knowledge cutoff
    if knowledge_cutoff and knowledge_cutoff.strip():
        knowledge_part = f'Your Knowledge cutoff: {knowledge_cutoff.strip()}'
    else:
        knowledge_part = 'Your Knowledge cutoff: 15 January 2025'
    
    # Add current date/time
    date_time_string = get_current_date_time_string(date_time_override)
    
    # Combine system message parts
    if system_content_parts:
        system_content = f'{" ".join(system_content_parts)} {knowledge_part}; {date_time_string}'
    else:
        system_content = f'{knowledge_part}; {date_time_string}'
    
    # Build final message array starting with system message
    final_messages = [{'role': 'system', 'content': system_content}]
    
    # Add original user messages
    final_messages.extend(original_messages)
    
    # Add tool interactions
    final_messages.extend(tool_interactions)
    
    # Add last planning as user message with instruction
    if last_planning_message:
        instruction_text = """\n\n---\n\n<IMPORTANT>
- You cannot call any new tool now in any condition.
- If you don’t have enough information because something didn’t work or is missing, you still cannot use any new tool.
- Instead:
1) Choose the right opening based on who is responsible:
- If it’s our mistake: start with a clear, warm apology.
- If the issue is due to a tool or function failure, then do not say “sorry.” Instead, provide a brief, kind, and transparent overview in plain, non-technical language—without jargon or detailed explanations—so a layperson can understand.
2) Briefly explain the reason in the simplest, friendliest way—without technical terms or deep details. Do not mention words like “tools” or “functions.” Use plain, user-friendly words that fit the context, such as service, system, dashboard, provider, vendor and other user-friendly terms.
3) Say what you can do right now with the information you have. If possible, give a partial answer. If not possible, clearly and politely say you can’t complete it at this moment.
4) Keep the tone warm, respectful, and easy to understand for everyone. Never blame the user.
- If you do have enough information, share the full answer directly in a helpful way.
</IMPORTANT>"""
        
        # Add backstory and goal to the instruction if provided
        if backstory and backstory.strip():
            instruction_text += f'\n\n### User Backstory:\n{backstory.strip()}'

        if goal and goal.strip():
            instruction_text += f'\n\n### User Goal:\n{goal.strip()}'
        
        final_messages.append({
            'role': 'user',
            'content': (last_planning_message.get('content') or last_planning_message.get('plan') or '') + instruction_text
        })

    return final_messages


async def generate_final_response_with_openai(messages: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final response using OpenAI API directly
    
    Args:
        messages: Array of message objects from agent conversation
        config: Configuration object with api_key, base_url, model, temperature, stop
        
    Returns:
        Final response message
    """
    # Validate input parameters
    if not messages or not isinstance(messages, list):
        raise Exception('Final Response Error: Messages must be an array')

    if not config or not isinstance(config, dict):
        raise Exception('Final Response Error: Configuration object is required')

    if not config.get('api_key'):
        raise Exception('Final Response Error: API key is required')

    try:
        # Separate known parameters from extra OpenAI parameters
        separated = separate_config_parameters(config)
        known_params = separated['known_params']
        extra_params = separated['extra_params']
        
        # Process messages for final response
        processed_messages = process_messages_for_final_response(
            messages, 
            known_params.get('date_time_override'), 
            config.get('backstory', ''), 
            config.get('goal', ''),
            known_params.get('introduction', ''),
            known_params.get('knowledge_cutoff', '')
        )

        # Initialize OpenAI client
        client = openai.AsyncOpenAI(
            api_key=known_params['api_key'],
            base_url=known_params.get('base_url', 'https://api.us.inc/usf/v1')
        )

        # Build API call parameters with known parameters and extra parameters
        # NOTE: Do not include 'tools' parameter for final response as it causes API errors
        api_params = {
            'model': known_params.get('model', 'usf-mini'),
            'messages': processed_messages,
            'stream': False,
            'temperature': known_params.get('temperature', 0.7),
            'stop': known_params.get('stop', []),
            **extra_params  # Pass through any additional OpenAI parameters
        }

        # Debug logging
        _debug_log("Final Response API Call", {
            'url': f"{known_params.get('base_url', 'https://api.us.inc/usf/v1')}/chat/completions",
            'method': 'POST',
            'headers': {
                'Authorization': f'Bearer {known_params["api_key"][:10]}...{known_params["api_key"][-4:]}',
                'Content-Type': 'application/json'
            },
            'payload': api_params
        }, config)

        # Make API call
        try:
            response = await client.chat.completions.create(**api_params)
            _debug_log("Final Response API Success", {
                'response_type': type(response).__name__,
                'has_choices': bool(response.choices),
                'choice_count': len(response.choices) if response.choices else 0
            }, config)
        except Exception as api_error:
            _debug_log("Final Response API Error", {
                'error_type': type(api_error).__name__,
                'error_message': str(api_error),
                'api_params_sent': api_params
            }, config)
            raise api_error

        if not response.choices or not response.choices[0] or not response.choices[0].message:
            raise Exception('Final Response Error: Invalid response format from OpenAI API')

        return response.choices[0].message.model_dump()
    except Exception as error:
        # Re-throw errors with proper context
        if 'Final Response Error' in str(error):
            raise error
        raise Exception(f'Final Response Error: {str(error)}')


async def stream_final_response_with_openai(messages: List[Dict[str, Any]], config: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream final response using OpenAI API directly
    
    Args:
        messages: Array of message objects from agent conversation
        config: Configuration object with api_key, base_url, model, temperature, stop
        
    Yields:
        Response chunks
    """
    # Validate input parameters
    if not messages or not isinstance(messages, list):
        raise Exception('Streaming Final Response Error: Messages must be an array')

    if not config or not isinstance(config, dict):
        raise Exception('Streaming Final Response Error: Configuration object is required')

    if not config.get('api_key'):
        raise Exception('Streaming Final Response Error: API key is required')

    try:
        # Separate known parameters from extra OpenAI parameters
        separated = separate_config_parameters(config)
        known_params = separated['known_params']
        extra_params = separated['extra_params']
        
        # Process messages for final response
        processed_messages = process_messages_for_final_response(
            messages, 
            known_params.get('date_time_override'), 
            config.get('backstory', ''), 
            config.get('goal', ''),
            known_params.get('introduction', ''),
            known_params.get('knowledge_cutoff', '')
        )

        # Initialize OpenAI client
        client = openai.AsyncOpenAI(
            api_key=known_params['api_key'],
            base_url=known_params.get('base_url', 'https://api.us.inc/usf/v1')
        )

        # Build API call parameters with known parameters and extra parameters
        # NOTE: Do not include 'tools' parameter for final response as it causes API errors
        api_params = {
            'model': known_params.get('model', 'usf-mini'),
            'messages': processed_messages,
            'stream': True,
            'temperature': known_params.get('temperature', 0.7),
            'stop': known_params.get('stop', []),
            **extra_params  # Pass through any additional OpenAI parameters
        }

        # Debug logging
        _debug_log("Streaming Final Response API Call", {
            'url': f"{known_params.get('base_url', 'https://api.us.inc/usf/v1')}/chat/completions",
            'method': 'POST',
            'headers': {
                'Authorization': f'Bearer {known_params["api_key"][:10]}...{known_params["api_key"][-4:]}',
                'Content-Type': 'application/json'
            },
            'payload': api_params
        }, config)

        # Make streaming API call
        try:
            stream = await client.chat.completions.create(**api_params)
            _debug_log("Streaming Final Response API Success", {
                'stream_created': True,
                'stream_type': type(stream).__name__
            }, config)
        except Exception as api_error:
            _debug_log("Streaming Final Response API Error", {
                'error_type': type(api_error).__name__,
                'error_message': str(api_error),
                'api_params_sent': api_params
            }, config)
            raise api_error

        # Process streaming response
        async for chunk in stream:
            if chunk.choices and chunk.choices[0] and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield {
                    'content': chunk.choices[0].delta.content
                }
    except Exception as error:
        # Re-throw errors with proper context
        if 'Streaming Final Response Error' in str(error):
            raise error
        raise Exception(f'Streaming Final Response Error: {str(error)}')


async def get_final_response(messages: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle final response generation using direct LLM API
    
    Args:
        messages: Array of message objects in OpenAI format
        config: Configuration object with api_key, base_url, model, temperature, stop
        
    Returns:
        Final response message
    """
    # Validate input parameters
    if not messages or not isinstance(messages, list):
        raise Exception('Message Handler Error: Messages must be an array')

    if not config or not isinstance(config, dict):
        raise Exception('Message Handler Error: Configuration object is required')

    if not config.get('api_key'):
        raise Exception('Message Handler Error: API key is required')

    # Use user-provided base_url and model, with defaults
    base_url = config.get('base_url', 'https://api.us.inc/usf/v1')
    model = config.get('model', 'usf-mini')

    try:
        # Separate known parameters from extra OpenAI parameters
        separated = separate_config_parameters(config)
        known_params = separated['known_params']
        extra_params = separated['extra_params']
        
        # Process messages for final response with date/time override support
        final_messages = process_messages_for_final_response(
            messages, 
            known_params.get('date_time_override'), 
            config.get('backstory', ''), 
            config.get('goal', ''),
            known_params.get('introduction', ''),
            known_params.get('knowledge_cutoff', '')
        )

        if len(final_messages) == 0:
            raise Exception('Message Handler Error: No valid messages to process')

        # Build API call parameters with known parameters and extra parameters
        api_params = {
            'model': model,
            'messages': final_messages,
            'stream': False,
            'temperature': known_params.get('temperature', 0.7),
            'stop': known_params.get('stop', []),
            **extra_params  # Pass through any additional OpenAI parameters
        }

        # Debug logging
        _debug_log("Legacy Final Response API Call", {
            'url': f'{base_url}/chat/completions',
            'method': 'POST',
            'headers': {
                'Authorization': f'Bearer {known_params["api_key"][:10]}...{known_params["api_key"][-4:]}',
                'Content-Type': 'application/json'
            },
            'payload': api_params
        }, config)

        # Make API call to direct LLM endpoint for final response
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{base_url}/chat/completions',
                    headers={
                        'Authorization': f'Bearer {known_params["api_key"]}',
                        'Content-Type': 'application/json'
                    },
                    json=api_params
                ) as response:
                    if not response.ok:
                        # Try to get response body for better error details
                        try:
                            error_body = await response.json()
                            _debug_log("Legacy Final Response API Error Details", {
                                'status': response.status,
                                'reason': response.reason,
                                'error_body': error_body,
                                'api_params_sent': api_params
                            }, config)
                        except:
                            error_body = None
                        
                        status_text = response.reason or 'Unknown error'
                        error_message = f'Final response API call failed: {response.status} {status_text}'
                        
                        if error_body:
                            error_message += f'. Server response: {error_body}'
                        
                        if response.status == 401:
                            error_message += '. Please check your API key.'
                        elif response.status == 403:
                            error_message += '. Access forbidden. Please check your API key permissions.'
                        elif response.status == 404:
                            error_message += '. API endpoint not found. Please check the endpoint URL.'
                        elif response.status == 429:
                            error_message += '. Rate limit exceeded. Please wait before making more requests.'
                        elif response.status >= 500:
                            error_message += '. Server error. Please try again later.'
                        
                        raise Exception(error_message)

                    try:
                        data = await response.json()
                        _debug_log("Legacy Final Response API Success", {
                            'response_status': response.status,
                            'has_choices': bool(data.get('choices')),
                            'choice_count': len(data.get('choices', [])),
                            'response_data': data
                        }, config)
                    except Exception as error:
                        _debug_log("Legacy Final Response JSON Parse Error", {
                            'error': str(error),
                            'response_status': response.status
                        }, config)
                        raise Exception('Message Handler Response Error: Invalid JSON response from LLM API')

        except aiohttp.ClientError as error:
            raise Exception(f'Message Handler Network Error: Cannot connect to LLM API at {base_url}. Please check your internet connection.')
        except Exception as error:
            if 'Message Handler' in str(error):
                raise error
            raise Exception(f'Message Handler Network Error: {str(error)}')

        if not data.get('choices') or not data['choices'][0] or not data['choices'][0].get('message'):
            raise Exception('Message Handler Response Error: Invalid response format from LLM API')

        message = data['choices'][0]['message']
        if not message.get('content') and not message.get('tool_calls'):
            raise Exception('Message Handler Response Error: Empty response content from LLM API')

        return message
    except Exception as error:
        # Re-throw errors with proper context
        if 'Message Handler' in str(error):
            raise error
        raise Exception(f'Message Handler Error: {str(error)}')


async def stream_final_response(messages: List[Dict[str, Any]], config: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream final response generation using direct LLM API
    
    Args:
        messages: Array of message objects in OpenAI format
        config: Configuration object with api_key, base_url, model, temperature, stop
        
    Yields:
        Response chunks
    """
    # Validate input parameters
    if not messages or not isinstance(messages, list):
        raise Exception('Streaming Handler Error: Messages must be an array')

    if not config or not isinstance(config, dict):
        raise Exception('Streaming Handler Error: Configuration object is required')

    if not config.get('api_key'):
        raise Exception('Streaming Handler Error: API key is required')

    # Use user-provided base_url and model, with defaults
    base_url = config.get('base_url', 'https://api.us.inc/usf/v1')
    model = config.get('model', 'usf-mini')

    try:
        # Separate known parameters from extra OpenAI parameters
        separated = separate_config_parameters(config)
        known_params = separated['known_params']
        extra_params = separated['extra_params']
        
        # Process messages for final response with date/time override support
        final_messages = process_messages_for_final_response(
            messages, 
            known_params.get('date_time_override'), 
            config.get('backstory', ''), 
            config.get('goal', ''),
            known_params.get('introduction', ''),
            known_params.get('knowledge_cutoff', '')
        )

        if len(final_messages) == 0:
            raise Exception('Streaming Handler Error: No valid messages to process')

        # Build API call parameters with known parameters and extra parameters
        api_params = {
            'model': model,
            'messages': final_messages,
            'stream': True,
            'temperature': known_params.get('temperature', 0.7),
            'stop': known_params.get('stop', []),
            **extra_params  # Pass through any additional OpenAI parameters
        }

        # Debug logging
        _debug_log("Legacy Streaming Final Response API Call", {
            'url': f'{base_url}/chat/completions',
            'method': 'POST',
            'headers': {
                'Authorization': f'Bearer {known_params["api_key"][:10]}...{known_params["api_key"][-4:]}',
                'Content-Type': 'application/json'
            },
            'payload': api_params
        }, config)

        # Make API call to direct LLM endpoint for streaming final response
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{base_url}/chat/completions',
                    headers={
                        'Authorization': f'Bearer {known_params["api_key"]}',
                        'Content-Type': 'application/json'
                    },
                    json=api_params
                ) as response:
                    if not response.ok:
                        # Try to get response body for better error details
                        try:
                            error_body = await response.json()
                            _debug_log("Legacy Streaming Final Response API Error Details", {
                                'status': response.status,
                                'reason': response.reason,
                                'error_body': error_body,
                                'api_params_sent': api_params
                            }, config)
                        except:
                            error_body = None
                        
                        status_text = response.reason or 'Unknown error'
                        error_message = f'Streaming final response API call failed: {response.status} {status_text}'
                        
                        if error_body:
                            error_message += f'. Server response: {error_body}'
                        
                        if response.status == 401:
                            error_message += '. Please check your API key.'
                        elif response.status == 403:
                            error_message += '. Access forbidden. Please check your API key permissions.'
                        elif response.status == 404:
                            error_message += '. API endpoint not found. Please check the endpoint URL.'
                        elif response.status == 429:
                            error_message += '. Rate limit exceeded. Please wait before making more requests.'
                        elif response.status >= 500:
                            error_message += '. Server error. Please try again later.'
                        
                        raise Exception(error_message)

                    if not response.content:
                        raise Exception('Streaming Handler Error: No response body available for streaming')

                    # Process streaming response
                    async for line in response.content:
                        try:
                            chunk = line.decode('utf-8').strip()
                        except Exception as error:
                            raise Exception(f'Streaming Handler Error: Failed to decode stream chunk: {str(error)}')

                        # Parse the chunk and yield content
                        lines = [l for l in chunk.split('\n') if l.strip()]
                        
                        for line in lines:
                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    return
                                
                                try:
                                    parsed = json.loads(data)
                                    if (parsed.get('choices') and parsed['choices'][0] and 
                                        parsed['choices'][0].get('delta') and 
                                        parsed['choices'][0]['delta'].get('content')):
                                        yield {
                                            'content': parsed['choices'][0]['delta']['content']
                                        }
                                except json.JSONDecodeError:
                                    # Skip invalid JSON lines but don't throw error
                                    print(f'Streaming Handler Warning: Failed to parse JSON line: {data}')

        except aiohttp.ClientError as error:
            raise Exception(f'Streaming Handler Network Error: Cannot connect to LLM API at {base_url}. Please check your internet connection.')
        except Exception as error:
            if 'Streaming Handler' in str(error):
                raise error
            raise Exception(f'Streaming Handler Network Error: {str(error)}')
    except Exception as error:
        # Re-throw errors with proper context
        if 'Streaming Handler' in str(error):
            raise error
        raise Exception(f'Streaming Handler Error: {str(error)}')
