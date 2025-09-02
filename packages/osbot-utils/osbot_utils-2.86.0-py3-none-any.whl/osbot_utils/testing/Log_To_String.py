import logging
from io import StringIO

class Log_To_String():

    def __init__(self,logger):
        self.logger         = logger
        self.string_stream  = None
        self.string_handler = None

    def __enter__(self):
        self.add_handler()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.remove_handler()

    def add_handler(self):
        self.string_stream = StringIO()
        self.string_handler = logging.StreamHandler(self.string_stream)
        self.logger.addHandler(self.string_handler)

    def contents(self):
        return self.string_stream.getvalue()

    def set_level(self, level):
        self.logger.setLevel(level)
        return self

    def set_level_critical(self): return self.set_level('CRITICAL') # level 50
    def set_level_debug   (self): return self.set_level('DEBUG'   ) # level 10
    def set_level_error   (self): return self.set_level('ERROR'   ) # level 40
    def set_level_info    (self): return self.set_level('INFO'    ) # level 20
    def set_level_warning (self): return self.set_level('WARNING' ) # level 30

    def remove_handler(self):
        self.logger.removeHandler(self.string_handler)