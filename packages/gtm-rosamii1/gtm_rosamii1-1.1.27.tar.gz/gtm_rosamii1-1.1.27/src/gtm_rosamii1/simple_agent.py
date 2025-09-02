import os
from typing import Annotated

from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages.utils import AnyMessage
from langchain_core.messages import AIMessage, ToolMessage
from psycopg import Connection
from typing_extensions import TypedDict

import llm_util


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        retry_count = 0
        max_retries = 3
        result = None

        while retry_count < max_retries:
            configuration = config.get("configurable", {})
            tenant_id = configuration.get("tenant_id", None)
            state = {**state, "tenant_info": tenant_id}
            result = self.runnable.invoke(state)

            if not result.tool_calls and (
                    not result.content
                    or isinstance(result.content, list)
                    and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
                retry_count += 1
            else:
                break

        if result is None or (retry_count >= max_retries and not result.content):
            from langchain_core.messages import AIMessage
            result = AIMessage(content="I apologize, but I'm having trouble generating a response. Please try again.")

        # Just return the messages - no iteration counter needed
        return {"messages": result}


def should_continue(state: State) -> str:
    """Determine if the graph should continue or end with simple loop prevention."""
    messages = state["messages"]
    if not messages:
        print("DEBUG: No messages, ending")
        return END

    last_message = messages[-1]

    # Count total messages to prevent infinite loops
    total_messages = len(messages)
    if total_messages > 30:  # Safety check based on message count
        print(f"DEBUG: Too many messages ({total_messages}), ending")
        return END

    # Check if the last message is an AI message with tool calls
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        print("DEBUG: Going to tools")
        return "tools"

    # If it's a tool message, go back to assistant
    if isinstance(last_message, ToolMessage):
        print("DEBUG: Going back to assistant")
        return "assistant"

    # If the assistant provided a final answer without tool calls, end
    print("DEBUG: Ending conversation")
    return END


def _get_graph(llm_runnable, tools, conn):
    builder = StateGraph(State)
    builder.add_node("assistant", Assistant(llm_runnable))
    builder.add_node("tools", llm_util.create_tool_node_with_fallback(tools))

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    builder.add_edge("tools", "assistant")

    if conn:
        try:
            checkpointer = PostgresSaver(conn)
            checkpointer.setup()
            graph = builder.compile(checkpointer=checkpointer)
        except Exception as e:
            print(f"PostgreSQL checkpointer failed: {e}")
            memory = MemorySaver()
            graph = builder.compile(checkpointer=memory)
    else:
        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)

    return graph


def _get_simple_graph(base_prompt, tools, conn=None):
    print("Getting new graph")
    llm = llm_util.get_llm()
    llm_runnable = base_prompt | llm.bind_tools(tools)
    graph = _get_graph(llm_runnable, tools, conn)
    return graph


async def execute_graph(base_prompt, tools, messages, config):
    try:
        graph = _get_simple_graph(base_prompt, tools, conn=None)
        response = await graph.ainvoke(messages, config)
        print("Graph execution completed successfully")
        return response
    except Exception as e:
        print(f"Graph execution failed: {e}")
        raise e

    # No need to initialize iteration counter
    try:
        with Connection.connect(os.environ["DATABASE_URL"], **connection_kwargs) as conn:
            graph = _get_simple_graph(base_prompt, tools, conn)
            response = graph.invoke(messages, config)
            print("Graph execution completed successfully")
            print(response)
            return response
    except Exception as e:
        print(f"Database connection failed: {e}")
        try:
            graph = _get_simple_graph(base_prompt, tools, conn=None)
            response = graph.invoke(messages, config)
            print("Graph execution completed with memory fallback")
            print(response)
            return response
        except Exception as inner_e:
            print(f"Memory fallback also failed: {inner_e}")
            raise inner_e