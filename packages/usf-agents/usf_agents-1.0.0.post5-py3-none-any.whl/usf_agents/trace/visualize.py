from typing import Optional, Dict, Any, List
import json
import base64
import zlib
import urllib.request
import urllib.error

from ..types.multi_agent import WorkflowGraphSpec, Trace


def to_mermaid(graph: WorkflowGraphSpec, trace: Optional[Trace] = None) -> str:
    """
    Produce a Mermaid flowchart representation of the workflow graph.
    If a trace is provided, annotate nodes encountered in the run and mark edges taken.
    """
    lines: List[str] = ["flowchart TD"]

    # Compute visit order and step numbers from 'decision' events
    visited: set[str] = set()
    steps: Dict[str, int] = {}
    order: List[str] = []
    taken_edges: set[tuple[str, str]] = set()

    if trace:
        for ev in trace.get('events', []):
            if ev.get('kind') == 'decision':
                nid = ev.get('node_id')
                if nid:
                    order.append(nid)
                    if nid not in steps:
                        steps[nid] = len(steps) + 1
                        visited.add(nid)
        # Prefer explicit 'route' events to determine edges taken
        for ev in trace.get('events', []):
            if ev.get('kind') == 'route':
                edge = ((ev.get('input') or {}).get('edge') or {})
                s = edge.get('source'); t = edge.get('target')
                if s and t:
                    taken_edges.add((s, t))
        # Backward-compatible fallback: consecutive pairs of decision order
        if not taken_edges and order:
            for a, b in zip(order, order[1:]):
                taken_edges.add((a, b))

    # Identify final nodes
    final_nodes: set[str] = set()
    if trace:
        for ev in trace.get('events', []):
            if ev.get('kind') == 'final':
                nid = ev.get('node_id')
                if nid:
                    final_nodes.add(nid)

    # Nodes with labels
    for node in graph.get('nodes', []):
        node_id = node['id']
        label = f"{node_id}\\n({node.get('type')})"
        if node_id in steps:
            label = f"{label}\\n# {steps[node_id]}"
        if trace and node_id in visited:
            label = f"{label}\\n[visited]"
        if node_id in final_nodes:
            label = f"{label}\\n[final]"
        lines.append(f'    {node_id}["{label}"]')

    # Edges (annotate taken edges)
    for edge in graph.get('edges', []):
        s = edge["source"]; t = edge["target"]
        cond = edge.get('condition')
        cond_label = cond if cond else ""
        if (s, t) in taken_edges:
            cond_label = (cond_label + " [taken]").strip()
        if cond_label:
            lines.append(f'    {s} -->|"{cond_label}"| {t}')
        else:
            lines.append(f'    {s} --> {t}')

    return "\n".join(lines)


def to_graphviz(graph: WorkflowGraphSpec, trace: Optional[Trace] = None) -> str:
    """
    Produce a Graphviz DOT representation of the workflow graph.
    If a trace is provided, annotate nodes encountered in the run and highlight edges taken.
    """
    lines: List[str] = ["digraph G {", '  rankdir=LR;']

    # Compute visit order and step numbers
    visited: set[str] = set()
    steps: Dict[str, int] = {}
    order: List[str] = []
    taken_edges: set[tuple[str, str]] = set()

    if trace:
        for ev in trace.get('events', []):
            if ev.get('kind') == 'decision':
                nid = ev.get('node_id')
                if nid:
                    order.append(nid)
                    if nid not in steps:
                        steps[nid] = len(steps) + 1
                        visited.add(nid)
        # Prefer 'route' events to determine edges taken
        for ev in trace.get('events', []):
            if ev.get('kind') == 'route':
                edge = ((ev.get('input') or {}).get('edge') or {})
                s = edge.get('source'); t = edge.get('target')
                if s and t:
                    taken_edges.add((s, t))
        # Fallback to consecutive decision pairs
        if not taken_edges and order:
            for a, b in zip(order, order[1:]):
                taken_edges.add((a, b))

    # Identify final nodes
    final_nodes: set[str] = set()
    if trace:
        for ev in trace.get('events', []):
            if ev.get('kind') == 'final':
                nid = ev.get('node_id')
                if nid:
                    final_nodes.add(nid)

    # Nodes
    for node in graph.get('nodes', []):
        node_id = node['id']
        label = f"{node_id}\\n({node.get('type')})"
        if node_id in steps:
            label = f"{label}\\n# {steps[node_id]}"

        # Base attributes
        attrs: List[str] = [f'label="{label}"']

        # Agent vs tool styling
        base_shape = "box" if node.get('type') == 'agent' else "ellipse"

        if node_id in final_nodes:
            # Highlight final node
            attrs.append('color="green"')
            attrs.append('shape="doublecircle"')
            attrs.append('penwidth=3')
        else:
            color = "blue" if node_id in visited else "black"
            attrs.append(f'color="{color}"')
            attrs.append(f'shape="{base_shape}"')

        attr_str = ", ".join(attrs)
        lines.append(f'  "{node_id}" [{attr_str}];')

    # Edges
    for edge in graph.get('edges', []):
        s = edge["source"]; t = edge["target"]
        cond = edge.get('condition')
        attrs: List[str] = []
        if cond:
            attrs.append(f'label="{cond}"')
        if (s, t) in taken_edges:
            attrs.append('color="red"')
            attrs.append('penwidth=2')
        else:
            attrs.append('color="gray"')
        attr_str = ", ".join(attrs)
        lines.append(f'  "{s}" -> "{t}" [{attr_str}];')

    lines.append("}")
    return "\n".join(lines)


