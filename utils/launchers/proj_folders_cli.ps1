# Launch the Project Folder Creator CLI
# Pass arguments after the script, e.g.:
#   .\proj_folders_cli.ps1 project MyFilm
#   .\proj_folders_cli.ps1 asset MyFilm char_hero --blend
$PipelineRoot = (Resolve-Path (Join-Path $PSScriptRoot ".." "..")).Path
$env:PYTHONPATH = "$PipelineRoot;$env:PYTHONPATH"
python -m proj_folders.cli @args
