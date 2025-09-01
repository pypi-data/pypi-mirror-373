from aiko_services.main.utilities import importer

__all__ = ["patch_capability"]


def patch_capability(module_import_str, patch_attr, patch):
    module = importer.load_module(module_import_str)
    setattr(module, patch_attr, patch)
