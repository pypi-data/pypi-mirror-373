from .hf_backend import LilleHuggingFace
from .onnx_backend import LilleONNX

def lille(backend: str = "huggingface", model_version: str = "130m-instruct"):
    """
    Loads the Lille-130m model with the specified backend and version.

    Args:
        backend (str): The backend to use, either "huggingface" or "onnx".
                       Defaults to "huggingface".
        model_version (str): The model version to load, e.g., "130m-instruct" or "130m-base".
                             Defaults to "130m-instruct".

    Returns:
        An instance of the Lille model wrapper for the chosen backend.
    """
    repo_id = f"Nikity/lille-{model_version}"
    print(f"Using repository: {repo_id}")
    
    if backend.lower() == "huggingface":
        print("Initializing Lille-130m with Hugging Face backend...")
        return LilleHuggingFace(repo_id=repo_id)
    elif backend.lower() == "onnx":
        print("Initializing Lille-130m with ONNX Runtime backend...")
        return LilleONNX(repo_id=repo_id)
    else:
        raise ValueError(f"Unsupported backend: '{backend}'. Please choose 'huggingface' or 'onnx'.")
