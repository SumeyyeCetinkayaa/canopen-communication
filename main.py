"""
Uygulamanın başlangıç noktasıdır.

Kullanıcıdan mevcut ve yeni Node ID ile baud rate değerlerini alır.
Encoder ayarlarını CANopen üzerinden uygular, kalıcı belleğe kaydeder,
iletişimi yeniden başlatır ve yeni bağlantı bilgileriyle doğrular.
"""


import time

from bus.can_bus import CanBus
from canopen.client import CANopenClient
from canopen.encoder_configurator import (
    EncoderConfigurator,
    EncoderSettings,
)
from canopen.object_dictionary import ObjectDictionary


BITRATE_VALUES = {
    10: 10_000,
    20: 20_000,
    50: 50_000,
    100: 100_000,
    125: 125_000,
    250: 250_000,
    500: 500_000,
    800: 800_000,
    1000: 1_000_000,
}


def parse_node_id(value):
    """
    Node ID değerini decimal veya hexadecimal olarak kabul eder.

    Örnek geçerli girişler:
        90
        0x5A
        5A
    """

    cleaned_value = value.strip()

    if not cleaned_value:
        raise ValueError("Node ID boş bırakılamaz.")

    try:
        if cleaned_value.lower().startswith("0x"):
            node_id = int(cleaned_value, 16)
        elif any(character in "abcdefABCDEF" for character in cleaned_value):
            node_id = int(cleaned_value, 16)
        else:
            node_id = int(cleaned_value, 10)
    except ValueError as error:
        raise ValueError(
            "Node ID decimal veya hexadecimal bir sayı olmalıdır."
        ) from error

    if not 1 <= node_id <= 127:
        raise ValueError(
            "Node ID 1 ile 127 arasında olmalıdır."
        )

    return node_id


def read_node_id(prompt, default_value=None):
    """
    Kullanıcıdan geçerli bir Node ID alıncaya kadar giriş ister.
    """

    while True:
        default_text = (
            f" [0x{default_value:02X}]"
            if default_value is not None
            else ""
        )

        user_input = input(f"{prompt}{default_text}: ").strip()

        if not user_input and default_value is not None:
            return default_value

        try:
            return parse_node_id(user_input)
        except ValueError as error:
            print(f"Hatalı giriş: {error}")


def read_baud_rate(prompt, default_value=None):
    """
    Kullanıcıdan desteklenen bir baud rate değeri alır.
    """

    supported_rates = ", ".join(
        str(rate)
        for rate in BITRATE_VALUES
    )

    while True:
        default_text = (
            f" [{default_value}]"
            if default_value is not None
            else ""
        )

        user_input = input(f"{prompt}{default_text}: ").strip()

        if not user_input and default_value is not None:
            return default_value

        try:
            baud_rate = int(user_input)
        except ValueError:
            print("Baud rate sayısal bir değer olmalıdır.")
            continue

        if baud_rate not in BITRATE_VALUES:
            print(
                f"Desteklenmeyen baud rate. "
                f"Geçerli değerler: {supported_rates} kbit/s"
            )
            continue

        return baud_rate


def read_confirmation():
    """
    Kullanıcıdan yapılandırma işlemi için onay alır.
    """

    while True:
        answer = input(
            "\nBu ayarlar encodera yazılsın mı? (E/H): "
        ).strip().lower()

        if answer in ("e", "evet", "y", "yes"):
            return True

        if answer in ("h", "hayır", "hayir", "n", "no"):
            return False

        print("Lütfen E veya H girin.")


def print_cob_ids(title, node_id):
    """
    Verilen Node ID için CANopen COB-ID değerlerini gösterir.
    """

    print(f"\n{title}")
    print(f"Node ID             : 0x{node_id:02X}")
    print(f"SDO Request COB-ID  : 0x{0x600 + node_id:03X}")
    print(f"SDO Response COB-ID : 0x{0x580 + node_id:03X}")
    print(f"Heartbeat COB-ID    : 0x{0x700 + node_id:03X}")


