import os
import asyncio
import openai
import gtm_agent
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from fastmcp.resources.types import FileResource

from pathlib import Path

import csv
import pandas as pd
import sys

print("MCP Wrapper starting...", file=sys.stderr)
sys.stderr.flush()

mcp = FastMCP("FactorialTool")

app = Server("GTM")

# @mcp.tool()
# def load_csv(file_path: str) -> list[dict]:
#     # Read uploaded file from Claude's temp location
#     rows = []
#     with open(file_path, newline='', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             rows.append(dict(row))
#     return rows


# @mcp.tool()
# def list_inputs() -> list[FileResource]:
#     # Return all available uploaded files
#     return list(mcp.resources.values())

# @mcp.resource()
# def upload_file(path: str) -> FileResource:
#     # Called when Claude uploads a file; returns a FileResource for discovery
#     return FileResource(
#         path=path,
#         description=f"Uploaded CSV: {path}",
#     )

@mcp.tool()
def Hello():
    print("Hello World")
    return None

@mcp.tool()
def parse_csv_to_list(res: FileResource) -> list[str]:
    rows = []
    with open(res.path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


@mcp.prompt()
def gtm_email_prompt(
    name: str,
    company: str,
    category: str,
    email: str,
    linkedin: str = "",
    business: str = "",
    title: str = "",
) -> str:
    # Load the markdown template
    config_dir = Path(__file__).parent
    template = (config_dir / "gtm_prompt.md").read_text(encoding="utf-8")
    email_sample = (config_dir / "emails_notepad.txt").read_text(encoding="utf-8")
    return template.format(
        name=name,
        company=company,
        category=category,
        linkedin=linkedin,
        email=email,
        business=business,
        title=title,
    )
@mcp.tool()
async def fill_template(email_list: list[str]) -> list[str]:
    ##answer_list = (["Challenges", "Personal Info", "Risks"])
    config_dir = Path(__file__).parent
    template = (config_dir / "gtm_prompt.md").read_text(encoding="utf-8")
    template_mod = ""
    df_char = pd.DataFrame(email_list)

    template_list = []
    for x in email_list:
        template_mod = template.format(
        name=email_list[x][0],
        company=email_list[x][1],
        category=email_list[x][2],
        linkedin=email_list[x][3],
        email=email_list[x][4],
        business=email_list[x][5],
        title=email_list[x][6],
        )
        template_list.append(template_mod)
    return template_list

@mcp.tool()
async def continue_email_generation(next_email: int, res: FileResource):
    next_email += 1
    await generate_email(res, next_email)

@mcp.tool()
async def start_email_generation(res: FileResource):
    await generate_email(res, 0)

@mcp.tool()
async def generate_email(res: FileResource, row_number: int):
    email = ""
    try:
        with open(res.path, mode="r", encoding="latin-1") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row

            processed = 0
            errors = 0

            for row in enumerate(csv_reader, start=0):
                try:
                    if len(row) < 6:  # Check if row has enough columns
                        print(f"Row {row_number}: Skipping - insufficient data")
                        continue

                    result = await gtm_agent.generate_mail(row, row_number)
                    email += f"Generated email:\n{result}"
                    processed += 1

                    # Add delay to prevent overwhelming the system
                    await asyncio.sleep(1)

                    # Progress indicator
                    if processed % 5 == 0:
                        print(f"Progress: {processed} emails processed")

                except Exception as e:
                    errors += 1
                    print(f"Row {row_number}: Error processing row: {e}")
                    continue

            print(f"Processing complete: {processed} emails processed, {errors} errors")

            return email, res, row_number

    except Exception as e:
        print(f"Error in process_emails: {e}")


def fetch_info():
    challenges = ""
    personal = ""
    risk = ""
    ##gain = fetch.get_gain_info(row["Company"], challenges)

    mod_ans = [challenges, personal, risk]
    ##answer_list = np.vstack([answer_list, mod_ans])

@mcp.prompt()
def gtm_inv_research(company: str) -> str:
    # Load the markdown template
    config_dir = Path(__file__).parent
    template = (config_dir / "inv_research_prompt.md").read_text(encoding="utf-8")
    return template.format(company=company)


@mcp.prompt()
def gtm_gen_research(company: str) -> str:
    # Load the markdown template
    config_dir = Path(__file__).parent
    template = (config_dir / "gen_research.md").read_text(encoding="utf-8")
    return template.format(company=company)


if __name__ == "__main__":
    mcp.run(transport="stdio")
