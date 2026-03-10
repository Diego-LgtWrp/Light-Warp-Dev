# Launch the Pipeline Manager GUI (CustomTkinter)
$PipelineRoot = (Resolve-Path (Join-Path (Join-Path $PSScriptRoot "..") "..")).Path
$env:PYTHONPATH = "$PipelineRoot\utils\tools;$PipelineRoot\utils\dev;$PipelineRoot;$env:PYTHONPATH"
python -m proj_folders.gui_ctk
