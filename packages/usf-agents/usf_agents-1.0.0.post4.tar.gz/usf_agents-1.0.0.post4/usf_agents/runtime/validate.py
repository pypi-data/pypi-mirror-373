from typing import List
from ..types import Message


class SequenceValidationError(Exception):
    pass


def validate_next_step(messages: List[Message]) -> None:
    """
    Guardrail: Ensure correct sequencing before calling agent.run() again.

    Rules:
    - If the last assistant message contains 'tool_calls', the next messages appended
      MUST be role: 'tool' with matching tool_call_id(s). Do not call run() again until then.
    - If the last message is role: 'tool', it's valid to call run() next.
    - Otherwise, no constraint is enforced here.

    Raises:
        SequenceValidationError if rules are violated.
    """
    if not messages:
        return

    last = messages[-1]
    if last.get('role') == 'assistant' and last.get('tool_calls'):
        raise SequenceValidationError(
            "Invalid sequence: last assistant message has tool_calls. "
            "Append tool result messages (role: 'tool' with matching tool_call_id) before calling run()."
        )
    # role: 'tool' is acceptable; next call to run() may proceed
    return
