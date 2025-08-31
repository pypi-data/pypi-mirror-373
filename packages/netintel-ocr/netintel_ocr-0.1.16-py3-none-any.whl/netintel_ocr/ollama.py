import base64
import requests

from .constants import OLLAMA_BASE_URL, TRANSCRIPTION_PROMPT


def check_for_server() -> bool:
    """
    Check if the Ollama server is running.
    """

    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        return True
    except requests.exceptions.RequestException:
        return False


def transcribe_image(image_path: str, model: str, prompt: str = None) -> str:
    """
    Transcribe an image using the specified model.

    Args:
        image_path (str): Path to the image file.
        model (str): The model to use for transcription.
        prompt (str, optional): Custom prompt to use. Defaults to TRANSCRIPTION_PROMPT.
    """
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Use custom prompt if provided, otherwise use default
    if prompt is None:
        prompt = TRANSCRIPTION_PROMPT

    # Prepare the request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "images": [image_data],
    }

    # Make the API call
    response = requests.post(f"{OLLAMA_BASE_URL}/generate", json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(
            f"API call failed with status code {response.status_code}: {response.text}"
        )
