"""
Uygulamanın ana penceresi.
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
from encoder_state import save_encoder_state

from PySide6.QtWidgets import (
    QComboBox,
    QApplication,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
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


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.can_bus = CanBus()
        self.is_connected = False
        self.current_node_id = None
        self.client = None

        self.setWindowTitle(
            "CANopen Encoder Configuration Tool"
        )
        self.resize(900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # ======================================================
        # Connection
        # ======================================================

        connection_group = QGroupBox("Connection")
        connection_layout = QHBoxLayout()

        channel_label = QLabel("Kanal:")
        channel_value = QLabel("PCAN_USBBUS1")

        baud_rate_label = QLabel("Mevcut CAN Baud Rate:")

        self.baud_rate_combo = QComboBox()
        self.baud_rate_combo.addItems(
            [
                "10 kbit/s",
                "20 kbit/s",
                "50 kbit/s",
                "100 kbit/s",
                "125 kbit/s",
                "250 kbit/s",
                "500 kbit/s",
                "800 kbit/s",
                "1000 kbit/s",
            ]
        )
        self.baud_rate_combo.setCurrentText(
            "250 kbit/s"
        )

        self.connect_button = QPushButton("Bağlan")
        self.connect_button.clicked.connect(
            self.connect_can
        )

        connection_layout.addWidget(channel_label)
        connection_layout.addWidget(channel_value)
        connection_layout.addWidget(baud_rate_label)
        connection_layout.addWidget(self.baud_rate_combo)
        connection_layout.addWidget(self.connect_button)

        connection_group.setLayout(
            connection_layout
        )
        main_layout.addWidget(
            connection_group
        )

        # ======================================================
        # Network Scan
        # ======================================================

        scan_group = QGroupBox("Network Scan")
        scan_layout = QVBoxLayout()

        self.scan_button = QPushButton(
            "CANopen Ağını Tara"
        )
        self.scan_button.clicked.connect(
            self.scan_network
        )

        scan_layout.addWidget(
            self.scan_button
        )
        scan_group.setLayout(
            scan_layout
        )
        main_layout.addWidget(
            scan_group
        )

        # ======================================================
        # Encoder Information
        # ======================================================

        info_group = QGroupBox(
            "Encoder Information"
        )
        info_layout = QFormLayout()

        self.vendor_label = QLabel("-")
        self.product_label = QLabel("-")
        self.revision_label = QLabel("-")
        self.serial_label = QLabel("-")
        self.position_label = QLabel("-")

        info_layout.addRow(
            "Vendor ID:",
            self.vendor_label
        )
        info_layout.addRow(
            "Product Code:",
            self.product_label
        )
        info_layout.addRow(
            "Revision Number:",
            self.revision_label
        )
        info_layout.addRow(
            "Serial Number:",
            self.serial_label
        )
        info_layout.addRow(
            "Position Value:",
            self.position_label
        )

        info_group.setLayout(
            info_layout
        )
        main_layout.addWidget(
            info_group
        )

        # ======================================================
        # Encoder Configuration
        # ======================================================

        configuration_group = QGroupBox(
            "Encoder Configuration"
        )
        configuration_layout = QFormLayout()

        self.new_node_id_input = QLineEdit()
        self.new_node_id_input.setPlaceholderText(
            "Örnek: 40 veya 0x28"
        )

        self.new_baud_rate_combo = QComboBox()
        self.new_baud_rate_combo.addItems(
            [
                "10 kbit/s",
                "20 kbit/s",
                "50 kbit/s",
                "100 kbit/s",
                "125 kbit/s",
                "250 kbit/s",
                "500 kbit/s",
                "800 kbit/s",
                "1000 kbit/s",
            ]
        )
        self.new_baud_rate_combo.setCurrentText(
            "250 kbit/s"
        )

        self.heartbeat_input = QLineEdit("100")
        self.transmission_type_input = QLineEdit("255")
        self.event_time_input = QLineEdit("80")

        # Bu değerler proje gereksiniminde sabit olduğu için
        # kullanıcı tarafından değiştirilmiyor.
        self.heartbeat_input.setReadOnly(True)
        self.transmission_type_input.setReadOnly(True)
        self.event_time_input.setReadOnly(True)

        self.configure_button = QPushButton(
            "Encoder'ı Yapılandır"
        )
        self.configure_button.clicked.connect(
            self.configure_encoder
        )

        # Encoder taranmadan yapılandırma yapılmasın.
        self.configure_button.setEnabled(False)

        configuration_layout.addRow(
            "Yeni Node ID:",
            self.new_node_id_input
        )
        configuration_layout.addRow(
            "Encoder İçin Yeni Baud Rate:",
            self.new_baud_rate_combo
        )
        configuration_layout.addRow(
            "Heartbeat Time (ms):",
            self.heartbeat_input
        )
        configuration_layout.addRow(
            "Transmission Type:",
            self.transmission_type_input
        )
        configuration_layout.addRow(
            "Event Time (ms):",
            self.event_time_input
        )
        configuration_layout.addRow(
            self.configure_button
        )

        configuration_group.setLayout(
            configuration_layout
        )
        main_layout.addWidget(
            configuration_group
        )

        # ======================================================
        # Log
        # ======================================================

        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText(
            "Uygulama mesajları burada görüntülenecek."
        )
        self.log_output.setMaximumBlockCount(120)

        log_layout.addWidget(
            self.log_output
        )
        log_group.setLayout(
            log_layout
        )
        main_layout.addWidget(
            log_group
        )

        self.log(
            "Uygulama hazır. Önce CAN bağlantısını açın."
        )

    def log(self, message):
        """
        Mesajı hem GUI log alanına hem terminale yazar.
        """

        self.log_output.appendPlainText(message)
        print(message)

    def connect_can(self):
        if self.is_connected:
            self.can_bus.shutdown()

            self.is_connected = False
            self.client = None
            self.current_node_id = None

            self.connect_button.setText(
                "Bağlan"
            )
            self.baud_rate_combo.setEnabled(
                True
            )

            self.clear_encoder_information()

            self.log(
                "CAN bağlantısı kapatıldı."
            )
            return

        selected_text = (
            self.baud_rate_combo.currentText()
        )

        bitrate_kbit = int(
            selected_text.split()[0]
        )
        bitrate = bitrate_kbit * 1000

        try:
            self.connect_button.setEnabled(False)
            self.connect_button.setText(
                "Bağlanıyor..."
            )

            self.can_bus.connect(
                bitrate=bitrate
            )

            self.is_connected = True

            self.connect_button.setText(
                "Bağlantıyı Kes"
            )
            self.connect_button.setEnabled(
                True
            )

            self.baud_rate_combo.setEnabled(
                False
            )

            self.log(
                f"✓ CAN bağlantısı kuruldu: "
                f"{bitrate_kbit} kbit/s"
            )

        except Exception as error:
            self.connect_button.setEnabled(True)
            self.connect_button.setText(
                "Bağlan"
            )

            self.log(
                f"✗ CAN bağlantısı kurulamadı: "
                f"{error}"
            )

    def scan_network(self):
        """
        CANopen ağını tarar ve bulunan encoder bilgilerini gösterir.
        """

        if not self.is_connected:
            self.log(
                "⚠ Önce CAN bağlantısını açmalısınız."
            )
            return

        try:
            self.scan_button.setEnabled(False)
            self.scan_button.setText(
                "Taranıyor..."
            )
            self.configure_button.setEnabled(False)

            self.log(
                "CANopen ağı taranıyor..."
            )
            QApplication.processEvents()

            scanner = NodeScanner(
                can_bus=self.can_bus
            )

            found_nodes = scanner.scan(
                start_node_id=1,
                end_node_id=127,
                timeout=0.05,
            )

            if not found_nodes:
                self.log(
                    "✗ CANopen ağında aktif cihaz bulunamadı."
                )
                self.clear_encoder_information()
                return

            # Şimdilik ilk bulunan cihaz kullanılıyor.
            found_node = found_nodes[0]

            self.current_node_id = (
                found_node.node_id
            )

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
                "Encoder kimlik ve pozisyon bilgileri okunuyor..."
            )

            reader = EncoderReader(
                client=self.client
            )

            information = reader.read_all(
                timeout=3.0
            )

            self.show_encoder_information(
                information
            )

            self.new_node_id_input.setText(
                str(self.current_node_id)
            )

            self.configure_button.setEnabled(
                True
            )

            self.log(
                "✓ Encoder bilgileri arayüzde gösterildi."
            )

        except Exception as error:
            self.clear_encoder_information()

            self.log(
                f"✗ CANopen ağ taraması başarısız: "
                f"{error}"
            )

        finally:
            self.scan_button.setEnabled(True)
            self.scan_button.setText(
                "CANopen Ağını Tara"
            )

    def show_encoder_information(
        self,
        information
    ):
        """
        EncoderReader tarafından okunan bilgileri arayüzde gösterir.
        """

        self.vendor_label.setText(
            self.format_hex(
                information.vendor_id
            )
        )

        self.product_label.setText(
            self.format_hex(
                information.product_code
            )
        )

        self.revision_label.setText(
            self.format_hex(
                information.revision_number
            )
        )

        self.serial_label.setText(
            self.format_hex(
                information.serial_number
            )
        )

        if information.position is None:
            self.position_label.setText("-")
        else:
            self.position_label.setText(
                str(information.position)
            )

    @staticmethod
    def format_hex(value):
        """
        Sayısal değeri 8 basamaklı hexadecimal gösterir.
        """

        if value is None:
            return "-"

        return f"0x{value:08X}"

    def clear_encoder_information(self):
        self.vendor_label.setText("-")
        self.product_label.setText("-")
        self.revision_label.setText("-")
        self.serial_label.setText("-")
        self.position_label.setText("-")

        self.new_node_id_input.clear()
        self.configure_button.setEnabled(False)

        self.current_node_id = None
        self.client = None

    def configure_encoder(self):
        """
        Arayüzdeki değerleri encoder'a yazar, kalıcı belleğe kaydeder
        ve yeni bağlantı bilgileriyle haberleşmeyi doğrular.
        """

        if self.client is None or self.current_node_id is None:
            self.log(
                "⚠ Önce CANopen ağını taramalısınız."
            )
            return

        try:
            new_node_id = self.parse_node_id(
                self.new_node_id_input.text()
            )

            new_baud_rate = int(
                self.new_baud_rate_combo.currentText().split()[0]
            )

            settings = EncoderSettings(
                current_node_id=self.current_node_id,
                new_node_id=new_node_id,
                baud_rate=new_baud_rate,
                heartbeat_time_ms=int(
                    self.heartbeat_input.text()
                ),
                transmission_type=int(
                    self.transmission_type_input.text()
                ),
                event_time_ms=int(
                    self.event_time_input.text()
                ),
            )

            current_baud_rate = int(
                self.baud_rate_combo.currentText().split()[0]
            )

            confirmation = QMessageBox.question(
                self,
                "Yapılandırmayı Onayla",
                (
                    "Aşağıdaki ayarlar encodera yazılacak:\n\n"
                    f"Node ID: 0x{settings.current_node_id:02X} "
                    f"→ 0x{settings.new_node_id:02X}\n"
                    f"Baud Rate: {current_baud_rate} "
                    f"→ {settings.baud_rate} kbit/s\n"
                    f"Heartbeat: {settings.heartbeat_time_ms} ms\n"
                    f"Transmission Type: {settings.transmission_type}\n"
                    f"Event Time: {settings.event_time_ms} ms\n\n"
                    "Devam edilsin mi?"
                ),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if confirmation != QMessageBox.StandardButton.Yes:
                self.log(
                    "⚠ Yapılandırma kullanıcı tarafından iptal edildi."
                )
                return

            self.configure_button.setEnabled(False)
            self.scan_button.setEnabled(False)
            self.configure_button.setText(
                "Yapılandırılıyor..."
            )

            self.log("Yapılandırma başlatılıyor...")

            self.client.change_node_id(
                settings.current_node_id
            )

            configurator = EncoderConfigurator(
                client=self.client
            )

            configured = configurator.configure(
                settings=settings
            )

            if not configured:
                raise RuntimeError(
                    "Encoder ayarları yazılamadı."
                )

            self.log(
                "✓ Encoder ayarları yazıldı."
            )

            saved = configurator.save()

            if not saved:
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

            self.log(
                f"✓ CAN bağlantısı "
                f"{settings.baud_rate} kbit/s ile yeniden açıldı."
            )

            state = self.client.wait_for_heartbeat(
                node_id=settings.new_node_id,
                timeout=8.0,
            )

            if state is None:
                raise RuntimeError(
                    "Encoder yeni Node ID ve baud rate ile bulunamadı."
                )

            self.log(
                "✓ Heartbeat doğrulandı."
            )

            self.client.change_node_id(
                settings.new_node_id
            )

            if not self.verify_new_connection(
                settings
            ):
                raise RuntimeError(
                    "Yeni bağlantı bilgileri doğrulanamadı."
                )

            self.log(
                "✓ SDO haberleşmesi doğrulandı."
            )

            save_encoder_state(
                settings.new_node_id,
                settings.baud_rate
            )

            self.current_node_id = (
                settings.new_node_id
            )

            self.baud_rate_combo.setCurrentText(
                f"{settings.baud_rate} kbit/s"
            )
            self.new_node_id_input.setText(
                str(settings.new_node_id)
            )

            self.log(
                "✓ Son encoder durumu kaydedildi."
            )
            self.log(
                f"✓ Encoder başarıyla yapılandırıldı. "
                f"Node ID: 0x{settings.new_node_id:02X}, "
                f"Baud Rate: {settings.baud_rate} kbit/s"
            )

            QMessageBox.information(
                self,
                "Yapılandırma Başarılı",
                (
                    "Encoder başarıyla yapılandırıldı.\n\n"
                    f"Node ID: 0x{settings.new_node_id:02X}\n"
                    f"Baud Rate: {settings.baud_rate} kbit/s"
                ),
            )

        except ValueError as error:
            self.log(
                f"✗ Geçersiz değer: {error}"
            )

            QMessageBox.warning(
                self,
                "Geçersiz Değer",
                str(error),
            )

        except Exception as error:
            self.log(
                f"✗ Yapılandırma başarısız: {error}"
            )

            QMessageBox.critical(
                self,
                "Yapılandırma Hatası",
                str(error),
            )

        finally:
            self.configure_button.setText(
                "Encoder'ı Yapılandır"
            )

            if self.client is not None:
                self.configure_button.setEnabled(
                    True
                )

            self.scan_button.setEnabled(
                True
            )

    @staticmethod
    def parse_node_id(value):
        """
        Node ID değerini decimal veya 0x önekli hexadecimal kabul eder.
        """

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Yeni Node ID boş bırakılamaz."
            )

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

    def verify_new_connection(self, settings):
        """
        Reset sonrasında yeni Node ID ve baud rate değerlerini doğrular.
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
            self.log(
                "✗ Baud rate kaydı okunamadı."
            )
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

        return True

    def closeEvent(self, event):
        """
        Pencere kapanırken CAN bağlantısını kapatır.
        """

        self.can_bus.shutdown()
        event.accept()