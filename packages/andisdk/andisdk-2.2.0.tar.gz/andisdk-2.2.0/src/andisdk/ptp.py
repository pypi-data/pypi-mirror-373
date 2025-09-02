# Copyright (c) 2020-2024 Technica Engineering GmbH. All rights reserved.

"""
andi.ptp
========
Helper module for synchronizing ECUs clocks with PC clock
"""
import sys
import typing
    
if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):              
    import clr
    clr.AddReference('PrimaTestCaseLibrary')
    from PrimaTestCaseLibrary.Utils import PTP
    from PrimaITestCaseLibrary.MessageManagment import PtpMessageTypes

__all__ = ['sync', 'cm_set_timestamp', 'send_pdelay_request', 'send_pdelay_response', 'send_pdelay_response_followup']

def sync(channel, timestamp = None, sequence_id = 0):
    """
    Args:
        channel (:py:class:`ChannelEthernet`): The channel to send PTP messages on.
        timestamp (:py:class:`float`): Timestamp to send in the PTP messages. Defaults to current time.
        sequence_id (:py:class:`int`): Sequence ID to send in the PTP messages. Defaults 0.
    """
    if timestamp is not None:
        timestamp = float(timestamp)
    return PTP.Sync(channel.NetworkHardwareDevice, timestamp, sequence_id)

def cm_set_timestamp(channel, timestamp = None):
    """
    Args:
        channel (:py:class:`ChannelEthernet`): The channel to send UDP message on.
        timestamp (:py:class:`float`): Timestamp to send in the UDP message. Defaults to current time.
    """
    if timestamp is not None:
        timestamp = float(timestamp)
    return PTP.CmSetTimestamp(channel.NetworkHardwareDevice, timestamp)

def send_pdelay_request(channel, sequence_id, timestamp):
    """
    Args:
        channel (:py:class:`ChannelEthernet`): The channel to send peer delay request message on.
        sequence_id (:py:class:`int`): Sequence ID of the peer delay request message.
        timestamp (:py:class:`float`): Timestamp to send in the peer delay request message.
    Returns:
        timestamp (:py:class:`float`): Timestamp when the peer delay request message was sent.
    """
    return PTP.SendPtpMessage(channel.NetworkHardwareDevice, PtpMessageTypes.PDelayReq, False, timestamp, sequence_id)

def send_pdelay_response(channel, request):
    """
    Args:
        channel (:py:class:`ChannelEthernet`): The channel to send peer delay response message on.
        request (:py:class:`int`): PTP message requesting of the peer delay response message.
    Returns:
        timestamp (:py:class:`float`): Timestamp when the peer delay response message was sent.
    """
    return PTP.SendPtpMessage(channel.NetworkHardwareDevice, PtpMessageTypes.PDelayResp, True, request.timestamp, request.sequence_id, request)

def send_pdelay_response_followup(channel, request, timestamp):
    """
    Args:
        channel (:py:class:`ChannelEthernet`): The channel to send peer delay response follow-up message on.
        request (:py:class:`int`): PTP message requesting of the peer delay response message.
        timestamp (:py:class:`float`): Timestamp when the peer delay response was sent.
    Returns:
        timestamp (:py:class:`float`): Timestamp when the peer delay response follow-up message was sent.
    """
    return PTP.SendPtpMessage(channel.NetworkHardwareDevice, PtpMessageTypes.PDelayRespFollowUp, False, timestamp, request.sequence_id, request)
