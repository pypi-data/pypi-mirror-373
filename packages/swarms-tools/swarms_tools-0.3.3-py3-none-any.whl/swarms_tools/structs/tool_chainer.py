from typing import Callable, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from swarms_tools.utils.formatted_string import (
    format_object_to_string,
)


def tool_chainer(
    tools: List[Callable[[], Any]], parallel: bool = True
) -> str:
    """
    Executes a list of callable tools in parallel or sequentially.

    Args:
        tools (List[Callable[[], Any]]): A list of callables (functions) to be executed.
        parallel (bool): If True, execute tools in parallel using threads. If False, execute sequentially.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the results or errors from each tool.
        Each dictionary contains:
            - "tool": The tool's name or callable representation.
            - "status": "success" or "error".
            - "result": The result of the callable, or the error message if execution fails.
    """
    logger.info(
        f"Executing {len(tools)} tools {'in parallel' if parallel else 'sequentially'}"
    )

    results = []

    if parallel:
        # Parallel execution using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            future_to_tool = {
                executor.submit(tool): tool for tool in tools
            }

            for future in as_completed(future_to_tool):
                tool = future_to_tool[future]
                try:
                    result = future.result()
                    logger.info(
                        f"Tool {tool.__name__} executed successfully"
                    )
                    results.append(
                        {
                            "tool": tool.__name__,
                            "status": "success",
                            "result": result,
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Error executing tool {tool.__name__}: {e}"
                    )
                    results.append(
                        {
                            "tool": tool.__name__,
                            "status": "error",
                            "result": str(e),
                        }
                    )
    else:
        # Sequential execution
        for tool in tools:
            try:
                logger.info(f"Executing tool {tool.__name__}")
                result = tool()
                logger.info(
                    f"Tool {tool.__name__} executed successfully"
                )
                results.append(
                    {
                        "tool": tool.__name__,
                        "status": "success",
                        "result": result,
                    }
                )
            except Exception as e:
                logger.error(
                    f"Error executing tool {tool.__name__}: {e}"
                )
                results.append(
                    {
                        "tool": tool.__name__,
                        "status": "error",
                        "result": str(e),
                    }
                )

    return format_object_to_string(results)


# # Example usage
# if __name__ == "__main__":
#     logger.add("tool_chainer.log", rotation="500 MB", level="INFO")

#     # Example tools
#     def tool1():
#         return "Tool1 Result"

#     def tool2():
#         return "Tool2 Result"

#     # def tool3():
#     #     raise ValueError("Simulated error in Tool3")

#     tools = [tool1, tool2]

#     # Parallel execution
#     parallel_results = tool_chainer(tools, parallel=True)
#     print("Parallel Results:", parallel_results)

#     # Sequential execution
#     # sequential_results = tool_chainer(tools, parallel=False)
#     # print("Sequential Results:", sequential_results)
