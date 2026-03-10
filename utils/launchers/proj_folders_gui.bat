@echo off
REM Launch the Pipeline Manager GUI (CustomTkinter)
REM Double-click this file or run from a terminal.

set "PIPELINE_ROOT=%~dp0..\.."
set "PYTHONPATH=%PIPELINE_ROOT%\utils\tools;%PIPELINE_ROOT%\utils\dev;%PIPELINE_ROOT%;%PYTHONPATH%"
python -m proj_folders.gui_ctk
pause
