"""
Projenin başlangıç noktasıdır.

CAN bağlantısını başlatır, CANopen istemcisini oluşturur ve
Object Dictionary üzerinden örnek SDO okuma işlemlerini gerçekleştirir.

Bu dosya yalnızca uygulamanın genel akışını yönetir.
CANopen ve CAN haberleşme detayları ilgili katmanlara bırakılmıştır.
"""

from bus.can_bus import CanBus
from canopen.client import CANopenClient
from canopen.object_dictionary import ObjectDictionary


def print_response(title, response):
    print(f"\n{title}")

    if response is None:
        print("Değer okunamadı.")
        return

    print(response)


def main():
    can_bus = CanBus()
    node_id = 1

    try:
        can_bus.connect()

        client = CANopenClient(can_bus, node_id)

        device_type = client.read_object(
            index=ObjectDictionary.DEVICE_TYPE,
            subindex=0
        )
        print_response("Device Type:", device_type)

        vendor_id = client.read_object(
            index=ObjectDictionary.IDENTITY_OBJECT,
            subindex=ObjectDictionary.IDENTITY_VENDOR_ID
        )
        print_response("Vendor ID:", vendor_id)

        product_code = client.read_object(
            index=ObjectDictionary.IDENTITY_OBJECT,
            subindex=ObjectDictionary.IDENTITY_PRODUCT_CODE
        )
        print_response("Product Code:", product_code)

        serial_number = client.read_object(
            index=ObjectDictionary.IDENTITY_OBJECT,
            subindex=ObjectDictionary.IDENTITY_SERIAL_NUMBER
        )
        print_response("Serial Number:", serial_number)

    except KeyboardInterrupt:
        print("\nProgram durduruldu.")

    except Exception as e:
        print("Hata:", e)

    finally:
        can_bus.shutdown()


if __name__ == "__main__":
    main()