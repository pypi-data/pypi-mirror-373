from typing import Dict, List, Any, Optional, Set, Tuple, Callable, Awaitable
from collections import defaultdict, deque
import uuid
import time

from ..types.multi_agent import (
    WorkflowGraphSpec,
    WorkflowNode,
    AgentEdge,
)
from ..types import Message
from ..types.multi_agent import TaskPayload
from ..multi_agent.registry import AgentRegistry
from ..trace.trace import TraceRecorder


class WorkflowValidationError(Exception):
    pass


class WorkflowGraph:
    """
    Validates and inspects a workflow graph consisting of nodes (agents/tools) and edges.
    """
    def __init__(self, spec: WorkflowGraphSpec):
        self.spec = spec
        self._node_index: Dict[str, WorkflowNode] = {n['id']: n for n in spec.get('nodes', [])}
        self._adj: Dict[str, List[AgentEdge]] = defaultdict(list)
        for e in spec.get('edges', []):
            self._adj[e['source']].append(e)

    def validate(self) -> None:
        # Basic checks: unique node ids, edges reference existing nodes
        if not self.spec.get('nodes'):
            raise WorkflowValidationError("Workflow must contain at least one node")

        if len(self._node_index) != len(self.spec['nodes']):
            raise WorkflowValidationError("Duplicate node IDs detected")

        for e in self.spec.get('edges', []):
            if e['source'] not in self._node_index:
                raise WorkflowValidationError(f"Edge source '{e['source']}' not found in nodes")
            if e['target'] not in self._node_index:
                raise WorkflowValidationError(f"Edge target '{e['target']}' not found in nodes")

    def detect_cycles(self, limit: int = 3) -> List[List[str]]:
        """
        Detect cycles in the graph using DFS. Returns up to 'limit' cycles as lists of node ids.
        """
        visited: Set[str] = set()
        stack: Set[str] = set()
        result: List[List[str]] = []

        def dfs(node: str, path: List[str]):
            if len(result) >= limit:
                return
            visited.add(node)
            stack.add(node)
            path.append(node)

            for edge in self._adj.get(node, []):
                nxt = edge['target']
                if nxt not in visited:
                    dfs(nxt, path)
                    if len(result) >= limit:
                        return
                elif nxt in stack:
                    # Found a cycle; extract subpath
                    try:
                        i = path.index(nxt)
                        cyc = path[i:] + [nxt]
                        result.append(cyc)
                    except ValueError:
                        pass

            stack.remove(node)
            path.pop()

        for node_id in self._node_index.keys():
            if len(result) >= limit:
                break
            if node_id not in visited:
                dfs(node_id, [])

        return result

    def neighbors(self, node_id: str) -> List[AgentEdge]:
        return list(self._adj.get(node_id, []))

    def get_node(self, node_id: str) -> WorkflowNode:
        return self._node_index[node_id]


