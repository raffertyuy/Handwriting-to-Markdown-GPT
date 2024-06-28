from openai import AzureOpenAI

def execute_image_completion(client, encoded_image, system_prompt):
    """
    Executes a GPT-4o chat completion based on the system prompt and encoded image.

    Args:
        client (object): The Azure OpenAI client object.
        encoded_image (str): The base64 encoded image.
        system_prompt (str, optional): The system prompt. Defaults to None.

    Returns:
        str: The generated response from the chat completion.
    """

    if client is None:
        raise ValueError("client parameter is required.")
    if encoded_image is None:
        raise ValueError("encoded_image parameter is required.")
    if system_prompt is None:
        raise ValueError("system_prompt parameter is required.")

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]
        }
    ]

    response = client.chat.completions.create(
        model="gpt4o",
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content


def execute_text_completion(client, text, system_prompt):
    """
    Executes a GPT-4o chat completion based on the system prompt and text input.

    Args:
        client (object): The Azure OpenAI client object.
        text (str): The user text input.
        system_prompt (str, optional): The system prompt. Defaults to None.

    Returns:
        str: The generated response from the chat completion.
    """

    if client is None:
        raise ValueError("client parameter is required.")
    if text is None:
        raise ValueError("text parameter is required.")
    if system_prompt is None:
        raise ValueError("system_prompt parameter is required.")

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": text
        }
    ]

    response = client.chat.completions.create(
        model="gpt4o",
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content


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


def save_string_to_file(string, file_path):
    """
    Saves a string to a file.

    Args:
        string (str): The string to be saved.
        file_path (str): The path to the file.

    Returns:
        None
    """
    with open(file_path, 'w') as file:
        file.write(string)