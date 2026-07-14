"""
Uygulamanın başlangıç noktasıdır.

CAN bağlantısını başlatır, CANopen istemcisini oluşturur ve
encoder yapılandırma işlemini EncoderConfigurator sınıfına bırakır.
"""

import time

from bus.can_bus import CanBus
from canopen.client import CANopenClient
from canopen.encoder_configurator import (
    EncoderConfigurator,
    EncoderSettings
)
from canopen.object_dictionary import ObjectDictionary


def print_configuration(settings):
    """
    Uygulanacak encoder ayarlarını ekrana yazdırır.
    """

    print("\nUygulanacak encoder ayarları:")
    print(f"Mevcut Node ID          : 0x{settings.current_node_id:02X}")
    print(f"Yeni Node ID            : 0x{settings.new_node_id:02X}")
    print(f"Baud Rate               : {settings.baud_rate} kbit/s")
    print(f"Producer Heartbeat Time : {settings.heartbeat_time_ms} ms")
    print(f"Transmission Type       : {settings.transmission_type}")
    print(f"Event Time              : {settings.event_time_ms} ms")


def main():
    # Encoder şu anda 0x5B Node ID ile çalışıyor.
    current_node_id = 0x5B

    # Güvenli testte Node ID değiştirilmez.
    new_node_id = 0x5B

    # Güvenli testte mevcut baud rate yeniden yazılır.
    baud_rate = 250

    settings = EncoderSettings(
        current_node_id=current_node_id,
        new_node_id=new_node_id,
        baud_rate=baud_rate,
        heartbeat_time_ms=100,
        transmission_type=255,
        event_time_ms=80
    )

    can_bus = CanBus()

    print(f"Node ID: 0x{current_node_id:02X}")
    print(
        f"SDO Request COB-ID: "
        f"0x{0x600 + current_node_id:03X}"
    )
    print(
        f"SDO Response COB-ID: "
        f"0x{0x580 + current_node_id:03X}"
    )
    print(
        f"Heartbeat COB-ID: "
        f"0x{0x700 + current_node_id:03X}"
    )

    print_configuration(settings)

    try:
        can_bus.connect()

        client = CANopenClient(
            can_bus=can_bus,
            node_id=settings.current_node_id
        )

        configurator = EncoderConfigurator(
            client=client
        )

        # ---------------------------------------------------------
        # 1. Encoder ayarlarını yaz ve geri okuyarak doğrula
        # ---------------------------------------------------------
        configured = configurator.configure(
            settings=settings
        )

        if not configured:
            print("\nEncoder yapılandırılamadı.")
            return

        # ---------------------------------------------------------
        # 2. Ayarları kalıcı hafızaya kaydet
        # ---------------------------------------------------------
        saved = configurator.save()

        if not saved:
            print(
                "\nAyarlar kalıcı hafızaya "
                "kaydedilemedi."
            )
            return

        print("\nEncoder başarıyla yapılandırıldı.")
        print("Ayarlar kalıcı hafızaya kaydedildi.")

        # EEPROM işleminin tamamlanması için kısa süre bekle.
        time.sleep(1.0)

        # ---------------------------------------------------------
        # 3. NMT Reset Communication gönder
        #
        # CAN-ID: 0x000
        # DATA: 82 5B
        # ---------------------------------------------------------
        print(
            "\nEncoder iletişim parametreleri "
            "yeniden başlatılıyor..."
        )

        client.reset_communication(
            node_id=settings.current_node_id
        )

        print("\nNMT Reset Communication komutu gönderildi.")

        # ---------------------------------------------------------
        # 4. Encoder'ın yeniden ayağa kalkmasını heartbeat veya
        #    boot-up mesajıyla doğrula
        # ---------------------------------------------------------
        state = client.wait_for_heartbeat(
            node_id=settings.new_node_id,
            timeout=5.0
        )

        if state is None:
            print(
                "\nReset sonrasında encoder'dan heartbeat veya "
                "boot-up mesajı alınamadı."
            )
            return

        print(
            "\nEncoder reset sonrasında CAN hattında "
            "yeniden görüldü."
        )

        # ---------------------------------------------------------
        # 5. Reset sonrası SDO haberleşmesini doğrula
        #
        # Bu güvenli testte eski ve yeni Node ID aynı olduğu için
        # istemcinin Node ID'si değişmiyor.
        # ---------------------------------------------------------
        client.change_node_id(
            settings.new_node_id
        )

        print(
            "\nReset sonrası SDO haberleşmesi "
            "kontrol ediliyor..."
        )

        device_type = client.read_object(
            index=ObjectDictionary.DEVICE_TYPE,
            subindex=0,
            timeout=5.0
        )

        if device_type is None:
            print(
                "\nEncoder heartbeat gönderdi ancak reset sonrası "
                "SDO isteğine cevap vermedi."
            )
            return

        print("\nReset sonrası SDO haberleşmesi doğrulandı.")
        print(f"Device Type: 0x{device_type.value:08X}")

        # ---------------------------------------------------------
        # 6. Sonuç
        # ---------------------------------------------------------
        print("\nUygulanan ayarlar:")
        print(
            f"Producer Heartbeat Time : "
            f"{settings.heartbeat_time_ms} ms"
        )
        print(
            f"Transmission Type       : "
            f"{settings.transmission_type}"
        )
        print(
            f"Event Time              : "
            f"{settings.event_time_ms} ms"
        )
        print(
            f"Node ID                 : "
            f"0x{settings.new_node_id:02X}"
        )
        print(
            f"Baud Rate               : "
            f"{settings.baud_rate} kbit/s"
        )

        print(
            "\nGüvenli reset testi başarıyla tamamlandı. "
            "Encoder reset sonrasında yeniden bulundu ve "
            "SDO haberleşmesi doğrulandı."
        )

    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")

    except Exception as error:
        print(f"\nHata: {error}")

    finally:
        can_bus.shutdown()


if __name__ == "__main__":
    main()