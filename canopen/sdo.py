"""
CANopen SDO (Service Data Object) haberleşmesini yönetir.

Bu modül;
- SDO Read Request oluşturur.
- SDO Write Request oluşturur.
- İstekleri CAN mesajına dönüştürür.
- Gelen SDO Response mesajlarını çözümler.
- Abort mesajlarını tespit eder.
"""

from bus.can_message import CanMessage

class SDORequest:
    READ_COMMAND = 0x40

    # Expedited SDO Write komutları
    WRITE_1_BYTE_COMMAND = 0x2F
    WRITE_2_BYTE_COMMAND = 0x2B
    WRITE_4_BYTE_COMMAND = 0x23

    def __init__(
        self,
        index,
        subindex,
        operation="read",
        value=None,
        size=None
    ):
        self.index = index
        self.subindex = subindex
        self.operation = operation
        self.value = value
        self.size = size

    @classmethod
    def read(cls, index, subindex=0):
        return cls(
            index=index,
            subindex=subindex,
            operation="read"
        )

    @classmethod
    def write(cls, index, subindex, value, size):
        """
        Expedited SDO Write isteği oluşturur.

        size:
            1 -> Unsigned8
            2 -> Unsigned16
            4 -> Unsigned32
        """

        if size not in (1, 2, 4):
            raise ValueError(
                "SDO Write veri boyutu yalnızca 1, 2 veya 4 byte olabilir."
            )

        max_value = (1 << (size * 8)) - 1

        if not 0 <= value <= max_value:
            raise ValueError(
                f"{size} byte için değer 0 ile {max_value} arasında olmalıdır."
            )

        return cls(
            index=index,
            subindex=subindex,
            operation="write",
            value=value,
            size=size
        )

    def _get_write_command(self):
        if self.size == 1:
            return self.WRITE_1_BYTE_COMMAND

        if self.size == 2:
            return self.WRITE_2_BYTE_COMMAND

        if self.size == 4:
            return self.WRITE_4_BYTE_COMMAND

        raise ValueError("Geçersiz SDO Write veri boyutu.")

    def to_bytes(self):
        index_lsb = self.index & 0xFF
        index_msb = (self.index >> 8) & 0xFF

        if self.operation == "read":
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

        if self.operation == "write":
            command = self._get_write_command()

            value_bytes = list(
                self.value.to_bytes(
                    length=self.size,
                    byteorder="little",
                    signed=False
                )
            )

            # CANopen SDO mesajı toplamda 8 byte olmalıdır.
            value_bytes.extend([0x00] * (4 - self.size))

            return [
                command,
                index_lsb,
                index_msb,
                self.subindex,
                *value_bytes
            ]

        raise ValueError(
            f"Desteklenmeyen SDO işlemi: {self.operation}"
        )

    def to_can_message(self, node_id):
        can_id = 0x600 + node_id

        return CanMessage(
            arbitration_id=can_id,
            data=self.to_bytes()
        )

    def __str__(self):
        data = " ".join(
            f"{byte:02X}"
            for byte in self.to_bytes()
        )

        if self.operation == "read":
            return (
                f"SDO Read Request | "
                f"Index: 0x{self.index:04X} | "
                f"Subindex: {self.subindex} | "
                f"DATA: {data}"
            )

        return (
            f"SDO Write Request | "
            f"Index: 0x{self.index:04X} | "
            f"Subindex: {self.subindex} | "
            f"Value: {self.value} | "
            f"Size: {self.size} byte | "
            f"DATA: {data}"
        )


class SDOResponse:
    WRITE_SUCCESS_COMMAND = 0x60
    ABORT_COMMAND = 0x80

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

    def is_abort(self):
        return self.command == self.ABORT_COMMAND

    def is_write_success(self):
        """
        Başarılı SDO Write cevabının komut byte'ı 0x60'tır.
        """

        return self.command == self.WRITE_SUCCESS_COMMAND

    def is_success(self):
        return not self.is_abort()

    def matches(self, request):
        return (
            self.index == request.index
            and self.subindex == request.subindex
        )

    def get_abort_code(self):
        """
        Abort cevabındaki 32-bit hata kodunu döndürür.
        """

        if not self.is_abort():
            return None

        return int.from_bytes(
            self.data[4:8],
            byteorder="little",
            signed=False
        )

    def __str__(self):
        if self.is_abort():
            return (
                f"SDO Abort Response | "
                f"Index: 0x{self.index:04X} | "
                f"Subindex: {self.subindex} | "
                f"Abort Code: 0x{self.get_abort_code():08X}"
            )

        if self.is_write_success():
            return (
                f"SDO Write Response | "
                f"Index: 0x{self.index:04X} | "
                f"Subindex: {self.subindex} | "
                f"Durum: Başarılı"
            )

        return (
            f"SDO Read Response | "
            f"Index: 0x{self.index:04X} | "
            f"Subindex: {self.subindex} | "
            f"Value: 0x{self.value:08X}"
        )