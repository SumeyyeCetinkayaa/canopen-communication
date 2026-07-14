"""
CANopen istemcisini temsil eder.

SDO isteklerini oluşturur, CAN Bus üzerinden gönderir,
gelen cevapları doğrular ve uygulamaya döndürür.

Ayrıca CANopen NMT komutlarını göndererek node'un
çalışma durumunu yönetir.
"""

import time

from canopen.nmt import NMTCommand
from canopen.sdo import SDORequest, SDOResponse


class CANopenClient:
    # CANopen NMT durum byte'ları
    NMT_BOOT_UP = 0x00
    NMT_STOPPED = 0x04
    NMT_OPERATIONAL = 0x05
    NMT_PRE_OPERATIONAL = 0x7F

    def __init__(self, can_bus, node_id):
        self.can_bus = can_bus
        self.node_id = node_id

    def _wait_for_sdo_response(self, request, timeout):
        """
        Gönderilen SDO isteğine ait cevabı bekler.

        Hem SDO Read hem de SDO Write işlemlerinde
        ortak olarak kullanılır.
        """

        expected_response_id = 0x580 + self.node_id

        print(
            f"Beklenen SDO cevap ID'si: "
            f"0x{expected_response_id:03X}"
        )

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
                print(response)
                return None

            return response

        print(
            f"{timeout} saniye içinde SDO cevabı alınamadı. "
            f"Beklenen CAN ID: 0x{expected_response_id:03X}"
        )

        return None

    def read_object(self, index, subindex=0, timeout=3.0):
        """
        Object Dictionary içerisindeki bir nesneyi SDO ile okur.
        """

        request = SDORequest.read(
            index=index,
            subindex=subindex
        )

        message = request.to_can_message(
            node_id=self.node_id
        )

        print("\nSDO Read gönderiliyor:")
        print(request)
        print(message)

        self.can_bus.send_message(message)

        response = self._wait_for_sdo_response(
            request=request,
            timeout=timeout
        )

        if response is None:
            return None

        print("Geçerli SDO Read cevabı alındı.")
        print(response)

        return response

    def write_object(
        self,
        index,
        subindex,
        value,
        size,
        timeout=3.0
    ):
        """
        Object Dictionary içerisindeki bir nesneye SDO ile veri yazar.

        size yalnızca 1, 2 veya 4 byte olabilir.
        """

        request = SDORequest.write(
            index=index,
            subindex=subindex,
            value=value,
            size=size
        )

        message = request.to_can_message(
            node_id=self.node_id
        )

        print("\nSDO Write gönderiliyor:")
        print(request)
        print(message)

        self.can_bus.send_message(message)

        response = self._wait_for_sdo_response(
            request=request,
            timeout=timeout
        )

        if response is None:
            return False

        if not response.is_write_success():
            print(
                "Beklenen SDO Write onayı alınamadı. "
                f"Komut byte'ı: 0x{response.command:02X}"
            )
            print(response)
            return False

        print("SDO Write işlemi başarılı.")
        print(response)

        return True

    def _send_nmt_command(self, command):
        """
        Oluşturulmuş bir NMT komutunu CAN hattına gönderir.

        NMT mesajlarının CAN-ID değeri 0x000'dır.
        """

        message = command.to_can_message()

        print("\nNMT komutu gönderiliyor:")
        print(command)
        print(message)

        self.can_bus.send_message(message)

        print("NMT komutu CAN hattına gönderildi.")

    def start_node(self, node_id=None):
        target_node_id = self.node_id if node_id is None else node_id

        command = NMTCommand.start_node(
            node_id=target_node_id
        )

        self._send_nmt_command(command)

    def stop_node(self, node_id=None):
        target_node_id = self.node_id if node_id is None else node_id

        command = NMTCommand.stop_node(
            node_id=target_node_id
        )

        self._send_nmt_command(command)

    def enter_pre_operational(self, node_id=None):
        target_node_id = self.node_id if node_id is None else node_id

        command = NMTCommand.enter_pre_operational(
            node_id=target_node_id
        )

        self._send_nmt_command(command)

    def reset_node(self, node_id=None):
        target_node_id = self.node_id if node_id is None else node_id

        command = NMTCommand.reset_node(
            node_id=target_node_id
        )

        self._send_nmt_command(command)

    def reset_communication(self, node_id=None):
        target_node_id = self.node_id if node_id is None else node_id

        command = NMTCommand.reset_communication(
            node_id=target_node_id
        )

        self._send_nmt_command(command)

    def wait_for_heartbeat(
        self,
        node_id=None,
        timeout=5.0,
        accepted_states=None
    ):
        """
        Belirli bir node'a ait heartbeat veya boot-up mesajını bekler.

        Heartbeat COB-ID:
            0x700 + Node ID

        Veri byte'ları:
            0x00 -> Boot-up
            0x04 -> Stopped
            0x05 -> Operational
            0x7F -> Pre-operational

        accepted_states verilmezse bilinen tüm NMT durumları
        kabul edilir.
        """

        target_node_id = self.node_id if node_id is None else node_id
        expected_heartbeat_id = 0x700 + target_node_id

        if accepted_states is None:
            accepted_states = {
                self.NMT_BOOT_UP,
                self.NMT_STOPPED,
                self.NMT_OPERATIONAL,
                self.NMT_PRE_OPERATIONAL,
            }
        else:
            accepted_states = set(accepted_states)

        print(
            f"\nHeartbeat/boot-up mesajı bekleniyor. "
            f"Beklenen CAN ID: 0x{expected_heartbeat_id:03X}"
        )

        start_time = time.monotonic()

        while time.monotonic() - start_time < timeout:
            message = self.can_bus.read_message()

            if message is None:
                continue

            print("CAN mesajı alındı:")
            print(message)

            if message.arbitration_id != expected_heartbeat_id:
                print("Mesaj beklenen heartbeat ID'sine ait değil.")
                continue

            if len(message.data) < 1:
                print("Heartbeat mesajının veri alanı boş.")
                continue

            state = message.data[0]

            if state not in accepted_states:
                print(
                    f"Heartbeat durumu beklenen durumlar arasında değil: "
                    f"0x{state:02X}"
                )
                continue

            state_name = self._get_nmt_state_name(state)

            print(
                f"Geçerli heartbeat/boot-up mesajı alındı. "
                f"Durum: {state_name} (0x{state:02X})"
            )

            return state

        print(
            f"{timeout} saniye içinde heartbeat/boot-up "
            f"mesajı alınamadı. "
            f"Beklenen CAN ID: 0x{expected_heartbeat_id:03X}"
        )

        return None

    def wait_for_bootup(self, node_id=None, timeout=5.0):
        """
        Yalnızca 0x00 boot-up mesajını bekler.
        """

        return self.wait_for_heartbeat(
            node_id=node_id,
            timeout=timeout,
            accepted_states={self.NMT_BOOT_UP}
        )

    @classmethod
    def _get_nmt_state_name(cls, state):
        state_names = {
            cls.NMT_BOOT_UP: "Boot-up",
            cls.NMT_STOPPED: "Stopped",
            cls.NMT_OPERATIONAL: "Operational",
            cls.NMT_PRE_OPERATIONAL: "Pre-operational",
        }

        return state_names.get(
            state,
            f"Bilinmeyen durum 0x{state:02X}"
        )

    def change_node_id(self, new_node_id):
        """
        İstemcinin bundan sonraki SDO işlemlerinde kullanacağı
        hedef Node ID bilgisini günceller.

        Bu metot encoder'a herhangi bir değer yazmaz.
        """

        if not 1 <= new_node_id <= 127:
            raise ValueError(
                "Node ID 1 ile 127 arasında olmalıdır."
            )

        old_node_id = self.node_id
        self.node_id = new_node_id

        print(
            f"\nCANopenClient Node ID güncellendi: "
            f"0x{old_node_id:02X} -> 0x{new_node_id:02X}"
        )