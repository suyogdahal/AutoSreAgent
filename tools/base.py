import re
from typing import Type, Union

from langchain.tools import BaseTool
from utils.logger import logger
from pydantic import BaseModel


class AutoSreAgentBaseTool(BaseTool):
    def _input_parser(
        self,
        ip: Union[str, dict],
    ) -> Type[BaseModel]:
        """
        Langchain agent gives input to the tool as either dictionary or string, so need this boiler plate to parse this
        This should've been handled natively by langchain 🤷
        """
        logger.debug(f"Parser recived input of type -> {type(ip)} \n value -> {ip}")
        keys = list(self.args_schema.model_fields.keys())

        if isinstance(ip, dict):
            values = {key: ip.get(key) for key in keys}
            return self.args_schema(**values)

        elif isinstance(ip, str):
            pattern = ",\s*".join([f"{key}='([^']+)'" for key in keys])
            logger.debug(f"Checking for pattern {pattern}")
            match = re.search(pattern, ip)
            if match:
                logger.debug(f"Regex patterns matched {match.groups()}")
                return self.args_schema(**dict(zip(keys, match.groups())))
            elif "{" in ip or "}" in ip:
                values = eval(ip)
                return self.args_schema(**values)
            else:
                logger.warning(f"Cannot parse the input string {ip}")
                return self.args_schema()
        else:
            raise ValueError("Input must be either a dictionary or string")
