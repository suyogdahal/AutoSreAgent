import os
import time
import re
from datetime import datetime, timedelta
from pathlib import Path

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import OpenAI
from langchain_community.utilities.stackexchange import StackExchangeAPIWrapper
from dotenv import load_dotenv

# Import custom tools
from tools.oncall_employees import GetOncallEmployeesTool
from tools.jira import CreateJiraTicketTool
from tools.file import FilteredLogReaderTool

# Load environment variables
load_dotenv()

# Configure the log file path
LOG_FILE_PATH = Path("output/logs.log")
LOG_FILE_PATH.parent.mkdir(exist_ok=True)

# Monitoring interval in seconds
MONITORING_INTERVAL = 60

# Keep track of issues we've already addressed
processed_issues = set()
last_check_time = None


def setup_agent():
    """Set up the ReAct agent with the necessary tools."""
    # Initialize LLM
    llm = OpenAI(temperature=0)

    # Load ReAct prompt
    prompt = hub.pull("hwchase17/react")

    # Initialize tools
    tools = [
        FilteredLogReaderTool(log_file_path=LOG_FILE_PATH),
        StackExchangeAPIWrapper(),
        GetOncallEmployeesTool(),
        CreateJiraTicketTool(),
    ]

    # Create the agent
    agent = create_react_agent(llm, tools, prompt)

    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )

    return agent_executor


def generate_error_fingerprint(error_info: str) -> str:
    """Generate a unique fingerprint for an error to avoid duplicates."""
    # Extract error type and key information
    error_type_match = re.search(
        r"Error type: ([A-Za-z0-9_]+(?:Error|Exception|Failure))", error_info
    )
    error_type = error_type_match.group(1) if error_type_match else "UnknownError"

    # Look for specific error messages or details
    relevant_lines = []
    for line in error_info.split("\n"):
        if "Line" in line and ".py" in line:
            relevant_lines.append(line)

    # Combine the information to create a fingerprint
    fingerprint_parts = [error_type] + relevant_lines[:2]
    return "::".join(fingerprint_parts)


def monitor_logs():
    """Main function to periodically monitor logs."""
    print("Starting log monitoring service...")

    global last_check_time

    # Initialize last_check_time to a short while ago for the first run
    last_check_time = datetime.now() - timedelta(minutes=5)

    # Set up the agent
    agent = setup_agent()

    # Ensure log file exists
    _ensure_log_file_exists()

    while True:
        try:
            current_time = datetime.now()
            print(f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Checking logs...")

            # Check for and process any new errors
            _process_new_errors(agent, last_check_time, current_time)

            # Update the last check time
            last_check_time = current_time

            # Wait for the next check
            print(f"Waiting {MONITORING_INTERVAL} seconds until next check...")
            time.sleep(MONITORING_INTERVAL)

        except Exception as e:
            print(f"Error in monitoring loop: {str(e)}")
            time.sleep(MONITORING_INTERVAL)


def _ensure_log_file_exists():
    """Ensure the log file exists, creating it if necessary."""
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w") as f:
            f.write("")
        print(f"Created empty log file at {LOG_FILE_PATH}")


def _process_new_errors(agent, from_time, to_time):
    """Check for new errors and process them if found."""
    # Format times for the filtered log reader
    from_time_str = from_time.strftime("%Y-%m-%d %H:%M:%S")
    to_time_str = to_time.strftime("%Y-%m-%d %H:%M:%S")

    # Read only the logs from the last check until now
    prompt = (
        f"Read logs from {from_time_str} to {to_time_str} and check for any errors or critical issues. "
        f"Use the filtered_log_reader tool with these exact timestamps to only look at new logs since the last check."
    )

    response = agent.invoke({"input": prompt})

    # Check if new errors were found
    if (
        "No errors found" not in response["output"]
        and "error" in response["output"].lower()
    ):
        error_fingerprint = generate_error_fingerprint(response["output"])

        # Process only if we haven't seen this error before
        if error_fingerprint not in processed_issues:
            processed_issues.add(error_fingerprint)
            print("Found new error, investigating and creating ticket...")

            # Investigate and create ticket
            _investigate_and_create_ticket(agent, response["output"])
        else:
            print(f"Already processed this error, skipping: {error_fingerprint}")
    else:
        print("No new errors detected.")


def _investigate_and_create_ticket(agent, error_output):
    """Investigate an error and create a ticket for it."""
    investigation_prompt = (
        f"Based on this error information, find out more about this issue using StackExchange if needed: {error_output}. "
        f"Then determine which team should handle this issue, get the oncall employees for that team, "
        f"and create an appropriate Jira ticket."
    )

    investigation_response = agent.invoke({"input": investigation_prompt})
    print(f"Agent response: {investigation_response['output']}")


if __name__ == "__main__":
    monitor_logs()
