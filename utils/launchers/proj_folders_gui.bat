@echo off
REM Launch the Project Folder Creator GUI
REM Double-click this file or run from a terminal.

set "PIPELINE_ROOT=%~dp0..\.."
set "PYTHONPATH=%PIPELINE_ROOT%;%PYTHONPATH%"
python -m utils.dev.proj_folders.gui
pause
