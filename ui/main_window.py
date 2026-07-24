"""
Uygulamanın ana penceresi.
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from canopen.encoder_configurator import EncoderSettings
from services.encoder_controller import EncoderController
from ui.configuration_panel import ConfigurationPanel
from ui.connection_panel import ConnectionPanel
from ui.encoder_info_panel import EncoderInfoPanel
from ui.status_panel import StatusPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "CANopen Encoder Configuration Tool"
        )
        self.resize(900, 800)

        self.controller = EncoderController(
            log_callback=self.log
        )

        self.connection_panel = ConnectionPanel()
        self.status_panel = StatusPanel()
        self.encoder_info_panel = EncoderInfoPanel()
        self.configuration_panel = ConfigurationPanel()

        self.scan_button = QPushButton(
            "CANopen Ağını Tara"
        )
        self.scan_button.setObjectName(
            "scanButton"
        )

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText(
            "Uygulama mesajları burada görüntülenecek."
        )
        self.log_output.setMaximumBlockCount(120)

        self.position_timer = QTimer(self)
        self.position_timer.setInterval(250)
        self.position_timer.timeout.connect(
            self.update_position
        )

        self._create_layout()
        self._connect_buttons()

        self.status_panel.set_disconnected()

        self.log(
            "Uygulama hazır. Önce CAN bağlantısını açın."
        )

    def _create_layout(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        main_layout.setContentsMargins(
            12,
            10,
            12,
            12,
        )
        main_layout.setSpacing(8)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        top_layout.addWidget(
            self.connection_panel,
            4,
        )

        scan_group = QGroupBox("CAN Scan")
        scan_layout = QVBoxLayout(scan_group)

        scan_layout.setContentsMargins(
            10,
            12,
            10,
            8,
        )

        scan_layout.addWidget(
            self.scan_button
        )

        top_layout.addWidget(
            scan_group,
            1,
        )

        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(8)

        middle_layout.addWidget(
            self.encoder_info_panel,
            1,
        )

        middle_layout.addWidget(
            self.configuration_panel,
            2,
        )

        log_group = QGroupBox(
            "Application Logs"
        )
        log_layout = QVBoxLayout(log_group)

        log_layout.setContentsMargins(
            8,
            12,
            8,
            8,
        )

        log_layout.addWidget(
            self.log_output
        )

        main_layout.addLayout(top_layout)
        main_layout.addWidget(
            self.status_panel
        )
        main_layout.addLayout(
            middle_layout,
            3,
        )
        main_layout.addWidget(
            log_group,
            2,
        )

        self.setCentralWidget(
            central_widget
        )

    def _connect_buttons(self):
        self.connection_panel.connect_button.clicked.connect(
            self.connect_can
        )

        self.scan_button.clicked.connect(
            self.scan_network
        )

        self.configuration_panel.configure_button.clicked.connect(
            self.configure_encoder
        )

        self.configuration_panel.restore_button.clicked.connect(
            self.restore_encoder
        )

    def log(self, message):
        if hasattr(self, "log_output"):
            self.log_output.appendPlainText(
                str(message)
            )

        print(message)

    def connect_can(self):
        if self.controller.is_connected:
            self.position_timer.stop()

            self.controller.disconnect()

            self.connection_panel.set_connected(
                False
            )

            self.status_panel.set_disconnected()

            self.clear_encoder_information()
            return

        baud_rate = (
            self.connection_panel
            .get_selected_baud_rate_kbit()
        )

        try:
            self.connection_panel.set_connecting()
            self.status_panel.set_connecting()

            QApplication.processEvents()

            self.controller.connect(
                baud_rate
            )

            self.connection_panel.set_connected(
                True
            )

            self.status_panel.set_connected(
                baud_rate
            )

        except Exception as error:
            self.connection_panel.set_connected(
                False
            )

            self.status_panel.set_disconnected()

            self.log(
                f"✗ CAN bağlantısı kurulamadı: "
                f"{error}"
            )

    def scan_network(self):
        if not self.controller.is_connected:
            self.log(
                "⚠ Önce CAN bağlantısını açmalısınız."
            )
            return

        self.position_timer.stop()

        try:
            self.scan_button.setEnabled(False)
            self.scan_button.setText(
                "Taranıyor..."
            )

            self.status_panel.set_scanning()

            self.configuration_panel.set_encoder_available(
                False
            )

            QApplication.processEvents()

            result = self.controller.scan_network(
                start_node_id=1,
                end_node_id=127,
                timeout=0.05,
            )

            if result is None:
                self.clear_encoder_information()

                self.status_panel.set_connected(
                    self.controller.current_baud_rate
                )

                return

            node_id, information = result

            self.encoder_info_panel.set_information(
                information
            )

            self.configuration_panel.set_node_id(
                node_id
            )

            self.configuration_panel.set_encoder_available(
                True
            )

            heartbeat_time = (
                self.configuration_panel
                .heartbeat_time()
            )

            self.status_panel.set_encoder_detected(
                node_id=node_id,
                baud_rate_kbit=(
                    self.controller
                    .current_baud_rate
                ),
                heartbeat_time_ms=(
                    heartbeat_time
                ),
            )

            self.position_timer.start()

            self.log(
                "✓ Encoder bilgileri arayüzde "
                "gösterildi."
            )

        except Exception as error:
            self.clear_encoder_information()

            self.status_panel.set_error()

            self.log(
                "✗ CANopen ağ taraması başarısız: "
                f"{error}"
            )

        finally:
            self.scan_button.setEnabled(True)
            self.scan_button.setText(
                "CANopen Ağını Tara"
            )

    def update_position(self):
        """
        Encoder'ın anlık Position Value değerini
        okuyarak bilgi panelini günceller.
        """

        if self.controller.client is None:
            self.position_timer.stop()
            return

        try:
            position = (
                self.controller.read_position()
            )

            if position is not None:
                self.encoder_info_panel.set_position(
                    position
                )

                self.status_panel.update_last_communication()

        except Exception as error:
            self.position_timer.stop()

            self.status_panel.set_error()

            self.log(
                "✗ Position Value takibi "
                "durduruldu: "
                f"{error}"
            )

    def clear_encoder_information(self):
        self.position_timer.stop()

        self.encoder_info_panel.clear()
        self.configuration_panel.clear_node_id()

        self.configuration_panel.set_encoder_available(
            False
        )

        self.controller.clear_encoder()

        self.status_panel.clear_encoder()

    def configure_encoder(self):
        if self.controller.client is None:
            self.log(
                "⚠ Önce CANopen ağını "
                "taramalısınız."
            )
            return

        try:
            settings = self._get_encoder_settings()

            confirmation = QMessageBox.question(
                self,
                "Yapılandırmayı Onayla",
                (
                    "Aşağıdaki ayarlar encodera "
                    "yazılacak:\n\n"
                    f"Node ID: "
                    f"0x{settings.current_node_id:02X} "
                    f"→ 0x{settings.new_node_id:02X}\n"
                    f"Baud Rate: "
                    f"{self.controller.current_baud_rate} "
                    f"→ {settings.baud_rate} kbit/s\n"
                    f"Heartbeat: "
                    f"{settings.heartbeat_time_ms} ms\n"
                    f"Transmission Type: "
                    f"{settings.transmission_type}\n"
                    f"Event Time: "
                    f"{settings.event_time_ms} ms\n"
                    f"Preset Value: "
                    f"{settings.preset_value}\n\n"
                    "Devam edilsin mi?"
                ),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if (
                confirmation
                != QMessageBox.StandardButton.Yes
            ):
                self.log(
                    "⚠ Yapılandırma kullanıcı "
                    "tarafından iptal edildi."
                )
                return

            self.position_timer.stop()

            self.status_panel.set_configuring()

            self.configuration_panel.set_configuring()
            self.scan_button.setEnabled(False)

            QApplication.processEvents()

            node_id, baud_rate = (
                self.controller.configure(
                    settings
                )
            )

            self.connection_panel.set_baud_rate(
                baud_rate
            )

            self.configuration_panel.set_baud_rate(
                baud_rate
            )

            self.configuration_panel.set_node_id(
                node_id
            )

            self.encoder_info_panel.set_preset_value(
                settings.preset_value
            )

            self.status_panel.set_encoder_detected(
                node_id=node_id,
                baud_rate_kbit=baud_rate,
                heartbeat_time_ms=(
                    settings.heartbeat_time_ms
                ),
            )

            QMessageBox.information(
                self,
                "Yapılandırma Başarılı",
                (
                    "Encoder başarıyla "
                    "yapılandırıldı.\n\n"
                    f"Node ID: 0x{node_id:02X}\n"
                    f"Baud Rate: "
                    f"{baud_rate} kbit/s\n"
                    f"Preset Value: "
                    f"{settings.preset_value}"
                ),
            )

        except ValueError as error:
            self.status_panel.set_error()

            self.log(
                f"✗ Geçersiz değer: {error}"
            )

            QMessageBox.warning(
                self,
                "Geçersiz Değer",
                str(error),
            )

        except Exception as error:
            self.status_panel.set_error()

            self.log(
                f"✗ Yapılandırma başarısız: "
                f"{error}"
            )

            QMessageBox.critical(
                self,
                "Yapılandırma Hatası",
                str(error),
            )

        finally:
            self.scan_button.setEnabled(True)

            if self.controller.client is not None:
                self.configuration_panel.finish_configuring()
                self.position_timer.start()

            else:
                self.configuration_panel.set_encoder_available(
                    False
                )

    def _get_encoder_settings(self):
        return EncoderSettings(
            current_node_id=(
                self.controller.current_node_id
            ),
            new_node_id=self.parse_node_id(
                self.configuration_panel
                .get_node_id_text()
            ),
            baud_rate=(
                self.configuration_panel
                .get_selected_baud_rate()
            ),
            heartbeat_time_ms=(
                self.configuration_panel
                .heartbeat_time()
            ),
            transmission_type=(
                self.configuration_panel
                .transmission_type()
            ),
            event_time_ms=(
                self.configuration_panel
                .event_time()
            ),
            preset_value=(
                self.configuration_panel
                .preset_value()
            ),
        )

    def restore_encoder(self):
        if self.controller.client is None:
            self.log(
                "⚠ Önce CANopen ağını "
                "taramalısınız."
            )
            return

        confirmation = QMessageBox.warning(
            self,
            "Fabrika Ayarlarını Geri Yükle",
            (
                "Encoder'ın kayıtlı yapılandırma "
                "parametreleri fabrika ayarlarına "
                "döndürülecek.\n\n"
                "Node ID, baud rate, heartbeat, "
                "preset ve TPDO ayarları "
                "değişebilir.\n\n"
                "İşleme devam edilsin mi?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            confirmation
            != QMessageBox.StandardButton.Yes
        ):
            self.log(
                "⚠ Fabrika ayarlarına dönüş "
                "kullanıcı tarafından iptal edildi."
            )
            return

        self.position_timer.stop()

        try:
            self.status_panel.set_restoring()

            self.configuration_panel.set_restoring()
            self.scan_button.setEnabled(False)

            QApplication.processEvents()

            old_node_id, old_baud_rate = (
                self.controller
                .restore_default_parameters()
            )

            self.clear_encoder_information()

            self.status_panel.set_connected(
                self.controller.current_baud_rate
                or old_baud_rate
            )

            QMessageBox.information(
                self,
                "Restore Komutu Başarılı",
                (
                    "Encoder fabrika ayarlarına "
                    "dönüş komutunu kabul etti.\n\n"
                    f"Restore öncesi Node ID: "
                    f"0x{old_node_id:02X}\n"
                    f"Restore öncesi Baud Rate: "
                    f"{old_baud_rate} kbit/s\n\n"
                    "Encoder'ın Node ID ve baud rate "
                    "değerleri fabrika değerlerine "
                    "dönmüş olabilir.\n\n"
                    "Gerekirse encoder'ın enerjisini "
                    "kapatıp yeniden açın. Daha sonra "
                    "doğru baud rate değerini seçip "
                    "ağı tekrar tarayın."
                ),
            )

        except Exception as error:
            self.status_panel.set_error()

            self.log(
                "✗ Fabrika ayarlarına dönüş "
                "başarısız: "
                f"{error}"
            )

            QMessageBox.critical(
                self,
                "Restore Hatası",
                str(error),
            )

        finally:
            self.scan_button.setEnabled(True)

            if self.controller.client is not None:
                self.configuration_panel.finish_restoring()
            else:
                self.configuration_panel.restore_button.setText(
                    "Fabrika Ayarlarını Geri Yükle"
                )

                self.configuration_panel.set_encoder_available(
                    False
                )

    @staticmethod
    def parse_node_id(value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Yeni Node ID boş bırakılamaz."
            )

        try:
            node_id = int(
                value,
                (
                    16
                    if value.lower().startswith(
                        "0x"
                    )
                    else 10
                ),
            )

        except ValueError as error:
            raise ValueError(
                "Node ID decimal veya 0x önekli "
                "hexadecimal olmalıdır. "
                "Örnek: 40 veya 0x28."
            ) from error

        if not 1 <= node_id <= 127:
            raise ValueError(
                "Node ID 1 ile 127 arasında "
                "olmalıdır."
            )

        return node_id

    def closeEvent(self, event):
        self.position_timer.stop()
        self.controller.shutdown()
        event.accept()