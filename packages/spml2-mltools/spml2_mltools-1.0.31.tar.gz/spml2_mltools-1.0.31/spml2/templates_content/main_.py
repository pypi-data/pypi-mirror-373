main_content = """\n
from spml2 import Process, Process_cache
from options_user import options
from models_user import models


Process(options, models)
Process_cache(options, models)


"""
