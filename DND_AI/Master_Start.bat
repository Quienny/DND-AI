@echo off
chcp 65001 >nul
color 0A
title "D&D AI Master Control"

:: === Define key paths ===
set "ROOT_DIR=%~dp0"
set "PYTHON_DIR=%ROOT_DIR%AI\DM_Character_Card"
set "FRAMEWORK_DIR=%ROOT_DIR%Memory Framework"
set "CAMPAIGN_DIR=%FRAMEWORK_DIR%\campaigns"
set "CHARACTER_DIR=%FRAMEWORK_DIR%\characters"
set "AUTO_SUMMARIZE=%PYTHON_DIR%\auto_summarize_parts.py"
set "TTS_SCRIPT=%ROOT_DIR%STT\TTS.py"
set "LOG_FILE=%ROOT_DIR%\Logs\launch_log.txt"

:: === Start new log ===
echo Launch started at %DATE% %TIME% > "%LOG_FILE%" 2>&1

echo.
echo ============================================
echo        "D&D AI MASTER START SCRIPT"
echo ============================================
echo.

:: === Campaign Selection ===
echo Available Campaigns:
setlocal enabledelayedexpansion
set i=0
for /d %%C in ("%CAMPAIGN_DIR%\*") do (
    set /a i+=1
    set "campaign[!i!]=%%~nxC"
    echo !i!. %%~nxC
)
echo.
set /p selection="Enter campaign number to activate: "
call set "chosen_campaign=%%campaign[%selection%]%%"

if not defined chosen_campaign (
    echo ? Invalid selection. >> "%LOG_FILE%" 2>&1
    echo Invalid campaign selection. Exiting...
    timeout /t 3
    exit /b
)

:: === Set Active Campaign using safe file input ===
python "%FRAMEWORK_DIR%\init_campaign_folders.py" "%chosen_campaign%" >> "%LOG_FILE%" 2>&1

:: === Prompt to open folders ===
set /p openCamp="Open campaign folder? (y/n): "
if /i "%openCamp%"=="y" start "" "%CAMPAIGN_DIR%\%chosen_campaign%"

set /p openChars="Open characters folder? (y/n): "
if /i "%openChars%"=="y" start "" "%CHARACTER_DIR%\%chosen_campaign%"

:: === Run memory engine ===
echo Launching auto_summarize_parts.py... >> "%LOG_FILE%" 2>&1
python "%AUTO_SUMMARIZE%" >> "%LOG_FILE%" 2>&1

:: === Launch Whisper STT (TTS.py) in background ===
start "" /min powershell -WindowStyle Hidden -Command "Start-Process python -ArgumentList '"%TTS_SCRIPT%"' -WindowStyle Hidden"

:: === Launch AI GPT Query Interface ===
cd /d "%PYTHON_DIR%"
python query_gpt.py
