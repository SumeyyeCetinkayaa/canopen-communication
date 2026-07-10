
"""
Gerçek CAN donanımı bulunmadığında kullanılan simülasyon katmanıdır.

Gönderilen CAN mesajlarını yorumlar, Fake Object Dictionary üzerinde
arama yapar ve uygun CANopen cevaplarını oluşturarak test ortamı sağlar.
"""
import time

from bus.can_message import CanMessage
from bus.fake_object_dictionary import FakeObjectDictionary


class FakeCan:
    def __init__(self):
        self.messages = [
            CanMessage(0x701, [0x05]),
        ]

        self.index = 0
        self.object_dictionary = FakeObjectDictionary()

    def connect(self):
        print("Fake CAN bağlantısı açıldı.")

    def send(self, message):
        print("Fake CAN gönderildi:")
        print(message)

        node_id = message.arbitration_id - 0x600

        if not 1 <= node_id <= 127:
            return

        if len(message.data) != 8:
            return

        command = message.data[0]
        index = message.data[1] | (message.data[2] << 8)
        subindex = message.data[3]

        # Şimdilik yalnızca SDO Read Request destekleniyor.
        if command != 0x40:
            return

        value = self.object_dictionary.get_value(index, subindex)

        if value is None:
            response = self._create_abort_response(
                node_id=node_id,
                index=index,
                subindex=subindex
            )
        else:
            response = self._create_read_response(
                node_id=node_id,
                index=index,
                subindex=subindex,
                value=value
            )

        self.messages.append(response)

    def _create_read_response(self, node_id, index, subindex, value):
        response_id = 0x580 + node_id

        data = [
            0x43,
            index & 0xFF,
            (index >> 8) & 0xFF,
            subindex,
            value & 0xFF,
            (value >> 8) & 0xFF,
            (value >> 16) & 0xFF,
            (value >> 24) & 0xFF,
        ]

        return CanMessage(
            arbitration_id=response_id,
            data=data
        )

    def _create_abort_response(self, node_id, index, subindex):
        response_id = 0x580 + node_id

        # 0x06020000:
        # Object does not exist in the Object Dictionary.
        abort_code = 0x06020000

        data = [
            0x80,
            index & 0xFF,
            (index >> 8) & 0xFF,
            subindex,
            abort_code & 0xFF,
            (abort_code >> 8) & 0xFF,
            (abort_code >> 16) & 0xFF,
            (abort_code >> 24) & 0xFF,
        ]

        return CanMessage(
            arbitration_id=response_id,
            data=data
        )

    def recv(self, timeout=1.0):
        time.sleep(timeout)

        if not self.messages:
            return None

        return self.messages.pop(0) 

    def shutdown(self):
        print("Fake CAN bağlantısı kapatıldı.")