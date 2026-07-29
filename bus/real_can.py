"""
Gerçek PEAK PCAN-USB donanımı üzerinden CAN Bus haberleşmesini
gerçekleştirir.

Bu modül python-can kütüphanesini kullanarak fiziksel CAN ağına
bağlanır. CAN bağlantısının farklı bitrate değerleriyle yeniden
açılmasını destekler.
"""

import can
import can.interfaces.pcan


from config import CHANNEL, BITRATE


class RealCan:
    def __init__(self):
        self.bus = None
        self.channel = CHANNEL
        self.bitrate = BITRATE

    def connect(self, bitrate=None):
        """
        PEAK PCAN-USB üzerinden CAN bağlantısını açar.

        bitrate verilmezse mevcut bitrate değeri kullanılır.
        İlk bağlantıda bu değer config.py içindeki BITRATE değeridir.
        """

        if self.bus is not None:
            return

        if bitrate is not None:
            self.bitrate = bitrate

        self.bus = can.Bus(
            interface="pcan",
            channel=self.channel,
            bitrate=self.bitrate
        )

        print(
            f"Gerçek CAN bağlantısı açıldı. "
            f"Kanal: {self.channel}, "
            f"Bitrate: {self.bitrate}"
        )

    def reconnect(self, bitrate):
        """
        Mevcut CAN bağlantısını kapatır ve verilen yeni bitrate
        değeriyle tekrar açar.
        """

        print(
            f"\nCAN bağlantısı {bitrate} bit/s "
            f"ile yeniden açılıyor..."
        )

        self.shutdown()
        self.connect(bitrate=bitrate)

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