@echo off
setlocal enabledelayedexpansion

:: Set current directory
cd /d %~dp0

:: Set the URL and file name
set "MODEL_URL=https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/openhermes-2.5-mistral-7b.Q5_K_M.gguf"
set "FILE_NAME=openhermes-2.5-mistral-7b.Q5_K_M.gguf"
set "FOLDER_PATH=model"

:: Create the directory if it doesn't exist
if not exist "%FOLDER_PATH%" (
    mkdir "%FOLDER_PATH%"
    echo Created directory: %FOLDER_PATH%
)

:: Change to the target directory
cd "%FOLDER_PATH%"

:: Check if the file already exists
if exist "%FILE_NAME%" (
    echo %FILE_NAME% already exists in %FOLDER_PATH%.
    echo Skipping download.
) else (
    echo Attempting to download %FILE_NAME%...

    :: Try PowerShell first
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object Net.WebClient).DownloadFile('%MODEL_URL%', '%FILE_NAME%')" 2>nul
    if exist "%FILE_NAME%" (
        echo Download completed successfully using PowerShell.
        goto :DownloadComplete
    )

    :: Try curl if PowerShell failed
    curl -L -o "%FILE_NAME%" "%MODEL_URL%" 2>nul
    if exist "%FILE_NAME%" (
        echo Download completed successfully using curl.
        goto :DownloadComplete
    )

    :: Try bitsadmin if curl failed
    bitsadmin /transfer mydownloadjob /download /priority normal "%MODEL_URL%" "%CD%\%FILE_NAME%" >nul
    if exist "%FILE_NAME%" (
        echo Download completed successfully using bitsadmin.
        goto :DownloadComplete
    )

    :: Try certutil as a last resort
    certutil -urlcache -split -f "%MODEL_URL%" "%FILE_NAME%" >nul
    if exist "%FILE_NAME%" (
        echo Download completed successfully using certutil.
        goto :DownloadComplete
    )

    echo Failed to download the file using all available methods.
    goto :DownloadFailed
)

:DownloadComplete
:: Return to the original directory
cd ..\..
echo Script execution completed successfully.
goto :END

:DownloadFailed
:: Return to the original directory
cd ..\..
echo Script execution failed.

:END
pause