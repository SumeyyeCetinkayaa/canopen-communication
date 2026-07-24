"""
CAN bağlantısını ve CANopen encoder işlemlerini yönetir.

Bu dosyada GUI elemanları kullanılmaz.
"""

import time

from bus.can_bus import CanBus
from canopen.client import CANopenClient
from canopen.encoder_configurator import EncoderConfigurator
from canopen.encoder_reader import EncoderReader
from canopen.node_scanner import NodeScanner
from canopen.object_dictionary import ObjectDictionary
from encoder_state import save_encoder_state


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


class EncoderController:
    def __init__(self, log_callback=None):
        self.can_bus = CanBus()
        self.client = None

        self.current_node_id = None
        self.current_baud_rate = None

        self.is_connected = False
        self.log_callback = log_callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def connect(self, baud_rate):
        """
        Verilen kbit/s değeriyle CAN bağlantısını açar.
        """

        if baud_rate not in BITRATE_VALUES:
            raise ValueError(
                f"Desteklenmeyen baud rate: "
                f"{baud_rate} kbit/s"
            )

        self.can_bus.connect(
            bitrate=BITRATE_VALUES[baud_rate]
        )

        self.current_baud_rate = baud_rate
        self.is_connected = True

        self.log(
            f"✓ CAN bağlantısı kuruldu: "
            f"{baud_rate} kbit/s"
        )

    def disconnect(self):
        """
        CAN bağlantısını kapatır.
        """

        self.can_bus.shutdown()

        self.is_connected = False
        self.current_baud_rate = None

        self.clear_encoder()

        self.log("CAN bağlantısı kapatıldı.")

    def clear_encoder(self):
        """
        Taranmış encoder bilgilerini temizler.
        """

        self.client = None
        self.current_node_id = None

    def scan_network(
        self,
        start_node_id=1,
        end_node_id=127,
        timeout=0.05,
    ):
        """
        CANopen ağını tarar ve ilk bulunan encoder'ın
        bilgilerini okur.

        Başarılı olursa:
            node_id, information

        Cihaz bulunamazsa:
            None
        """

        if not self.is_connected:
            raise RuntimeError(
                "Önce CAN bağlantısını açmalısınız."
            )

        self.log("CANopen ağı taranıyor...")

        scanner = NodeScanner(
            can_bus=self.can_bus
        )

        found_nodes = scanner.scan(
            start_node_id=start_node_id,
            end_node_id=end_node_id,
            timeout=timeout,
        )

        if not found_nodes:
            self.clear_encoder()

            self.log(
                "✗ CANopen ağında aktif cihaz bulunamadı."
            )

            return None

        found_node = found_nodes[0]

        self.current_node_id = found_node.node_id

        self.client = CANopenClient(
            can_bus=self.can_bus,
            node_id=self.current_node_id,
        )

        self.log(
            f"✓ Encoder bulundu. "
            f"Node ID: 0x{self.current_node_id:02X} "
            f"({self.current_node_id})"
        )

        self.log(
            "Encoder kimlik ve pozisyon bilgileri "
            "okunuyor..."
        )

        reader = EncoderReader(
            client=self.client
        )

        information = reader.read_all(
            timeout=3.0
        )

        self.log("✓ Encoder bilgileri okundu.")

        return self.current_node_id, information

    def read_position(self):
        """
        Encoder'ın anlık Position Value değerini okur.

        Encoder taranmamışsa None döndürür.
        """

        if (
            not self.is_connected
            or self.client is None
            or self.current_node_id is None
        ):
            return None

        reader = EncoderReader(
            client=self.client
        )

        return reader.read_position(
            timeout=0.15
        )

    def configure(self, settings):
        """
        Encoder ayarlarını yazar, EEPROM'a kaydeder ve
        yeni Node ID ile baud rate değerlerini doğrular.

        Başarılı olursa:
            yeni_node_id, yeni_baud_rate
        """

        if (
            self.client is None
            or self.current_node_id is None
        ):
            raise RuntimeError(
                "Önce CANopen ağını taramalısınız."
            )

        if settings.baud_rate not in BITRATE_VALUES:
            raise ValueError(
                f"Desteklenmeyen baud rate: "
                f"{settings.baud_rate} kbit/s"
            )

        self.log("Yapılandırma başlatılıyor...")

        self.client.change_node_id(
            settings.current_node_id
        )

        configurator = EncoderConfigurator(
            client=self.client
        )

        if not configurator.configure(
            settings=settings
        ):
            raise RuntimeError(
                "Encoder ayarları yazılamadı."
            )

        self.log("✓ Encoder ayarları yazıldı.")

        if not configurator.save():
            raise RuntimeError(
                "Ayarlar EEPROM'a kaydedilemedi."
            )

        self.log(
            "✓ Ayarlar EEPROM'a kaydedildi."
        )

        time.sleep(1.0)

        self.client.reset_communication(
            node_id=settings.current_node_id
        )

        self.log(
            "✓ Reset Communication gönderildi."
        )

        self.can_bus.reconnect(
            bitrate=BITRATE_VALUES[
                settings.baud_rate
            ]
        )

        self.current_baud_rate = (
            settings.baud_rate
        )

        self.log(
            f"✓ CAN bağlantısı "
            f"{settings.baud_rate} kbit/s ile "
            f"yeniden açıldı."
        )

        state = self.client.wait_for_heartbeat(
            node_id=settings.new_node_id,
            timeout=8.0,
        )

        if state is None:
            raise RuntimeError(
                "Encoder yeni Node ID ve baud rate "
                "ile bulunamadı."
            )

        self.log("✓ Heartbeat doğrulandı.")

        self.client.change_node_id(
            settings.new_node_id
        )

        if not self.verify_new_connection(
            settings
        ):
            raise RuntimeError(
                "Yeni bağlantı bilgileri "
                "doğrulanamadı."
            )

        self.log(
            "✓ SDO haberleşmesi doğrulandı."
        )

        save_encoder_state(
            settings.new_node_id,
            settings.baud_rate,
        )

        self.current_node_id = (
            settings.new_node_id
        )

        self.log(
            "✓ Son encoder durumu kaydedildi."
        )

        self.log(
            f"✓ Encoder başarıyla yapılandırıldı. "
            f"Node ID: 0x{settings.new_node_id:02X}, "
            f"Baud Rate: "
            f"{settings.baud_rate} kbit/s"
        )

        return (
            settings.new_node_id,
            settings.baud_rate,
        )

    def verify_new_connection(self, settings):
        """
        Yeni Node ID, baud rate ve preset value
        değerlerini SDO ile doğrular.
        """

        device_type = self.client.read_object(
            index=ObjectDictionary.DEVICE_TYPE,
            subindex=0,
            timeout=5.0,
        )

        if device_type is None:
            self.log(
                "✗ Encoder SDO isteğine cevap vermedi."
            )

            return False

        node_id_response = self.client.read_object(
            index=ObjectDictionary.NODE_ID,
            subindex=0,
            timeout=5.0,
        )

        if node_id_response is None:
            self.log(
                "✗ Node ID kaydı okunamadı."
            )

            return False

        if (
            node_id_response.value
            != settings.new_node_id
        ):
            self.log(
                "✗ Node ID doğrulaması başarısız. "
                f"Beklenen: "
                f"0x{settings.new_node_id:02X}, "
                f"okunan: "
                f"0x{node_id_response.value:02X}"
            )

            return False

        baud_rate_response = (
            self.client.read_object(
                index=ObjectDictionary.BAUD_RATE,
                subindex=0,
                timeout=5.0,
            )
        )

        if baud_rate_response is None:
            self.log(
                "✗ Baud rate kaydı okunamadı."
            )

            return False

        expected_code = (
            EncoderConfigurator
            .BAUD_RATE_CODES[
                settings.baud_rate
            ]
        )

        if (
            baud_rate_response.value
            != expected_code
        ):
            self.log(
                "✗ Baud rate doğrulaması başarısız. "
                f"Beklenen kod: {expected_code}, "
                f"okunan kod: "
                f"{baud_rate_response.value}"
            )

            return False

        preset_response = self.client.read_object(
            index=ObjectDictionary.PRESET_VALUE,
            subindex=0,
            timeout=5.0,
        )

        if preset_response is None:
            self.log(
                "✗ Preset Value kaydı okunamadı."
            )

            return False

        if (
            preset_response.value
            != settings.preset_value
        ):
            self.log(
                "✗ Preset Value doğrulaması başarısız. "
                f"Beklenen: "
                f"{settings.preset_value}, "
                f"okunan: "
                f"{preset_response.value}"
            )

            return False

        self.log(
            f"✓ Preset Value doğrulandı: "
            f"{preset_response.value}"
        )

        return True

    def restore_default_parameters(self):
        """
        Encoder fabrika ayarlarını geri yükler.

        Başarılı olursa restore öncesindeki:
            node_id, baud_rate

        değerlerini döndürür.
        """

        if (
            self.client is None
            or self.current_node_id is None
        ):
            raise RuntimeError(
                "Önce CANopen ağını taramalısınız."
            )

        old_node_id = self.current_node_id
        old_baud_rate = self.current_baud_rate

        self.log(
            "Fabrika ayarlarına geri yükleme "
            "başlatılıyor..."
        )

        configurator = EncoderConfigurator(
            client=self.client
        )

        if not (
            configurator
            .restore_default_parameters()
        ):
            raise RuntimeError(
                "Encoder restore komutunu "
                "kabul etmedi."
            )

        self.log(
            "✓ Restore Parameters komutu "
            "kabul edildi."
        )

        self.log(
            "✓ 0x1011:01 nesnesine restore "
            "imzası yazıldı."
        )

        time.sleep(1.0)

        self.client.reset_communication(
            node_id=old_node_id
        )

        self.log(
            "✓ NMT Reset Communication gönderildi."
        )

        time.sleep(2.0)

        self.clear_encoder()

        self.log(
            "✓ Restore işlemi tamamlandı."
        )

        self.log(
            "⚠ Encoder'ın Node ID veya baud rate "
            "değeri değişmiş olabilir."
        )

        self.log(
            "⚠ Gerekirse encoder'ın enerjisini "
            "kapatıp yeniden açın."
        )

        return old_node_id, old_baud_rate

    def shutdown(self):
        """
        Uygulama kapanırken CAN bağlantısını kapatır.
        """

        self.can_bus.shutdown()

        self.is_connected = False
        self.current_baud_rate = None

        self.clear_encoder()