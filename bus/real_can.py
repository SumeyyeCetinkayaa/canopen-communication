"""
Gerçek PEAK PCAN-USB donanımı üzerinden CAN Bus haberleşmesini gerçekleştirir.

Bu modül python-can kütüphanesini kullanarak fiziksel CAN ağına bağlanır.
Gerçek donanım entegrasyonu tamamlandığında kullanılacaktır.
"""
import can
from config import CHANNEL, BITRATE


class RealCan:
    def __init__(self):
        self.bus = None

    def connect(self):
        self.bus = can.interface.Bus(
            interface="pcan",
            channel=CHANNEL,
            bitrate=BITRATE
        )
        print("Gerçek CAN bağlantısı açıldı.")

    def send(self, message):
        can_msg = can.Message(
            arbitration_id=message.arbitration_id,
            data=message.data,
            is_extended_id=False
        )
        self.bus.send(can_msg)

    def recv(self, timeout=1.0):
        return self.bus.recv(timeout=timeout)

    def shutdown(self):
        if self.bus is not None:
            self.bus.shutdown()
            print("Gerçek CAN bağlantısı kapatıldı.")