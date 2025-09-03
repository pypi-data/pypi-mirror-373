import os

from lumipy.lumiflex._atlas.atlas import get_atlas
from lumipy.client import get_client
from lumipy.lumiflex.window import window
from lumipy.lumiflex.utility_functions import concat, from_pandas
from lumipy.lumiflex._column.case import when
from lumipy.lumiflex._column.accessors.json_fn_accessor import json
from lumipy.client import LumiError
from lumipy._config_manager import config

if os.name == 'nt':
    os.system('color')
