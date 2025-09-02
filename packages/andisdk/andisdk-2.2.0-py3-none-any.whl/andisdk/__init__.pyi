from ._andi_docs import *
from ._andi_docs import Andi

class AndiApi(dict):
    @property
    def message_builder(self) -> MessageBuilder:
        """message builder object."""
        pass

    @property
    def andi(self) -> Andi:
        """andi object."""
        pass

    @property
    def channels(self) -> dict[str, IChannelAdapter]:
        """project channels"""
        pass

    @property
    def databases(self) -> dict[str, Database]:
        """project databases"""
        pass

    @property
    def messages(self) -> dict[str, Message]:
        """project messages"""
        pass

    @property
    def ecus(self) -> dict[str, Node]:
        """project ecus"""
        pass

# give user ability to load project
message_builder = MessageBuilder()
series_builder = SeriesBuilder()
andi = Andi()
def load_project(atp: str) -> AndiApi:
    """
    Method to load an atp project and create a scope object that contains the message builder and the andi object.
    params:
        **atp: str, path to andi project file**
    returns:
        returns AndiApi object with message builder, andi object, and the project channels.
    """
    pass

def enable_rich_logging():
    """Enable rich-based logging."""
    pass

def disable_rich_logging():
    """Disable rich-based logging"""
    pass
    
