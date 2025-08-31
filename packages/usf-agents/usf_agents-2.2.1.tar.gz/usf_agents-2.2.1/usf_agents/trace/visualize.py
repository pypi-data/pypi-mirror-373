from typing import Optional, Dict, Any, List
import json

from ..types.multi_agent import WorkflowGraphSpec, Trace


def to_mermaid(graph: WorkflowGraphSpec, trace: Optional[Trace] = None) -> str:
    """
    Produce a Mermaid flowchart representation of the workflow graph.
    If a trace is provided, annotate nodes encountered in the run.
    """
    lines: List[str] = ["flowchart TD"]

    # Map node id to label
    for node in graph.get('nodes', []):
        node_id = node['id']
        label = f"{node_id}\\n({node.get('type')})"
        if trace:
            # Check if node_id appears in trace events
            if any((ev.get('node_id') == node_id) for ev in trace.get('events', [])):
                label = f"{label}\\n[visited]"
        lines.append(f'    {node_id}["{label}"]')

    # Edges
    for edge in graph.get('edges', []):
        cond = edge.get('condition')
        if cond:
            lines.append(f'    {edge["source"]} -->|"{cond}"| {edge["target"]}')
        else:
            lines.append(f'    {edge["source"]} --> {edge["target"]}')

    return "\n".join(lines)


def to_graphviz(graph: WorkflowGraphSpec, trace: Optional[Trace] = None) -> str:
    """
    Produce a Graphviz DOT representation of the workflow graph.
    If a trace is provided, annotate nodes encountered in the run.
    """
    lines: List[str] = ["digraph G {", '  rankdir=LR;']

    # Nodes
    for node in graph.get('nodes', []):
        node_id = node['id']
        label = f"{node_id}\\n({node.get('type')})"
        color = "black"
        if trace and any((ev.get('node_id') == node_id) for ev in trace.get('events', [])):
            color = "blue"
        # Agent vs tool styling
        shape = "box" if node.get('type') == 'agent' else "ellipse"
        lines.append(f'  "{node_id}" [label="{label}", color="{color}", shape="{shape}"];')

    # Edges
    for edge in graph.get('edges', []):
        cond = edge.get('condition')
        if cond:
            lines.append(f'  "{edge["source"]}" -> "{edge["target"]}" [label="{cond}"];')
        else:
            lines.append(f'  "{edge["source"]}" -> "{edge["target"]}";')

    lines.append("}")
    return "\n".join(lines)


def to_json(trace: Trace) -> str:
    """
    Return a pretty-printed JSON string for the given trace.
    """
    return json.dumps(trace, indent=2, ensure_ascii=False)
