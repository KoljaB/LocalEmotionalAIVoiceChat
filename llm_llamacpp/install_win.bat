@echo off
set PYTHON_PATH=D:\Programme\miniconda3\envs\textgen\python.exe

:: Set current directory
cd /d %~dp0
cd ..

echo Starting installation process...

:: Create and activate virtual environment
echo Creating and activating virtual environment...
%PYTHON_PATH% -m venv venv
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install llama-cpp-python webserver python library
echo Installing llama-cpp-python webserver python library...
set "CMAKE_ARGS=-DLLAMA_CUBLAS=on"
set FORCE_CMAKE=1
python -m pip install llama-cpp-python[server]==0.2.74 --force-reinstall --upgrade --no-cache-dir
python -m pip install numpy==1.23.5


echo Installation completed.
pause