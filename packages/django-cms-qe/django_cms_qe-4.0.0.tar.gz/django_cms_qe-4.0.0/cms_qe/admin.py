from .export import get_supported_export_types, register_export_action

for ext, item in get_supported_export_types().items():
    register_export_action(ext, item.label)
