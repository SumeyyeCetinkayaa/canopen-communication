"""
CANopen SDO (Service Data Object) haberleşmesini yönetir.

Bu modül;
- SDO Read Request oluşturur.
- CAN mesajına dönüştürür.
- Gelen SDO Response mesajlarını çözümler.
- Abort mesajlarını tespit eder.
"""

from bus.can_message import CanMessage

class SDORequest:
    READ_COMMAND = 0x40

    def __init__(self, index, subindex):
        self.index = index
        self.subindex = subindex

    @classmethod
    def read(cls, index, subindex=0):
        return cls(index, subindex)

    def to_bytes(self):
        index_lsb = self.index & 0xFF
        index_msb = (self.index >> 8) & 0xFF

        return [
            self.READ_COMMAND,
            index_lsb,
            index_msb,
            self.subindex,
            0x00,
            0x00,
            0x00,
            0x00,
        ]

    def to_can_message(self, node_id):
        can_id = 0x600 + node_id

        return CanMessage(
            arbitration_id=can_id,
            data=self.to_bytes()
        )

    def __str__(self):
        data = " ".join(f"{byte:02X}" for byte in self.to_bytes())

        return (
            f"SDO Read Request | "
            f"Index: 0x{self.index:04X} | "
            f"Subindex: {self.subindex} | "
            f"DATA: {data}"
        )


class SDOResponse:
    def __init__(self, message):
        self.message = message
        self.data = message.data

        self.command = self.data[0]
        self.index = self.data[1] | (self.data[2] << 8)
        self.subindex = self.data[3]

        self.value = int.from_bytes(
            self.data[4:8],
            byteorder="little",
            signed=False
        )

    @staticmethod
    def is_sdo_response(message, node_id):
        return message.arbitration_id == (0x580 + node_id)

    def as_signed_32(self):
        return int.from_bytes(
            self.data[4:8],
            byteorder="little",
            signed=True
        )

    def __str__(self):
        return (
            f"SDO Response | "
            f"Index: 0x{self.index:04X} | "
            f"Subindex: {self.subindex} | "
            f"Value: 0x{self.value:08X}"
        )

    def is_abort(self):
        return self.command == 0x80

    def is_success(self):
        return self.command != 0x80

    def matches(self, request):
        return (
            self.index == request.index
            and self.subindex == request.subindex
        )