# Launch the Project Folder Creator GUI
$PipelineRoot = (Resolve-Path (Join-Path $PSScriptRoot ".." "..")).Path
$env:PYTHONPATH = "$PipelineRoot;$env:PYTHONPATH"
python -m proj_folders.gui
