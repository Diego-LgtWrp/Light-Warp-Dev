# Blender Integration

This package will contain Blender-specific pipeline integrations:

- Startup scripts (loaded via Blender's Python API)
- Custom operators for asset publishing, loading, and versioning
- Menu entries for pipeline actions
- Add-on registration

## Development

Blender uses its own bundled Python. To develop here, make sure
`pipeline/` is on Blender's `sys.path` (via startup script or
PYTHONPATH in launch config).
