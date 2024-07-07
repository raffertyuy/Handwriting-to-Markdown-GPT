import datetime
import logging


# A function that takes a text as input and removes possible ```markdown``` code blocks
# for example, if the text is "```markdown\n# Title\n```", it will return "# Title"
# or if the text is "```markdown # Title ```", it will return "# Title"
def remove_markdown_code_blocks(text: str) -> str:
    """
    Removes markdown code blocks from the given text.

    Args:
        text (str): The input text containing markdown code blocks.

    Returns:
        str: The text with markdown code blocks removed.
    """
    text = text.strip()
    if text.startswith("```markdown") and text.endswith("```"):
        text = text[len("```markdown"):]
        text = text[:-len("```")]
        
    return text.strip()

import datetime

def add_datestamp(title):
    """
    Replaces the "{DateStamp}" placeholder in the given title with the current date in the format "%Y%m%d".

    Args:
        title (str): The title string containing the "{DateStamp}" placeholder.

    Returns:
        str: The updated title string with the "{DateStamp}" replaced by the current date.

    Example:
        >>> add_datestamp("{DateStamp} My Notes")
        '20240701 My Notes'
    """
    title = title.replace("{DateStamp}", datetime.datetime.now().strftime("%Y%m%d"))
    return title