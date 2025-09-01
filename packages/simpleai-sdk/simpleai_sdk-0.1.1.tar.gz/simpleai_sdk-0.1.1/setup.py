import sys
from setuptools import setup, find_packages

def get_onnxruntime_dependency():
    """
    Determines the appropriate onnxruntime package to install based on
    the available hardware (CUDA or CPU) and CUDA version.
    """
    try:
        import torch
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda
            if cuda_version and cuda_version.startswith('11.'):
                print("=" * 80, file=sys.stderr)
                print("WARNING: CUDA 11.x detected.", file=sys.stderr)
                print("To enable GPU support, you must install onnxruntime-gpu manually after this installation finishes.", file=sys.stderr)
                print("Please run the following command:", file=sys.stderr)
                print("\npip install onnxruntime-gpu --index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-11/pypi/simple/\n", file=sys.stderr)
                print("Installing the CPU version of onnxruntime for now.", file=sys.stderr)
                print("=" * 80, file=sys.stderr)
                return ["onnxruntime"]
            else:
                print("CUDA 12.x or newer detected. Installing onnxruntime-gpu.")
                return ["onnxruntime-gpu"]
        else:
            print("No CUDA device found. Installing CPU version of onnxruntime.")
            return ["onnxruntime"]
    except ImportError:
        print("PyTorch not found. Defaulting to CPU version of onnxruntime.", file=sys.stderr)
        print("If you have a GPU, please install PyTorch with CUDA support first, then install this package.", file=sys.stderr)
        return ["onnxruntime"]
    
onnx_dependency = get_onnxruntime_dependency()

install_requires = [
    "torch",
    "transformers",
    "tiktoken",
    "huggingface-hub",
    "numpy",
    "dataclasses",
] + onnx_dependency

setup(
    packages=find_packages(),
    install_requires=install_requires,
)
