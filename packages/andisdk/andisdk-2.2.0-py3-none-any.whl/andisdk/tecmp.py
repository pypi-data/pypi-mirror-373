# Copyright (c) 2021-2024 Technica Engineering GmbH. All rights reserved.

"""
andi.tecmp
============

Helper module for extract TECMP status messages from ethernet messages and return the parsed status.
See documentation for more details :doc:`/Tutorials/TECMP`.	
"""
import sys
import typing
    
if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):
  import clr
  clr.AddReference('PrimaTestCaseLibrary')
  from PrimaTestCaseLibrary.Utils import TecmpUtils as _TecmpUtils   

def get_cm_status(message):
	"""
	Get capture module status from an ethernet message.
    Args:
        message(:py:class:`MessageEthernet`) : The received ethernet message.
    Returns:
        :py:class:`CmStatus` object if message is a valid tecmp capture module status message otherwise 'none'.
    Return Type:
        :py:class:`CmStatus`
	"""
	return _TecmpUtils.TecmpStatusDecoder.GetCmStatus(message)
def get_bus_status(message):
	"""
	Get bus status from an ethernet message.
    Args:
        message(:py:class:`MessageEthernet`) : The received ethernet message.
    Returns:
        :py:class:`BusStatus` object if message is a valid tecmp bus status message otherwise 'none'.
    Return Type:
        :py:class:`BusStatus`
	"""
	return _TecmpUtils.TecmpStatusDecoder.GetBusStatus(message)
def get_control_data(message):
	"""
	Get control message event from an ethernet message.
    Args:
        message(:py:class:`MessageEthernet`) : The received ethernet message.
	Returns:
        :py:class:`ControlMessageData` object if message is a valid tecmp control message otherwise 'none'.
    Return Type:
        :py:class:`ControlMessageData`
	"""
	return _TecmpUtils.TecmpControlDecoder.GetControlMessageData(message)

__all__ = ['get_cm_status', 'get_bus_status', 'get_control_data']