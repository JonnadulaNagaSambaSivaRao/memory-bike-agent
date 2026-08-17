# agent.py

import os
import json

from dotenv import load_dotenv
from openai import AsyncOpenAI

from memory import MemoryManager


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# GROQ CLIENT
# ============================================================

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# ============================================================
# MODEL
# ============================================================

MODEL = "openai/gpt-oss-20b"


# ============================================================
# MEMORY MANAGER
# ============================================================

memory = MemoryManager()


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a helpful Memory-Aware AI Agent.

You have access to three types of context:

1. Relevant long-term user memories.
2. A summary of older conversations.
3. Recent conversation messages.

You must use this information intelligently.

IMPORTANT MEMORY RULES:

- Use relevant memories when they help answer the user's
  current request.
- Do not invent memories.
- Do not claim to remember information that is not present
  in the supplied context.
- Do not ask the user for information that is already
  available in the supplied memory or recent conversation.
- Combine multiple relevant memories when appropriate.
- If the user previously stated a preference, requirement,
  budget, duration, or goal, use it naturally.
- Do not mention the internal memory system unless the user
  asks about it.
- Do not repeat every memory in every response.
- Prioritize the current user request.
- If information is genuinely missing, ask a concise
  follow-up question.

For example, if the memory says:

- User prefers Honda bikes.
- User wants good mileage.
- User has a limited budget.
- User needs a bike for 3 days.

and the user says:

"I need another bike for my trip."

You should use those memories and respond with recommendations
that consider Honda, mileage, budget, and the 3-day requirement.

Do not ask again for information that is already known.
"""


# ============================================================
# CALL LLM
# ============================================================

async def call_llm(messages):
    """
    Send messages to the Groq LLM.
    """

    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content


# ============================================================
# BUILD PROMPT
# ============================================================

def build_messages(user_request):
    """
    Build the context sent to the LLM.

    Only the following are sent:

    1. System instructions
    2. Relevant long-term memories
    3. Conversation summary
    4. Recent conversation
    5. Current request
    """

    context = memory.get_context(
        user_request
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # ========================================================
    # RELEVANT LONG-TERM MEMORIES
    # ========================================================

    if context["relevant_memories"]:

        memory_text = (
            "Relevant long-term user memories:\n"
        )

        for item in context[
            "relevant_memories"
        ]:

            memory_text += (
                f"- {item}\n"
            )

        messages.append(
            {
                "role": "system",
                "content": memory_text
            }
        )

    # ========================================================
    # CONVERSATION SUMMARY
    # ========================================================

    if context["summary"]:

        messages.append(
            {
                "role": "system",
                "content":
                    "Summary of older conversation:\n"
                    + context["summary"]
            }
        )

    # ========================================================
    # RECENT CONVERSATION
    # ========================================================

    for message in context[
        "recent_messages"
    ]:

        messages.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )

    # ========================================================
    # CURRENT REQUEST
    # ========================================================

    messages.append(
        {
            "role": "user",
            "content": user_request
        }
    )

    return messages


# ============================================================
# EXTRACT LONG-TERM MEMORIES
# ============================================================

async def extract_memories(
    user_request: str,
    assistant_response: str
):
    """
    Ask the LLM to identify stable information explicitly
    provided by the user that may be useful in future chats.
    """

    prompt = f"""
Analyze the following interaction.

USER:
{user_request}

ASSISTANT:
{assistant_response}

Identify information about the USER that is worth remembering
for future conversations.

Only save information that:

- Was explicitly stated by the user.
- Is useful in future conversations.
- Is reasonably stable.
- Is a preference, requirement, goal, budget, recurring need,
  or other useful user-provided information.

Do NOT save:

- Assistant-generated information.
- Temporary conversation details.
- Questions asked by the user.
- Recommendations generated by the assistant.
- Sensitive personal information.
- Information that is not actually stated by the user.

IMPORTANT:

If the user says something like:

"I prefer Honda bikes"

save:

"User prefers Honda bikes"

If the user says:

"I need good mileage"

save:

"User wants a vehicle with good mileage"

If the user says:

"My budget is limited"

save:

"User has a limited budget"

If the user says:

"I need it for three days"

save:

"User needs a bike for 3 days"

Return ONLY valid JSON.

Format:

{{
    "memories": [
        {{
            "memory": "User prefers Honda bikes",
            "category": "preference"
        }}
    ]
}}

If there is nothing useful to remember:

