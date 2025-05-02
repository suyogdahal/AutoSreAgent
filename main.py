# main script that coniniously monitors the log file as per the set interval
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from loguru import logger

from tools.file import FilteredLogReaderTool
from tools.jira import CreateJiraTicketTool
from tools.oncall_employees import GetOncallEmployeesTool

# Load environment variables
load_dotenv()

# Configure the log file path
LOG_FILE_PATH = Path(os.getenv("LOG_FILE_PATH", "output/logs.log"))
LOG_FILE_PATH.parent.mkdir(exist_ok=True)

# Monitoring interval in seconds
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", 60))

# Keep track of issues we've already addressed
processed_issues = set()
last_check_time = None


def setup_agent():
    """Set up the ReAct agent with the necessary tools."""
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Load ReAct prompt
    prompt = hub.pull("hwchase17/react")

    # Initialize tools
    tools = [
        FilteredLogReaderTool(log_file_path=LOG_FILE_PATH),
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


def monitor_logs():
    """Main function to periodically monitor logs."""
    logger.info("Starting log monitoring service...")

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
            logger.debug(
                f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Checking logs..."
            )

            # Check for and process any new errors
            _process_new_errors(agent, last_check_time, current_time)

            # Update the last check time
            last_check_time = current_time

            # Wait for the next check
            logger.debug(f"Waiting {MONITORING_INTERVAL} seconds until next check...")
            time.sleep(MONITORING_INTERVAL)

        except Exception as e:
            logger.debug(f"Error in monitoring loop: {str(e)}")
            time.sleep(MONITORING_INTERVAL)


def _ensure_log_file_exists():
    """Ensure the log file exists, creating it if necessary."""
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w") as f:
            f.write("")
        logger.debug(f"Created empty log file at {LOG_FILE_PATH}")


def _process_new_errors(agent, from_time, to_time):
    """Check for new errors and process them if found."""
    from_time_str = from_time.strftime("%Y-%m-%d %H:%M:%S")
    to_time_str = to_time.strftime("%Y-%m-%d %H:%M:%S")

    prompt = (
        f"Read logs from {from_time_str} to {to_time_str} and check for any errors or critical issues. "
        "Use the filtered_log_reader tool with these exact timestamps to only look at new logs since the last check."
        "You need to then idenify the potential cause and the possible solution for each of the error you saw."
        "After idenifying the potential cause and possible solution use get_oncall_employees tool to find filter out on-call employees best suited to handle each error"
        "Finally use create_jira_ticket to create appropriate tickets and assign it to the right employee"
    )

    response = agent.invoke({"input": prompt})
    logger.debug(f"Final response from agent: {response}")


if __name__ == "__main__":
    monitor_logs()
