"""
Uygulamanın ana penceresi.
"""

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
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
from ui.encoder_table_panel import EncoderTablePanel
from ui.status_panel import StatusPanel



class EncoderDiscoveryWorker(QObject):
    """
    Uzun süren CAN taramasını GUI iş parçacığından ayrı çalıştırır.
    """

    finished = Signal(object)
    failed = Signal(str)
    log_message = Signal(str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    @Slot()
    def run(self):
        old_log_callback = self.controller.log_callback
        self.controller.log_callback = self.log_message.emit

        try:
            result = self.controller.discover_encoders(
                probe_timeout=0.03,
                scan_timeout=0.012,
            )
            self.finished.emit(result)

        except Exception as error:
            self.failed.emit(str(error))

        finally:
            self.controller.log_callback = old_log_callback


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "CANopen Encoder Configuration Tool"
        )
        self.resize(1050, 850)
        self.setMinimumSize(900, 700)   

        self.controller = EncoderController(
            log_callback=self.log
        )

        self.connection_panel = ConnectionPanel()
        self.status_panel = StatusPanel()
        self.encoder_info_panel = EncoderInfoPanel()
        self.configuration_panel = ConfigurationPanel()
        self.encoder_table_panel = EncoderTablePanel()

        self.scan_button = QPushButton(
            "Encoderları Bul"
        )
        self.scan_button.setObjectName(
            "scanButton"
        )

        self.encoder_selector = QComboBox()
        self.encoder_selector.setEnabled(False)
        self.encoder_selector.setMinimumWidth(220)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumBlockCount(120)

        self.log_output.setMinimumHeight(80)
        self.log_output.setMaximumHeight(115)

        # Her timer tetiklenmesinde yalnızca bir encoder okunur.
        self.position_update_index = 0

        self.position_timer = QTimer(self)
        self.position_timer.setInterval(150)
        self.position_timer.timeout.connect(
            self.update_all_positions
        )

        self.discovery_thread = None
        self.discovery_worker = None

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
        main_layout.addWidget(
            self.encoder_table_panel
        )

        main_layout.addLayout(
            middle_layout,
            4,
        )

        main_layout.addWidget(
            log_group
        )

        self.setCentralWidget(
            central_widget
        )



        self.status_panel.setMaximumHeight(115)
        self.encoder_table_panel.setMaximumHeight(150)
        log_group.setMaximumHeight(155)

    def _connect_buttons(self):
        self.connection_panel.connect_button.clicked.connect(
            self.connect_can
        )
        self.scan_button.clicked.connect(
            self.discover_network
        )
        self.encoder_selector.currentIndexChanged.connect(
            self.encoder_selection_changed
        )
        self.encoder_table_panel.encoder_selected.connect(
            self.select_encoder_from_table
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
        if (
            self.discovery_thread is not None
            and self.discovery_thread.isRunning()
        ):
            self.log(
                "⚠ Tarama devam ederken bağlantı değiştirilemez."
            )
            return

        if self.controller.is_connected:
            self.position_timer.stop()
            self.controller.disconnect()
            self.connection_panel.set_connected(False)
            self.status_panel.set_disconnected()
            self.clear_encoder_information(
                clear_controller=False
            )
            return

        baud_rate = (
            self.connection_panel
            .get_selected_baud_rate_kbit()
        )

        try:
            self.connection_panel.set_connecting()
            self.status_panel.set_connecting()
            QApplication.processEvents()

            self.controller.connect(baud_rate)

            self.connection_panel.set_connected(True)
            self.status_panel.set_connected(baud_rate)

        except Exception as error:
            self.connection_panel.set_connected(False)
            self.status_panel.set_disconnected()
            self.log(
                f"✗ CAN bağlantısı kurulamadı: {error}"
            )

    def _prepare_scan_ui(self):
        self.position_timer.stop()

        self.scan_button.setEnabled(False)
        self.scan_button.setText(
            "Encoderlar Aranıyor..."
        )

        self.status_panel.set_scanning()

        self.configuration_panel.set_encoder_available(
            False
        )

        self.encoder_selector.blockSignals(True)
        self.encoder_selector.clear()
        self.encoder_selector.blockSignals(False)
        self.encoder_selector.setEnabled(False)

        self.encoder_table_panel.clear()

        QApplication.processEvents()

    def _finish_scan_ui(self):
        self.scan_button.setEnabled(True)
        self.scan_button.setText(
            "Encoderları Bul"
        )

    def _display_detected_encoders(self, node_ids):
        encoder_information = {}

        self.encoder_selector.blockSignals(True)

        for node_id in node_ids:
            information = (
                self.controller
                .read_encoder_information(node_id)
            )

            encoder_information[node_id] = information

            self.encoder_selector.addItem(
                f"Node 0x{node_id:02X} ({node_id})",
                node_id,
            )

            self.encoder_table_panel.add_encoder(
                node_id=node_id,
                serial_number=information.serial_number,
                position=information.position,
                status="Online",
            )

            QApplication.processEvents()

        self.encoder_selector.setCurrentIndex(0)
        self.encoder_selector.blockSignals(False)
        self.encoder_selector.setEnabled(True)

        first_node_id = node_ids[0]

        self.load_selected_encoder(
            first_node_id,
            information=encoder_information[
                first_node_id
            ],
        )

        self.encoder_table_panel.select_node(
            first_node_id
        )

        self.position_update_index = 0
        self.position_timer.start()

    def discover_network(self):
        """
        Otomatik encoder aramasını arka planda başlatır.
        Böylece uzun tarama sırasında pencere donmaz.
        """

        if not self.controller.is_connected:
            self.log(
                "⚠ Önce CAN bağlantısını açmalısınız."
            )
            return

        if (
            self.discovery_thread is not None
            and self.discovery_thread.isRunning()
        ):
            self.log(
                "⚠ Encoder araması zaten devam ediyor."
            )
            return

        self._prepare_scan_ui()

        self.discovery_thread = QThread(self)
        self.discovery_worker = EncoderDiscoveryWorker(
            self.controller
        )

        self.discovery_worker.moveToThread(
            self.discovery_thread
        )

        self.discovery_thread.started.connect(
            self.discovery_worker.run
        )

        self.discovery_worker.log_message.connect(
            self.log
        )
        self.discovery_worker.finished.connect(
            self._on_discovery_finished
        )
        self.discovery_worker.failed.connect(
            self._on_discovery_failed
        )

        self.discovery_worker.finished.connect(
            self.discovery_thread.quit
        )
        self.discovery_worker.failed.connect(
            self.discovery_thread.quit
        )

        self.discovery_thread.finished.connect(
            self.discovery_worker.deleteLater
        )
        self.discovery_thread.finished.connect(
            self._cleanup_discovery_thread
        )
        self.discovery_thread.finished.connect(
            self.discovery_thread.deleteLater
        )

        self.discovery_thread.start()

    @Slot(object)
    def _on_discovery_finished(self, result):
        baud_rate, node_ids = result

        if not node_ids:
            self.clear_encoder_information(
                clear_controller=False
            )

            self.status_panel.set_connected(
                self.controller.current_baud_rate
            )

            QMessageBox.warning(
                self,
                "Encoder Bulunamadı",
                (
                    "Desteklenen baud rate değerlerinde "
                    "aktif encoder bulunamadı.\n\n"
                    "Encoder beslemesini, CAN bağlantısını "
                    "ve terminasyon direncini kontrol edin."
                ),
            )
            return

        try:
            self.connection_panel.set_baud_rate(
                baud_rate
            )

            self.status_panel.set_connected(
                baud_rate
            )

            self._display_detected_encoders(
                node_ids
            )

            self.log(
                f"✓ Otomatik arama tamamlandı: "
                f"{len(node_ids)} encoder bulundu."
            )

        except Exception as error:
            self._on_discovery_failed(
                str(error)
            )

    @Slot(str)
    def _on_discovery_failed(self, error_message):
        self.clear_encoder_information(
            clear_controller=False
        )

        self.status_panel.set_error()

        self.log(
            "✗ Otomatik encoder araması başarısız: "
            f"{error_message}"
        )

        QMessageBox.critical(
            self,
            "Tarama Hatası",
            error_message,
        )

    @Slot()
    def _cleanup_discovery_thread(self):
        self.discovery_worker = None
        self.discovery_thread = None
        self._finish_scan_ui()

    def encoder_selection_changed(self, index):
        if index < 0:
            return

        node_id = self.encoder_selector.itemData(index)

        if node_id is None:
            return

        try:
            self.load_selected_encoder(node_id)
            self.encoder_table_panel.select_node(
                node_id
            )
        except Exception as error:
            self.status_panel.set_error()
            self.log(
                f"✗ Encoder seçilemedi: {error}"
            )

    def select_encoder_from_table(self, node_id):
        index = self.encoder_selector.findData(
            node_id
        )

        if index == -1:
            return

        if (
            self.encoder_selector.currentData()
            == node_id
        ):
            return

        self.encoder_selector.setCurrentIndex(index)

    def load_selected_encoder(
        self,
        node_id,
        information=None,
    ):
        if information is None:
            information = (
                self.controller.select_encoder(
                    node_id
                )
            )
        else:
            self.controller.current_node_id = node_id
            self.controller.client = (
                self.controller._create_client(node_id)
            )

        self.encoder_info_panel.set_information(
            information
        )
        self.configuration_panel.set_node_id(
            node_id
        )
        self.configuration_panel.set_baud_rate(
            self.controller.current_baud_rate
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
                self.controller.current_baud_rate
            ),
            heartbeat_time_ms=heartbeat_time,
        )

        self.log(
            f"✓ Node 0x{node_id:02X} ({node_id}) "
            "aktif encoder olarak seçildi."
        )

    def update_all_positions(self):
        """
        Her çağrıda listedeki tek bir encoderın
        pozisyonunu günceller. Böylece SDO istekleri
        üst üste binmez.
        """

        node_ids = self.controller.detected_nodes

        if (
            not self.controller.is_connected
            or not node_ids
        ):
            self.position_timer.stop()
            return

        if self.position_update_index >= len(node_ids):
            self.position_update_index = 0

        node_id = node_ids[
            self.position_update_index
        ]

        self.position_update_index += 1

        try:
            position = (
                self.controller
                .read_position_for_node(node_id)
            )

            if position is None:
                self.encoder_table_panel.set_offline(
                    node_id
                )
                return

            self.encoder_table_panel.update_position(
                node_id=node_id,
                position=position,
                status="Online",
            )

            if (
                node_id
                == self.controller.current_node_id
            ):
                self.encoder_info_panel.set_position(
                    position
                )
                self.status_panel.update_last_communication()

        except Exception:
            self.encoder_table_panel.set_offline(
                node_id
            )

    def clear_encoder_information(
        self,
        clear_controller=True,
    ):
        self.position_timer.stop()
        self.position_update_index = 0

        self.encoder_selector.blockSignals(True)
        self.encoder_selector.clear()
        self.encoder_selector.blockSignals(False)
        self.encoder_selector.setEnabled(False)

        self.encoder_table_panel.clear()
        self.encoder_info_panel.clear()
        self.configuration_panel.clear_node_id()
        self.configuration_panel.set_encoder_available(
            False
        )

        if clear_controller:
            self.controller.clear_encoder()

        self.status_panel.clear_encoder()

    def configure_encoder(self):
        if self.controller.client is None:
            self.log(
                "⚠ Önce CANopen ağını tarayıp "
                "bir encoder seçmelisiniz."
            )
            return

        try:
            settings = self._get_encoder_settings()

            if (
                settings.baud_rate
                != self.controller.current_baud_rate
                and len(
                    self.controller.detected_nodes
                ) > 1
            ):
                QMessageBox.warning(
                    self,
                    "Baud Rate Uyarısı",
                    (
                        "Ağda birden fazla encoder var.\n\n"
                        "Bütün encoderlar aynı baud "
                        "rate değerinde kalmalıdır."
                    ),
                )
                return

            confirmation = QMessageBox.question(
                self,
                "Yapılandırmayı Onayla",
                (
                    "Aşağıdaki ayarlar seçili encodera "
                    "yazılacak:\n\n"
                    f"Node ID: "
                    f"0x{settings.current_node_id:02X} "
                    f"→ 0x{settings.new_node_id:02X}\n"
                    f"Baud Rate: "
                    f"{self.controller.current_baud_rate} "
                    f"→ {settings.baud_rate} kbit/s\n"
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
                return

            self.position_timer.stop()
            self.status_panel.set_configuring()
            self.configuration_panel.set_configuring()
            self.scan_button.setEnabled(False)
            self.encoder_selector.setEnabled(False)

            QApplication.processEvents()

            old_node_id = settings.current_node_id

            node_id, baud_rate = (
                self.controller.configure(settings)
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

            self.update_encoder_selector_after_node_change(
                old_node_id,
                node_id,
            )

            self.encoder_table_panel.update_node_id(
                old_node_id,
                node_id,
            )
            self.encoder_table_panel.select_node(
                node_id
            )

            QMessageBox.information(
                self,
                "Yapılandırma Başarılı",
                (
                    "Seçili encoder başarıyla "
                    "yapılandırıldı."
                ),
            )

        except ValueError as error:
            self.status_panel.set_error()
            QMessageBox.warning(
                self,
                "Geçersiz Değer",
                str(error),
            )

        except Exception as error:
            self.status_panel.set_error()
            self.log(
                f"✗ Yapılandırma başarısız: {error}"
            )
            QMessageBox.critical(
                self,
                "Yapılandırma Hatası",
                str(error),
            )

        finally:
            self.scan_button.setEnabled(True)
            self.scan_button.setText(
                "Encoderları Bul"
            )

            if self.controller.detected_nodes:
                self.encoder_selector.setEnabled(True)

            if self.controller.client is not None:
                self.configuration_panel.finish_configuring()
                self.position_timer.start()

    def update_encoder_selector_after_node_change(
        self,
        old_node_id,
        new_node_id,
    ):
        self.encoder_selector.blockSignals(True)

        for index in range(
            self.encoder_selector.count()
        ):
            if (
                self.encoder_selector.itemData(index)
                == old_node_id
            ):
                self.encoder_selector.setItemText(
                    index,
                    (
                        f"Node 0x{new_node_id:02X} "
                        f"({new_node_id})"
                    ),
                )
                self.encoder_selector.setItemData(
                    index,
                    new_node_id,
                )
                self.encoder_selector.setCurrentIndex(
                    index
                )
                break

        self.encoder_selector.blockSignals(False)

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
                "⚠ Önce bir encoder seçmelisiniz."
            )
            return

        confirmation = QMessageBox.warning(
            self,
            "Fabrika Ayarlarını Geri Yükle",
            (
                "Yalnızca seçili encoder fabrika "
                "ayarlarına döndürülecek.\n\n"
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

            self.clear_encoder_information(
                clear_controller=False
            )

            self.status_panel.set_connected(
                self.controller.current_baud_rate
                or old_baud_rate
            )

            QMessageBox.information(
                self,
                "Restore Komutu Başarılı",
                (
                    f"Restore öncesi Node ID: "
                    f"0x{old_node_id:02X}\n\n"
                    "Ağı yeniden tarayın."
                ),
            )

        except Exception as error:
            self.status_panel.set_error()
            self.log(
                "✗ Fabrika ayarlarına dönüş "
                f"başarısız: {error}"
            )

        finally:
            self.scan_button.setEnabled(True)

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
                "hexadecimal olmalıdır."
            ) from error

        if not 1 <= node_id <= 127:
            raise ValueError(
                "Node ID 1 ile 127 arasında olmalıdır."
            )

        return node_id

    def closeEvent(self, event):
        if (
            self.discovery_thread is not None
            and self.discovery_thread.isRunning()
        ):
            QMessageBox.information(
                self,
                "Tarama Devam Ediyor",
                (
                    "Encoder taraması devam ediyor. "
                    "Lütfen taramanın tamamlanmasını bekleyin."
                ),
            )
            event.ignore()
            return

        self.position_timer.stop()
        self.controller.shutdown()
        event.accept()