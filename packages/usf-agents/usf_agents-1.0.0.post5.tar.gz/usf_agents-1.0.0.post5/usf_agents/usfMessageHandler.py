import openai
import aiohttp
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator


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
    Separate known configuration parameters from extra LLM client parameters
    
    Args:
        config: Full configuration object
        
    Returns:
        Object with known_params and extra_params
    """
    # USF-specific parameters that should NOT be passed directly to the LLM SDK
    usf_specific_params = [
        'api_key', 'model', 'provider', 'temperature', 'stop', 
        'date_time_override', 'backstory', 'goal', 'introduction', 'knowledge_cutoff', 'debug', 'base_url',
        'final_instruction_mode', 'final_instruction_text', 'final_instruction_append', 'disable_final_instruction'
    ]
    
    known: Dict[str, Any] = {}
    extra: Dict[str, Any] = {}
    
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


class BaseURLResolutionError(Exception):
    pass


async def _resolve_base_url_for_final_response(
    api_key: str,
    default_base_url: str,
    model: Optional[str],
    provider: Optional[str],
    debug_cfg: Dict[str, Any]
) -> str:
    """
    Resolve the OpenAI-compatible base URL for final response based on provider/model.
    - If provider is falsy: return default_base_url (no network call).
    - Else: call GET /usf/v1/usf-agent/get-base-url with headers { apiKey } and params.
      On any server-declared error (status:0) or HTTP error, raise BaseURLResolutionError with the raw JSON/text.
    """
    if not provider:
        return default_base_url

    base_resolver_url = 'https://api.us.inc/usf/v1/usf-agent/get-base-url'
    params: Dict[str, str] = {}
    if isinstance(provider, str) and provider.strip():
        params['provider'] = provider.strip()
    if isinstance(model, str) and model.strip():
        params['model'] = model.strip()

    _debug_log("Base URL Resolver Call", {
        'url': base_resolver_url,
        'method': 'GET',
        'headers': {
            'apiKey': f'{api_key[:10]}...{api_key[-4:]}' if isinstance(api_key, str) and len(api_key) >= 14 else '****',
        },
        'query': params
    }, debug_cfg)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                base_resolver_url,
                headers={'apiKey': api_key},
                params=params
            ) as resp:
                text = await resp.text()

                # Try to parse JSON body (both for success and error)
                parsed = None
                try:
                    parsed = json.loads(text)
                except Exception:
                    parsed = None

                if not resp.ok:
                    # Bubble server response verbatim (JSON if parsable, else raw text)
                    _debug_log("Base URL Resolver Error", {
                        'status': resp.status,
                        'reason': resp.reason,
                        'body': parsed if parsed is not None else text
                    }, debug_cfg)
                    raise BaseURLResolutionError(
                        json.dumps(parsed) if parsed is not None else text
                    )

                # Success path: expect {"status":1,"data":{"baseUrl": "...", ...}}
                if isinstance(parsed, dict) and parsed.get('status') == 1:
                    base_url = (parsed.get('data') or {}).get('baseUrl') or default_base_url
                    _debug_log("Base URL Resolver Success", {
                        'baseUrl': base_url,
                        'provider': (parsed.get('data') or {}).get('provider'),
                        'model': (parsed.get('data') or {}).get('model')
                    }, debug_cfg)
                    return base_url

                # Unexpected or status:0 JSON => bubble as-is
                raise BaseURLResolutionError(json.dumps(parsed) if parsed is not None else text)
    except BaseURLResolutionError:
        # Re-throw verbatim to keep exact server error visible upstream
        raise
    except aiohttp.ClientError as net_err:
        raise BaseURLResolutionError(str(net_err))
    except Exception as err:
        raise BaseURLResolutionError(str(err))


def build_final_instruction(
    base_instruction: str,
    mode: str = "default",
    overwrite_text: Optional[str] = None,
    append_text: Optional[str] = None
) -> str:
    """
    Build the final instruction block based on the selected mode.

    Modes:
    - "disable": return empty string (no instruction will be appended)
    - "overwrite": return overwrite_text exactly (or empty string if None)
    - "append": insert append_text just before </IMPORTANT> in base_instruction,
                prefixed with a "\n---\n" separator. If the closing tag is not
                found, append the separator and text to the end.
    - "default" or any other value: return base_instruction unchanged
    """
    try:
        normalized_mode = (mode or "default").strip().lower()
    except Exception:
        normalized_mode = "default"

    if normalized_mode == "disable":
        return ""

    if normalized_mode == "overwrite":
        return "\n\n---\n\n"+overwrite_text or ""

    if normalized_mode == "append":
        if not append_text or str(append_text).strip() == "":
            # Nothing to append; return base as-is
            return base_instruction
        closing_tag = "</IMPORTANT>"
        idx = base_instruction.rfind(closing_tag)
        if idx != -1:
            return (
                base_instruction[:idx]
                + "\n---\n"
                + str(append_text)
                + "\n"
                + closing_tag
                + base_instruction[idx + len(closing_tag):]
            )
        # Fallback: closing tag not found, append at end
        return base_instruction + "\n---\n" + str(append_text)

    # Default behavior: keep base instruction unchanged
    return base_instruction


def process_messages_for_final_response(
    messages: List[Dict[str, Any]], 
    date_time_override: Optional[Dict[str, Any]] = None,
    backstory: str = '',
    goal: str = '',
    introduction: str = '',
    knowledge_cutoff: str = '',
    final_instruction_mode: str = 'default',
    final_instruction_text: Optional[str] = None,
    final_instruction_append: Optional[str] = None,
    disable_final_instruction: Optional[bool] = None
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
    tool_interactions: List[Dict[str, Any]] = []
    
    for tool_call in tool_call_messages:
        tool_interactions.append(tool_call)
        if tool_call.get('tool_calls'):
            corresponding_responses = [response for response in tool_response_messages 
                                     if any(call.get('id') == response.get('tool_call_id') 
                                           for call in tool_call['tool_calls'])]
            tool_interactions.extend(corresponding_responses)

    # Create system message with introduction and knowledge_cutoff
    system_content_parts: List[str] = []
    
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
        base_instruction = """\n\n---\n\n<IMPORTANT>
