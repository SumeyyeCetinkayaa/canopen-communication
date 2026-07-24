"""
Uygulamanın başlangıç noktasıdır.

CANopen ağındaki encoder'ı tarar.

Kullanıcı isterse encoder parametrelerini yapılandırır ve kaydeder,
isterse Restore Parameters komutuyla fabrika ayarlarını geri yükler.
"""

import time

from bus.can_bus import CanBus
from canopen.client import CANopenClient
from canopen.encoder_reader import EncoderReader
from canopen.encoder_configurator import (
    EncoderConfigurator,
    EncoderSettings,
)
from canopen.object_dictionary import ObjectDictionary
from canopen.node_scanner import NodeScanner
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
    Node ID değerini decimal veya 0x önekli hexadecimal olarak kabul eder.

    Kurallar:
        40   -> decimal 40
        0x28 -> hexadecimal 40

    Öneksiz girilen tüm değerler decimal kabul edilir.
    """

    cleaned_value = value.strip()

    if not cleaned_value:
        raise ValueError("Node ID boş bırakılamaz.")

    try:
        if cleaned_value.lower().startswith("0x"):
            node_id = int(cleaned_value, 16)
        else:
            node_id = int(cleaned_value, 10)

    except ValueError as error:
        raise ValueError(
            "Node ID decimal veya 0x önekli hexadecimal olmalıdır. "
            "Örnek: 40 veya 0x28."
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


def read_operation():
    """
    Kullanıcının yapmak istediği işlemi seçmesini sağlar.
    """

    print("\nYapılacak işlem")
    print("----------------")
    print("1 - Encoder'ı yapılandır")
    print("2 - Fabrika ayarlarını geri yükle")
    print("0 - Çıkış")

    while True:
        choice = input("\nSeçiminiz: ").strip()

        if choice in ("0", "1", "2"):
            return choice

        print_warning(
            "Lütfen 0, 1 veya 2 girin."
        )


def read_configuration_confirmation():
    """
    Yapılandırma işlemi için kullanıcıdan onay alır.
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


