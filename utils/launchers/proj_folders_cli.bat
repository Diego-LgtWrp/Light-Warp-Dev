@echo off
REM Launch the Project Folder Creator CLI
REM Pass arguments after this script, e.g.:
REM   proj_folders_cli.bat project MyFilm
REM   proj_folders_cli.bat asset MyFilm char_hero --blend

set "PIPELINE_ROOT=%~dp0..\.."
set "PYTHONPATH=%PIPELINE_ROOT%;%PYTHONPATH%"
python -m utils.dev.proj_folders.cli %*
