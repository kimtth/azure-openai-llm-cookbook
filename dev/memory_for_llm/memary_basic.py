from memary.agent.chat_agent import ChatAgent

# Define file paths for configuration and memory data
system_persona_txt = "data/system_persona.txt"
user_persona_txt = "data/user_persona.txt"
past_chat_json = "data/past_chat.json"
memory_stream_json = "data/memory_stream.json"
entity_knowledge_store_json = "data/entity_knowledge_store.json"

# Initialize the chat agent
chat_agent = ChatAgent(
    "Personal Agent",
    memory_stream_json,
    entity_knowledge_store_json,
    system_persona_txt,
    user_persona_txt,
    past_chat_json,
)

# Example: Adding a custom tool to multiply two integers
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result."""
    return a * b

chat_agent.add_tool({"multiply": multiply})

# Later, if needed, you can remove the custom tool:
chat_agent.remove_tool("multiply")