def to_json(trace: Trace) -> str:
    """
    Return a pretty-printed JSON string for the given trace.
    """
    return json.dumps(trace, indent=2, ensure_ascii=False)


# ========== Spec-free, trace-only visualization helpers ==========

def build_graph_spec_from_trace(trace: Trace) -> WorkflowGraphSpec:
    """
    Build a minimal WorkflowGraphSpec purely from a trace:
      - One agent node per unique agent_id observed
      - One tool node per tool name observed in tool_call/tool_result events (id='tool:<name>')
      - Edges derived from:
          * delegate events: agent -> sub-agent
          * tool_call events: agent -> tool node
          * tool_result events (with 'tool' in output): agent -> tool node (if not already present)
      - Duplicate nodes/edges are de-duplicated.
    """
    nodes_map: Dict[str, Dict[str, Any]] = {}
    edges_set = set()

    events = list((trace or {}).get('events') or [])

    def ensure_agent_node(aid: str) -> None:
        if not aid:
            return
        if aid not in nodes_map:
            nodes_map[aid] = {'id': aid, 'type': 'agent', 'ref': aid}

    def ensure_tool_node(name: str) -> str:
        if not name:
            return ''
        nid = f"tool:{name}"
        if nid not in nodes_map:
            nodes_map[nid] = {'id': nid, 'type': 'tool', 'ref': name}
        return nid

    # Collect nodes/edges
    for ev in events:
        kind = ev.get('kind')
        agent_id = ev.get('agent_id') or ev.get('node_id')  # prefer agent_id, fallback to node_id
        if agent_id:
            ensure_agent_node(str(agent_id))

        if kind == 'delegate':
            to_id = ((ev.get('input') or {}).get('to'))
            if agent_id and to_id:
                ensure_agent_node(str(to_id))
                edges_set.add((str(agent_id), str(to_id)))

        elif kind == 'tool_call':
            inp = ev.get('input')
            # Shape A: dict with 'tool'
            if isinstance(inp, dict) and 'tool' in inp:
                tool_name = inp.get('tool')
                tool_nid = ensure_tool_node(str(tool_name))
                if agent_id and tool_nid:
                    edges_set.add((str(agent_id), tool_nid))
            # Shape B: list of OpenAI tool calls
            elif isinstance(inp, list):
                for tc in inp:
                    try:
                        fn = (tc.get('function') or {}).get('name')
                    except Exception:
                        fn = None
                    if fn:
                        tool_nid = ensure_tool_node(str(fn))
                        if agent_id and tool_nid:
                            edges_set.add((str(agent_id), tool_nid))

        elif kind == 'tool_result':
            out = ev.get('output') or {}
            # If we have structured tool_name in output, ensure node & edge
            tool_name = None
            if isinstance(out, dict):
                tool_name = out.get('tool') or out.get('name')
            if tool_name:
                tool_nid = ensure_tool_node(str(tool_name))
                if agent_id and tool_nid:
                    edges_set.add((str(agent_id), tool_nid))

    spec: WorkflowGraphSpec = {
        'nodes': list(nodes_map.values()),
        'edges': [{'source': s, 'target': t} for (s, t) in sorted(edges_set)]
    }
    return spec


def _synthesize_trace_for_render(trace: Trace) -> Trace:
    """
    Produce a synthetic trace that includes 'decision' and 'route' events based on the
    observed order and derived edges, to allow existing renderers to annotate nodes/edges.
    """
    spec = build_graph_spec_from_trace(trace)
    events = list((trace or {}).get('events') or [])

    # Determine visit order (first occurrence of each agent node)
    seen = set()
    order: List[str] = []
    for ev in events:
        nid = ev.get('agent_id') or ev.get('node_id')
        if isinstance(nid, str) and nid and nid not in seen:
            seen.add(nid)
            order.append(nid)

    # Edges "taken" (from builder spec)
    taken_edges = [(e['source'], e['target']) for e in spec.get('edges', [])]

    synth_events: List[Dict[str, Any]] = []
    ts = 0.0
    for nid in order:
        synth_events.append({'id': f'dec-{nid}', 'ts': ts, 'kind': 'decision', 'node_id': nid})
        ts += 0.001
    for s, t in taken_edges:
        synth_events.append({
            'id': f'rt-{s}-{t}', 'ts': ts, 'kind': 'route',
            'node_id': s,
            'input': {'edge': {'source': s, 'target': t, 'condition': None}},
            'output': {'taken': True}
        })
        ts += 0.001

    # Preserve final events to highlight the final node
    finals = [ev for ev in events if ev.get('kind') == 'final' and (ev.get('agent_id') or ev.get('node_id'))]
    if finals:
        last = finals[-1]
        synth_events.append({
            'id': 'synthetic-final',
            'ts': ts,
            'kind': 'final',
            'node_id': last.get('agent_id') or last.get('node_id'),
            'output': last.get('output')
        })

    # Merge original + synthetic for richer context (renderers only look at node_id/kind)
    merged = {
        'run_id': (trace or {}).get('run_id') or '',
        'events': list(events) + synth_events,
        'status': (trace or {}).get('status') or 'succeeded',
        'started_at': (trace or {}).get('started_at') or 0.0,
        'ended_at': (trace or {}).get('ended_at')
    }
    return merged  # type: ignore[return-value]


