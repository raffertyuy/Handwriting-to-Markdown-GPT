import base64

def append_text_to_system_prompt(prompt, text):
    """
    Appends text to the system prompt.
    Args:
        prompt (list): The existing system prompt.
        text (str): The text to be appended.
    Returns:
        list: The updated system prompt with the appended text.
    """
    if not prompt:
        prompt = []
    
    prompt.append({"type": "text", "text": text})
    return prompt


def append_image_to_system_prompt(prompt, encoded_image):
    """
    Appends an image to the system prompt.
    Args:
        prompt (list): The existing system prompt.
        encoded_image (str): The base64 encoded image.
    Returns:
        list: The updated system prompt with the appended image.
    """
    if not prompt:
        prompt = []
    
    prompt.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}", "detail": "low"}})
    return prompt


def read_file(file_path):
    """
    Reads the contents of a file and returns it as a string.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The contents of the file as a string.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    return content


def get_encoded_image(image_path):
    """
    Encodes an image file to base64.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded image.
    """
    return base64.b64encode(open(image_path, 'rb').read()).decode('ascii')