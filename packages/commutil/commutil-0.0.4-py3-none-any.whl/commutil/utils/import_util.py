# import os
# import importlib
# import pkgutil
#
# __path__ = [os.path.dirname(__file__)]
#
# for _, module_name, is_pkg in pkgutil.iter_modules(__path__):
#     module = importlib.import_module(f"{__name__}.{module_name}")
#     for attr_name in dir(module):
#         if not attr_name.startswith('_'):
#             globals()[attr_name] = getattr(module, attr_name)
#     globals()[module_name] = module