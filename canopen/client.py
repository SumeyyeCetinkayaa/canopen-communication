"""
CANopen istemcisini temsil eder.

SDO isteklerini oluşturur, CAN Bus üzerinden gönderir,
gelen cevapları doğrular ve uygulamaya döndürür.
"""
from canopen.sdo import SDORequest, SDOResponse

class CANopenClient:
    def __init__(self, can_bus, node_id):
        self.can_bus = can_bus
        self.node_id = node_id

    def read_object(self, index, subindex=0):
        request = SDORequest.read(
            index=index,
            subindex=subindex
        )

        message = request.to_can_message(
            node_id=self.node_id
        )

        print("SDO Read gönderiliyor:")
        print(message)

        self.can_bus.send_message(message)

        while True:
            response_msg = self.can_bus.read_message()

            if response_msg is None:
                continue

            print(response_msg)

            if not SDOResponse.is_sdo_response(
                response_msg,
                node_id=self.node_id
            ):
                continue

            response = SDOResponse(response_msg)

            if not response.matches(request):
                print("Yanlış isteğe ait cevap geldi.")
                continue

            if response.is_abort():
                print("Cihaz SDO Abort gönderdi.")
                return None

            return response