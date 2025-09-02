"""
Technica CAN Interface.

"""
from typing import List, Optional, Tuple, Iterable
from can import BusABC, Message
from can.typechecking import AutoDetectedConfig, Channel
from andisdk import andi, message_builder, MessageCAN, DataDirection
import queue


class TechnicaBus(BusABC):
    """
    Technica CAN bus class
    """

    def _enqueue_message(self, msg: MessageCAN):
        message = Message(
            arbitration_id=msg.can_header.message_id,
            is_extended_id=msg.can_header.extended,
            bitrate_switch=msg.can_header.brs,
            is_fd=msg.fd,
            data=msg.payload,
            timestamp=float(msg.timestamp),
            is_rx = msg.direction == DataDirection.DIR_INPUT,
        )
        self.queue.put(message)

    def __init__(
        self,
        channel: Channel,
        # API for custom channel
        driver: str = None,
        link: str = None,
        dev_port: int = None,
        dev_id: int = None,
        dev_ip: str = None,
        dev_mac: str = None,
        sys_nic: str = None,
        # From python-can,
        fd: bool = False,
        **kwargs
    ) -> None:
        """
        Args: 
            channel (str): CAN Adapter's name.
            driver (str): Protocol/driver used.
                Possible values: tecmp, bts, btsevo
            link (str): Link layer.
                Possible values: can, canfd
            dev_port (int32): Port assigned to the channel (CM Channel ID or BTS interface ID).
            dev_id (int32 or None): Device ID (CM ID or BTS Board Index).
            dev_ip (str): Device IP.
            dev_mac (str): Device MAC address.
            sys_nic (str): PC network interface.
        """
        super().__init__(channel, **kwargs)
        if isinstance(dev_port, str):
            dev_port = int(dev_port,0)
            
        config = dict(
            driver=driver,
            link=link,
            dev_port=dev_port,
            dev_id=dev_id,
            dev_ip=dev_ip,
            dev_mac=dev_mac,
            sys_nic=sys_nic,
        )
        config = {k: v for k, v in config.items() if v is not None}
        if driver is None:
            # No driver means no other config
            if len(config):
                bad_keys = ", ".join(config.keys())
                raise ValueError((
                    f'The arguments {bad_keys} were provided,'
                    'but no driver was specified'
                ))
            self.channel = andi.create_channel(channel)
        else:
            if link is None:
                config['link'] = 'canfd' if fd else 'can'
            self.channel = andi.create_channel(**config)

        self.channel_info = str(channel)
        self.queue = queue.Queue()
        self.listener = message_builder.create_can_message(
            self.channel,
            self.channel,
        )
        self.listener.on_message_received += self._enqueue_message
        self.listener.start_capture()

    def _recv_internal(
        self, timeout: Optional[float]
    ) -> Tuple[Optional[Message], bool]:
        """Block waiting for a message from the Bus.

        :param float timeout: Seconds to wait for a message.

        :return:
            None on timeout or a Message object.
        :rtype: can.Message
        """
        try:
            msg = self.queue.get(timeout=timeout)
        except queue.Empty:
            return None, False
        else:
            return msg, False

    def send(self, msg: Message, timeout: Optional[float] = None) -> None:
        can_message = message_builder.create_can_message(sender=self.channel)
        can_message.can_header.extended = msg.is_extended_id
        can_message.can_header.brs = msg.bitrate_switch
        can_message.can_header.message_id = msg.arbitration_id
        can_message.fd = msg.is_fd
        can_message.payload = msg.data
        can_message.send()

    def shutdown(self) -> None:
        """
        Shutdown by closing the interface and freeing resources
        """
        super().shutdown()
        self.listener.stop_capture()
        self.channel = None
        self.listener = None
        self.queue = None

    @staticmethod
    def _detect_available_configs() -> Iterable[AutoDetectedConfig]:
        """
        Identify CAN devices
        """
        andi.detect_hardware()
        for adapter in andi.get_adapters():
            device = adapter.create_channel().NetworkHardwareDevice
            if str(device.interfaceType) == 'CAN':
                yield dict(interface='andisdk', channel=adapter.id)
