"""
CANopen encoder kimlik bilgilerini, preset değerini
ve anlık pozisyon değerini okur.

Identity Object:
    0x1018:01 -> Vendor ID
    0x1018:02 -> Product Code
    0x1018:03 -> Revision Number
    0x1018:04 -> Serial Number

Preset Value:
    0x6003:00 -> Atanmış preset değeri

Position Value:
    0x6004:00 -> Anlık pozisyon
"""

from dataclasses import dataclass

from canopen.object_dictionary import ObjectDictionary


@dataclass
class EncoderInformation:
    vendor_id: int | None
    product_code: int | None
    revision_number: int | None
    serial_number: int | None
    position: int | None
    preset_value: int | None


class EncoderReader:
    def __init__(self, client):
        self.client = client

    def _read_unsigned(self, index, subindex=0, timeout=3.0):
        response = self.client.read_object(
            index=index,
            subindex=subindex,
            timeout=timeout,
        )

        if response is None:
            return None

        return response.value

    def read_identity(self, timeout=3.0):
        """
        Encoder'ın 0x1018 Identity Object bilgilerini okur.
        """

        return {
            "vendor_id": self._read_unsigned(
                ObjectDictionary.IDENTITY_OBJECT,
                ObjectDictionary.IDENTITY_VENDOR_ID,
                timeout,
            ),
            "product_code": self._read_unsigned(
                ObjectDictionary.IDENTITY_OBJECT,
                ObjectDictionary.IDENTITY_PRODUCT_CODE,
                timeout,
            ),
            "revision_number": self._read_unsigned(
                ObjectDictionary.IDENTITY_OBJECT,
                ObjectDictionary.IDENTITY_REVISION_NUMBER,
                timeout,
            ),
            "serial_number": self._read_unsigned(
                ObjectDictionary.IDENTITY_OBJECT,
                ObjectDictionary.IDENTITY_SERIAL_NUMBER,
                timeout,
            ),
        }

    def read_preset_value(self, timeout=3.0):
        """
        Encoder'ın 0x6003:00 Preset Value değerini
        unsigned 32-bit olarak okur.
        """

        return self._read_unsigned(
            index=ObjectDictionary.PRESET_VALUE,
            subindex=0,
            timeout=timeout,
        )

    def read_position(self, timeout=3.0):
        """
        Encoder'ın 0x6004:00 anlık pozisyon değerini
        signed 32-bit olarak okur.
        """

        response = self.client.read_object(
            index=ObjectDictionary.POSITION_VALUE,
            subindex=0,
            timeout=timeout,
        )

        if response is None:
            return None

        return response.as_signed_32()

    def read_all(self, timeout=3.0):
        identity = self.read_identity(timeout=timeout)
        preset_value = self.read_preset_value(timeout=timeout)
        position = self.read_position(timeout=timeout)

        return EncoderInformation(
            vendor_id=identity["vendor_id"],
            product_code=identity["product_code"],
            revision_number=identity["revision_number"],
            serial_number=identity["serial_number"],
            position=position,
            preset_value=preset_value,
        )