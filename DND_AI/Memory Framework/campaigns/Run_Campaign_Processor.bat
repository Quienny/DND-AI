@echo off
cls
echo ====================================================
echo 🗂 Running Campaign Processor (No VENV)
echo ====================================================

cd /d "%~dp0"
python process_campaigns.py

echo ----------------------------------------------------
echo ✅ Finished.
pause
