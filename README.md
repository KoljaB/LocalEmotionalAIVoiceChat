# Emotional AI Voice Chat 

A fast conversational System with emotional TTS output.

This project implements an AI-powered conversational system with real-time emotional text-to-speech (TTS) capabilities. It uses a large language model (LLM) for generating responses and a TTS engine with voice-cloning for voice output.

## Features

- Real-time speech-to-text input
- LLM-powered conversation generation
- Emotion-aware realtime text-to-speech output
- Configurable system and user personas

## Requirements

- Python <=3.10 (3.10.9 is recommended)
- CUDA-enabled GPU (for TTS and LLM processing)
- Various Python libraries (see `requirements.txt`)

## Installation

1. Clone the repository
2. Open _install_win.bat, chang the path behind PYTHON_EXE to the path to your Python 3.10.9 executable
3. Select your LLM provider:
  - open `main.py` and enter your desired LLM provider under llm_provider in class Config ("llamacpp" or "ollama" or "openai" or "anthropic")
  - llama.cpp:
    - start "install_win.bat" in the llm_llamacpp folder to install llama cpp webserver
    - also start "download_model.bat" in the llm_llamacpp folder to download the openhermes-2.5-mistral-7b.Q5_K_M.gguf model we use for inference
    - open start_llamacpp_server.bat in the llm_llamacpp folder, adjust especially --n_gpu_layers 25 to your environment and GPU capabilities
    - start "start_llamacpp_server.bat" in the main or the llm_llamacpp folder to start the server
  - ollama:
    - start "install_win.bat" in the llm_ollama folder to install ollama
    - start "start_ollama_server.bat" in the main or the llm_ollama folder to start the server
  - openai:
    - put your openai key in the environment variable "OPENAI_API_KEY"
  - anthropic:
    - put your anthropic key in the environment variable "ANTHROPIC_API_KEY" 
4. Download the specific Lasinya XTTS voice model from huggingface: start the download_tts_model.py which will download the needed files.
  Then open tts_config.json and enter the filepath to the model files there.

### CUDA Installation (for better performance)

These steps are recommended for those who require better performance and have a compatible NVIDIA GPU.

> **Note**: To check if your NVIDIA GPU supports CUDA, visit the [official CUDA GPUs list](https://developer.nvidia.com/cuda-gpus).

1. **Install NVIDIA CUDA Toolkit**:
   - Visit [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads) for the latest version, or [NVIDIA CUDA Toolkit Archive](https://developer.nvidia.com/cuda-11-8-0-download-archive) for version 11.8.
   - Select your operating system, system architecture, and OS version.
   - Download and install the software.

2. **Install NVIDIA cuDNN**:
   - Visit [NVIDIA cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive).
   - Download and install the appropriate version for your CUDA Toolkit.

3. **Install ffmpeg**:
   - Download from the [ffmpeg Website](https://ffmpeg.org/download.html), or use a package manager:
     ```bash
     # Ubuntu or Debian
     sudo apt update && sudo apt install ffmpeg

     # Arch Linux
     sudo pacman -S ffmpeg

     # MacOS (using Homebrew)
     brew install ffmpeg

     # Windows (using Chocolatey)
     choco install ffmpeg

     # Windows (using Scoop)
     scoop install ffmpeg
     ```

4. **Install PyTorch with CUDA support**:
   Choose the appropriate command based on your CUDA version:

   - For CUDA 11.8:
     ```bash
     pip install torch==2.3.1+cu118 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu118
     ```

   - For CUDA 12.X:
     ```bash
     pip install torch==2.3.1+cu121 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121
     ```

   Replace `2.3.1` with the version of PyTorch that matches your system and requirements.

## Usage

Run the main script:

```
python main.py
```

The system will start a conversation based on the configured scenario. Speak into your microphone to interact with the AI character.

**Note:** When starting the application, you may see warnings similar to:

```
[ctranslate2] [warning] The compute type inferred from the saved model is float16, but the target device or backend do not support efficient float16 computation. The model weights have been automatically converted to use the float32 compute type instead.

FutureWarning: `resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`.
```

These warnings are normal and do not affect the functionality of the system. There's no need to worry about them.


## Configuration

- Adjust `chat_params.json` to modify character and user descriptions, and conversation scenario
- Adjust `llm_xxx/completion_params.json` to modify LLM completion parameters
