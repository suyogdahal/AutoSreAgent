import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from langchain_core.tools.base import ArgsSchema
from loguru import logger
from pydantic import BaseModel, Field
from tools.base import AutoSreAgentBaseTool

LOG_FILE_PATH = Path(
    "/Users/suyog/personal/sreAgent/output/logs.log"
)  # Default system log on macOS


class FilteredLogReaderInput(BaseModel):
    from_time: Optional[str] = Field(
        default=None, description="Start time for filtering logs (YYYY-MM-DD HH:MM:SS)"
    )
    to_time: Optional[str] = Field(
        default=None, description="End time for filtering logs (YYYY-MM-DD HH:MM:SS)"
    )


class FilteredLogReaderTool(AutoSreAgentBaseTool):
    """Tool that reads and filters log entries by timestamp."""

    name: str = "filtered_log_reader"
    description: str = """
    Use this tool to read log entries filtered by timestamp.
    Provide 'from_time' and 'to_time' in the format 'YYYY-MM-DD HH:MM:SS'.
    If no timestamps are provided, returns the entire log entries.
    """
    args_schema: ArgsSchema = FilteredLogReaderInput
    log_file_path: Path = Field(default=LOG_FILE_PATH)

    def __init__(self, log_file_path: Path = LOG_FILE_PATH):
        super().__init__()
        self.log_file_path = log_file_path
        logger.debug(
            f"FilteredLogReaderTool initialized with log path: {log_file_path}"
        )

    def _parse_timestamp_str(self, timestamp_str: str):
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.warning(f"Failed to parse timestamp: {timestamp_str}")
            return None

    def _parse_timestamp(self, log_line: str) -> Optional[datetime]:
        """Extract timestamp from log line."""
        timestamp_match = re.match(
            r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\]", log_line
        )
        if timestamp_match:
            timestamp_str = timestamp_match.group(1)
            # Remove milliseconds for easier parsing
            timestamp_str = timestamp_str.split(".")[0]
            return self._parse_timestamp_str(timestamp_str)
        # logger.debug(f"No timestamp found in log line: {log_line[:50]}...")
        return None

    def _run(self, ip: Union[str | dict]) -> str:
        """Read log entries filtered by timestamp."""
        parsed_input = self._input_parser(ip)
        from_time, to_time = parsed_input.from_time, parsed_input.to_time
        logger.info(
            f"Reading logs with filters - from_time: {from_time}, to_time: {to_time}"
        )

        try:
            if not self.log_file_path.exists():
                logger.error(f"Log file not found at: {self.log_file_path}")
                return "Log file not found."

            # Parse input timestamps if provided
            from_dt = None
            to_dt = None

            if from_time:
                try:
                    from_dt = datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S")
                    logger.debug(f"Parsed from_time to {from_dt}")
                except ValueError:
                    logger.error(f"Invalid from_time format: {from_time}")
                    return "Invalid from_time format. Please use 'YYYY-MM-DD HH:MM:SS'"

            if to_time:
                try:
                    to_dt = datetime.strptime(to_time, "%Y-%m-%d %H:%M:%S")
                    logger.debug(f"Parsed to_time to {to_dt}")
                except ValueError:
                    logger.error(f"Invalid to_time format: {to_time}")
                    return "Invalid to_time format. Please use 'YYYY-MM-DD HH:MM:SS'"

            # Read and filter the log file
            logger.debug(f"Opening log file: {self.log_file_path}")
            with open(self.log_file_path, "r") as file:
                all_lines = file.readlines()
                logger.debug(f"Read {len(all_lines)} lines from log file")

                if not from_dt and not to_dt:
                    # If no filtering, return all lines
                    logger.info("No time filtering applied, returning all log entries")
                    return "".join(all_lines)

                filtered_lines = []
                added_lines = set()
                for idx, line in enumerate(all_lines):
                    line_dt = self._parse_timestamp(line)

                    if line_dt:
                        if from_dt and line_dt < from_dt:
                            continue

                        if to_dt and line_dt > to_dt:
                            continue

                    # if consecutive line is not in added_lines continue
                    if added_lines and (idx - 1) not in added_lines:
                        continue

                    added_lines.add(idx)
                    filtered_lines.append(line)

                logger.info(
                    f"Filtered {len(filtered_lines)}/{len(all_lines)} log entries"
                )

                if not filtered_lines:
                    logger.warning("No log entries found in the specified time range")
                    return "No log entries found in the specified time range."

                return "".join(filtered_lines)

        except Exception as e:
            logger.exception(f"Error reading log file: {e}")
            return f"Error reading log file: {str(e)}"

    async def _arun(self, **kwargs):
        """Async implementation would go here."""
        logger.warning("Async operation attempted but not implemented")
        raise NotImplementedError("This tool does not support async")


if __name__ == "__main__":
    # Example usage
    tool = FilteredLogReaderTool()
    result = tool._run(
        ip={"from_time": "2025-05-01 17:44:43", "to_time": "2025-05-01 17:45:17"}
    )
    print(result)
