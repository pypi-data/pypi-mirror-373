import base64
import requests

from .constants import BASE_TRANSCRIPTION_PROMPT


def check_for_server(server_url: str) -> bool:
    """
    Check if the Ollama server is running.
    """

    try:
        response = requests.get(f"{server_url}/api/tags")
        return True
    except requests.exceptions.RequestException:
        return False


def transcribe_image(
    image_path: str, model: str, custom_instructions: str = None, server_url: str = None
) -> str:
    """
    Transcribe an image using the specified model.

    Args:
        image_path (str): Path to the image file.
        model (str): The model to use for transcription.
        custom_instructions (str, optional): Additional instructions to include in the prompt.
        server_url (str, optional): The URL of the Ollama server.
    """
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Prepare the prompt with context if provided
    prompt = BASE_TRANSCRIPTION_PROMPT
    if custom_instructions:
        prompt = prompt + f"\n\n{custom_instructions}"

    # Prepare the request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "images": [image_data],
    }

    # Make the API call
    response = requests.post(f"{server_url}/generate", json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(
            f"API call failed with status code {response.status_code}: {response.text}"
        )
