import json
import logging

# Create a logger for your chatbot application
logger = logging.getLogger("chatbotLogger")
logger.setLevel(logging.DEBUG)

# Create a stream handler to output logs to the console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Define the format for log messages
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
stream_handler.setFormatter(formatter)

# Add the handler to the logger if no handlers have been added yet
if not logger.handlers:
    logger.addHandler(stream_handler)

# Log an initialization message
logger.debug("Logger has been initialized.")

# Note:
# The logging module used above is part of Python's standard library.
# No extra package installation is required.

def parse_code_block(response: str) -> str:
    """
    Extracts code blocks from the response and returns the code content.

    Args:
        response (str): The response text from the model.

    Returns:
        str: The extracted code content.
    """
    if "```" in response:
        start = response.find("```") + 3
        end = response.find("```", start)
        if end != -1:
            code_block = response[start:end].strip()
            lines = code_block.splitlines()
            if len(lines) > 0 and len(lines[0]) > 0:
                return "\n".join(lines[1:])
    return ""

# Log a message indicating that the helper functions have been loaded
def parse_json_from_response(response: str) -> dict:
    """
    Extracts JSON content from the response and returns the JSON object.

    Args:
        response (str): The response text from the model. 
            Example: " { "key": "value" } || [ {"key": "value"}, {"key": "value"}, ... ] "

    Returns:
        dict: The extracted JSON object.
    """
    string = response.strip()

    if string.startswith("```") and string.endswith("```"):
        return parse_code_block(string)

    if string.startswith("{") and string.endswith("}"):
        try:
            return json.loads(string)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from response.")
    elif string.startswith("[") and string.endswith("]"):
        try:
            return json.loads(string)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from response.")
    return {}