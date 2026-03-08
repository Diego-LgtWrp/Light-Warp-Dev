@echo off
REM Launch the Secure Transfer GUI
set "PIPELINE_ROOT=%~dp0..\.."
set "PYTHONPATH=%PIPELINE_ROOT%;%PYTHONPATH%"
python -m secure_transfer.gui
pause
