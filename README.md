# EmoTTS

Simulate conversations with an AI that can express emotions.

# Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/KoljaB/EmoTTS.git
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Upgrade PyTorch and Torchaudio:**
   ```
   pip install torch==2.2.2+cu118 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu118
   ```

4. **(Optional) Use a specific TTS model:**
   - Download the Lasinya XTTS voice model from [huggingface](https://huggingface.co/KoljaB/XTTS_Lasinya/tree/main).
   - Save the model files to a local directory.
   - Modify the `emotts.py` file to specify the model and its path:
     - Find the line starting with `engine = CoquiEngine(`.
     - Set `specific_model="Lasinya"` and `local_models_path` to the directory just above where you saved the model files (local_models_path should references the parent directory of your model files)
