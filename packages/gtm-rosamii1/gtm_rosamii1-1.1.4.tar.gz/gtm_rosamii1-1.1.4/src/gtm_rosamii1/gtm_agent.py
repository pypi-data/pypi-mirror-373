import csv
import os
import uuid
import asyncio

from typing import Any, List
from langchain.chains import llm
from langchain.memory import ConversationBufferMemory
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

import simple_agent
import samples
import util

from typing import Annotated

from typing_extensions import TypedDict

# Initialize OpenAI Search Tool


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)
memory = ConversationBufferMemory()

openai_key = os.environ.get('OPENAI_API_KEY')

headers = {"Authorization": f"Bearer {openai_key}"}

llm = init_chat_model("openai:gpt-4.1-nano")

run_chatbot = False


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")

graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            return value["messages"][-1].content


class EmailReq(BaseModel):
    name: str = Field(description="recipient name")
    email_id: str = Field(description="recipient email id")
    company: str = Field(description="company name")
    subject: str = Field(description="subject of the email")
    content: str = Field(description="Content of the email")
    supported_links: list[str] = Field(
        description="Supported links for the email content"
    )


async def _get_base_template(title: str, category: str, business: str, company: str) -> ChatPromptTemplate:
    with open(os.path.join(os.path.dirname(__file__), "gtm_prompt.md"), "r") as file:
        prompt = file.read()
    with open(os.path.join(os.path.dirname(__file__), "sample_placeholder.md"), "r") as file:
        placeholder_file = file.read()
    sample_emails = ".".join(samples.get_sample_emails(title, category, business))
    prompt = prompt + "\n Sample emails \n" + sample_emails + placeholder_file
    return ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("placeholder", "{messages}"),
        ]
    )


async def send_email(email_req: EmailReq, ) -> str:
    """This takes emailReq as input and sends email to the recipient"""
    print("Email content -----------")
    print(email_req.subject + "\n")
    print(email_req.content + "\n")
    with open("emails_notepad.txt", "a") as file:
        file.write(f"EmailId: {email_req.email_id}\n")
        file.write(f"Subject: {email_req.subject}\n")
        file.write(f"Content: {email_req.content}\n")
        file.write("-" * 40 + "\n")
    util.send_email_to(email_req.subject, email_req.content, email_req.email_id)
    return "Email sent successfully!"


# Google Search tool, Allows AI to search the web for information
async def get_tools() -> List[Any]:
    return [TavilySearch(max_results=5), send_email]


async def answer_agent_question(question: str, title: str, category: str, business: str, company: str) -> str:
    """Answer agent question with proper error handling and limits."""
    try:
        base_template = await _get_base_template(title, category, business, company)
        tools = await get_tools()

        config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
            },
            "recursion_limit": 100,
        }

        messages = {"messages": ("user", question)}
        print(question)
        print(f"Processing question for {title} at {category}...")

        # Add timeout to prevent hanging
        result = await asyncio.wait_for(
            simple_agent.execute_graph(base_template, tools, messages, config),
            timeout=30  # 60 second timeout
        )

        if result and "messages" in result and result["messages"]:
            return result["messages"][-1].content
        else:
            return "Failed to generate email content. Please try again."

    except asyncio.TimeoutError:
        print("Graph execution timed out")
        return "Email generation timed out. Please try again."
    except Exception as e:
        print(f"Error in answer_agent_question: {e}")
        return f"Error generating email: {str(e)}"


async def generate_mail(row, row_number) -> str:
    """Generate email with improved error handling."""
    try:
        company = row[0] if len(row) > 0 else "Unknown Company"
        name = row[3] if len(row) > 3 else "Unknown Name"
        title = row[4] if len(row) > 4 else "Unknown Title"
        category = row[1] if len(row) > 1 else "Unknown Category"
        linkedin = row[5] if len(row) > 5 else ""
        email = row[6] if len(row) > 6 else ""
        business = row[2] if len(row) > 2 else "Unknown Business"

        question = f"""
         ### send outreach mail for below person
         Name: {name}|{title}
         Email: {email}
         Linkedin: {linkedin}
         Company Name: {company}
         Category: {category}
         Business: {business}

         ### send outreach mail for below person

         """

        print(f"Row {row_number}: Processing {name} at {company}")
        response = await answer_agent_question(question, title, category, business, company)
        print(f"Row {row_number}: Completed")
        return response

    except Exception as e:
        print(f"Row {row_number}: Error in generate_mail: {e}")
        return f"Error: {str(e)}"


async def process_emails(file_path: str) -> str | None:
    email = ""
    """Process emails with better error handling and progress tracking."""
    try:
        file_path = os.path.join(os.path.dirname(__file__), file_path)

        with open(file_path, mode="r", encoding="latin-1") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row

            processed = 0
            errors = 0

            for row_number, row in enumerate(csv_reader, start=1):
                try:
                    if len(row) < 7:  # Check if row has enough columns
                        print(f"Row {row_number}: Skipping - insufficient data")
                        continue

                    result = await generate_mail(row, row_number)
                    email += f"Generated email:\n{result}"
                    print(email)
                    processed += 1

                    # Progress indicator
                    if processed % 5 == 0:
                        print(f"Progress: {processed} emails processed")

                except Exception as e:
                    errors += 1
                    print(f"Row {row_number}: Error processing row: {e}")
                    continue

            print(f"Processing complete: {processed} emails processed, {errors} errors")

            return email

    except Exception as e:
        print(f"Error in process_emails: {e}")


async def start(file_name: str) -> str | None:
    email = await process_emails(file_name)
    return email