{{
    "memories": []
}}
"""

    try:

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content":
                        "You are a long-term memory extraction system. "
                        "Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        result = (
            response
            .choices[0]
            .message
            .content
        )

        if not result:
            return

        result = result.strip()

        # ----------------------------------------------------
        # Remove markdown code fences
        # ----------------------------------------------------

        if result.startswith("```"):

            result = result.replace(
                "```json",
                ""
            )

            result = result.replace(
                "```",
                ""
            )

            result = result.strip()

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        data = json.loads(result)

        memories = data.get(
            "memories",
            []
        )

        # ----------------------------------------------------
        # Save memories
        # ----------------------------------------------------

        for item in memories:

            if not isinstance(item, dict):
                continue

            memory_text = item.get(
                "memory"
            )

            category = item.get(
                "category",
                "general"
            )

            if not memory_text:
                continue

            memory.add_long_term_memory(
                memory_text.strip(),
                category.strip()
                if isinstance(category, str)
                else "general"
            )

    except json.JSONDecodeError:

        print(
            "\nMemory extraction skipped: "
            "LLM returned invalid JSON."
        )

    except Exception as e:

        print(
            f"\nMemory extraction skipped: {e}"
        )


# ============================================================
# SUMMARIZE CONVERSATION
# ============================================================

async def summarize_conversation():
    """
    Summarize older SQLite conversation messages.

    IMPORTANT:
    This version does NOT use memory.short_term_memory.

    Everything comes from SQLite.
    """

    old_messages = (
        memory.get_messages_for_summary(
            keep_recent=6
        )
    )

    if not old_messages:
        return

    conversation_text = ""

    for message in old_messages:

        conversation_text += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n\n"
        )

    previous_summary = (
        memory.get_summary()
    )

    prompt = f"""
Create a concise summary of the conversation.

The summary will be used by an AI agent in future turns.

Keep important information such as:

- User goals
- User preferences
- User requirements
- Important decisions
- Tasks already completed
- Unresolved questions
- Important context

Do not include unnecessary details.

Previous summary:
{previous_summary}

Older conversation:
{conversation_text}

Return only the summary text.
"""

    try:

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content":
                        "You are a conversation summarization system."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        summary = (
            response
            .choices[0]
            .message
            .content
        )

        if not summary:
            return

        # ----------------------------------------------------
        # Save summary
        # ----------------------------------------------------

        memory.set_summary(
            summary.strip()
        )

        # ----------------------------------------------------
        # Delete old messages.
        # Keep only latest 6.
        # ----------------------------------------------------

        memory.keep_recent_messages(
            limit=6
        )

        print(
            "\n[Conversation summarized successfully]"
        )

    except Exception as e:

        print(
            f"\nSummarization failed: {e}"
        )


# ============================================================
# MAIN AGENT FUNCTION
# ============================================================

async def run_agent(
    user_request: str
):
    """
    Main Memory-Aware AI Agent.

    Flow:

        User Request
             ↓
        Retrieve relevant memories
             ↓
        Retrieve summary
             ↓
        Retrieve recent conversation
             ↓
        Build compact context
             ↓
        LLM
             ↓
        Response
             ↓
        Save conversation
             ↓
        Extract long-term memory
             ↓
        Summarize if necessary
    """

    # ========================================================
    # VALIDATE
    # ========================================================

    if not user_request.strip():

        return (
            "Please enter a valid request."
        )

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    messages = build_messages(
        user_request
    )

    # ========================================================
    # CALL LLM
    # ========================================================

    response = await call_llm(
        messages
    )

    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    memory.add_message(
        "user",
        user_request
    )

    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    memory.add_message(
        "assistant",
        response
    )

    # ========================================================
    # EXTRACT LONG-TERM MEMORY
    # ========================================================

    await extract_memories(
        user_request,
        response
    )

    # ========================================================
    # CHECK FOR SUMMARIZATION
    # ========================================================

    if memory.needs_summarization():

        await summarize_conversation()

    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return response


# ============================================================
# SHOW MEMORIES
# ============================================================

def show_memories():

    memory.show_memory()


# ============================================================
# CLEAR MEMORIES
# ============================================================

def clear_memories():

    memory.clear_long_term_memory()

    print(
        "All long-term memories cleared."
    )


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    import asyncio

    async def test():

        print(
            "\nMemory-Aware AI Agent"
        )

        print(
            "Type 'exit' to quit."
        )

        while True:

            user_input = input(
                "\nYou: "
            ).strip()

            if user_input.lower() in {
                "exit",
                "quit",
                "bye"
            }:

                print(
                    "Goodbye!"
                )

                break

            if user_input.lower() == "show memory":

                show_memories()

                continue

            if user_input.lower() == "clear memory":

                clear_memories()

                continue

            try:

                response = await run_agent(
                    user_input
                )

                print(
                    f"\nAgent: {response}"
                )

            except Exception as e:

                print(
                    f"\nError: {e}"
                )

    asyncio.run(test())