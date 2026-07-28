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
from encoder_state import (
    remove_encoder_state,
    save_encoder_state,
)


BITRATE_SCAN_ORDER = (
    250,
    125,
    500,
    100,
    50,
    20,
    10,
    800,
    1000,
)


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
        self.detected_nodes = []

        self.is_connected = False
        self.log_callback = log_callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def connect(self, baud_rate):
        if baud_rate not in BITRATE_VALUES:
            raise ValueError(
                f"Desteklenmeyen baud rate: {baud_rate} kbit/s"
            )

        self.can_bus.connect(
            bitrate=BITRATE_VALUES[baud_rate]
        )

        self.current_baud_rate = baud_rate
        self.is_connected = True

        self.log(
            f"✓ CAN bağlantısı kuruldu: {baud_rate} kbit/s"
        )

    def disconnect(self):
        self.can_bus.shutdown()

        self.is_connected = False
        self.current_baud_rate = None

        self.clear_encoder()

        self.log("CAN bağlantısı kapatıldı.")

    def clear_encoder(self):
        self.client = None
        self.current_node_id = None
        self.detected_nodes = []

    def clear_selected_encoder(self):
        self.client = None
        self.current_node_id = None

    def scan_network(
        self,
        start_node_id=1,
        end_node_id=127,
        timeout=0.05,
    ):
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
            return []

        self.detected_nodes = sorted(
            found_node.node_id
            for found_node in found_nodes
        )

        self.clear_selected_encoder()

        self.log(
            f"✓ Toplam {len(self.detected_nodes)} encoder bulundu."
        )

        return self.detected_nodes.copy()

    def _reconnect_for_scan(self, baud_rate):
        """
        Tarama sırasında CAN bağlantısını verilen baud rate ile açar.
        """

        if self.current_baud_rate == baud_rate:
            self.log(
                f"Mevcut bağlantı {baud_rate} kbit/s ile "
                "kullanılıyor..."
            )
            return

        self.log(
            f"Bağlantı {baud_rate} kbit/s ile deneniyor..."
        )

        self.can_bus.reconnect(
            bitrate=BITRATE_VALUES[baud_rate]
        )

        self.current_baud_rate = baud_rate

    def _probe_node(self, node_id, timeout):
        """
        Belirtilen Node ID'ye kısa bir Device Type isteği gönderir.
        """

        client = CANopenClient(
            can_bus=self.can_bus,
            node_id=node_id,
        )

        response = client.read_object(
            index=ObjectDictionary.DEVICE_TYPE,
            subindex=0,
            timeout=timeout,
            silent=True,
        )

        return response is not None

    def _get_discovery_baud_order(self, saved_states):
        """
        Tarama sırasını oluşturur.

        Öncelik:
        1. Mevcut bağlantı baud rate'i
        2. JSON içindeki kayıtlı baud rate'ler
        3. Genel baud rate tarama sırası
        """

        baud_order = []

        def add_baud_rate(baud_rate):
            if (
                baud_rate in BITRATE_VALUES
                and baud_rate not in baud_order
            ):
                baud_order.append(baud_rate)

        add_baud_rate(self.current_baud_rate)

        for state in saved_states.values():
            try:
                add_baud_rate(
                    int(state["baud_rate"])
                )
            except (
                TypeError,
                ValueError,
                KeyError,
            ):
                continue

        for baud_rate in BITRATE_SCAN_ORDER:
            add_baud_rate(baud_rate)

        return baud_order

    def _get_saved_encoders_by_baud(self, saved_states):
        """
        JSON kayıtlarını baud rate değerlerine göre gruplar.

        Dönüş biçimi:

        {
            250: [36, 91],
            125: [40]
        }
        """

        grouped_encoders = {}

        for node_id_text, state in saved_states.items():
            try:
                node_id = int(node_id_text)
                baud_rate = int(state["baud_rate"])
            except (
                TypeError,
                ValueError,
                KeyError,
            ):
                continue

            if not 1 <= node_id <= 127:
                continue

            if baud_rate not in BITRATE_VALUES:
                continue

            grouped_encoders.setdefault(
                baud_rate,
                []
            ).append(node_id)

        for baud_rate in grouped_encoders:
            grouped_encoders[baud_rate] = sorted(
                set(grouped_encoders[baud_rate])
            )

        return grouped_encoders

    def _scan_current_baud(
        self,
        timeout,
        deadline,
    ):
        """
        Mevcut baud rate üzerinde Node ID 1-127 taraması yapar.

        Toplam tarama süresi deadline değerini aşarsa işlem
        kontrollü biçimde durdurulur.
        """

        found_node_ids = []

        for node_id in range(1, 128):
            if time.monotonic() >= deadline:
                self.log(
                    "⚠ Maksimum otomatik tarama süresine ulaşıldı."
                )
                break

            if self._probe_node(
                node_id=node_id,
                timeout=timeout,
            ):
                found_node_ids.append(node_id)

                self.log(
                    f"✓ Node bulundu: "
                    f"0x{node_id:02X} ({node_id})"
                )

        return found_node_ids

    def _accept_discovery_result(
        self,
        baud_rate,
        node_ids,
    ):
        """
        Bulunan encoderları controller ve JSON ile eşitler.
        """

        self.current_baud_rate = baud_rate
        self.detected_nodes = sorted(
            set(node_ids)
        )

        self.clear_selected_encoder()

        for node_id in self.detected_nodes:
            save_encoder_state(
                node_id=node_id,
                baud_rate=baud_rate,
            )

        self.log(
            f"✓ {len(self.detected_nodes)} encoder "
            f"{baud_rate} kbit/s üzerinde bulundu."
        )
        self.log(
            "✓ Bulunan encoder bilgileri JSON ile eşitlendi."
        )

        return (
            baud_rate,
            self.detected_nodes.copy(),
        )

    def discover_encoders(
        self,
        probe_timeout=None,
        scan_timeout=0.05,
        max_scan_seconds=10.0,
    ):
        """
        Yalnızca mevcut bağlantı baud rate'i üzerinde
        Node ID 1-127 aralığını tarar.

        JSON kayıtları kullanılmaz.
        Diğer baud rate değerlerine otomatik geçilmez.

        probe_timeout parametresi, eski çağrılarla uyumluluk
        sağlamak için kabul edilir ancak kullanılmaz.
        """

        if not self.is_connected:
            raise RuntimeError(
                "Önce CAN bağlantısını açmalısınız."
            )

        if self.current_baud_rate is None:
            raise RuntimeError(
                "Geçerli baud rate bilgisi bulunamadı."
            )

        baud_rate = self.current_baud_rate
        deadline = (
            time.monotonic()
            + max_scan_seconds
        )

        found_node_ids = []

        self.log(
            f"Encoder araması başlatılıyor: "
            f"{baud_rate} kbit/s"
        )

        self.log(
            "Node ID 1-127 taranıyor..."
        )

        for node_id in range(1, 128):
            if time.monotonic() >= deadline:
                self.log(
                    "⚠ Maksimum tarama süresine ulaşıldı."
                )
                break

            if self._probe_node(
                node_id=node_id,
                timeout=scan_timeout,
            ):
                found_node_ids.append(node_id)

                self.log(
                    f"✓ Encoder bulundu: "
                    f"0x{node_id:02X} ({node_id})"
                )

        if found_node_ids:
            self.current_baud_rate = baud_rate
            self.detected_nodes = sorted(
                set(found_node_ids)
            )

            self.clear_selected_encoder()

            self.log(
                f"✓ Toplam {len(self.detected_nodes)} "
                "encoder bulundu."
            )

            return (
                baud_rate,
                self.detected_nodes.copy(),
            )

        self.clear_encoder()

        self.log(
            f"✗ {baud_rate} kbit/s üzerinde "
            "aktif encoder bulunamadı."
        )

        return None, []

    def _create_client(self, node_id):
        return CANopenClient(
            can_bus=self.can_bus,
            node_id=node_id,
        )

    def read_encoder_information(self, node_id):
        """
        Belirtilen encoderın kimlik, pozisyon ve preset
        bilgilerini okur. Aktif encoder seçimini değiştirmez.
        """

        if not self.is_connected:
            raise RuntimeError(
                "Önce CAN bağlantısını açmalısınız."
            )

        if node_id not in self.detected_nodes:
            raise ValueError(
                f"Node ID {node_id} taranan encoderlar arasında yok."
            )

        client = self._create_client(node_id)
        reader = EncoderReader(client=client)

        return reader.read_all(timeout=3.0)

    def select_encoder(self, node_id):
        if not self.is_connected:
            raise RuntimeError(
                "Önce CAN bağlantısını açmalısınız."
            )

        if node_id not in self.detected_nodes:
            raise ValueError(
                f"Node ID {node_id}, taramada bulunan "
                "encoderlar arasında yer almıyor."
            )

        self.current_node_id = node_id
        self.client = self._create_client(node_id)

        self.log(
            f"✓ Encoder seçildi. "
            f"Node ID: 0x{node_id:02X} ({node_id})"
        )

        information = self.read_encoder_information(node_id)

        self.log("✓ Encoder bilgileri okundu.")

        return information

    def read_position(self):
        if (
            not self.is_connected
            or self.client is None
            or self.current_node_id is None
        ):
            return None

        reader = EncoderReader(
            client=self.client
        )

        return reader.read_position(timeout=0.15)

    def read_position_for_node(self, node_id):
        """
        Belirtilen encoderın pozisyonunu, aktif encoder
        seçimini değiştirmeden okur.
        """

        if (
            not self.is_connected
            or node_id not in self.detected_nodes
        ):
            return None

        client = self._create_client(node_id)
        reader = EncoderReader(client=client)

        return reader.read_position(timeout=0.15)

    def configure(self, settings):
        if (
            self.client is None
            or self.current_node_id is None
        ):
            raise RuntimeError(
                "Önce CANopen ağını tarayıp "
                "bir encoder seçmelisiniz."
            )

        if settings.baud_rate not in BITRATE_VALUES:
            raise ValueError(
                f"Desteklenmeyen baud rate: "
                f"{settings.baud_rate} kbit/s"
            )

        if (
            settings.new_node_id
            != settings.current_node_id
            and settings.new_node_id
            in self.detected_nodes
        ):
            raise ValueError(
                f"Node ID {settings.new_node_id} "
                "başka bir encoder tarafından kullanılıyor."
            )

        self.log(
            f"Node 0x{settings.current_node_id:02X} "
            "için yapılandırma başlatılıyor..."
        )

        self.client.change_node_id(
            settings.current_node_id
        )

        configurator = EncoderConfigurator(
            client=self.client
        )

        if not configurator.configure(settings=settings):
            raise RuntimeError(
                "Encoder ayarları yazılamadı."
            )

        self.log("✓ Encoder ayarları yazıldı.")

        if not configurator.save():
            raise RuntimeError(
                "Ayarlar EEPROM'a kaydedilemedi."
            )

        self.log("✓ Ayarlar EEPROM'a kaydedildi.")

        # Yeni bilgiler EEPROM'a yazıldığı için, reset veya doğrulama
        # sırasında hata oluşsa bile cihazın son bilinen bilgileri korunur.
        save_encoder_state(
            node_id=settings.new_node_id,
            baud_rate=settings.baud_rate,
            old_node_id=settings.current_node_id,
        )

        self.log(
            "✓ Yeni Node ID ve baud rate bilgileri "
            "hemen JSON dosyasına kaydedildi."
        )

        time.sleep(1.0)

        self.client.reset_communication(
            node_id=settings.current_node_id
        )

        self.log("✓ Reset Communication gönderildi.")

        self.can_bus.reconnect(
            bitrate=BITRATE_VALUES[settings.baud_rate]
        )

        self.current_baud_rate = settings.baud_rate

        self.log(
            f"✓ CAN bağlantısı {settings.baud_rate} kbit/s "
            "ile yeniden açıldı."
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

        if not self.verify_new_connection(settings):
            raise RuntimeError(
                "Yeni bağlantı bilgileri doğrulanamadı."
            )

        self.log("✓ SDO haberleşmesi doğrulandı.")

        old_node_id = self.current_node_id
        self.current_node_id = settings.new_node_id

        if old_node_id in self.detected_nodes:
            index = self.detected_nodes.index(old_node_id)
            self.detected_nodes[index] = settings.new_node_id

        self.detected_nodes = sorted(
            set(self.detected_nodes)
        )

        self.log("✓ Son encoder durumu kaydedildi.")

        self.log(
            f"✓ Encoder başarıyla yapılandırıldı. "
            f"Node ID: 0x{settings.new_node_id:02X}, "
            f"Baud Rate: {settings.baud_rate} kbit/s"
        )

        return settings.new_node_id, settings.baud_rate

    def verify_new_connection(self, settings):
        device_type = self.client.read_object(
            index=ObjectDictionary.DEVICE_TYPE,
            subindex=0,
            timeout=5.0,
        )

        if device_type is None:
            self.log("✗ Encoder SDO isteğine cevap vermedi.")
            return False

        node_id_response = self.client.read_object(
            index=ObjectDictionary.NODE_ID,
            subindex=0,
            timeout=5.0,
        )

        if node_id_response is None:
            self.log("✗ Node ID kaydı okunamadı.")
            return False

        if node_id_response.value != settings.new_node_id:
            self.log(
                "✗ Node ID doğrulaması başarısız. "
                f"Beklenen: 0x{settings.new_node_id:02X}, "
                f"okunan: 0x{node_id_response.value:02X}"
            )
            return False

        baud_rate_response = self.client.read_object(
            index=ObjectDictionary.BAUD_RATE,
            subindex=0,
            timeout=5.0,
        )

        if baud_rate_response is None:
            self.log("✗ Baud rate kaydı okunamadı.")
            return False

        expected_code = (
            EncoderConfigurator.BAUD_RATE_CODES[
                settings.baud_rate
            ]
        )

        if baud_rate_response.value != expected_code:
            self.log(
                "✗ Baud rate doğrulaması başarısız. "
                f"Beklenen kod: {expected_code}, "
                f"okunan kod: {baud_rate_response.value}"
            )
            return False

        preset_response = self.client.read_object(
            index=ObjectDictionary.PRESET_VALUE,
            subindex=0,
            timeout=5.0,
        )

        if preset_response is None:
            self.log("✗ Preset Value kaydı okunamadı.")
            return False

        if preset_response.value != settings.preset_value:
            self.log(
                "✗ Preset Value doğrulaması başarısız. "
                f"Beklenen: {settings.preset_value}, "
                f"okunan: {preset_response.value}"
            )
            return False

        self.log(
            f"✓ Preset Value doğrulandı: "
            f"{preset_response.value}"
        )

        return True

    def restore_default_parameters(self):
        if (
            self.client is None
            or self.current_node_id is None
        ):
            raise RuntimeError(
                "Önce CANopen ağını tarayıp "
                "bir encoder seçmelisiniz."
            )

        old_node_id = self.current_node_id
        old_baud_rate = self.current_baud_rate

        self.log(
            f"Node 0x{old_node_id:02X} için "
            "fabrika ayarlarına geri yükleme başlatılıyor..."
        )

        configurator = EncoderConfigurator(
            client=self.client
        )

        if not configurator.restore_default_parameters():
            raise RuntimeError(
                "Encoder restore komutunu kabul etmedi."
            )

        self.log(
            "✓ Restore Parameters komutu kabul edildi."
        )

        time.sleep(1.0)

        self.client.reset_communication(
            node_id=old_node_id
        )

        self.log("✓ NMT Reset Communication gönderildi.")

        time.sleep(2.0)

        remove_encoder_state(
            old_node_id
        )

        self.log(
            "✓ Eski encoder kaydı JSON dosyasından silindi."
        )

        if old_node_id in self.detected_nodes:
            self.detected_nodes.remove(old_node_id)

        self.clear_selected_encoder()

        self.log("✓ Restore işlemi tamamlandı.")
        self.log("⚠ Ağı yeniden tarayın.")

        return old_node_id, old_baud_rate

    def shutdown(self):
        self.can_bus.shutdown()

        self.is_connected = False
        self.current_baud_rate = None

        self.clear_encoder()