def print_configuration(settings, current_baud_rate):
    """
    Mevcut ve uygulanacak encoder ayarlarını gösterir.
    """

    print("\nUygulanacak encoder ayarları:")
    print(f"Mevcut Node ID          : 0x{settings.current_node_id:02X}")
    print(f"Yeni Node ID            : 0x{settings.new_node_id:02X}")
    print(f"Mevcut Baud Rate        : {current_baud_rate} kbit/s")
    print(f"Yeni Baud Rate          : {settings.baud_rate} kbit/s")
    print(f"Producer Heartbeat Time : {settings.heartbeat_time_ms} ms")
    print(f"Transmission Type       : {settings.transmission_type}")
    print(f"Event Time              : {settings.event_time_ms} ms")


def get_user_settings():
    """
    Encoder yapılandırma değerlerini kullanıcıdan alır.

    Heartbeat, transmission type ve event time görev gereği
    sabit değerlerdir. Node ID ve baud rate kullanıcıdan alınır.
    """

    print("\nEncoder yapılandırma ekranı")
    print("----------------------------")
    print("Node ID decimal veya hexadecimal girilebilir.")
    print("Örnek: 90, 0x5A veya 5A")
    print(
        "Bir alanı varsayılan değerde bırakmak için "
        "doğrudan Enter'a basabilirsiniz."
    )

    # Encoder'ın şu anki doğrulanmış değerleri.
    current_node_id = read_node_id(
        prompt="Mevcut Node ID",
        default_value=0x5A,
    )

    new_node_id = read_node_id(
        prompt="Yeni Node ID",
        default_value=current_node_id,
    )

    current_baud_rate = read_baud_rate(
        prompt="Mevcut baud rate (kbit/s)",
        default_value=500,
    )

    new_baud_rate = read_baud_rate(
        prompt="Yeni baud rate (kbit/s)",
        default_value=current_baud_rate,
    )

    settings = EncoderSettings(
        current_node_id=current_node_id,
        new_node_id=new_node_id,
        baud_rate=new_baud_rate,
        heartbeat_time_ms=100,
        transmission_type=255,
        event_time_ms=80,
    )

    return settings, current_baud_rate


def verify_new_connection(client, settings):
    """
    Reset sonrasında encoder'ın yeni Node ID ve baud rate ile
    çalıştığını SDO okumalarıyla doğrular.
    """

    print(
        "\nYeni bağlantı bilgileriyle SDO haberleşmesi "
        "kontrol ediliyor..."
    )

    device_type = client.read_object(
        index=ObjectDictionary.DEVICE_TYPE,
        subindex=0,
        timeout=5.0,
    )

    if device_type is None:
        print(
            "\nEncoder heartbeat gönderdi ancak "
            "SDO isteğine cevap vermedi."
        )
        return False

    print("\nSDO haberleşmesi doğrulandı.")
    print(f"Device Type: 0x{device_type.value:08X}")

    node_id_response = client.read_object(
        index=ObjectDictionary.NODE_ID,
        subindex=0,
        timeout=5.0,
    )

    if node_id_response is None:
        print("\nNode ID kaydı tekrar okunamadı.")
        return False

    if node_id_response.value != settings.new_node_id:
        print("\nNode ID doğrulaması başarısız.")
        print(
            f"Beklenen: 0x{settings.new_node_id:02X}"
        )
        print(
            f"Okunan  : 0x{node_id_response.value:02X}"
        )
        return False

    baud_rate_response = client.read_object(
        index=ObjectDictionary.BAUD_RATE,
        subindex=0,
        timeout=5.0,
    )

    if baud_rate_response is None:
        print("\nBaud rate kaydı tekrar okunamadı.")
        return False

    expected_baud_rate_code = (
        EncoderConfigurator.BAUD_RATE_CODES[
            settings.baud_rate
        ]
    )

    if baud_rate_response.value != expected_baud_rate_code:
        print("\nBaud rate doğrulaması başarısız.")
        print(f"Beklenen kod: {expected_baud_rate_code}")
        print(f"Okunan kod  : {baud_rate_response.value}")
        return False

    print(
        f"\nNode ID kalıcı olarak doğrulandı: "
        f"0x{settings.new_node_id:02X}"
    )

    print(
        f"Baud rate kalıcı olarak doğrulandı: "
        f"{settings.baud_rate} kbit/s "
        f"(kod: {baud_rate_response.value})"
    )

    return True


