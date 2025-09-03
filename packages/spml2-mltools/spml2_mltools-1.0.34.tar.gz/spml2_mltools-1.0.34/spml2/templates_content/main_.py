main_content = """\n
from spml2 import Process, Process_cache
from options_user import options
from models_user import models

# Initialize and run the main processing
Process(options, models)

# Reuse results saved while processing and create plots 
# (Uncomment this and comment previous if already have run Process above)
# Process_cache(options, models)
"""
