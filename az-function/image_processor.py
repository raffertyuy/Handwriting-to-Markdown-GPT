import logging
import json

def execute_image_completion(client, encoded_image, system_prompt, deployment_name="gpt-4o", temperature=0):
    """
    Executes a GPT-4o chat completion based on the system prompt and encoded image.

    Args:
        client (object): The Azure OpenAI client object.
        encoded_image (str): The base64 encoded image.
        system_prompt (str, optional): The system prompt. Defaults to None.
        deployment_name (str): The deployment name of the vision model.
        temperature (float, optional): The temperature of the completion. Defaults to 0.

    Returns:
        str: The generated response from the chat completion.
    """

    if client is None:
        logging.info("client parameter is required.")
        raise ValueError("client parameter is required.")
    if encoded_image is None:
        logging.info("encoded_image parameter is required.")
        raise ValueError("encoded_image parameter is required.")
    if system_prompt is None:
        logging.info("system_prompt parameter is required.")
        raise ValueError("system_prompt parameter is required.")
    
    if isinstance(system_prompt, list) or isinstance(system_prompt, dict):
        messages = [
            {
                "role": "system",
                "content": json.dumps(system_prompt)
            }
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": json.dumps(system_prompt)
            }
        ]
    
    messages.append(
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
    )

    logging.info("Executing image completion...")
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        temperature=temperature
    )

    return response.choices[0].message.content


def execute_text_completion(client, text, system_prompt, deployment_name="gpt-4o", temperature=0.3):
    """
    Executes a GPT-4o chat completion based on the system prompt and text input.

    Args:
        client (object): The Azure OpenAI client object.
        text (str): The user text input.
        system_prompt (str, optional): The system prompt. Defaults to None.
        deployment_name (str): The deployment name of the chat completion model.
        temperature (float, optional): The temperature of the completion. Defaults to 0.3.

    Returns:
        str: The generated response from the chat completion.
    """

    if client is None:
        logging.info("client parameter is required.")
        raise ValueError("client parameter is required.")
    if text is None:
        logging.info("text parameter is required.")
        raise ValueError("text parameter is required.")
    if system_prompt is None:
        logging.info("system_prompt parameter is required.")
        raise ValueError("system_prompt parameter is required.")
    
    if isinstance(system_prompt, list) or isinstance(system_prompt, dict):
        messages = [
            {
                "role": "system",
                "content": json.dumps(system_prompt)
            }
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": json.dumps(system_prompt)
            }
        ]
    
    messages.append(
        {
            "role": "user",
            "content": text
        }
    )

    logging.info("Executing text completion...")
    response = client.chat.completions.create(
        model="gpt4o",
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content