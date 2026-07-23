"""
Uygulamanın başlangıç noktasıdır.

Kullanıcıdan yeni Node ID ve baud rate değerlerini alır.
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
from encoder_state import load_encoder_state, save_encoder_state


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


def print_success(message):
    print(f"✓ {message}")


def print_error(message):
    print(f"✗ {message}")


def print_warning(message):
    print(f"⚠ {message}")


def parse_node_id(value):
    """
    Node ID değerini decimal veya hexadecimal olarak kabul eder.

    Örnek:
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

        elif any(
            character in "abcdefABCDEF"
            for character in cleaned_value
        ):
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

        user_input = input(
            f"{prompt}{default_text}: "
        ).strip()

        if not user_input and default_value is not None:
            return default_value

        try:
            return parse_node_id(user_input)

        except ValueError as error:
            print_error(str(error))


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

        user_input = input(
            f"{prompt}{default_text}: "
        ).strip()

        if not user_input and default_value is not None:
            return default_value

        try:
            baud_rate = int(user_input)

        except ValueError:
            print_error(
                "Baud rate sayısal bir değer olmalıdır."
            )
            continue

        if baud_rate not in BITRATE_VALUES:
            print_error(
                "Desteklenmeyen baud rate. "
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

        print_warning("Lütfen E veya H girin.")


def print_configuration(settings, current_baud_rate):
    """
    Mevcut ve yeni encoder ayarlarını gösterir.
    """

    print("\nYapılandırma özeti")
    print("------------------")
    print(
        f"Node ID    : "
        f"0x{settings.current_node_id:02X} "
        f"→ 0x{settings.new_node_id:02X}"
    )
    print(
        f"Baud Rate  : "
        f"{current_baud_rate} "
        f"→ {settings.baud_rate} kbit/s"
    )
    print(
        f"Heartbeat  : "
        f"{settings.heartbeat_time_ms} ms"
    )
    print(
        f"Transmission Type : "
        f"{settings.transmission_type}"
    )
    print(
        f"Event Time : "
        f"{settings.event_time_ms} ms"
    )


def get_user_settings():
    """
    Encoder yapılandırma değerlerini kullanıcıdan alır.
    """

    current_node_id, current_baud_rate = (
        load_encoder_state()
    )

    print("\nCANopen Encoder Yapılandırması")
    print("------------------------------")
    print(
        f"Mevcut Node ID   : "
        f"0x{current_node_id:02X}"
    )
    print(
        f"Mevcut Baud Rate : "
        f"{current_baud_rate} kbit/s"
    )
    print(
        "Node ID için 91, 0x5B veya 5B "
        "biçimi kullanılabilir."
    )
    print(
        "Varsayılan değeri kullanmak için "
        "Enter'a basın.\n"
    )

    new_node_id = read_node_id(
        prompt="Yeni Node ID",
        default_value=current_node_id,
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
    Reset sonrasında encoder'ın yeni bağlantı bilgileriyle
    çalıştığını doğrular.
    """

    device_type = client.read_object(
        index=ObjectDictionary.DEVICE_TYPE,
        subindex=0,
        timeout=5.0,
    )

    if device_type is None:
        print_error(
            "Encoder heartbeat gönderdi ancak "
            "SDO isteğine cevap vermedi."
        )
        return False

    node_id_response = client.read_object(
        index=ObjectDictionary.NODE_ID,
        subindex=0,
        timeout=5.0,
    )

    if node_id_response is None:
        print_error(
            "Node ID kaydı tekrar okunamadı."
        )
        return False

    if node_id_response.value != settings.new_node_id:
        print_error(
            "Node ID doğrulaması başarısız. "
            f"Beklenen: 0x{settings.new_node_id:02X}, "
            f"okunan: 0x{node_id_response.value:02X}"
        )
        return False

    baud_rate_response = client.read_object(
        index=ObjectDictionary.BAUD_RATE,
        subindex=0,
        timeout=5.0,
    )

    if baud_rate_response is None:
        print_error(
            "Baud rate kaydı tekrar okunamadı."
        )
        return False

    expected_baud_rate_code = (
        EncoderConfigurator.BAUD_RATE_CODES[
            settings.baud_rate
        ]
    )

    if baud_rate_response.value != expected_baud_rate_code:
        print_error(
            "Baud rate doğrulaması başarısız. "
            f"Beklenen kod: {expected_baud_rate_code}, "
            f"okunan kod: {baud_rate_response.value}"
        )
        return False

    return True


def main():
    can_bus = CanBus()

    try:
        settings, current_baud_rate = (
            get_user_settings()
        )

        print_configuration(
            settings=settings,
            current_baud_rate=current_baud_rate,
        )

        if not read_confirmation():
            print_warning(
                "İşlem kullanıcı tarafından iptal edildi."
            )
            return

        print("\nYapılandırma başlatılıyor...\n")

        can_bus.connect(
            bitrate=BITRATE_VALUES[
                current_baud_rate
            ]
        )

        client = CANopenClient(
            can_bus=can_bus,
            node_id=settings.current_node_id,
        )

        configurator = EncoderConfigurator(
            client=client
        )

        configured = configurator.configure(
            settings=settings
        )

        if not configured:
            print_error(
                "Encoder yapılandırılamadı."
            )
            return

        saved = configurator.save()

        if not saved:
            print_error(
                "Ayarlar kalıcı hafızaya "
                "kaydedilemedi."
            )
            return

        print_success(
            "Ayarlar EEPROM'a kaydedildi."
        )

        time.sleep(1.0)

        client.reset_communication(
            node_id=settings.current_node_id
        )

        print_success(
            "Reset Communication gönderildi."
        )

        can_bus.reconnect(
            bitrate=BITRATE_VALUES[
                settings.baud_rate
            ]
        )

        print_success(
            f"CAN bağlantısı "
            f"{settings.baud_rate} kbit/s "
            f"ile yeniden açıldı."
        )

        state = client.wait_for_heartbeat(
            node_id=settings.new_node_id,
            timeout=8.0,
        )

        if state is None:
            print_error(
                "Encoder yeni bağlantı "
                "bilgileriyle bulunamadı."
            )
            print(
                f"  Beklenen Node ID   : "
                f"0x{settings.new_node_id:02X}"
            )
            print(
                f"  Beklenen baud rate : "
                f"{settings.baud_rate} kbit/s"
            )
            return

        print_success(
            "Heartbeat doğrulandı."
        )

        client.change_node_id(
            settings.new_node_id
        )

        if not verify_new_connection(
            client=client,
            settings=settings,
        ):
            return

        print_success(
            "SDO haberleşmesi doğrulandı."
        )

        save_encoder_state(
            settings.new_node_id,
            settings.baud_rate
        )

        print_success(
            "Son encoder durumu kaydedildi."
        )

        print("\n--------------------------------")
        print("Encoder başarıyla yapılandırıldı")
        print("--------------------------------")

        print(
            f"Node ID   : "
            f"0x{settings.new_node_id:02X}"
        )
        print(
            f"Baud Rate : "
            f"{settings.baud_rate} kbit/s"
        )

    except KeyboardInterrupt:
        print_warning(
            "Program kullanıcı tarafından durduruldu."
        )

    except ValueError as error:
        print_error(
            f"Geçersiz değer: {error}"
        )

    except Exception as error:
        print_error(
            f"Beklenmeyen hata: {error}"
        )

    finally:
        can_bus.shutdown()


if __name__ == "__main__":
    main()