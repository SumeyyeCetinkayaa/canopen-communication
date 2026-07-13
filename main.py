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

    # Heartbeat COB-ID:
    # 0x75B = 0x700 + 0x5B
    node_id = 0x5B

    print(f"Node ID: 0x{node_id:02X}")
    print(f"SDO Request COB-ID: 0x{0x600 + node_id:03X}")
    print(f"SDO Response COB-ID: 0x{0x580 + node_id:03X}")

    try:
        can_bus.connect()

        client = CANopenClient(
            can_bus=can_bus,
            node_id=node_id
        )

        device_type = client.read_object(
            index=ObjectDictionary.DEVICE_TYPE,
            subindex=0,
            timeout=3.0
        )

        print_response(
            title="Device Type:",
            response=device_type
        )

        position = client.read_object(
            index=ObjectDictionary.POSITION_VALUE,
            subindex=0,
            timeout=3.0
        )

        print("\nPosition Value:")

        if position is None:
            print("Değer okunamadı.")
        else:
            print(f"{position.as_signed_32()} count")

    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")

    except Exception as error:
        print(f"\nHata: {error}")

    finally:
        can_bus.shutdown()


if __name__ == "__main__":
    main()