def read_restore_confirmation():
    """
    Fabrika ayarlarını geri yükleme işlemi için onay alır.
    """

    print("\nDİKKAT")
    print("------")
    print(
        "Bu işlem encoder parametrelerini "
        "fabrika varsayılanlarına döndürecektir."
    )
    print(
        "Node ID ve baud rate değerleri de değişebilir."
    )

    while True:
        answer = input(
            "\nFabrika ayarları geri yüklensin mi? (E/H): "
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


def get_user_settings(current_node_id, current_baud_rate):
    """
    Encoder yapılandırma değerlerini kullanıcıdan alır.
    """

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
        "Node ID decimal veya 0x önekli hexadecimal girilebilir."
    )
    print(
        "Örnek: 40 (decimal) veya 0x28 (hexadecimal)."
    )
    print(
        "Sadece sayı girilirse decimal kabul edilir."
    )
    print(
        "Varsayılan değeri kullanmak için "
        "Enter'a basın.\n"
    )

    new_node_id = read_node_id(
        prompt="Yeni Node ID (decimal veya 0x ile hexadecimal)",
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


def select_scanned_node(found_nodes):
    """
    Tarama sonucunda bulunan node'lardan kullanılacak olanı seçer.
    """

    if len(found_nodes) == 1:
        return found_nodes[0].node_id

    valid_node_ids = {
        node.node_id
        for node in found_nodes
    }

    print("\nBirden fazla CANopen node bulundu.")

    while True:
        selected_node_id = read_node_id(
            "Kullanılacak Node ID "
            "(decimal veya 0x ile hexadecimal)"
        )

        if selected_node_id in valid_node_ids:
            return selected_node_id

        print_error(
            "Seçilen Node ID tarama sonucunda bulunmadı."
        )


def format_hex(value, width=8):
    """
    Okunamayan değerler için '-' gösterir.
    """

    if value is None:
        return "-"

    return f"0x{value:0{width}X}"


def print_encoder_information(client):
    """
    Encoder Identity Object ve anlık pozisyon bilgisini gösterir.
    """

    reader = EncoderReader(
        client=client
    )

    information = reader.read_all(
        timeout=3.0
    )

    print("\nEncoder bilgileri")
    print("------------------")
    print(
        f"Vendor ID       : "
        f"{format_hex(information.vendor_id)}"
    )
    print(
        f"Product Code    : "
        f"{format_hex(information.product_code)}"
    )
    print(
        f"Revision Number : "
        f"{format_hex(information.revision_number)}"
    )
    print(
        f"Serial Number   : "
        f"{format_hex(information.serial_number)}"
    )

    if information.position is None:
        print("Position Value  : Okunamadı")
    else:
        print(
            f"Position Value  : "
            f"{information.position}"
        )


def configure_encoder(
    can_bus,
    client,
    current_node_id,
    current_baud_rate,
):
    """
    Encoder yapılandırma işlemini gerçekleştirir.
    """

    settings, current_baud_rate = get_user_settings(
        current_node_id=current_node_id,
        current_baud_rate=current_baud_rate,
    )

    print_configuration(
        settings=settings,
        current_baud_rate=current_baud_rate,
    )

    if not read_configuration_confirmation():
        print_warning(
            "İşlem kullanıcı tarafından iptal edildi."
        )
        return

    print("\nYapılandırma başlatılıyor...\n")

    client.change_node_id(
        settings.current_node_id
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
            "Ayarlar kalıcı hafızaya kaydedilemedi."
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
            "Encoder yeni bağlantı bilgileriyle bulunamadı."
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


def restore_encoder(client, current_node_id):
    """
    Encoder'a Restore Default Parameters komutunu gönderir.
    """

    if not read_restore_confirmation():
        print_warning(
            "Restore işlemi kullanıcı tarafından iptal edildi."
        )
        return

    print("\nFabrika ayarları geri yükleniyor...\n")

    client.change_node_id(
        current_node_id
    )

    configurator = EncoderConfigurator(
        client=client
    )

    restored = configurator.restore_default_parameters()

    if not restored:
        print_error(
            "Restore Parameters komutu başarısız oldu."
        )
        return

    print_success(
        "Restore Parameters komutu encoder tarafından kabul edildi."
    )

    time.sleep(1.0)

    client.reset_communication(
        node_id=current_node_id
    )

    print_success(
        "Reset Communication gönderildi."
    )

    print("\n-----------------------------------------")
    print("Fabrika ayarlarını geri yükleme başlatıldı")
    print("-----------------------------------------")

    print(
        "Restore edilen değerlerin tamamen etkinleşmesi için "
        "encoder'ın enerjisini kapatıp tekrar açın."
    )

    print(
        "Restore sonrasında Node ID ve baud rate fabrika "
        "varsayılanlarına dönmüş olabilir."
    )

    print(
        "Bu nedenle cihaz mevcut baud rate ile bulunamazsa "
        "desteklenen baud rate değerlerinde yeniden taranmalıdır."
    )


def main():
    can_bus = CanBus()

    try:
        _, current_baud_rate = load_encoder_state()

        can_bus.connect(
            bitrate=BITRATE_VALUES[
                current_baud_rate
            ]
        )

        scanner = NodeScanner(
            can_bus=can_bus
        )

        found_nodes = scanner.scan(
            start_node_id=1,
            end_node_id=127,
            timeout=0.05,
        )

        if not found_nodes:
            print_error(
                "İşlem başlatılamadı. "
                "Önce encoder bağlantısını ve baud rate değerini kontrol edin."
            )
            return

        current_node_id = select_scanned_node(
            found_nodes
        )

        client = CANopenClient(
            can_bus=can_bus,
            node_id=current_node_id,
        )

        print_encoder_information(
            client=client
        )

        operation = read_operation()

        if operation == "0":
            print_warning(
                "Program kapatıldı."
            )
            return

        if operation == "1":
            configure_encoder(
                can_bus=can_bus,
                client=client,
                current_node_id=current_node_id,
                current_baud_rate=current_baud_rate,
            )

        elif operation == "2":
            restore_encoder(
                client=client,
                current_node_id=current_node_id,
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