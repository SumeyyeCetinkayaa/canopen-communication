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
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ConfigurationPanel(QGroupBox):
    BAUD_RATE_OPTIONS = [
        10,
        20,
        50,
        100,
        125,
        250,
        500,
        800,
        1000,
    ]

    DEFAULT_BAUD_RATE = 250

    def __init__(self, parent=None):
        super().__init__(
            "Encoder Configuration",
            parent,
        )

        # Panel içeriğinin kesilmesini engeller.
        self.setMinimumHeight(230)

        # -------------------------------------------------
        # Giriş alanları
        # -------------------------------------------------

        self.new_node_id_input = QLineEdit()
        self.new_node_id_input.setPlaceholderText(
            "Örnek: 40 veya 0x28"
        )

        self.new_baud_rate_combo = QComboBox()

        for baud_rate in self.BAUD_RATE_OPTIONS:
            self.new_baud_rate_combo.addItem(
                f"{baud_rate} kbit/s",
                baud_rate,
            )

        self.set_baud_rate(
            self.DEFAULT_BAUD_RATE
        )

        self.heartbeat_input = QLineEdit("100")
        self.transmission_type_input = QLineEdit("255")
        self.event_time_input = QLineEdit("80")
        self.preset_value_input = QLineEdit("0")

        self.preset_value_input.setPlaceholderText(
            "0 - 4294967295"
        )

        self.heartbeat_input.setReadOnly(True)
        self.transmission_type_input.setReadOnly(True)
        self.event_time_input.setReadOnly(True)

        # Alanların çok yüksek olmasını engeller.
        inputs = [
            self.new_node_id_input,
            self.new_baud_rate_combo,
            self.heartbeat_input,
            self.transmission_type_input,
            self.event_time_input,
            self.preset_value_input,
        ]

        for widget in inputs:
            widget.setMinimumHeight(27)
            widget.setMaximumHeight(30)

        # -------------------------------------------------
        # Butonlar
        # -------------------------------------------------

        self.configure_button = QPushButton(
            "Ayarları Uygula ve Kaydet"
        )
        self.configure_button.setObjectName(
            "primaryButton"
        )

        self.restore_button = QPushButton(
            "Fabrika Ayarlarını Geri Yükle"
        )
        self.restore_button.setObjectName(
            "dangerButton"
        )

        self.configure_button.setFixedSize(
            220,
            38,
        )

        self.restore_button.setFixedSize(
            220,
            38,
        )

        self.configure_button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        self.restore_button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        # -------------------------------------------------
        # Sol form
        # -------------------------------------------------

        form_widget = QWidget()

        form_layout = QFormLayout(
            form_widget
        )

        form_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        form_layout.setHorizontalSpacing(12)

        # Burayı düşük tutuyoruz ki tüm alanlar sığsın.
        form_layout.setVerticalSpacing(4)

        form_layout.addRow(
            "Yeni Node ID:",
            self.new_node_id_input,
        )

        form_layout.addRow(
            "Encoder İçin Yeni Baud Rate:",
            self.new_baud_rate_combo,
        )

        form_layout.addRow(
            "Heartbeat Time (ms):",
            self.heartbeat_input,
        )

        form_layout.addRow(
            "Transmission Type:",
            self.transmission_type_input,
        )

        form_layout.addRow(
            "Event Time (ms):",
            self.event_time_input,
        )

        form_layout.addRow(
            "Preset Value:",
            self.preset_value_input,
        )

        # -------------------------------------------------
        # Sağ buton alanı
        # -------------------------------------------------

        button_widget = QWidget()

        button_layout = QVBoxLayout(
            button_widget
        )

        button_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        button_layout.setSpacing(10)

        button_layout.addStretch()

        button_layout.addWidget(
            self.configure_button
        )

        button_layout.addWidget(
            self.restore_button
        )

        button_layout.addStretch()

        # -------------------------------------------------
        # Ana yatay layout
        # -------------------------------------------------

        main_layout = QHBoxLayout()

        main_layout.setContentsMargins(
            12,
            12,
            12,
            10,
        )

        main_layout.setSpacing(20)

        main_layout.addWidget(
            form_widget,
            stretch=1,
        )

        main_layout.addWidget(
            button_widget,
            stretch=0,
        )

        self.setLayout(
            main_layout
        )

        self.set_encoder_available(False)

    def set_encoder_available(self, available):
        self.configure_button.setEnabled(
            available
        )

        self.restore_button.setEnabled(
            available
        )

    def set_configuring(self):
        self.configure_button.setEnabled(False)
        self.restore_button.setEnabled(False)

        self.configure_button.setText(
            "Yapılandırılıyor..."
        )

    def finish_configuring(self):
        self.configure_button.setText(
            "Ayarları Uygula ve Kaydet"
        )

        self.set_encoder_available(True)

    def set_restoring(self):
        self.configure_button.setEnabled(False)
        self.restore_button.setEnabled(False)

        self.restore_button.setText(
            "Geri Yükleniyor..."
        )

    def finish_restoring(self):
        self.restore_button.setText(
            "Fabrika Ayarlarını Geri Yükle"
        )

        self.set_encoder_available(True)

    def get_node_id_text(self):
        return self.new_node_id_input.text()

    def set_node_id(self, node_id):
        self.new_node_id_input.setText(
            str(node_id)
        )

    def clear_node_id(self):
        self.new_node_id_input.clear()

    def get_selected_baud_rate(self):
        return int(
            self.new_baud_rate_combo.currentData()
        )

    def set_baud_rate(self, baud_rate):
        index = self.new_baud_rate_combo.findData(
            baud_rate
        )

        if index != -1:
            self.new_baud_rate_combo.setCurrentIndex(
                index
            )

    def heartbeat_time(self):
        return int(
            self.heartbeat_input.text()
        )

    def transmission_type(self):
        return int(
            self.transmission_type_input.text()
        )

    def event_time(self):
        return int(
            self.event_time_input.text()
        )

    def preset_value(self):
        value = (
            self.preset_value_input
            .text()
            .strip()
        )

        if not value:
            raise ValueError(
                "Preset Value boş bırakılamaz."
            )

        try:
            preset_value = int(value)

        except ValueError as error:
            raise ValueError(
                "Preset Value tam sayı olmalıdır."
            ) from error

        if not 0 <= preset_value <= 0xFFFFFFFF:
            raise ValueError(
                "Preset Value 0 ile "
                "4294967295 arasında olmalıdır."
            )

        return preset_value