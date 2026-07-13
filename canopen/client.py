"""
CANopen istemcisini temsil eder.

SDO isteklerini oluşturur, CAN Bus üzerinden gönderir,
gelen cevapları doğrular ve uygulamaya döndürür.
"""

import time

from canopen.sdo import SDORequest, SDOResponse


class CANopenClient:
    def __init__(self, can_bus, node_id):
        self.can_bus = can_bus
        self.node_id = node_id

    def read_object(self, index, subindex=0, timeout=3.0):
        request = SDORequest.read(
            index=index,
            subindex=subindex
        )

        message = request.to_can_message(
            node_id=self.node_id
        )

        print("\nSDO Read gönderiliyor:")
        print(message)

        expected_response_id = 0x580 + self.node_id

        print(
            f"Beklenen SDO cevap ID'si: "
            f"0x{expected_response_id:03X}"
        )

        self.can_bus.send_message(message)

        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:
            response_msg = self.can_bus.read_message()

            if response_msg is None:
                continue

            print("CAN mesajı alındı:")
            print(response_msg)

            if not SDOResponse.is_sdo_response(
                response_msg,
                node_id=self.node_id
            ):
                print("Mesaj bu node'a ait bir SDO cevabı değil.")
                continue

            response = SDOResponse(response_msg)

            if not response.matches(request):
                print("Yanlış isteğe ait SDO cevabı geldi.")
                continue

            if response.is_abort():
                print("Cihaz SDO Abort gönderdi.")
                return None

            print("Geçerli SDO cevabı alındı.")
            return response

        print(
            f"{timeout} saniye içinde SDO cevabı alınamadı. "
            f"Beklenen CAN ID: 0x{expected_response_id:03X}"
        )

        return None