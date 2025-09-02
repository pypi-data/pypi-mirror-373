# Copyright (c) 2021-2024 Technica Engineering GmbH. All rights reserved.

import sys
import threading
from pdb import Pdb
from io import TextIOWrapper

debugger = None
lock = threading.RLock()

class Debugger(Pdb):
    """
        Creates a debugger and overrides some functionalities of the base Pdb class.
    """
    def __init__(self, remote_debugger):
        """
            Creates a new Pdb debugger and redirects its output to the remote debugger.
        """
        super().__init__(stdout = TextIOWrapper(open(remote_debugger.CreateOutputStream())))
        self.remote_debugger = remote_debugger

    def interaction(self, frame, traceback):
        """
            Sniff out the base interaction method and redirect its calls to the remote debugger.
        """
        # When debugging a script, some encoding issues causes that the concerned file 
        # is not correctly recongnized.
        # When an exception is raised during debugging, calling interaction will cause a
        # NotImplementedException because co_lnotab is not implemented in FunctionCode.
        # For this reason we do not call interaction in these 2 cases.
        if frame and (frame.f_code.co_filename == "<string>" or (frame.f_locals.get('__exception__') and frame.f_locals['__exception__'])):
            return
        self.remote_debugger.interaction(self, frame)
        Pdb.interaction(self, frame, traceback)
        
        
    def message(self, msg):
        self.stdout.write(msg)

    def error(self, msg):
        self.stdout.write('***' + msg)
        
    def trace_dispatch(self, frame, event, arg):
        if self.quitting:
            return # None
            
        with lock:
            # When debugging a script, some encoding issues causes that the concerned file 
            # is not correctly recongnized. no call for trace_dispatch is needed in this case.
            if  frame and frame.f_code.co_filename == "<string>":
                return
            return Pdb.trace_dispatch(self, frame, event, arg)

def __init_debug__(remote_debugger):
    """
        Creates and initiates a new debugger.
    """
    global debugger
    debugger = Debugger(remote_debugger)

def set_trace():
    """
        This function will be entered whenver there is a call for breakpoint() function in the code.
    """
    global debugger
    new_debugger = Debugger(debugger.remote_debugger)
    new_debugger.breaks = debugger.breaks
    debugger = new_debugger
    debugger.set_trace(sys._getframe().f_back)
