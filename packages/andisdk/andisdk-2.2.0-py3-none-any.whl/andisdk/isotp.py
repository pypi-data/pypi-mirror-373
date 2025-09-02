# Copyright (c) 2021-2024 Technica Engineering GmbH. All rights reserved.

"""
andi.isotp
============

Helper module to handle ISO-TP Socket implementation.
See documentation for more details :doc:`/Tutorials/Iso_tp`.
"""
import sys
import typing
    
if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):

    import clr
    clr.AddReference('PrimaTestCaseLibrary')
    from PrimaTestCaseLibrary.Utils.IsoTp import IsoTpSocket as _IT
    
    class IsoTpSocket(_IT):
        def __init__(self, **kwargs):
            super().__init__()
            for (name, value) in list(kwargs.items()):
            
                if hasattr(self, name):
                    setattr(self, name, value)
                    
                elif hasattr(self.tx, name):
                    setattr(self.tx, name, value)
                    # Those are usually only needed for Tx
                    if name not in ('block_size', 'separation_time'):
                        setattr(self.rx, name, value)
                    
                elif name.startswith('tx_'):
                    setattr(self.tx, name[3:], value)
                    
                elif name.startswith('rx_'):
                    setattr(self.rx, name[3:], value)
                    
                else:
                    raise TypeError("__init__() got an unexpected keyword argument '{}'".format(name))
    
else:

    class IsoTpSocket:
        def __init__(self, **kwargs):
            """
                specifies an ISO-TP socket object
            """
            pass
            
        def send(data):
            """
            Sends the data to the configured destination using IsoTp standards.
            Args:
                data : The data bytes to be sent by the socket.
            """
            pass

        def create_messages(data):
            """
            Helper method to transform data input into list of messages to be sent.
            Args:
                data : The data to be segmented
            Returns:
                List of messages to be sent.
            Return Type:
                :py:class:`List`\[:py:class:`MessageBase`]
            """
            pass
    
__all__ = ['IsoTpSocket']
