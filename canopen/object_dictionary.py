"""
CANopen standardında tanımlanan Object Dictionary Index ve
Subindex tanımlarını içerir.

Kod içerisinde sabit hexadecimal değerler yerine anlamlı isimlerin
kullanılmasını sağlar.
"""


class ObjectDictionary:
    # Communication Profile Area
    DEVICE_TYPE = 0x1000
    ERROR_REGISTER = 0x1001
    MANUFACTURER_DEVICE_NAME = 0x1008
    MANUFACTURER_HARDWARE_VERSION = 0x1009
    MANUFACTURER_SOFTWARE_VERSION = 0x100A
    IDENTITY_OBJECT = 0x1018

    # Identity Object subindex değerleri
    IDENTITY_VENDOR_ID = 1
    IDENTITY_PRODUCT_CODE = 2
    IDENTITY_REVISION_NUMBER = 3
    IDENTITY_SERIAL_NUMBER = 4

    # Encoder Profile Area
    POSITION_VALUE = 0x6004