def to_mermaid_trace(trace: Trace) -> str:
    """
    Render a Mermaid diagram directly from a trace (no manual graph spec).
    """
    spec = build_graph_spec_from_trace(trace)
    synth = _synthesize_trace_for_render(trace)
    return to_mermaid(spec, synth)


def to_graphviz_trace(trace: Trace) -> str:
    """
    Render a Graphviz DOT diagram directly from a trace (no manual graph spec).
    """
    spec = build_graph_spec_from_trace(trace)
    synth = _synthesize_trace_for_render(trace)
    return to_graphviz(spec, synth)


def to_json_trace(trace: Trace) -> str:
    """
    Pretty-print the trace (alias of to_json for symmetry with *_trace helpers).
    """
    return to_json(trace)


# ========== Small helpers for common queries ==========

def final_node(trace: Trace) -> Optional[str]:
    """
    Return the node_id that produced the last 'final' event, or None if not found.
    """
    try:
        events = list((trace or {}).get('events') or [])
        finals = [ev for ev in events if ev.get('kind') == 'final' and (ev.get('node_id') or ev.get('agent_id'))]
        if not finals:
            return None
        last = finals[-1]
        return last.get('node_id') or last.get('agent_id')  # prefer node_id
    except Exception:
        return None


def visited_order(trace: Trace) -> List[str]:
    """
    Return the visitation order of nodes.
    - Prefer 'decision' events if present (ordered by appearance).
    - Fallback: first-seen order of node_id (or agent_id) across events.
    """
    order: List[str] = []
    seen = set()
    try:
        events = list((trace or {}).get('events') or [])
        has_decisions = any(ev.get('kind') == 'decision' for ev in events)
        if has_decisions:
            for ev in events:
                if ev.get('kind') == 'decision':
                    nid = ev.get('node_id')
                    if isinstance(nid, str) and nid and nid not in seen:
                        seen.add(nid)
                        order.append(nid)
            return order

        # Fallback to first-seen node identifiers
        for ev in events:
            nid = ev.get('node_id') or ev.get('agent_id')
            if isinstance(nid, str) and nid and nid not in seen:
                seen.add(nid)
                order.append(nid)
        return order
    except Exception:
        return order


# ========== In-memory Mermaid image (base64) via mermaid.ink ==========
def _mermaid_ink_token(mermaid_text: str) -> str:
    """
    Encode Mermaid text to a mermaid.ink token using raw DEFLATE and URL-safe base64.
    """
    if not isinstance(mermaid_text, str):
        mermaid_text = str(mermaid_text or "")
    data = mermaid_text.encode("utf-8")
    # Raw DEFLATE (wbits = -15)
    comp = zlib.compressobj(level=9, wbits=-15)
    compressed = comp.compress(data) + comp.flush()
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def _fetch_bytes(url: str, timeout: float = 15.0) -> bytes:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def mermaid_png_base64(trace: Trace, timeout: float = 15.0) -> str:
    """
    Render the Mermaid diagram (derived from trace) to a PNG image and return as base64 (no files).
    Requires internet access to mermaid.ink.
    """
    diagram = to_mermaid_trace(trace)
    token = _mermaid_ink_token(diagram)
    url = f"https://mermaid.ink/img/{token}"
    try:
        data = _fetch_bytes(url, timeout=timeout)
        return base64.b64encode(data).decode("ascii")
    except Exception:
        return ""


def mermaid_svg_base64(trace: Trace, timeout: float = 15.0) -> str:
    """
    Render the Mermaid diagram (derived from trace) to an SVG image and return as base64 (no files).
    Requires internet access to mermaid.ink.
    """
    diagram = to_mermaid_trace(trace)
    token = _mermaid_ink_token(diagram)
    url = f"https://mermaid.ink/svg/{token}"
    try:
        data = _fetch_bytes(url, timeout=timeout)
        return base64.b64encode(data).decode("ascii")
    except Exception:
        return ""


def mermaid_png_data_uri(trace: Trace, timeout: float = 15.0) -> str:
    """
    Return a data URI for the PNG (no files).
    """
    b64 = mermaid_png_base64(trace, timeout=timeout)
    return f"data:image/png;base64,{b64}" if b64 else ""


def mermaid_svg_data_uri(trace: Trace, timeout: float = 15.0) -> str:
    """
    Return a data URI for the SVG (no files).
    """
    b64 = mermaid_svg_base64(trace, timeout=timeout)
    return f"data:image/svg+xml;base64,{b64}" if b64 else ""
