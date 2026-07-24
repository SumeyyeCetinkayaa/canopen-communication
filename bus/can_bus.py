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

    def connect(self, bitrate=None):
        """
        CAN bağlantısını açar.

        Gerçek CAN kullanıldığında bitrate verilebilir.
        FakeCan kullanıldığında bitrate dikkate alınmaz.
        """

        if USE_REAL_CAN:
            self.adapter.connect(bitrate=bitrate)
        else:
            self.adapter.connect()

    def reconnect(self, bitrate):
        """
        CAN bağlantısını verilen yeni bitrate ile yeniden açar.
        """

        if not USE_REAL_CAN:
            print(
                "FakeCan kullanılırken bitrate değişikliği "
                "uygulanmaz."
            )
            return

        self.adapter.reconnect(bitrate=bitrate)

    def send_message(self, message):
        self.adapter.send(message)

    def read_message(self, timeout=None):
        """
        CAN hattından mesaj okur.

        timeout verilmezse config.py içindeki READ_TIMEOUT kullanılır.
        Tarama gibi hızlı işlemler kendi kısa timeout değerini verebilir.
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
        self.adapter.shutdown()