import re


def snake_to_camel(snake_str: str) -> str:
    # Remove any leading/trailing whitespace and split by underscores or spaces
    components = re.split(r'[_\s]+', snake_str.strip())
    # Capitalize each component and join them into a single string
    return ''.join(word.capitalize() for word in components)
