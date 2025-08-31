from .usfPlanner import plan_with_usf, call_tool_with_usf
from .usfMessageHandler import (
    stream_final_response, 
    get_final_response, 
    generate_final_response_with_openai, 
    stream_final_response_with_openai
)
from typing import Dict, List, Any, Optional, Union, AsyncGenerator


class USFAgent:
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {}
            
        # Default configuration (fallback for all stages)
        self.default_config = {
            'api_key': config.get('api_key'),
            'base_url': config.get('base_url') or config.get('endpoint', 'https://api.us.inc/usf/v1'),
            'model': config.get('model', 'usf-mini'),
            'introduction': config.get('introduction', ''),
            'knowledge_cutoff': config.get('knowledge_cutoff', '15 January 2025'),
            'debug': config.get('debug', False)
        }
        
        # Store backstory and goal as instance properties
        self.backstory = config.get('backstory', '')
        self.goal = config.get('goal', '')
        
        # Stage-specific configurations with fallback to defaults
        self.planning_config = self._merge_config(self.default_config, config.get('planning', {}))
        self.tool_calling_config = self._merge_config(self.default_config, config.get('tool_calling', {}))
        self.final_response_config = self._merge_config(self.default_config, config.get('final_response', {}))
        
        # Legacy properties for backward compatibility
        self.api_key = self.default_config['api_key']
        self.endpoint = self.default_config['base_url']
        self.model = self.default_config['model']
        self.stream = config.get('stream', False)
        self.introduction = self.default_config['introduction']
        self.knowledge_cutoff = self.default_config['knowledge_cutoff']
        
        # Loop configuration
        self.max_loops = config.get('max_loops', 20)  # Default to 20 loops
        
        # Memory configuration
        self.temp_memory = config.get('temp_memory', {})
        self.memory = {
            'messages': [],
            'enabled': self.temp_memory.get('enabled', False),
            'max_length': self.temp_memory.get('max_length', 10),
            'auto_trim': self.temp_memory.get('auto_trim', True)
        }
        
        # Enhanced API key validation
        self._validate_configuration()

    def _merge_config(self, default_config: Dict[str, Any], stage_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'api_key': stage_config.get('api_key') or default_config['api_key'],
            'base_url': stage_config.get('base_url') or default_config['base_url'],
            'model': stage_config.get('model') or default_config['model'],
            'introduction': stage_config.get('introduction') or default_config['introduction'],
            'knowledge_cutoff': stage_config.get('knowledge_cutoff') or default_config['knowledge_cutoff'],
            'temperature': stage_config.get('temperature'),
            'stop': stage_config.get('stop'),
            'debug': stage_config.get('debug') or default_config.get('debug'),
            **{k: v for k, v in stage_config.items() if k not in ['api_key', 'base_url', 'model', 'introduction', 'knowledge_cutoff', 'temperature', 'stop', 'debug']}
        }

    def _validate_configuration(self):
        if not self.api_key:
            raise Exception('USFAgent Error: API key is required. Please provide a valid API key from https://us.inc')
        
        if not isinstance(self.api_key, str) or self.api_key.strip() == '':
            raise Exception('USFAgent Error: API key must be a non-empty string. Please check your API key from https://us.inc')
        
        if self.endpoint and not isinstance(self.endpoint, str):
            raise Exception('USFAgent Error: Endpoint must be a valid URL string')
        
        if self.model and not isinstance(self.model, str):
            raise Exception('USFAgent Error: Model must be a valid string')

        if self.introduction and not isinstance(self.introduction, str):
            raise Exception('USFAgent Error: Introduction must be a string')

        if self.knowledge_cutoff and not isinstance(self.knowledge_cutoff, str):
            raise Exception('USFAgent Error: Knowledge cutoff must be a string')

        if self.max_loops is not None and (not isinstance(self.max_loops, int) or self.max_loops < 1 or self.max_loops > 100):
            raise Exception('USFAgent Error: max_loops must be a positive number between 1 and 100')

        if self.backstory and not isinstance(self.backstory, str):
            raise Exception('USFAgent Error: backstory must be a string')

        if self.goal and not isinstance(self.goal, str):
            raise Exception('USFAgent Error: goal must be a string')

    def _create_detailed_error(self, original_error: Exception, context: str) -> Exception:
        error_message = str(original_error)
        
        # Check for common error patterns and provide helpful guidance
        if '401' in error_message or 'Unauthorized' in error_message:
            return Exception(f'USFAgent API Error: Invalid API key. Please check your API key from https://us.inc and ensure it\'s valid. Original error: {error_message}')
        
        if '403' in error_message or 'Forbidden' in error_message:
            return Exception(f'USFAgent API Error: Access forbidden. Your API key may not have the required permissions or may be expired. Please check your account at https://us.inc. Original error: {error_message}')
        
        if '404' in error_message or 'Not Found' in error_message:
            return Exception(f'USFAgent API Error: API endpoint not found. Please check if the endpoint URL is correct. Original error: {error_message}')
        
        if '429' in error_message or 'Too Many Requests' in error_message:
            return Exception(f'USFAgent API Error: Rate limit exceeded. Please wait a moment before making more requests. Original error: {error_message}')
        
        if any(code in error_message for code in ['500', '502', '503', 'Bad Gateway', 'Service Unavailable']):
            return Exception(f'USFAgent API Error: Server error from USF API. This is usually temporary. Please try again in a few moments. If the problem persists, check the status at https://us.inc. Original error: {error_message}')
        
        if any(term in error_message for term in ['ENOTFOUND', 'ECONNREFUSED', 'network']):
            return Exception(f'USFAgent Network Error: Cannot connect to USF API. Please check your internet connection and ensure the endpoint is accessible. Original error: {error_message}')
        
        # Generic error with context
        return Exception(f'USFAgent Error in {context}: {error_message}')

    # Add messages to memory
    def _add_to_memory(self, messages: List[Dict[str, Any]]):
        if not self.memory['enabled']:
            return
        
        # Add new messages to memory
        self.memory['messages'].extend(messages)
        
        # Auto-trim if enabled
        if self.memory['auto_trim'] and len(self.memory['messages']) > self.memory['max_length']:
            # Keep the most recent messages with a maximum of max_length
            self.memory['messages'] = self.memory['messages'][-self.memory['max_length']:]

    # Get messages from memory + new messages
    def _get_messages_with_memory(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.memory['enabled']:
            return messages
        
        # Combine memory messages with new messages
        return self.memory['messages'] + messages

    async def run(self, messages: Union[str, List[Dict[str, Any]]], options: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        if options is None:
            options = {}
            
        try:
            # Validate input parameters
            self._validate_run_parameters(messages, options)
            
            # Handle both string and array formats for messages
            formatted_messages = []
            if isinstance(messages, str):
                formatted_messages = [{'role': 'user', 'content': messages}]
            elif isinstance(messages, list):
                formatted_messages = messages
            else:
                raise Exception('USFAgent Error: Messages must be either a string or an array of message objects')
            
            # Get messages with memory context
            messages_with_context = self._get_messages_with_memory(formatted_messages)
            
            # Check if messages already contain tool results that indicate we should continue from a previous state
            has_tool_results = any(msg.get('role') == 'tool' for msg in messages_with_context)
            
            # If we have tool results, we need to continue the planning/tool cycle
            if has_tool_results:
                # Find the last agent plan message to understand current state
                last_plan_index = -1
                for i in range(len(messages_with_context) - 1, -1, -1):
                    msg = messages_with_context[i]
                    if msg.get('role') == 'assistant' and (msg.get('type') == 'agent_plan' or msg.get('plan')):
                        last_plan_index = i
                        break
                
                if last_plan_index == -1:
                    raise Exception('USFAgent Error: Tool results found but no corresponding plan message')
                
                # Continue from where we left off
                messages_with_context = (messages_with_context[:last_plan_index + 1] + 
                                       messages_with_context[last_plan_index + 1:])

            # Create stage-specific configurations with option overrides
            plan_config = {
                **self.planning_config,
                'tools': options.get('tools', []),
                'backstory': self.backstory,
                'goal': self.goal,
            }
            
            # Allow per-request overrides for planning
            if options.get('planning'):
                plan_config.update({
                    'api_key': options['planning'].get('api_key') or self.planning_config['api_key'],
                    'base_url': options['planning'].get('base_url') or self.planning_config['base_url'],
                    'model': options['planning'].get('model') or self.planning_config['model'],
                    'introduction': options['planning'].get('introduction') or self.planning_config['introduction'],
                    'knowledge_cutoff': options['planning'].get('knowledge_cutoff') or self.planning_config['knowledge_cutoff']
                })

            tool_config = {
                **self.tool_calling_config,
                'tools': options.get('tools', []),
                'backstory': self.backstory,
                'goal': self.goal,
            }
            
            # Allow per-request overrides for tool calling
            if options.get('tool_calling'):
                tool_config.update({
                    'api_key': options['tool_calling'].get('api_key') or self.tool_calling_config['api_key'],
                    'base_url': options['tool_calling'].get('base_url') or self.tool_calling_config['base_url'],
                    'model': options['tool_calling'].get('model') or self.tool_calling_config['model'],
                    'introduction': options['tool_calling'].get('introduction') or self.tool_calling_config['introduction'],
                    'knowledge_cutoff': options['tool_calling'].get('knowledge_cutoff') or self.tool_calling_config['knowledge_cutoff']
                })

            final_config = {
                **self.final_response_config,
                'backstory': self.backstory,
                'goal': self.goal,
            }
            
            # Allow per-request overrides for final response
            if options.get('final_response'):
                final_config.update({
                    'api_key': options['final_response'].get('api_key') or self.final_response_config['api_key'],
                    'base_url': options['final_response'].get('base_url') or self.final_response_config['base_url'],
                    'model': options['final_response'].get('model') or self.final_response_config['model'],
                    'temperature': options['final_response'].get('temperature') or self.final_response_config.get('temperature'),
                    'stop': options['final_response'].get('stop') or self.final_response_config.get('stop')
                })
            
            # Legacy option overrides (for backward compatibility)
            final_config.update({
                'temperature': options.get('temperature') or final_config.get('temperature'),
                'stop': options.get('stop') or final_config.get('stop'),
                # Date/time override support
                'date_time_override': options.get('date_time_override') or final_config.get('date_time_override'),
                # Debug mode override support
                'debug': options.get('debug') or final_config.get('debug')
            })

            # Also apply debug override to planning and tool configs
            if options.get('debug') is not None:
                plan_config['debug'] = options['debug']
                tool_config['debug'] = options['debug']

            # Main agent loop - continue until agent decides no more tools are needed
            current_messages = messages_with_context.copy()
            agent_status = 'running'
            loop_count = 0
            max_loops = options.get('max_loops', self.max_loops)  # Use configurable max loops

            while agent_status == 'running' and loop_count < max_loops:
                loop_count += 1

                # Step 1: Plan using USF Agent SDK Plan API with planning-specific config
                try:
                    planning_result = await plan_with_usf(current_messages, plan_config)
                except Exception as error:
                    raise self._create_detailed_error(error, 'planning phase')

                # Update agent status
                agent_status = planning_result['agent_status']

                # Yield planning result
                yield {
                    'type': 'plan',
                    'content': planning_result['content'],
                    'plan': planning_result['plan'],
                    'final_decision': planning_result['final_decision'],
                    'agent_status': agent_status,
                    'tool_choice': planning_result['tool_choice']
                }

                # Add plan message to current conversation
                current_messages.append({
                    'role': 'assistant',
                    'content': planning_result['content'],
                    'plan': planning_result['plan'],
                    'final_decision': planning_result['final_decision'],
                    'agent_status': agent_status,
                    'tool_choice': planning_result['tool_choice'],
                    'type': planning_result['type']
                })

                # Step 2: If tools are needed, call Tool Call API with tool-calling-specific config
                if planning_result['tool_choice'] and agent_status == 'running':
                    try:
                        tool_call_result = await call_tool_with_usf(current_messages, {
                            **tool_config,
                            'tool_choice': planning_result['tool_choice']
                        })
                    except Exception as error:
                        raise self._create_detailed_error(error, 'tool call phase')

                    # Add tool call message to conversation
                    current_messages.append({
                        'role': 'assistant',
                        'content': '',
                        'tool_calls': tool_call_result['tool_calls'],
                        'type': tool_call_result['type']
                    })

                    # Update agent status
                    agent_status = tool_call_result['agent_status']

                    # Yield tool calls for execution
                    yield {
                        'type': 'tool_calls',
                        'tool_calls': tool_call_result['tool_calls'],
                        'agent_status': agent_status
                    }

                    # Stop here and wait for tool results to be added externally
                    # The user will add tool results and call run() again
                    break
                else:
                    # No tools needed, break the loop
                    break

            # If we've reached the end of the planning cycle or agent_status is not 'running'
            if agent_status != 'running' or loop_count >= max_loops:
                # Step 3: Generate final answer
                try:
                    # Check if agent status is preparing_final_response to use OpenAI-based handler
                    if agent_status == 'preparing_final_response':
                        # Use new OpenAI-based final response handling
                        if self.stream:
                            # Stream final response using OpenAI
                            full_content = ''
                            try:
                                async for chunk in stream_final_response_with_openai(current_messages, final_config):
                                    full_content += chunk['content']
                                    yield {
                                        'type': 'final_answer',
                                        'content': chunk['content']
                                    }
                                # Add clean messages and final response to memory after streaming completes
                                clean_messages = [msg for msg in formatted_messages 
                                                if msg.get('role') == 'user' and not msg.get('plan') and not msg.get('tool_calls')]
                                self._add_to_memory([
                                    *clean_messages,
                                    {'role': 'assistant', 'content': full_content}
                                ])
                            except Exception as error:
                                raise self._create_detailed_error(error, 'OpenAI streaming response generation')
                        else:
                            # Non-streaming final response using OpenAI
                            try:
                                final_response = await generate_final_response_with_openai(current_messages, final_config)
                            except Exception as error:
                                raise self._create_detailed_error(error, 'OpenAI final response generation')
                            
                            # Add clean messages and final response to memory (only original user messages + final response)
                            clean_messages = [msg for msg in formatted_messages 
                                            if msg.get('role') == 'user' and not msg.get('plan') and not msg.get('tool_calls')]
                            self._add_to_memory([
                                *clean_messages,
                                {'role': 'assistant', 'content': final_response['content']}
                            ])
                            
                            yield {
                                'type': 'final_answer',
                                'content': final_response['content']
                            }
                    else:
                        # Use legacy final response handling for backward compatibility
                        if self.stream:
                            # Stream final response
                            full_content = ''
                            try:
                                async for chunk in stream_final_response(current_messages, final_config):
                                    full_content += chunk['content']
                                    yield {
                                        'type': 'final_answer',
                                        'content': chunk['content']
                                    }
                                # Add clean messages and final response to memory after streaming completes
                                clean_messages = [msg for msg in formatted_messages 
                                                if msg.get('role') == 'user' and not msg.get('plan') and not msg.get('tool_calls')]
                                self._add_to_memory([
                                    *clean_messages,
                                    {'role': 'assistant', 'content': full_content}
                                ])
                            except Exception as error:
                                raise self._create_detailed_error(error, 'streaming response generation')
                        else:
                            # Non-streaming final response
                            try:
                                final_response = await get_final_response(current_messages, final_config)
                            except Exception as error:
                                raise self._create_detailed_error(error, 'final response generation')
                            
                            # Add clean messages and final response to memory (only original user messages + final response)
                            clean_messages = [msg for msg in formatted_messages 
                                            if msg.get('role') == 'user' and not msg.get('plan') and not msg.get('tool_calls')]
                            self._add_to_memory([
                                *clean_messages,
                                {'role': 'assistant', 'content': final_response['content']}
                            ])
                            
                            yield {
                                'type': 'final_answer',
                                'content': final_response['content']
                            }
                except Exception as error:
                    raise self._create_detailed_error(error, 'response generation')

        except Exception as error:
            # If it's already a detailed error, re-throw as-is
            if 'USFAgent' in str(error):
                raise error
            # Otherwise, create a detailed error
            raise self._create_detailed_error(error, 'agent execution')

    def _validate_run_parameters(self, messages: Union[str, List[Dict[str, Any]]], options: Dict[str, Any]):
        if not messages:
            raise Exception('USFAgent Error: Messages parameter is required')
        
        if options and not isinstance(options, dict):
            raise Exception('USFAgent Error: Options parameter must be an object')
        
        if options.get('tools') and not isinstance(options['tools'], list):
            raise Exception('USFAgent Error: Tools option must be an array')
        
        if options.get('temperature') and (not isinstance(options['temperature'], (int, float)) or options['temperature'] < 0 or options['temperature'] > 2):
            raise Exception('USFAgent Error: Temperature must be a number between 0 and 2')
        
        if options.get('stop') and not isinstance(options['stop'], list):
            raise Exception('USFAgent Error: Stop parameter must be an array of strings')

        if options.get('base_url') and not isinstance(options['base_url'], str):
            raise Exception('USFAgent Error: base_url must be a string')

        if options.get('model') and not isinstance(options['model'], str):
            raise Exception('USFAgent Error: model must be a string')

        if options.get('introduction') and not isinstance(options['introduction'], str):
            raise Exception('USFAgent Error: introduction must be a string')

        if options.get('knowledge_cutoff') and not isinstance(options['knowledge_cutoff'], str):
            raise Exception('USFAgent Error: knowledge_cutoff must be a string')

        if options.get('max_loops') and (not isinstance(options['max_loops'], int) or options['max_loops'] < 1 or options['max_loops'] > 100):
            raise Exception('USFAgent Error: max_loops must be a positive number between 1 and 100')
    
    # Method to manually clear memory
    def clear_memory(self):
        self.memory['messages'] = []
    
    # Method to get current memory state
    def get_memory(self) -> List[Dict[str, Any]]:
        return self.memory['messages'].copy()
    
    # Method to set memory state
    def set_memory(self, messages: List[Dict[str, Any]]):
        if not isinstance(messages, list):
            raise Exception('Memory must be an array of message objects')
        self.memory['messages'] = messages[-self.memory['max_length']:]
