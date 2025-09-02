import uuid
import sys
import importlib.util


def import_by_path(path):
    module_name = f'abc_{uuid.uuid4().hex}'
    spec = importlib.util.spec_from_file_location(module_name, path)
    package_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = package_module
    spec.loader.exec_module(package_module)
    return package_module