class ExecutionEngine:
    """
    Executes a WorkflowGraph by walking from entry nodes, applying simple conditional routing.
    Integrates with AgentRegistry and TraceRecorder for execution and observability.
    """
    def __init__(self, graph: WorkflowGraph, registry: AgentRegistry, recorder: TraceRecorder, tool_executor: Optional[Callable[[str, Any, Dict[str, Any]], Awaitable[Any]]] = None):
        self.graph = graph
        self.registry = registry
        self.recorder = recorder
        self.tool_executor = tool_executor

    async def run(
        self,
        entry_nodes: List[str],
        inputs: Dict[str, Any],
        max_steps: int = 200
    ) -> Dict[str, Any]:
        """
        Execute starting from entry_nodes. 'inputs' may contain per-node inputs:
          - If inputs[node_id] is a dict with 'task' or 'input' keys => treated as TaskPayload
          - Else inputs[node_id] is passed as TaskPayload.input
        Returns a dict mapping node_id -> execution summary {'success': bool, 'content': str, 'raw': Any}
        """
        self.graph.validate()
        run_id = self.recorder.start()
        outputs: Dict[str, Any] = {}
        visited_steps = 0

        q = deque(entry_nodes)
        last_result: Dict[str, Any] = {}

        while q and visited_steps < max_steps:
            node_id = q.popleft()
            visited_steps += 1
            node = self.graph.get_node(node_id)

            # Record decision to visit node
            self.recorder.record({
                'kind': 'decision',
                'node_id': node_id,
                'input': {'visited_steps': visited_steps},
                'output': None,
                'meta': {'run_id': run_id}
            })

            if node.get('type') == 'agent':
                agent_id = str(node.get('ref'))
                wrapper = self.registry.get(agent_id)

                # Prepare TaskPayload from inputs
                node_in = inputs.get(node_id)
                if isinstance(node_in, dict) and ('task' in node_in or 'input' in node_in):
                    task: TaskPayload = node_in  # type: ignore
                else:
                    task = {
                        'task': 'run',
                        'input': node_in if isinstance(node_in, dict) else {'value': node_in}
                    }

                # Execute as task (delegation style)
                self.recorder.record({
                    'kind': 'delegate',
                    'agent_id': agent_id,
                    'node_id': node_id,
                    'input': task,
                    'meta': {'run_id': run_id}
                })

                try:
                    collected = await wrapper.run_task(task)
                    success = collected.get('status') == 'final'
                    content = (collected.get('content') or '') if success else ''
                    last_result = {
                        'agent_id': agent_id,
                        'node_id': node_id,
                        'success': success,
                        'content': content,
                        'raw': collected
                    }
                    outputs[node_id] = last_result

                    self.recorder.record({
                        'kind': 'final' if success else 'error',
                        'agent_id': agent_id,
                        'node_id': node_id,
                        'input': task,
                        'output': content if success else collected,
                        'error': None if success else 'non-final result',
                        'meta': {'run_id': run_id}
                    })
                except Exception as e:
                    last_result = {
                        'agent_id': agent_id,
                        'node_id': node_id,
                        'success': False,
                        'content': '',
                        'raw': {'error': str(e)}
                    }
                    outputs[node_id] = last_result
                    self.recorder.record({
                        'kind': 'error',
                        'agent_id': agent_id,
                        'node_id': node_id,
                        'input': task,
                        'output': None,
                        'error': str(e),
                        'meta': {'run_id': run_id}
                    })
            else:
                # Tool node execution via optional executor callback; fallback to placeholder
                tool_ref = str(node.get('ref'))
                node_in = inputs.get(node_id)
                self.recorder.record({
                    'kind': 'tool_call',
                    'node_id': node_id,
                    'input': {'ref': tool_ref, 'input': node_in},
                    'meta': {'run_id': run_id}
                })
                if self.tool_executor:
                    try:
                        res = await self.tool_executor(tool_ref, node_in, {'last': last_result, 'outputs': outputs})
                        if isinstance(res, dict):
                            success = bool(res.get('success', True))
                            content = res.get('content', str(res))
                            raw = res
                        else:
                            success = True
                            content = str(res)
                            raw = res
                        last_result = {
                            'agent_id': None,
                            'node_id': node_id,
                            'success': success,
                            'content': content,
                            'raw': raw
                        }
                        outputs[node_id] = last_result
                        self.recorder.record({
                            'kind': 'tool_result' if success else 'error',
                            'node_id': node_id,
                            'input': {'ref': tool_ref, 'input': node_in},
                            'output': content if success else raw,
                            'error': None if success else 'tool execution failed',
                            'meta': {'run_id': run_id}
                        })
                    except Exception as e:
                        last_result = {
                            'agent_id': None,
                            'node_id': node_id,
                            'success': False,
                            'content': '',
                            'raw': {'error': str(e)}
                        }
                        outputs[node_id] = last_result
                        self.recorder.record({
                            'kind': 'error',
                            'node_id': node_id,
                            'input': {'ref': tool_ref, 'input': node_in},
                            'output': None,
                            'error': str(e),
                            'meta': {'run_id': run_id}
                        })
                else:
                    last_result = {
                        'agent_id': None,
                        'node_id': node_id,
                        'success': True,
                        'content': f"Tool {tool_ref} executed (placeholder).",
                        'raw': None
                    }
                    outputs[node_id] = last_result
                    self.recorder.record({
                        'kind': 'tool_result',
                        'node_id': node_id,
                        'input': {'ref': tool_ref, 'input': node_in},
                        'output': last_result['content'],
                        'error': None,
                        'meta': {'run_id': run_id}
                    })

            # Enqueue neighbors based on conditions
            for edge in self.graph.neighbors(node_id):
                cond = edge.get('condition')
                if self._evaluate_condition(cond, {'last': last_result, 'outputs': outputs}):
                    # Record route (edge taken)
                    self.recorder.record({
                        'kind': 'route',
                        'node_id': node_id,
                        'input': {'edge': {'source': node_id, 'target': edge['target'], 'condition': cond}},
                        'output': {'taken': True},
                        'meta': {'run_id': run_id}
                    })
                    q.append(edge['target'])

        status = 'succeeded'
        if visited_steps >= max_steps:
            status = 'partial'
        self.recorder.end(status=status)
        return outputs

    def _evaluate_condition(self, expr: Optional[str], context: Dict[str, Any]) -> bool:
        """
        Extremely conservative evaluator:
          - Empty/None => True
          - 'true'/'always'/'1' => True
          - 'false'/'0' => False
          - 'last.success' (dot path) => looks up truthiness
          - Fallback: returns False (no arbitrary eval for safety)
        """
        if expr is None:
            return True
        s = str(expr).strip().lower()
        if s in ('', 'true', 'always', '1'):
            return True
        if s in ('false', '0', 'never'):
            return False

        # Dot-path lookup support, e.g., "last.success"
        def get_path(root: Any, path: str) -> Any:
            cur = root
            for part in path.split('.'):
                if isinstance(cur, dict):
                    cur = cur.get(part)
                else:
                    return None
            return cur

        # Support simple comparisons like "last.success == true"
        if '==' in expr:
            left, right = [p.strip() for p in expr.split('==', 1)]
            left_val = get_path(context, left.replace(' ', ''))
            right_norm = right.replace(' ', '').strip("'\"")
            if right_norm in ('true', 'false'):
                right_val = (right_norm == 'true')
            elif right_norm.isdigit():
                right_val = int(right_norm)
            else:
                right_val = right.strip("'\"")
            return left_val == right_val

        # Simple truthiness check for a dot path
        val = get_path(context, expr.replace(' ', ''))
        return bool(val)
