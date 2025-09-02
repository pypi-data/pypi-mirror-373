# todo: finish code below so that log entries are stored in the queue
#       expand to other capabilites of QueueHandler (namely using multiple handlers)
# import logging
# import queue
# from io import StringIO
# from logging.handlers import QueueListener, QueueHandler
#
#
# class Log_To_Queue():
#
#     def __init__(self,logger):
#         self.logger         = logger
#         self.queue          = None
#         self.queue_listener = None
#         self.queue_handler  = None
#
#     def __enter__(self):
#         self.add_handler()
#         return self
#
#     def __exit__(self, exception_type, exception_value, exception_traceback):
#         self.remove_handler()
#
#     def add_handler(self):
#         self.queue          = queue.Queue(-1)
#         self.queue_listener = QueueListener(self.queue)        # not using any handlers
#         self.queue_handler  = QueueHandler (self.queue)
#         self.logger.addHandler(self.queue_handler)
#         self.queue_listener.start()
#
#     def contents(self):
#         return "self.string_stream.getvalue()"
#
#     def set_level(self, level):
#         self.logger.setLevel(level)
#         return self
#
#     def set_level_critical(self): return self.set_level('CRITICAL') # level 50
#     def set_level_debug   (self): return self.set_level('DEBUG'   ) # level 10
#     def set_level_error   (self): return self.set_level('ERROR'   ) # level 40
#     def set_level_info    (self): return self.set_level('INFO'    ) # level 20
#     def set_level_warning (self): return self.set_level('WARNING' ) # level 30
#
#     def remove_handler(self):
#         self.queue_listener.stop()
#         self.logger.removeHandler(self.queue_handler)