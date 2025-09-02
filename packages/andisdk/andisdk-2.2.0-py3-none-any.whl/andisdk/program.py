import atexit
import os
import sys
# set the python executable environment variable since some scripts might need it
os.environ["PYTHON_EXECUTABLE"] = sys.executable
current_dir = os.path.dirname(os.path.abspath(__file__))
# we need to set the runtime of pythonnet to use netcoreapp instead of netframework
from clr_loader import get_coreclr
from pythonnet import set_runtime, unload
# we get the core runtime configuration from the runtimeconfig file
rt = get_coreclr(runtime_config=os.path.join(current_dir, 'runtimeconfig.json'))

# we set the pythonnet runtime to use the core runtime we loaded from the config file
set_runtime(rt)

import clr

# add dll path to system path for clr to work 
dlls = os.path.join(current_dir, 'dlls')
sys.path.append(dlls)
clr.AddReference('PrimaTestCaseLibrary')

from PrimaTestCaseLibrary.BusinessTestCaseLibrary import MessageBuilderImpl, TestProjectImpl, ScriptSessionImpl
from PrimaTestCaseLibrary.Common import PythonOutputViewer
from PrimaTestCaseLibrary.Utils import Andi
from PrimaTestCaseLibrary.Utils.Series import SeriesBuilder
import logging
default_handlers = logging.root.handlers
logging.basicConfig(level=logging.NOTSET, format="%(message)s", datefmt="[%X]", handlers=default_handlers)
default_logger = logging.getLogger("andi.default")

# Workaround until https://github.com/pythonnet/pythonnet/issues/1977 gets fixed
atexit.unregister(unload)

import platform
import stat
if platform.system().lower() == "linux":
    linux_executables = ["blf_converter"]
    for exe in linux_executables:
        exe_file_path = os.path.join(dlls, exe)
        if not os.access(exe_file_path, os.X_OK):
            try:
                st = os.stat(exe_file_path)
                os.chmod(exe_file_path, st.st_mode | stat.S_IEXEC)
            except:
                default_logger.warning(f"{exe_file_path} is not marked as executable, this might cause the related feautre to not function properly.")

class AndiApi(dict):
    def __init__(self, *args, **kwargs):
        super(AndiApi, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @property
    def message_builder(self):
        """message builder object."""
        return self['message_builder']

    @property
    def andi(self):
        """andi object."""
        return self['andi']

    @property
    def channels(self):
        """project channels"""
        return self['channels']
    
    @property
    def databases(self):
        """project databases"""
        return self['databases']
    
    @property
    def messages(self):
        """project messages"""
        return self['messages']

    @property
    def ecus(self):
        """project ecus"""
        return self['ecus']

# give user ability to load project
__project = None
# if project creation throws an exception, it means that andisdk is not licensed.
from System import InvalidProgramException, TypeInitializationException
try:
    __project = TestProjectImpl()
except TypeInitializationException as ex:
    if type(ex.InnerException) is InvalidProgramException:
        default_logger.error("No valid license found, contact support@technica-engineering.de for license related inquiries.")
        sys.exit(66)
    else:
        raise ex
__project.SetOutputViewer("python", PythonOutputViewer(default_logger))
message_builder = MessageBuilderImpl(__project)
series_builder = SeriesBuilder()
session_logger = logging.getLogger("andi.session")
ScriptSessionImpl.getInstance().IOutputViewer = PythonOutputViewer(session_logger)
andi = Andi(__project)
def load_project(atp) -> AndiApi:
    project = TestProjectImpl.Deserialize(atp)
    project_logger = logging.getLogger("andi." + project.name)
    project.SetOutputViewer("python", PythonOutputViewer(project_logger))
    scope = AndiApi()
    scope['__project'] = project
    scope['andi'] = Andi(project)
    scope['message_builder'] = MessageBuilderImpl(project)
    scope['channels'] = {}
    scope['databases'] = {}
    scope['messages'] = {}
    scope['ecus'] = {}
    if project.Adapters:
        for channel in project.Adapters.Adapters:
            scope['channels'][channel.name] = channel.__implementation__
            scope[channel.name] = channel.__implementation__
    if project.DataBases:
        for db in project.DataBases.DataBases:
            scope['databases'][db.name] = db.__implementation__
            scope[db.name] = db.__implementation__
    if project.Messages:
        for msg in project.Messages.Messages:
            scope['messages'][msg.name] = msg.__implementation__
            scope[msg.name] = msg.__implementation__
    if project.Ecus:
        for ecu in project.Ecus.nodes:
            scope['ecus'][ecu.name] = ecu.__implementation__
            scope[ecu.name] = ecu.__implementation__
    return scope

rich_handler = None
def enable_rich_logging():
    """Setup rich-based logging."""
    global rich_handler
    import rich.logging
    rich_handler = rich.logging.RichHandler()
    logger = logging.getLogger('andi')
    logger.addHandler(rich_handler)
   

def disable_rich_logging():
    """Disable rich-based logging"""
    global rich_handler
    logger = logging.getLogger('andi')
    logger.removeHandler(rich_handler)
    
