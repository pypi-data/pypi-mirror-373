from .usfPlanner import plan_with_usf, call_tool_with_usf
from .usfMessageHandler import (
    generate_final_response_with_openai, 
    stream_final_response_with_openai,
    BaseURLResolutionError
)
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
import asyncio


class USFAgent:
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {}
            
        # Default configuration (fallback for all stages)
        self.default_config = {
            'api_key': config.get('api_key'),
            'model': config.get('model', 'usf-mini'),
            'provider': config.get('provider'),
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
        self.model = self.default_config['model']
        self.stream = config.get('stream', False)
        self.introduction = self.default_config['introduction']
        self.knowledge_cutoff = self.default_config['knowledge_cutoff']
        # Skip planning when no tools (opt-in, default False)
        self.skip_planning_if_no_tools = bool(config.get('skip_planning_if_no_tools', False))
        
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
        # Per-instance reentrancy guard
        self._run_lock = asyncio.Lock()
        
        # Enhanced API key validation
        self._validate_configuration()

    def _merge_config(self, default_config: Dict[str, Any], stage_config: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'api_key': stage_config.get('api_key') or default_config['api_key'],
            'model': stage_config.get('model') or default_config['model'],
            'provider': stage_config.get('provider') or default_config.get('provider'),
            'introduction': stage_config.get('introduction') or default_config['introduction'],
            'knowledge_cutoff': stage_config.get('knowledge_cutoff') or default_config['knowledge_cutoff'],
            'temperature': stage_config.get('temperature'),
            'stop': stage_config.get('stop'),
            'debug': stage_config.get('debug') or default_config.get('debug'),
            **{k: v for k, v in stage_config.items() if k not in ['api_key', 'model', 'provider', 'introduction', 'knowledge_cutoff', 'temperature', 'stop', 'debug']}
        }

    def _validate_configuration(self):
        if not self.api_key:
            raise Exception('USFAgent Error: API key is required. Please provide a valid API key')
        
        if not isinstance(self.api_key, str) or self.api_key.strip() == '':
            raise Exception('USFAgent Error: API key must be a non-empty string. Please check your API key')
        
        
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

        # Validate skip_planning_if_no_tools flag (boolean)
        if not isinstance(self.skip_planning_if_no_tools, bool):
            raise Exception('USFAgent Error: skip_planning_if_no_tools must be a boolean')

    def _create_detailed_error(self, original_error: Exception, context: str) -> Exception:
        error_message = str(original_error)
        
        # Check for common error patterns and provide helpful guidance
        if '401' in error_message or 'Unauthorized' in error_message:
            return Exception(f'USFAgent API Error: Invalid API key. Please check your API key and ensure it\'s valid. Original error: {error_message}')
        
        if '403' in error_message or 'Forbidden' in error_message:
            return Exception(f'USFAgent API Error: Access forbidden. Your API key may not have the required permissions or may be expired. Original error: {error_message}')
        
        if '404' in error_message or 'Not Found' in error_message:
            return Exception(f'USFAgent API Error: API endpoint not found. Please check if the endpoint URL is correct. Original error: {error_message}')
        
        if '429' in error_message or 'Too Many Requests' in error_message:
            return Exception(f'USFAgent API Error: Rate limit exceeded. Please wait a moment before making more requests. Original error: {error_message}')
        
        if any(code in error_message for code in ['500', '502', '503', 'Bad Gateway', 'Service Unavailable']):
            return Exception(f'USFAgent API Error: Server error from USF API. This is usually temporary. Please try again in a few moments. Original error: {error_message}')
        
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

    def _analyze_sequence(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the message history to enforce correct plan -> tool-call -> tool result sequencing.

        Returns:
          - last_tool_calls_index: index of the last assistant tool_calls envelope (or -1)
          - tool_call_ids: set of tool_call ids from the last envelope
          - satisfied_ids: set of tool_call ids that have corresponding role:'tool' results
          - outstanding_ids: tool_call ids that are still missing tool results
          - last_plan_index: index of the last assistant plan message (or -1)
          - last_plan_tool_choice: the tool_choice object from the last plan (if any)
        """
        last_tool_calls_index = -1
        tool_call_ids: set = set()
        satisfied_ids: set = set()
        last_plan_index = -1
        last_plan_tool_choice = None

        for i, m in enumerate(messages or []):
            role = m.get('role')
            mtype = m.get('type')

            # Track last plan
            if role == 'assistant' and (mtype == 'agent_plan' or m.get('plan')):
                last_plan_index = i
                last_plan_tool_choice = m.get('tool_choice') or last_plan_tool_choice

            # Track last assistant tool_calls envelope and reset tracking sets
            if role == 'assistant' and isinstance(m.get('tool_calls'), list):
                last_tool_calls_index = i
                tool_call_ids = set()
                satisfied_ids = set()
                for tc in (m.get('tool_calls') or []):
                    if isinstance(tc, dict):
                        tid = tc.get('id')
                        if tid:
                            tool_call_ids.add(tid)

            # Track tool results corresponding to last tool_calls
            if last_tool_calls_index != -1 and role == 'tool':
                tid = m.get('tool_call_id')
                if tid in tool_call_ids:
                    satisfied_ids.add(tid)

        outstanding_ids = tool_call_ids - satisfied_ids
        return {
            'last_tool_calls_index': last_tool_calls_index,
            'tool_call_ids': tool_call_ids,
            'satisfied_ids': satisfied_ids,
            'outstanding_ids': outstanding_ids,
            'last_plan_index': last_plan_index,
            'last_plan_tool_choice': last_plan_tool_choice
        }

    async def run(self, messages: Union[str, List[Dict[str, Any]]], options: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        if options is None:
            options = {}
            
        # Reentrancy guard to prevent overlapping runs on the same instance
        if self._run_lock.locked():
            raise Exception('USFAgent Sequencing Error: Agent run is already in progress for this instance. Avoid concurrent run() calls.')
        await self._run_lock.acquire()
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
                    'provider': options['planning'].get('provider') or self.planning_config.get('provider'),
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
                    'provider': options['tool_calling'].get('provider') or self.tool_calling_config.get('provider'),
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
                    'provider': options['final_response'].get('provider') or self.final_response_config.get('provider'),
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

            # Enforce sequencing and short-circuit to tool-call when appropriate
            state = self._analyze_sequence(current_messages)
            # If there is a pending assistant tool_calls envelope with missing tool results, block planning
            if state.get('tool_call_ids') and state.get('outstanding_ids'):
                raise Exception(
                    f"USFAgent Sequencing Error: Pending tool_calls require tool results before planning. "
                    f"Outstanding tool_call_ids: {sorted(list(state.get('outstanding_ids') or []))}"
                )
            # If a plan exists with a tool_choice but no assistant tool_calls were appended yet, perform tool-call now.
            if (
                state.get('last_plan_index', -1) != -1 and
                (state.get('last_tool_calls_index', -1) < state.get('last_plan_index', -1)) and
                state.get('last_plan_tool_choice')
            ):
                try:
                    tool_call_result = await call_tool_with_usf(current_messages, {
                        **tool_config,
                        'tool_choice': state.get('last_plan_tool_choice')
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

                # Yield tool calls for execution and return (wait for external tool results)
                yield {
                    'type': 'tool_calls',
                    'tool_calls': tool_call_result['tool_calls'],
                    'agent_status': tool_call_result.get('agent_status', 'running')
                }
                return

            agent_status = 'running'
            loop_count = 0
            max_loops = options.get('max_loops', self.max_loops)  # Use configurable max loops

            # Early bypass: if configured to skip planning when no tools, and effective tools are empty
            try:
                effective_tools = (plan_config.get('tools') or []) if isinstance(plan_config, dict) else []
                # Resolve skip flag precedence
                if options.get('planning') and isinstance(options.get('planning'), dict) and options['planning'].get('skip_planning_if_no_tools') is not None:
                    effective_skip = bool(options['planning'].get('skip_planning_if_no_tools'))
                elif options.get('skip_planning_if_no_tools') is not None:
                    effective_skip = bool(options.get('skip_planning_if_no_tools'))
                elif isinstance(self.planning_config, dict) and self.planning_config.get('skip_planning_if_no_tools') is not None:
                    effective_skip = bool(self.planning_config.get('skip_planning_if_no_tools'))
                else:
                    effective_skip = bool(getattr(self, 'skip_planning_if_no_tools', False))

                if effective_skip and len(effective_tools) == 0:
                    # Directly generate final response using OpenAI-compatible handler
                    if self.stream:
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
                        except BaseURLResolutionError as error:
                            raise error
                        except Exception as error:
                            raise self._create_detailed_error(error, 'OpenAI streaming response generation')
                    else:
                        try:
                            final_response = await generate_final_response_with_openai(current_messages, final_config)
                        except BaseURLResolutionError as error:
                            raise error
                        except Exception as error:
                            raise self._create_detailed_error(error, 'OpenAI final response generation')

                        # Add clean messages and final response to memory
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
                    return
            except Exception as error:
                # Ensure consistent error wrapping
                raise self._create_detailed_error(error, 'response generation')

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
                    # Final response using OpenAI-compatible handler
                    if True:
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
                            except BaseURLResolutionError as error:
                                raise error
                            except Exception as error:
                                raise self._create_detailed_error(error, 'OpenAI streaming response generation')
                        else:
                            # Non-streaming final response using OpenAI
                            try:
                                final_response = await generate_final_response_with_openai(current_messages, final_config)
                            except BaseURLResolutionError as error:
                                raise error
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
        finally:
            if self._run_lock.locked():
                self._run_lock.release()

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


        # Validate provider for planning/tool_calling (allowed set)
        allowed_providers = {'openrouter', 'openai', 'claude', 'huggingface-inference', 'groq'}
        def _validate_provider_value(value, ctx: str):
            if value is None:
                return
            if not isinstance(value, str):
                raise Exception(f'USFAgent Error: provider must be a string in {ctx}')
            if value and value not in allowed_providers:
                raise Exception(f"USFAgent Error: Invalid provider '{value}' in {ctx}. Allowed providers: {', '.join(sorted(allowed_providers))}")

        _validate_provider_value(options.get('provider'), 'options')
        if options.get('planning'):
            _validate_provider_value(options['planning'].get('provider'), 'options.planning')
        if options.get('tool_calling'):
            _validate_provider_value(options['tool_calling'].get('provider'), 'options.tool_calling')

        if options.get('model') and not isinstance(options['model'], str):
            raise Exception('USFAgent Error: model must be a string')

        if options.get('introduction') and not isinstance(options['introduction'], str):
            raise Exception('USFAgent Error: introduction must be a string')

        if options.get('knowledge_cutoff') and not isinstance(options['knowledge_cutoff'], str):
            raise Exception('USFAgent Error: knowledge_cutoff must be a string')

        if options.get('max_loops') and (not isinstance(options['max_loops'], int) or options['max_loops'] < 1 or options['max_loops'] > 100):
            raise Exception('USFAgent Error: max_loops must be a positive number between 1 and 100')

        # Validate skip_planning_if_no_tools flags when provided
        if options.get('skip_planning_if_no_tools') is not None and not isinstance(options.get('skip_planning_if_no_tools'), bool):
            raise Exception('USFAgent Error: skip_planning_if_no_tools must be a boolean in options')
        if options.get('planning') and isinstance(options.get('planning'), dict):
            if options['planning'].get('skip_planning_if_no_tools') is not None and not isinstance(options['planning'].get('skip_planning_if_no_tools'), bool):
                raise Exception('USFAgent Error: skip_planning_if_no_tools must be a boolean in options.planning')
    
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
