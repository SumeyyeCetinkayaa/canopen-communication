"""
Gerçek PEAK PCAN-USB donanımı üzerinden CAN Bus haberleşmesini gerçekleştirir.

Bu modül python-can kütüphanesini kullanarak fiziksel CAN ağına bağlanır.
"""

import can

from config import CHANNEL, BITRATE


class RealCan:
    def __init__(self):
        self.bus = None

    def connect(self):
        if self.bus is not None:
            return

        self.bus = can.Bus(
            interface="pcan",
            channel=CHANNEL,
            bitrate=BITRATE
        )

        print(
            f"Gerçek CAN bağlantısı açıldı. "
            f"Kanal: {CHANNEL}, Bitrate: {BITRATE}"
        )

    def send(self, message):
        if self.bus is None:
            raise RuntimeError("CAN bağlantısı açık değil.")

        can_msg = can.Message(
            arbitration_id=message.arbitration_id,
            data=message.data,
            is_extended_id=False
        )

        self.bus.send(can_msg)

    def recv(self, timeout=1.0):
        if self.bus is None:
            raise RuntimeError("CAN bağlantısı açık değil.")

        return self.bus.recv(timeout=timeout)

    def shutdown(self):
        if self.bus is None:
            return

        self.bus.shutdown()
        self.bus = None

        print("Gerçek CAN bağlantısı kapatıldı.")