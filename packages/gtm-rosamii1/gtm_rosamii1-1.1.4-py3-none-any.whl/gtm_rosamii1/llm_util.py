import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode


def get_llm():
    """Get the LLM instance."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.environ.get("OPENAI_API_KEY")
    )


def create_tool_node_with_fallback(tools):
    """Create a tool node with fallback handling."""
    return ToolNode(tools)