@echo off
cd /d "%~dp0"
python pubg_audio_gui.py
if errorlevel 1 pause
