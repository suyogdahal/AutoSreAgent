from typing import List, Dict, Any, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool


class OncallEmployee(BaseModel):
    name: str
    email: str
    role: str
    team: str


class OncallTeamInput(BaseModel):
    """Input for fetching oncall employees."""

    team: str = Field(
        default=None,
        description="Team name to filter oncall employees by. If not provided, returns all oncall employees.",
    )


class GetOncallEmployeesTool(BaseTool):
    """Tool that returns the list of employees currently on-call."""

    name: str = "get_oncall_employees"
    description: str = """
    Use this tool to get information about which employees are currently on-call.
    You can optionally specify a team name to filter the results. 
    Returns a list of on-call employees with their name, email, role and team.
    Valid team names: Infrastructure, Platform, Reliability, API Services, Data Platform.
    """
    args_schema: Type[BaseModel] = OncallTeamInput

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

    def _run(self, team: str = None) -> str:
        """
        Return the list of on-call employees, optionally filtered by team.

        Args:
            team (str, optional): Team name to filter by

        Returns:
            str: Formatted list of on-call employees
        """
        if team:
            # Check if provided team is in allowed teams (case-insensitive check)
            matching_teams = [
                t for t in self.ALLOWED_TEAMS if t.lower() == team.lower()
            ]
            if not matching_teams:
                return (
                    f"Error: '{team}' is not a valid team name. "
                    f"Valid team names are: {', '.join(self.ALLOWED_TEAMS)}"
                )

            # Use the correctly cased team name
            correct_team_name = matching_teams[0]
            oncall_list = [
                emp for emp in self._oncall_roster if emp["team"] == correct_team_name
            ]
            if not oncall_list:
                return f"No on-call employees found for team '{correct_team_name}'."
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
