"""
CAN haberleşmesi için ortak bir arayüz sağlar.

Uygulamanın gerçek PEAK PCAN-USB donanımı üzerinden
CAN haberleşmesi gerçekleştirmesini sağlar.
"""

from config import READ_TIMEOUT
from bus.real_can import RealCan


class CanBus:
    def __init__(self):
        self.adapter = RealCan()

    def connect(self, bitrate=None):
        """
        CAN bağlantısını açar.

        bitrate verilmezse config.py içindeki varsayılan
        bitrate değeri kullanılır.
        """

        self.adapter.connect(bitrate=bitrate)

    def reconnect(self, bitrate):
        """
        CAN bağlantısını verilen bitrate ile yeniden açar.
        """

        self.adapter.reconnect(bitrate=bitrate)

    def send_message(self, message):
        """
        CAN mesajı gönderir.
        """

        self.adapter.send(message)

    def read_message(self, timeout=None):
        """
        CAN hattından mesaj okur.

        timeout verilmezse config.py içindeki READ_TIMEOUT
        değeri kullanılır.
        """

        effective_timeout = (
            READ_TIMEOUT
            if timeout is None
            else timeout
        )

        return self.adapter.recv(
            timeout=effective_timeout
        )

    def shutdown(self):
        """
        CAN bağlantısını kapatır.
        """

        self.adapter.shutdown()