def main():
    can_bus = CanBus()

    try:
        settings, current_baud_rate = get_user_settings()

        print_cob_ids(
            title="Mevcut CANopen haberleşme bilgileri:",
            node_id=settings.current_node_id,
        )

        print_cob_ids(
            title="Reset sonrasında beklenen haberleşme bilgileri:",
            node_id=settings.new_node_id,
        )

        print_configuration(
            settings=settings,
            current_baud_rate=current_baud_rate,
        )

        if not read_confirmation():
            print("\nİşlem kullanıcı tarafından iptal edildi.")
            return

        # Encoder'a mevcut baud rate üzerinden bağlan.
        can_bus.connect(
            bitrate=BITRATE_VALUES[current_baud_rate]
        )

        client = CANopenClient(
            can_bus=can_bus,
            node_id=settings.current_node_id,
        )

        configurator = EncoderConfigurator(
            client=client
        )

        # Tüm ayarları yaz ve reset öncesinde geri okuyarak doğrula.
        configured = configurator.configure(
            settings=settings
        )

        if not configured:
            print("\nEncoder yapılandırılamadı.")
            return

        # Ayarları EEPROM'a kaydet.
        saved = configurator.save()

        if not saved:
            print("\nAyarlar kalıcı hafızaya kaydedilemedi.")
            return

        print("\nEncoder ayarları yazıldı ve kaydedildi.")

        time.sleep(1.0)

        # Reset komutu, encoder henüz eski Node ID ve baud rate
        # ile çalışırken gönderilir.
        print(
            "\nEncoder iletişim parametreleri "
            "yeniden başlatılıyor..."
        )

        client.reset_communication(
            node_id=settings.current_node_id
        )

        print(
            "\nNMT Reset Communication komutu "
            f"0x{settings.current_node_id:02X} Node ID'sine "
            "gönderildi."
        )

        # PCAN bağlantısını yeni baud rate ile yeniden aç.
        can_bus.reconnect(
            bitrate=BITRATE_VALUES[settings.baud_rate]
        )

        print(
            f"\nPCAN bağlantısı {settings.baud_rate} kbit/s "
            "ile yeniden açıldı."
        )

        # Encoder'ın yeni Node ID ve baud rate ile görünmesini bekle.
        state = client.wait_for_heartbeat(
            node_id=settings.new_node_id,
            timeout=8.0,
        )

        if state is None:
            print(
                "\nEncoder yeni bağlantı bilgileriyle bulunamadı."
            )
            print(
                f"Beklenen Node ID   : "
                f"0x{settings.new_node_id:02X}"
            )
            print(
                f"Beklenen baud rate : "
                f"{settings.baud_rate} kbit/s"
            )
            return

        print(
            "\nEncoder yeni bağlantı bilgileriyle "
            "CAN hattında görüldü."
        )

        # Bundan sonraki SDO isteklerinde yeni Node ID kullanılır.
        client.change_node_id(
            settings.new_node_id
        )

        if not verify_new_connection(
            client=client,
            settings=settings,
        ):
            return

        print("\nYapılandırma başarıyla tamamlandı.")

        print("\nSon encoder ayarları:")
        print(
            f"Node ID                 : "
            f"0x{settings.new_node_id:02X}"
        )
        print(
            f"Baud Rate               : "
            f"{settings.baud_rate} kbit/s"
        )
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

    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")

    except ValueError as error:
        print(f"\nGeçersiz değer: {error}")

    except Exception as error:
        print(f"\nHata: {error}")

    finally:
        can_bus.shutdown()


if __name__ == "__main__":
    main()