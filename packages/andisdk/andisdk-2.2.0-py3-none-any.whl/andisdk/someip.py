# Copyright (C) 2023-2024 Technica Engineering GmbH. All rights reserved.

"""
andi.someip
===========

Helper module to handle SOME/IP messages.
"""

import sys
import typing
from typing import Iterable, Callable

if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):
    import clr
    from System import Action
    clr.AddReference('PrimaTestCaseLibrary')
    from functools import update_wrapper    
    from .modules import MessageSomeIP
    from PrimaTestCaseLibrary.RestBusSimulation.RestBusSimulationSOMEIP import (
        SomeIpTpSegmenter,
        SomeIpTpAssembler,
    )
    clr.AddReference('PrimaITestCaseLibrary')
    from PrimaITestCaseLibrary.MessageManagment import IMessageSomeIP


def segmentize(someip: "MessageSomeIP", max_segment_length: int) -> Iterable["MessageSomeIP"]:
    """Segmentize the given SOME/IP message into a list of
    TP segment messages.
    If the payload length <= the given max segment length
    the original message is returned as a one-element list.
    
    args:
        someip(:py:class:`MessageSomeIP`) : the original message
        max_segment_length(int): a segment's maximum payload length
    returns:
        segmented messages as a list
    """
    return SomeIpTpSegmenter.Segmentize(someip, max_segment_length)


SomeIPCallback = Callable[["MessageSomeIP"], None]


def reassemble(timeout: float = 1, forward_discarded: bool = True) -> Callable[["SomeIPCallback"], "SomeIPCallback"]:

    """
    This is a Python decorator factory you can add to on_message_received callbacks
    It changes the callback so that it receives reassembled SOME/IP-TP messages

    See https://docs.python.org/3/glossary.html#term-decorator for more information about Python decorators.
    
    args:
        timeout (float): Maximum time, after which incomplete TP transmissions are discarded
        forward_discarded (bool): Should discarded TP messages be forwarded to the callback or not
    returns:
        a Python decorator
    """
    def decorator(func):
        assembler = SomeIpTpAssembler(timeout, forward_discarded, Action[IMessageSomeIP](func))

        def wrapper(msg):
            assembler.OnReceive(msg)
        return update_wrapper(wrapper, func)
    return decorator
