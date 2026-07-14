"""
CANopen standardında ve encoder üreticisine özel tanımlanan
Object Dictionary index ve subindex sabitlerini içerir.

Kod içerisinde sabit hexadecimal değerler yerine anlamlı isimlerin
kullanılmasını sağlar.
"""


class ObjectDictionary:
    # ---------------------------------------------------------
    # Communication Profile Area
    # ---------------------------------------------------------
    DEVICE_TYPE = 0x1000
    ERROR_REGISTER = 0x1001

    STORE_PARAMETERS = 0x1010
    STORE_ALL_PARAMETERS_SUBINDEX = 1

    PRODUCER_HEARTBEAT_TIME = 0x1017

    MANUFACTURER_DEVICE_NAME = 0x1008
    MANUFACTURER_HARDWARE_VERSION = 0x1009
    MANUFACTURER_SOFTWARE_VERSION = 0x100A

    IDENTITY_OBJECT = 0x1018

    # Identity Object subindex değerleri
    IDENTITY_VENDOR_ID = 1
    IDENTITY_PRODUCT_CODE = 2
    IDENTITY_REVISION_NUMBER = 3
    IDENTITY_SERIAL_NUMBER = 4

    # ---------------------------------------------------------
    # TPDO Communication Parameters
    # ---------------------------------------------------------
    TPDO1_COMMUNICATION_PARAMETER = 0x1800

    TPDO1_COB_ID_SUBINDEX = 1
    TPDO1_TRANSMISSION_TYPE_SUBINDEX = 2
    TPDO1_INHIBIT_TIME_SUBINDEX = 3
    TPDO1_EVENT_TIMER_SUBINDEX = 5

    # ---------------------------------------------------------
    # Manufacturer Specific Area
    # ---------------------------------------------------------
    BAUD_RATE = 0x2100
    NODE_ID = 0x2101

    # ---------------------------------------------------------
    # Encoder Profile Area
    # ---------------------------------------------------------
    POSITION_VALUE = 0x6004

    # ---------------------------------------------------------
    # Store Parameters imzası
    # ---------------------------------------------------------
    SAVE_SIGNATURE = 0x65766173