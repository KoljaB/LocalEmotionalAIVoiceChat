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

:: Install openai python library
echo Installing openai python library...
python -m pip install openai


echo Installation completed.
pause