# Launch the Project Folder Creator GUI
$PipelineRoot = (Resolve-Path (Join-Path $PSScriptRoot ".." "..")).Path
$env:PYTHONPATH = "$PipelineRoot;$env:PYTHONPATH"
python -m utils.dev.proj_folders.gui
