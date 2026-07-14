"""
CANopen NMT (Network Management) komutlarını yönetir.

NMT mesajları tüm node'ların veya belirli bir node'un
çalışma durumunu değiştirmek için kullanılır.
"""

from bus.can_message import CanMessage


class NMTCommand:
    START_REMOTE_NODE = 0x01
    STOP_REMOTE_NODE = 0x02
    ENTER_PRE_OPERATIONAL = 0x80
    RESET_NODE = 0x81
    RESET_COMMUNICATION = 0x82

    def __init__(self, command, node_id):
        self.command = command
        self.node_id = node_id

    @classmethod
    def start_node(cls, node_id):
        return cls(
            command=cls.START_REMOTE_NODE,
            node_id=node_id
        )

    @classmethod
    def stop_node(cls, node_id):
        return cls(
            command=cls.STOP_REMOTE_NODE,
            node_id=node_id
        )

    @classmethod
    def enter_pre_operational(cls, node_id):
        return cls(
            command=cls.ENTER_PRE_OPERATIONAL,
            node_id=node_id
        )

    @classmethod
    def reset_node(cls, node_id):
        return cls(
            command=cls.RESET_NODE,
            node_id=node_id
        )

    @classmethod
    def reset_communication(cls, node_id):
        return cls(
            command=cls.RESET_COMMUNICATION,
            node_id=node_id
        )

    def to_bytes(self):
        return [
            self.command,
            self.node_id
        ]

    def to_can_message(self):
        """
        NMT mesajlarının CAN-ID değeri her zaman 0x000'dır.
        Veri alanı 2 byte'tır:

        Byte 0: NMT komutu
        Byte 1: Hedef Node ID

        Node ID = 0 verilirse komut tüm node'lara gönderilir.
        """

        return CanMessage(
            arbitration_id=0x000,
            data=self.to_bytes()
        )

    def __str__(self):
        data = " ".join(
            f"{byte:02X}"
            for byte in self.to_bytes()
        )

        return (
            f"NMT Command | "
            f"Command: 0x{self.command:02X} | "
            f"Node ID: 0x{self.node_id:02X} | "
            f"DATA: {data}"
        )