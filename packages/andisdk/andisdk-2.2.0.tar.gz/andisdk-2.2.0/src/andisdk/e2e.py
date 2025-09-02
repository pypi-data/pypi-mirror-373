# Copyright (c) 2022-2024 Technica Engineering GmbH. All rights reserved.

"""
andi.e2e
========

Helper module to handle E2E messages.
See documentation for more details :doc:`/Tutorials/e2e`.
"""
import sys
import typing

if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):

  import clr
  clr.AddReference('PrimaTestCaseLibrary')
  from PrimaTestCaseLibrary.Utils import E2EUtils as _E2EUtils

def get_actual_crc(message, e2e = None):
	"""
	Gets CRC value from a message based on e2e information.
    Args:
        message(:py:class:`IMessageBase`) : The concerned message.
        e2e(:py:class:`IE2EInformation`) : The e2e information.
    Returns:
        :py:class:`UInt64` actual CRC value if coherent message and e2e otherwise 'None'.
    Return Type:
        :py:class:`UInt64`
	"""
	return _E2EUtils.GetActualCrc(message, e2e)

def get_actual_alive(message, e2e = None):
	"""
	Deprecated, use :py:meth:`get_actual_counter` instead.
	"""
	return get_actual_counter(message, e2e)

def get_actual_counter(message, e2e = None):
	"""
	Gets counter value from a message based on e2e information.
    Args:
        message(:py:class:`IMessageBase`) : The concerned message.
        e2e(:py:class:`IE2EInformation`) : The e2e information.
    Returns:
        :py:class:`UInt64` actual alive value if coherent message and e2e otherwise 'None'.
    Return Type:
        :py:class:`UInt64`
	"""
	return _E2EUtils.GetActualCounter(message, e2e)

def get_expected_crc(message, e2e = None):
	"""
	Calculates CRC value based on a message and e2e information.
    Args:
        message(:py:class:`IMessageBase`) : The concerned message.
        e2e(:py:class:`IE2EInformation`) : The e2e information.
    Returns:
        :py:class:`UInt64` expected CRC value if coherent message and e2e otherwise 'None'.
    Return Type:
        :py:class:`UInt64`
	"""
	return _E2EUtils.GetExpectedCrc(message, e2e)

def get_next_counter(message, e2e = None):
	"""
	Calculates next counter value based on the previous message and e2e information.
    Args:
        message(:py:class:`IMessageBase`) : The previous message.
        e2e(:py:class:`IE2EInformation`) : The e2e information.
    Returns:
        :py:class:`UInt64` next alive value if coherent message and e2e otherwise 'None'.
    Return Type:
        :py:class:`UInt64`
	"""
	return _E2EUtils.GetNextCounter(message, e2e)

def update_crc(message, e2e = None):
	"""
	Updates the CRC in the message's payload.
    Args:
        message(:py:class:`IMessageBase`) : The concerned message.
        e2e(:py:class:`IE2EInformation`) : The e2e information.
    Returns:
        :py:class:`bool` if the CRC is updated or not.
    Return Type:
        :py:class:`bool`
	"""
	return _E2EUtils.UpdateCrc(message, e2e)

def increment_counter(message, e2e = None):
	"""
	Updates the counter in the message's payload.
    Args:
        message(:py:class:`IMessageBase`) : The concerned message.
        e2e(:py:class:`IE2EInformation`) : The e2e information.
    Returns:
        :py:class:`bool` if the counter is updated or not.
    Return Type:
        :py:class:`bool`
	"""
	return _E2EUtils.IncrementCounter(message, e2e)

def protect(message, e2e = None):
	"""
	Updates the CRC, Length and DataId in the message's payload.
    Args:
        message(:py:class:`IMessageBase`) : The concerned message.
        e2e(:py:class:`IE2EInformation`) : The e2e information.
    Returns:
        :py:class:`bool` if the fields are updated or not.
    Return Type:
        :py:class:`bool`
	"""
	return _E2EUtils.Protect(message, e2e)
