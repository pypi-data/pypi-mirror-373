# Copyright (c) 2020-2024 Technica Engineering GmbH. All rights reserved.

"""
andi.autosar
============

Helper module for extract PDU messages from ethernet messages and transform it on receive message event of other ethernet messages to handle PDU messages.
See documentation for more details :doc:`/Tutorials/socket_adaptor`.
"""
import sys
import typing
    
if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):

    import clr
    clr.AddReference('PrimaTestCaseLibrary')
    from PrimaTestCaseLibrary.Utils.pdu import SocketAdaptor as _SA
    
    class SocketAdaptor(_SA):
        """
            Extract autosar PDUs from messages
        """
        def transform(self, handler):
            """
            Args:
                handler : Get the list of PDU messages from ethernet message.
            """
            def newHandler(msg):
                for pdu in self.get_pdus(msg):
                    handler(pdu)    
            return newHandler
    
else: 
    class SocketAdaptor:
        """
            Extract autosar PDUs from messages
        """
        def get_pdus(self, message):
            """
            Args:
                message : The ethernet message received from start capture method.
            Returns:
                List of pdu messages from the captured ethernet message.  
            Return Type:
                :py:class:`List`\[:py:class:`MessagePDU`]
            """
            pass
        def transform(self, handler):
            """
			Decorator function to transform ethernet messages to PDU messages.
            Args:
                handler : Get the list of PDU messages from ethernet message.
            """
            pass
    
        
__all__ = ['SocketAdaptor']