You are now providing your FINAL response directly to the user. You CANNOT call any new tools under any circumstances.

Remember: The user cannot see any of your previous tool calls, function invocations, or their responses. To them, this is your first and only message.

### Follow these guidelines:

1. **Opening Based on Context:**
- If WE made an error or misunderstood: Start with a warm, sincere apology
- If a service/system had issues: Skip apologies. Instead, briefly acknowledge what happened using everyday language (e.g., "The search service had trouble finding that information" not "The web_search tool returned an error")

2. **Explain Simply:**
- Use plain, conversational language anyone can understand
- Avoid technical terms like "tools," "functions," "parameters," "API," etc.
- Use context-appropriate alternatives: service, system, search, database, provider, platform, etc.
- Keep explanations brief and relevant to what the user needs to know

3. **Provide What You Can:**
- If you have partial information: Share it clearly, noting any limitations
- If you cannot complete the request: Politely explain this and suggest alternatives when possible
- Focus on being helpful with whatever information is available
   
5. **Address their question directly**

Remember: This is your only chance to help the user with their current query. Make it count.
</IMPORTANT>"""
        
        # Determine effective mode (disable flag takes precedence)
        effective_mode = 'disable' if (disable_final_instruction is True) else (final_instruction_mode or 'default')
        
        # Build instruction per mode
        built_instruction = build_final_instruction(
            base_instruction,
            mode=effective_mode,
            overwrite_text=final_instruction_text,
            append_text=final_instruction_append
        )
        
        # Prepare addition: include backstory/goal only when instruction is present
        addition = ''
        if built_instruction and built_instruction.strip():
            addition = built_instruction
            if backstory and backstory.strip():
                addition += f'\n\n### User Backstory:\n{backstory.strip()}'
            if goal and goal.strip():
                addition += f'\n\n### User Goal:\n{goal.strip()}'
        
        final_messages.append({
            'role': 'user',
            'content': (last_planning_message.get('content') or last_planning_message.get('plan') or '') + addition
        })

    return final_messages


async def generate_final_response_with_openai(messages: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate final response using OpenAI-compatible client
    
    Args:
        messages: Array of message objects from agent conversation
        config: Configuration object with api_key, model, temperature, stop
        
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
        # Separate known parameters from extra client parameters
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
            known_params.get('knowledge_cutoff', ''),
            final_instruction_mode=known_params.get('final_instruction_mode'),
            final_instruction_text=known_params.get('final_instruction_text'),
            final_instruction_append=known_params.get('final_instruction_append'),
            disable_final_instruction=known_params.get('disable_final_instruction')
        )

        # Resolve base URL (if provider is provided, use resolver; else default)
        default_base_url = known_params.get('base_url', 'https://api.us.inc/usf/v1')
        model = known_params.get('model', 'usf-mini')
        provider = known_params.get('provider')

        base_url = await _resolve_base_url_for_final_response(
            known_params['api_key'],
            default_base_url,
            model,
            provider,
            config
        )

        # Initialize OpenAI-compatible client
        client = openai.AsyncOpenAI(
            api_key=known_params['api_key'],
            base_url=base_url
        )

        # Build API call parameters with known parameters and extra parameters
        # NOTE: Do not include 'tools' parameter for final response as it causes API errors
        api_params: Dict[str, Any] = {
            'model': known_params.get('model', 'usf-mini'),
            'messages': processed_messages,
            'stream': False,
            'temperature': known_params.get('temperature', 0.7),
            'stop': known_params.get('stop', []),
            **extra_params  # Pass through any additional SDK parameters
        }

        # Debug logging
        _debug_log("Final Response API Call", {
            'url': 'OpenAI SDK chat.completions',
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
            raise Exception('Final Response Error: Invalid response format from LLM API')

        return response.choices[0].message.model_dump()
    except BaseURLResolutionError as error:
        # Bubble resolver error verbatim (do not wrap)
        raise error
    except Exception as error:
        if 'Final Response Error' in str(error):
            raise error
        raise Exception(f'Final Response Error: {str(error)}')


async def stream_final_response_with_openai(messages: List[Dict[str, Any]], config: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream final response using OpenAI-compatible client
    
    Args:
        messages: Array of message objects from agent conversation
        config: Configuration object with api_key, model, temperature, stop
        
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
        # Separate known parameters from extra client parameters
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
            known_params.get('knowledge_cutoff', ''),
            final_instruction_mode=known_params.get('final_instruction_mode'),
            final_instruction_text=known_params.get('final_instruction_text'),
            final_instruction_append=known_params.get('final_instruction_append'),
            disable_final_instruction=known_params.get('disable_final_instruction')
        )

        # Resolve base URL (if provider is provided, use resolver; else default)
        default_base_url = known_params.get('base_url', 'https://api.us.inc/usf/v1')
        model = known_params.get('model', 'usf-mini')
        provider = known_params.get('provider')

        base_url = await _resolve_base_url_for_final_response(
            known_params['api_key'],
            default_base_url,
            model,
            provider,
            config
        )

        # Initialize OpenAI-compatible client
        client = openai.AsyncOpenAI(
            api_key=known_params['api_key'],
            base_url=base_url
        )

        # Build API call parameters with known parameters and extra parameters
        api_params: Dict[str, Any] = {
            'model': known_params.get('model', 'usf-mini'),
            'messages': processed_messages,
            'stream': True,
            'temperature': known_params.get('temperature', 0.7),
            'stop': known_params.get('stop', []),
            **extra_params
        }

        # Debug logging
        _debug_log("Streaming Final Response API Call", {
            'url': 'OpenAI SDK chat.completions (stream)',
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
    except BaseURLResolutionError as error:
        # Bubble resolver error verbatim (do not wrap)
        raise error
    except Exception as error:
        if 'Streaming Final Response Error' in str(error):
            raise error
        raise Exception(f'Streaming Final Response Error: {str(error)}')
