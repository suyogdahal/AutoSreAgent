import os
from typing import Optional, Union

from atlassian import Jira
from dotenv import load_dotenv
from langchain_core.tools.base import ArgsSchema
from loguru import logger
from pydantic import BaseModel, Field

from base import AutoSreAgentBaseTool

load_dotenv("/Users/suyog/personal/sreAgent/.env")


class JiraTicketInput(BaseModel):
    summary: str = Field(..., description="Summary/title of the Jira ticket")
    description: str = Field(..., description="Detailed description of the Jira ticket")
    issue_type: Optional[str] = Field(
        default="Task", description="Type of issue (e.g., 'Bug')"
    )
    assignee: Optional[str] = Field(default=None, description="Assignee's username")


class CreateJiraTicketTool(AutoSreAgentBaseTool):
    name: str = "create_jira_ticket"
    description: str = """
    Use this tool to create a Jira ticket with a summary, description,
    and optionally issue type, and assignee.
    """
    args_schema: Optional[ArgsSchema] = JiraTicketInput
    jira_base_url: str = os.environ.get("JIRA_BASE_URL")
    jira_email: str = os.environ.get("JIRA_EMAIL")
    jira_api_token: str = os.environ.get("JIRA_API_TOKEN")
    jira_project_name: str = os.environ.get("JIRA_PROJECT_NAME")

    def _run(self, ip: Union[str | dict]) -> str:
        if not all(
            [
                self.jira_base_url,
                self.jira_email,
                self.jira_api_token,
                self.jira_project_name,
            ]
        ):
            return (
                "Error: Jira credentials are not properly set in environment variables"
            )

        parsed_input = self._input_parser(ip)
        summary, description, issue_type, assignee = (
            parsed_input.summary,
            parsed_input.description,
            parsed_input.issue_type,
            parsed_input.assignee,
        )

        logger.debug(
            f"Connecting to JIRA at {self.jira_base_url} with user {self.jira_email}"
        )
        jira = Jira(
            url=self.jira_base_url,
            username=self.jira_email,
            password=self.jira_api_token,
            cloud=True,
        )

        fields = {
            "project": {"key": self.jira_project_name},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type or "Task"},
        }

        if assignee:
            fields["assignee"] = {"name": assignee}

        try:
            result = jira.issue_create(fields=fields)
            ticket_key = result.get("key")
            ticket_url = f"{self.jira_base_url}/browse/{ticket_key}"
            return f"Successfully created Jira ticket: {ticket_key}. View it here: {ticket_url}"
        except Exception as e:
            logger.exception("Failed to create Jira ticket")
            return f"Error creating Jira ticket: {str(e)}"

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")


if __name__ == "__main__":
    tool = CreateJiraTicketTool()
    ticket_input = {
        "summary": "Connection reset by peer while fetching data from cache server",
        "description": "An error occurred while processing the /api/auth request. ConnectionResetError indicates that the cache server connection was closed unexpectedly. Please investigate the status of the cache server, ensuring it is operational and not overloaded.",
        "assignee": "alice.johnson@example.com",
    }
    result = tool._run(ticket_input)
    print(result)
