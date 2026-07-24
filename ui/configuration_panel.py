"""
Encoder yapılandırma paneli.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class ConfigurationPanel(QGroupBox):
    BAUD_RATE_OPTIONS = [10, 20, 50, 100, 125, 250, 500, 800, 1000]
    DEFAULT_BAUD_RATE = 250

    def __init__(self, parent=None):
        super().__init__("Encoder Configuration", parent)

        self.new_node_id_input = QLineEdit()
        self.new_node_id_input.setPlaceholderText("Örnek: 40 veya 0x28")

        self.new_baud_rate_combo = QComboBox()
        for baud_rate in self.BAUD_RATE_OPTIONS:
            self.new_baud_rate_combo.addItem(
                f"{baud_rate} kbit/s",
                baud_rate,
            )

        self.set_baud_rate(self.DEFAULT_BAUD_RATE)

        self.heartbeat_input = QLineEdit("100")
        self.transmission_type_input = QLineEdit("255")
        self.event_time_input = QLineEdit("80")
        self.preset_value_input = QLineEdit("0")

        self.preset_value_input.setPlaceholderText("0 - 4294967295")

        self.heartbeat_input.setReadOnly(True)
        self.transmission_type_input.setReadOnly(True)
        self.event_time_input.setReadOnly(True)

        # Butonlar ve CSS Stil Nesne İsimleri (objectName)
        self.configure_button = QPushButton("Encoder'ı Yapılandır")
        self.configure_button.setObjectName("primaryButton")

        self.restore_button = QPushButton("Fabrika Ayarlarını Geri Yükle")
        self.restore_button.setObjectName("dangerButton")

        # Layout Tanımlamaları
        layout = QFormLayout()
        layout.addRow("Yeni Node ID:", self.new_node_id_input)
        layout.addRow(
            "Encoder İçin Yeni Baud Rate:",
            self.new_baud_rate_combo,
        )
        layout.addRow("Heartbeat Time (ms):", self.heartbeat_input)
        layout.addRow(
            "Transmission Type:",
            self.transmission_type_input,
        )
        layout.addRow("Event Time (ms):", self.event_time_input)
        layout.addRow("Preset Value:", self.preset_value_input)

        # Butonları Yan Yana Koymak İçin Yatay Düzen (QHBoxLayout)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        # Yapılandır butonuna 2, Fabrika Ayarları butonuna 1 esneklik oranı (stretch) verildi
        button_layout.addWidget(self.configure_button, stretch=2)
        button_layout.addWidget(self.restore_button, stretch=1)

        # Yatay buton düzenini ana QFormLayout'a ekliyoruz
        layout.addRow(button_layout)

        self.setLayout(layout)
        self.set_encoder_available(False)

    def set_encoder_available(self, available):
        self.configure_button.setEnabled(available)
        self.restore_button.setEnabled(available)

    def set_configuring(self):
        self.configure_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        self.configure_button.setText("Yapılandırılıyor...")

    def finish_configuring(self):
        self.configure_button.setText("Encoder'ı Yapılandır")
        self.set_encoder_available(True)

    def set_restoring(self):
        self.configure_button.setEnabled(False)
        self.restore_button.setEnabled(False)
        self.restore_button.setText("Geri Yükleniyor...")

    def finish_restoring(self):
        self.restore_button.setText("Fabrika Ayarlarını Geri Yükle")
        self.set_encoder_available(True)

    def get_node_id_text(self):
        return self.new_node_id_input.text()

    def set_node_id(self, node_id):
        self.new_node_id_input.setText(str(node_id))

    def clear_node_id(self):
        self.new_node_id_input.clear()

    def get_selected_baud_rate(self):
        return int(self.new_baud_rate_combo.currentData())

    def set_baud_rate(self, baud_rate):
        index = self.new_baud_rate_combo.findData(baud_rate)
        if index != -1:
            self.new_baud_rate_combo.setCurrentIndex(index)

    def heartbeat_time(self):
        return int(self.heartbeat_input.text())

    def transmission_type(self):
        return int(self.transmission_type_input.text())

    def event_time(self):
        return int(self.event_time_input.text())

    def preset_value(self):
        value = self.preset_value_input.text().strip()

        if not value:
            raise ValueError("Preset Value boş bırakılamaz.")

        try:
            preset_value = int(value)
        except ValueError as error:
            raise ValueError("Preset Value tam sayı olmalıdır.") from error

        if not 0 <= preset_value <= 0xFFFFFFFF:
            raise ValueError(
                "Preset Value 0 ile 4294967295 arasında olmalıdır."
            )

        return preset_value