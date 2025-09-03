from .llm import LLM, models
from .key_manager import KeyManager

def input_check(str_input: str) -> str:
    """Check if the input is a string with the desired content or the path markdown file, in which case reads it to get the content."""

    if str_input.endswith(".md"):
        with open(str_input, 'r') as f:
            content = f.read()
    elif isinstance(str_input, str):
        content = str_input
    else:
        raise ValueError("Input must be a string or a path to a markdown file.")
    return content

def llm_parser(llm: LLM | str) -> LLM:
    """Get the LLM instance from a string."""
    if isinstance(llm, str):
        try:
            llm = models[llm]
        except KeyError:
            raise KeyError(f"LLM '{llm}' not available. Please select from: {list(models.keys())}")
    return llm
