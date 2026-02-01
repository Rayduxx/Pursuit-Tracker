@echo off
cd /d "%~dp0"
echo Starting Racing Timer...
pip install keyboard mouse >nul 2>&1
echo Note: If controls don't work inside FiveM, run this as Administrator.
python main.py
pause
