@echo off
REM Launch the Project Folder Creator GUI
REM Double-click this file or run from a terminal.

set "PIPELINE_ROOT=%~dp0..\.."
set "PYTHONPATH=%PIPELINE_ROOT%;%PYTHONPATH%"
python -m proj_folders.gui
pause
