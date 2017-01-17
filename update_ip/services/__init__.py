import inspect
import os
import imp
import glob
from base import BaseDNSService


def find_classes():
    for service_file_path in glob.glob(os.path.join(os.path.dirname(__file__), '*.py')):
        module_name = os.path.splitext(os.path.basename(service_file_path))[0]

        # Skip special files and base class
        if module_name.startswith("__") or module_name == 'base':
            continue

        yield module_name, service_file_path


def find_services():
    for srvc, filename in find_classes():
        module = imp.load_source(srvc, filename)

        for item in dir(module):
            obj = getattr(module, item)
            if not obj or not inspect.isclass(obj):
                continue

            if not issubclass(obj, BaseDNSService):
                continue

            yield obj

services = {}

for srv in find_services():
    services[srv.name] = srv
del services[BaseDNSService.name]