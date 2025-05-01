import os
import requests
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


class JiraTicketInput(BaseModel):
    """Inputs for creating a Jira ticket."""

    project_key: str = Field(
        ...,
        description="The project key where the ticket should be created (e.g., 'SRE')",
    )
    summary: str = Field(..., description="The summary/title of the Jira ticket")
    description: str = Field(
        ..., description="The detailed description of the Jira ticket"
    )
    issue_type: str = Field(
        default="Task", description="The type of issue (e.g., 'Bug', 'Task', 'Story')"
    )
    priority: Optional[str] = Field(
        default="Medium",
        description="Priority of the ticket (e.g., 'High', 'Medium', 'Low')",
    )
    assignee: Optional[str] = Field(
        default=None, description="Username of the assignee"
    )


class CreateJiraTicketTool(BaseTool):
    """Tool that creates a Jira ticket."""

    name: str = "create_jira_ticket"
    description: str = """
    Use this tool to create a Jira ticket when there's an issue that needs to be tracked or work that needs to be done.
    Provide project key, summary, description, and optionally issue type, priority, and assignee.
    """
    args_schema: Type[BaseModel] = JiraTicketInput

    def _run(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        assignee: Optional[str] = None,
    ) -> str:
        """Create a Jira ticket with the specified details."""
        # Get Jira credentials from environment variables
        jira_base_url = os.environ.get("JIRA_BASE_URL")
        jira_email = os.environ.get("JIRA_EMAIL")
        jira_api_token = os.environ.get("JIRA_API_TOKEN")

        if not all([jira_base_url, jira_email, jira_api_token]):
            return "Error: Jira credentials not found in environment variables"

        # Prepare the request
        url = f"{jira_base_url}/rest/api/2/issue/"
        auth = (jira_email, jira_api_token)

        # Prepare the payload
        payload: Dict[str, Any] = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
            }
        }

        # Add assignee if provided
        if assignee:
            payload["fields"]["assignee"] = {"name": assignee}

        try:
            response = requests.post(
                url,
                json=payload,
                auth=auth,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            ticket_id = data.get("key")
            ticket_url = f"{jira_base_url}/browse/{ticket_id}"
            return f"Successfully created Jira ticket: {ticket_id}. View it here: {ticket_url}"
        except requests.exceptions.RequestException as e:
            return f"Error creating Jira ticket: {str(e)}"

    def _arun(self, query: str):
        """Async implementation would go here."""
        raise NotImplementedError("This tool does not support async")
