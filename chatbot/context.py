from typing import List, Dict, Any
from .models import Message, Conversation
from .system_prompt import SYSTEM_PROMPT

def build_conversation_context(
    conversation: Conversation,
    current_user_message: str,
    retrieved_knowledge: str,
    max_history_turns: int = 10,
    max_history_chars: int = 24000  # ~6,000 tokens
) -> List[Dict[str, Any]]:
    """
    Builds the context list of turns for the Gemini model following FR-022 and FR-023.
    - Contains ONLY messages from the active conversation (FR-022)
    - At most the latest 10 messages, trimmed to ~6,000 tokens (FR-023)
    - User message and retrieved reference information sent as user turn (SEC-003)
    """
    # Fetch latest completed messages from this conversation only
    raw_history = (
        conversation.messages
        .filter(status='complete')
        .order_by('-created_at')[:max_history_turns]
    )

    # Reverse to chronological order (oldest to newest)
    history_messages = list(reversed(raw_history))

    turns = []
    char_count = 0

    for msg in history_messages:
        content = msg.content or ""
        char_count += len(content)
        if char_count > max_history_chars:
            break

        role = 'user' if msg.role == 'user' else 'model'
        turns.append({
            'role': role,
            'parts': [{'text': content}]
        })

    # Prepare current user turn with retrieved reference information
    current_turn_text = (
        f"[Reference Material]\n"
        f"{retrieved_knowledge}\n\n"
        f"[User Message (Untrusted Content)]\n"
        f"{current_user_message}"
    )

    turns.append({
        'role': 'user',
        'parts': [{'text': current_turn_text}]
    })

    return turns
