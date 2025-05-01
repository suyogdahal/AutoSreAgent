from langchain_community.utilities.stackexchange import StackExchangeAPIWrapper
from langchain.tools import BaseTool
from typing import Optional, Type


class StackExchangeTool(BaseTool):
    name: str = "stack_exchange"
    description: str = """
    Use this tool when you need to search Stack Exchange sites for answers to technical questions.
    Input should be a dictionary with the following keys:
    - 'query': The question or search query
    - 'site': (Optional) The Stack Exchange site to search (default is 'stackoverflow')
    - 'max_results': (Optional) Maximum number of results to return (default is 5)
    
    Example: {"query": "How to handle Kubernetes CrashLoopBackOff", "site": "serverfault", "max_results": 3}
    """
    stack_exchange_wrapper: Optional[Type[StackExchangeAPIWrapper]] = None
    default_site: str = "stackoverflow"
    default_max_results: int = 1

    def __init__(self, site: str = "stackoverflow", max_results: int = 5):
        """Initialize the Stack Exchange tool.

        Args:
            site: The Stack Exchange site to search (default: 'stackoverflow')
            max_results: Maximum number of results to return (default: 5)
        """
        super().__init__()
        self.stack_exchange_wrapper = StackExchangeAPIWrapper(site=site)
        self.default_site = site
        self.default_max_results = max_results

    def _run(self, input_str: str) -> str:
        """Run the Stack Exchange tool.

        Args:
            input_str: Input can be a simple string query or a JSON string with
                       'query', 'site', and 'max_results' keys.

        Returns:
            String containing the search results.
        """
        try:
            # Try to parse input as JSON dictionary
            import json

            input_dict = json.loads(input_str)
            query = input_dict.get("query")
            site = input_dict.get("site", self.default_site)
            max_results = input_dict.get("max_results", self.default_max_results)

            # If site is different from the default, create a new wrapper
            if site != self.default_site:
                stack_exchange = StackExchangeAPIWrapper(site=site)
            else:
                stack_exchange = self.stack_exchange_wrapper

        except (json.JSONDecodeError, TypeError):
            # If input is not valid JSON, treat it as a simple query
            query = input_str
            stack_exchange = self.stack_exchange_wrapper
            max_results = self.default_max_results

        if not query:
            return "Error: No query provided. Please provide a search query."

        return stack_exchange.run(
            query,
        )

    def _arun(self, query: str) -> str:
        """Async implementation of run."""
        # This returns a future, which is treated as awaitable by LangChain
        import asyncio

        return asyncio.get_event_loop().run_in_executor(None, self._run, query)


# Example usage:
if __name__ == "__main__":
    stack_exchange_tool = StackExchangeTool()
    result = stack_exchange_tool.run("How to fix Docker container connection refused")
    print(result)

    # Advanced usage with parameters
    query = '{"query": "Kubernetes troubleshooting guide", "site": "devops", "max_results": 3}'
    result = stack_exchange_tool.run(query)
    print(result)
