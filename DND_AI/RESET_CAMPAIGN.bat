@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
color 0C
title Reset Campaign Memory Data

:: Setup
set "ROOT_DIR=%~dp0"
set "FRAMEWORK_DIR=%ROOT_DIR%Memory Framework"
set "LOG_DIR=%ROOT_DIR%Logs"
set "LOG_FILE=%LOG_DIR%\reset_campaign_datalog.txt"

:: Ensure log directory exists
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Memory paths
set "CHARACTERS_DIR=%FRAMEWORK_DIR%\characters"
set "SUMMARIES_DIR=%FRAMEWORK_DIR%\summaries"
set "NPCS_DIR=%FRAMEWORK_DIR%\npcs"
set "ITEMS_DIR=%FRAMEWORK_DIR%\items"
set "FACTIONS_DIR=%FRAMEWORK_DIR%\factions"
set "TOWNS_DIR=%FRAMEWORK_DIR%\towns"
set "LOREBOOKS_DIR=%FRAMEWORK_DIR%\lorebooks"
set "SESSION_TRACKER_DIR=%FRAMEWORK_DIR%\session_tracker"

:: Logging timestamp
echo. >> "%LOG_FILE%"
echo === Reset Script Run on %DATE% at %TIME% === >> "%LOG_FILE%"

echo.
echo ===============================
echo  "D&D AI CAMPAIGN RESET TOOL"
echo ===============================
echo.

:: Build campaign list
set i=0
for /d %%C in ("%CHARACTERS_DIR%\*") do (
    set /a i+=1
    set "campaign[!i!]=%%~nxC"
    echo !i!. %%~nxC
)

if %i%==0 (
    echo ? No campaigns found in: %CHARACTERS_DIR%
    echo No campaigns found. >> "%LOG_FILE%"
    pause
    exit /b
)

echo.
set /p selection="Enter the number of the campaign to reset: "
call set "chosen_campaign=%%campaign[%selection%]%%"

if not defined chosen_campaign (
    echo ? Invalid selection. Exiting...
    echo Invalid selection >> "%LOG_FILE%"
    pause
    exit /b
)

echo.
echo WARNING: You are about to permanently delete memory files for:
echo   !chosen_campaign!
echo.
set /p confirm="Are you absolutely sure? Type YES to continue: "

if /i "!confirm!" NEQ "YES" (
    echo ? Cancelled. No data was deleted.
    echo Cancelled by user. >> "%LOG_FILE%"
    pause
    exit /b
)

echo.
echo ?? Deleting memory data for campaign: !chosen_campaign!
echo.

:: Delete and log each target
(
    del /f /q "%CHARACTERS_DIR%\!chosen_campaign!\characters.json" && echo Deleted characters.json
    del /f /q "%SUMMARIES_DIR%\!chosen_campaign!\summaries.json" && echo Deleted summaries.json
    del /f /q "%NPCS_DIR%\!chosen_campaign!\npcs.json" && echo Deleted npcs.json
    del /f /q "%ITEMS_DIR%\!chosen_campaign!\items.json" && echo Deleted items.json
    del /f /q "%FACTIONS_DIR%\!chosen_campaign!\factions.json" && echo Deleted factions.json
    del /f /q "%TOWNS_DIR%\!chosen_campaign!\towns.json" && echo Deleted towns.json
    del /f /q "%LOREBOOKS_DIR%\!chosen_campaign!\lorebooks.json" && echo Deleted lorebooks.json
    del /f /q "%SESSION_TRACKER_DIR%\!chosen_campaign!\session_tracker.json" && echo Deleted session_tracker.json
    del /f /q "%SUMMARIES_DIR%\!chosen_campaign!\summary_part_*.json" && echo Deleted summary_part_*.json
    rd /s /q "%FRAMEWORK_DIR%\memory\!chosen_campaign!" && echo Deleted memory folder
) >> "%LOG_FILE%" 2>&1

echo ? Reset complete for !chosen_campaign!
echo Reset completed for !chosen_campaign! >> "%LOG_FILE%"
pause
exit /b
