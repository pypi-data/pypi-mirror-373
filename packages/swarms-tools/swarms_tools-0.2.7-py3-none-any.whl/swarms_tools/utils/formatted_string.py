from typing import Union


def format_object_to_string(
    obj: Union[dict, list], indent: int = 4, level: int = 0
) -> str:
    """
    Converts any serializable Python object into a formatted string without braces,
    displaying key-value pairs row by row.

    Args:
        obj (Union[dict, list]): The object to format (e.g., dict, list).
        indent (int): The number of spaces to use for indentation.
        level (int): The current indentation level (used internally for recursion).

    Returns:
        str: A human-readable formatted string representation of the object.
    """
    lines = []
    prefix = " " * (level * indent)

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(
                    format_object_to_string(value, indent, level + 1)
                )
            else:
                lines.append(f"{prefix}{key}: {value}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(
                    format_object_to_string(item, indent, level + 1)
                )
            else:
                lines.append(f"{prefix}- {item}")
    else:
        lines.append(f"{prefix}{obj}")

    return "\n".join(lines)


# # Example usage
# example_data = {
#     "name": "Alice",
#     "age": 30,
#     "hobbies": ["reading", "traveling"],
#     "education": {
#         "degree": "Bachelor's",
#         "field": "Computer Science",
#         "year": 2015
#     }
# }

# formatted_string = format_object_to_string(example_data)
# print(formatted_string)
