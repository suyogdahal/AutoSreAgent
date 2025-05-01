from pathlib import Path
from typing import Optional
from langchain.tools import BaseTool
from datetime import datetime
import re
from pydantic import Field


LOG_FILE_PATH = Path(
    "/Users/suyog/personal/sreAgent/output/system.log"
)  # Default system log on macOS


class FilteredLogReaderTool(BaseTool):
    """Tool that reads and filters log entries by timestamp."""

    name: str = "filtered_log_reader"
    description: str = """
    Use this tool to read log entries filtered by timestamp.
    Provide from_time and to_time in the format 'YYYY-MM-DD HH:MM:SS' to filter entries.
    If no timestamps are provided, returns the latest 50 log entries.
    """
    log_file_path: Path = Field(default=LOG_FILE_PATH)

    def __init__(self, log_file_path: Path = LOG_FILE_PATH):
        super().__init__()
        self.log_file_path = log_file_path

    def _parse_timestamp(self, log_line: str) -> Optional[datetime]:
        """Extract timestamp from log line."""
        timestamp_match = re.match(
            r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\]", log_line
        )
        if timestamp_match:
            timestamp_str = timestamp_match.group(1)
            # Remove milliseconds for easier parsing
            timestamp_str = timestamp_str.split(".")[0]
            try:
                return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
        return None

    def _run(self, from_time: str = None, to_time: str = None) -> str:
        """Read log entries filtered by timestamp."""
        try:
            if not self.log_file_path.exists():
                return "Log file not found."

            # Parse input timestamps if provided
            from_dt = None
            to_dt = None

            if from_time:
                try:
                    from_dt = datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return "Invalid from_time format. Please use 'YYYY-MM-DD HH:MM:SS'"

            if to_time:
                try:
                    to_dt = datetime.strptime(to_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return "Invalid to_time format. Please use 'YYYY-MM-DD HH:MM:SS'"

            # Read and filter the log file
            with open(self.log_file_path, "r") as file:
                all_lines = file.readlines()

                if not from_dt and not to_dt:
                    # If no filtering, return all last lines
                    return "".join(all_lines)

                filtered_lines = []
                for line in all_lines:
                    line_dt = self._parse_timestamp(line)

                    if not line_dt:
                        continue

                    if from_dt and line_dt < from_dt:
                        continue

                    if to_dt and line_dt > to_dt:
                        continue

                    filtered_lines.append(line)

                if not filtered_lines:
                    return "No log entries found in the specified time range."

                return "".join(filtered_lines)

        except Exception as e:
            return f"Error reading log file: {str(e)}"

    async def _arun(self, from_time: str = None, to_time: str = None):
        """Async implementation would go here."""
        raise NotImplementedError("This tool does not support async")
