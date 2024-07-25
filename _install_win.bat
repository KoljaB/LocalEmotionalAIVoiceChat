@echo off

:: Set Python path (adjust this if needed)
set PYTHON_EXE=D:\Programme\miniconda3\envs\textgen\python.exe


echo Installing EmotionalLocalVoiceChat...
setlocal enabledelayedexpansion

:: Set current directory
cd /d %~dp0

echo Starting installation process...

:: Create and activate virtual environment
echo Creating and activating virtual environment...
%PYTHON_EXE% -m venv venv
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install other requirements
echo Installing other requirements...
python -m pip install -r requirements.txt

:: Detect CUDA version
echo Detecting CUDA version...
for /f "tokens=* USEBACKQ" %%F in (`nvcc --version ^| findstr /C:"release"`) do (
    set nvcc_output=%%F
)
echo NVCC Output: !nvcc_output!

if not "!nvcc_output!"=="" (
    echo !nvcc_output! | findstr /C:"11.8" >nul
    if !errorlevel! equ 0 (
        echo CUDA 11.8 detected. Installing PyTorch for CUDA 11.8...
        python -m pip install torch==2.3.1+cu118 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu118
    ) else (
        echo CUDA 12.x detected. Installing PyTorch for CUDA 12.1...
        python -m pip install torch==2.3.1+cu121 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121
    )
) else (
    echo CUDA not detected. Skipping PyTorch CUDA installation.
)

echo Installation completed.
pause