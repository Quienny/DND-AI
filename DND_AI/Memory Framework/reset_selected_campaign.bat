@echo off
setlocal EnableDelayedExpansion
cls
echo ====================================================
echo   🧹 SELECT CAMPAIGN TO RESET
echo ====================================================

set BASEDIR=%~dp0
set CAMPAIGNDIR=%BASEDIR%campaigns

set i=0
for /d %%C in ("%CAMPAIGNDIR%\*") do (
    set /a i+=1
    set "campaign[!i!]=%%~nxC"
    echo !i!. %%~nxC
)

if "!i!"=="0" (
    echo ❌ No campaigns found.
    pause
    exit /b
)

set /p choice=Enter campaign number to reset: 
set "selected=!campaign[%choice%]!"

if not defined selected (
    echo ❌ Invalid selection.
    pause
    exit /b
)

echo ----------------------------------------------------
echo You selected: !selected!
set TARGET=%selected%
set CONFIRM=
set /p CONFIRM=Are you sure you want to reset !TARGET!? (Y/N): 
if /i not "!CONFIRM!"=="Y" (
    echo ❌ Cancelled.
    pause
    exit /b
)

REM === Delete per-campaign data ===
for %%F in (sessions session_tracker characters npcs items towns factions lorebooks) do (
    if exist "%BASEDIR%%%F\!TARGET!" (
        echo Deleting %%F\!TARGET!...
        rmdir /s /q "%BASEDIR%%%F\!TARGET!"
        mkdir "%BASEDIR%%%F\!TARGET!"
    )
)

REM Remove processed.txt in selected folder
if exist "%CAMPAIGNDIR%\!TARGET!\processed.txt" (
    del /q "%CAMPAIGNDIR%\!TARGET!\processed.txt"
)

REM Clear active campaign only if it matches
for /f "delims=" %%A in ('type "%BASEDIR%active_campaign.json" 2^>nul') do (
    echo %%A | findstr /i "\"name\": \"!TARGET!\"" >nul
    if !errorlevel! == 0 (
        del /q "%BASEDIR%active_campaign.json"
        echo Removed active_campaign.json (matched target)
    )
)

echo ====================================================
echo ✅ Campaign "!TARGET!" has been reset.
echo ====================================================
pause
