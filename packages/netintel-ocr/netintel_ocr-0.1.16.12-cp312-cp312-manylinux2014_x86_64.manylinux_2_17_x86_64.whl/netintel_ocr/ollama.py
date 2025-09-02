import base64
import os
import requests

from .constants import TRANSCRIPTION_PROMPT, OLLAMA_BASE_URL


def get_ollama_base_url() -> str:
    """Get the Ollama base URL from environment or default."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    return f"{host}/api"


def check_for_server() -> bool:
    """
    Check if the Ollama server is running.
    """
    try:
        base_url = get_ollama_base_url()
        response = requests.get(f"{base_url}/tags")
        return True
    except requests.exceptions.RequestException:
        return False


def get_correct_model_name(model: str) -> str:
    """
    Get the correctly-cased model name from the server.
    
    Args:
        model (str): The model name to check (case-insensitive).
        
    Returns:
        str: The correctly-cased model name, or the original if not found.
    """
    try:
        # Get the base URL dynamically
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        # Try the v1/models endpoint first
        response = requests.get(f"{host}/v1/models")
        if response.status_code == 200:
            models_data = response.json().get('data', [])
            model_lower = model.lower()
            for m in models_data:
                model_id = m.get('id', '')
                if model_id.lower() == model_lower:
                    return model_id
                # Check without tag
                if ':' not in model and model_id.lower().startswith(model_lower + ':'):
                    return model_id
            
        # Fallback to api/tags endpoint
        base_url = get_ollama_base_url()
        response = requests.get(f"{base_url}/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_lower = model.lower()
            for m in models:
                model_name = m.get('name', '')
                if model_name.lower() == model_lower:
                    return model_name
                # Check without tag
                if ':' not in model and model_name.lower().startswith(model_lower + ':'):
                    return model_name
    except requests.exceptions.RequestException:
        pass
    
    return model  # Return original if not found


def check_model_availability(model: str) -> bool:
    """
    Check if a specific model is available in Ollama.
    
    Args:
        model (str): The model name to check.
        
    Returns:
        bool: True if model is available, False otherwise.
    """
    try:
        # Try the v1/models endpoint first (OpenAI compatible)
        response = requests.get(f"{OLLAMA_BASE_URL}/v1/models")
        if response.status_code == 200:
            models_data = response.json().get('data', [])
            # Case-insensitive check for model name
            model_lower = model.lower()
            for m in models_data:
                model_id = m.get('id', '').lower()
                if model_id == model_lower:
                    return True
                # Also check without tag if model doesn't have one
                if ':' not in model and model_id.startswith(model_lower + ':'):
                    return True
            
        # Fallback to api/tags endpoint
        base_url = get_ollama_base_url()
        response = requests.get(f"{base_url}/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            # Case-insensitive check
            model_lower = model.lower()
            for m in models:
                model_name = m.get('name', '').lower()
                if model_name == model_lower:
                    return True
                # Also check without tag
                if ':' not in model and model_name.startswith(model_lower + ':'):
                    return True
        return False
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

    # Use custom prompt if provided, otherwise use unified extraction prompt for text and tables
    if prompt is None:
        from .constants import UNIFIED_EXTRACTION_PROMPT
        prompt = UNIFIED_EXTRACTION_PROMPT

    # Prepare the request payload
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "images": [image_data],
    }

    # Make the API call
    base_url = get_ollama_base_url()
    response = requests.post(f"{base_url}/generate", json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(
            f"API call failed with status code {response.status_code}: {response.text}"
        )
