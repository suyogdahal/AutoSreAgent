from typing import Any, Dict, List, Optional, Type, Union

from langchain.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from utils.logger import logger
from pydantic import BaseModel, Field

from tools.base import AutoSreAgentBaseTool


class OncallEmployee(BaseModel):
    name: str
    email: str
    role: str
    team: str


class OncallTeamInput(BaseModel):
    """Input for fetching oncall employees."""

    team_name: Optional[str] = Field(
        default=None,
        description="Team's name to filter oncall employees by. If not provided, returns all oncall employees.",
    )


class GetOncallEmployeesTool(AutoSreAgentBaseTool):
    """Tool that returns the list of employees currently on-call."""

    name: str = "get_oncall_employees"
    description: str = """
    Use this tool to get information about which employees are currently on-call.
    You can optionally specify a team_name to filter the results. 
    Returns a list of on-call employees with their name, email, role and team.
    Valid team names: Infrastructure, Platform, Reliability, API Services, Data Platform.
    """
    args_schema: ArgsSchema = OncallTeamInput

    # Define allowed team names as a class attribute
    ALLOWED_TEAMS: List[str] = [
        "Infrastructure",
        "Platform",
        "Reliability",
        "API Services",
        "Data Platform",
    ]

    def __init__(self):
        """Initialize with static oncall data."""
        super().__init__()
        # Static on-call roster for demonstration
        self._oncall_roster = [
            {
                "name": "Alice Johnson",
                "email": "alice.johnson@example.com",
                "role": "Senior SRE",
                "team": "Infrastructure",
            },
            {
                "name": "Bob Smith",
                "email": "bob.smith@example.com",
                "role": "DevOps Engineer",
                "team": "Platform",
            },
            {
                "name": "Carol Davis",
                "email": "carol.davis@example.com",
                "role": "SRE Manager",
                "team": "Reliability",
            },
            {
                "name": "Dave Wilson",
                "email": "dave.wilson@example.com",
                "role": "Backend Engineer",
                "team": "API Services",
            },
            {
                "name": "Eva Martinez",
                "email": "eva.martinez@example.com",
                "role": "Database Engineer",
                "team": "Data Platform",
            },
            {
                "name": "Frank Lee",
                "email": "frank.lee@example.com",
                "role": "Network Engineer",
                "team": "Infrastructure",
            },
        ]

    def _run(self, ip: Union[str | dict]) -> str:
        """
        Return the list of on-call employees, optionally filtered by team_name.

        Args:
            team_name (str, optional): Team name to filter by

        Returns:
            str: Formatted list of on-call employees
        """
        parsed_input = self._input_parser(ip=ip)
        team = parsed_input.team_name
        if team not in self.ALLOWED_TEAMS:
            logger.warning(
                f"Invalid team name provided: {team}. Ignoring the filter ..."
                f"Valid team names are: {', '.join(self.ALLOWED_TEAMS)}"
            )
            team = None

        if team:
            oncall_list = [emp for emp in self._oncall_roster if emp["team"] == team]
            if not oncall_list:
                return f"No on-call employees found for team '{team}'."
        else:
            oncall_list = self._oncall_roster

        # Format the response
        result = "Current on-call employees:\n\n"
        for emp in oncall_list:
            result += (
                f"Name: {emp['name']}\n"
                f"Email: {emp['email']}\n"
                f"Role: {emp['role']}\n"
                f"Team: {emp['team']}\n\n"
            )

        return result

    def _arun(self, team: str = None):
        """Async implementation would go here."""
        raise NotImplementedError("This tool does not support async")


if __name__ == "__main__":
    tool = GetOncallEmployeesTool()
    result = tool._run(ip="team_name='Infrastructure' ")
    print(result)
