import os
plugin_path = os.path.join(os.path.dirname(__file__), ".")
os.environ["QT_PLUGIN_PATH"] = plugin_path

from .pyvcadviz import *