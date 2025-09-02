# Copyright (c) 2021-2024 Technica Engineering GmbH. All rights reserved.

"""
andi.uds
============

Helper module to handle UDS messages.
See documentation for more details `UDS <https://udsoncan.readthedocs.io/en/latest>`_.
"""
import sys
import typing   
import queue

if not (typing.TYPE_CHECKING or ('sphinx' in sys.modules)):
    import clr
    clr.AddReference('PrimaITestCaseLibrary')
    from PrimaITestCaseLibrary import HSFZCtrlWordMapping
from udsoncan.connections import BaseConnection as _BaseConnection
from udsoncan.client import Client as _Client
from .exceptions import TimeoutException

class MessageConnection(_BaseConnection):

    def __init__(self, message):
        super().__init__(message.name)
        self.rxqueue = queue.Queue()
        self.opened = False
        self.message = message

    def open(self):
        self.message.on_message_received += self._on_message_received
        self.message.connect()
        self.opened = True
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def is_open(self):
        return self.opened

    def close(self):
        if not self.opened:
            return
        self.message.on_message_received -= self._on_message_received
        self.message.disconnect()
        self.opened = False

    def specific_wait_frame(self, timeout=2):
        if not self.opened:
            raise RuntimeError("Connection is not open")

        timedout = False
        frame = None
        try:
            frame = self.rxqueue.get(block=True, timeout=timeout)

        except queue.Empty:
            timedout = True

        if timedout:
            raise TimeoutException("Did not receive frame in time (timeout=%s sec)" % timeout)

        return frame

    def empty_rxqueue(self):
        while not self.rxqueue.empty():
            self.rxqueue.get()

class HsfzConnection(MessageConnection):
    """
    Sends and receives data through a HSFZ message.
    """
    def _on_message_received(self, msg):
        if msg.ctr_word == HSFZCtrlWordMapping.CTRLWORD_ACK:
            return
        if msg.diag:
            self.rxqueue.put(bytes(msg.diag.data))

    def specific_send(self, payload):
        self.message.ctr_word = HSFZCtrlWordMapping.CTRLWORD_REQUEST_RESPONSE
        self.message.diag.data = tuple(payload)
        self.message.send()

class DoIpConnection(MessageConnection):

    def __init__(self, message, protocol_version = 2, activation_response_timeout = 1000):
        super().__init__(message)
        self.protocol_version = protocol_version
        self.activation_response_timeout = activation_response_timeout

    """
    Sends and receives data through a DoIP message.
    """
    def open(self):
        super().open()
        self.__activate_routing()
        return self

    def __activate_routing(self):
        # after establishing connection, send a routing activation request
        message = self.message
        message.protocol_version = self.protocol_version
        message.payload_type = 0x0005
        old_payload = message.payload
        # 2 bytes source address, 1 byte activation type (0 for default), 4 bytes reserved (0x00000000)
        message.payload = tuple(message.payload)[0:2] +(0x00, 0x00, 0x00, 0x00, 0x00)
        response = message.send_receive(self.activation_response_timeout)
        message.payload = old_payload
        if not response :
            raise TimeoutException("Did not receive activation response in time")
        if not self.__activation_response_correct(response):
            raise ConnectionRefusedError("Did not receive a positive response to activation request")  

    def __activation_response_correct(self, response) -> bool:
        return response.payload[4] == 0x10
        
    def _on_message_received(self, msg):
        # if message is diag payload save it
        if msg.payload_type == 0x8001:
            self.rxqueue.put(bytes(msg.payload)[4:])

    def specific_send(self, payload):
        message = self.message
        message.payload_type = 0x8001
        message.payload = tuple(message.payload)[0:4] + tuple(payload)
        message.send()

class IsoTpConnection(MessageConnection):

    """
    Sends and receives data through a ISO-TP message.
    """
    def _on_message_received(self, msg):
        self.rxqueue.put(bytes(msg.payload))

    def specific_send(self, payload):
        self.message.send(tuple(payload))

class UdsClient(_Client):

    """
    Returns UDS client with specific target address target_addr.

    :param target_addr: Target address (e.g. ECUName=0x10)
    :type channel: int

    :return: The UDS client
    :rtype: :ref:`UdsClient`
    """
    def __call__(self, target_addr) -> _Client:
        if self.conn is HsfzConnection:
            self.conn.message.diag.target_address = target_addr
        elif self.conn is DoIpConnection:
            self.conn.message.target_address = target_addr
        else:
            raise NotImplementedError
        return self
