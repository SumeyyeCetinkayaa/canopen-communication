"""
CAN haberleşmesi için ortak bir arayüz sağlar.

Uygulamanın gerçek CAN donanımı (RealCan) veya simülasyon ortamı
(FakeCan) kullandığını bilmesine gerek kalmadan aynı yöntemlerle
haberleşmesini sağlar.
"""

from config import USE_REAL_CAN, READ_TIMEOUT
from bus.fake_can import FakeCan
from bus.real_can import RealCan


class CanBus: 
    def __init__(self):
        if USE_REAL_CAN:
            self.adapter = RealCan()
        else:
            self.adapter = FakeCan()

    def connect(self):
        self.adapter.connect()

    def send_message(self, message):
        self.adapter.send(message)

    def read_message(self):
        return self.adapter.recv(timeout=READ_TIMEOUT)

    def shutdown(self):
        self.adapter.shutdown()