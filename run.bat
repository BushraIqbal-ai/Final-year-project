@echo off
title NeuroScan AI — Parkinson's Dementia Detection
color 0B
cls
echo.
echo  ==================================================
echo    NeuroScan AI — Parkinson's Dementia Detection
echo  ==================================================
echo.
echo  Checking Python...
python --version
echo.
echo  Starting Flask application...
echo  URL: http://127.0.0.1:5000
echo.
echo  NOTE: If PyTorch is not installed, the site still
echo  runs — visit the Analyze page for install instructions.
echo.
cd /d "%~dp0"
python app.py
pause
