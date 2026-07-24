"""
CAN bağlantısı için kullanılan arayüz paneli.
"""

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
)


class ConnectionPanel(QGroupBox):
    BAUD_RATE_OPTIONS = [10, 20, 50, 100, 125, 250, 500, 800, 1000]
    DEFAULT_BAUD_RATE = 250
    DEFAULT_CHANNEL = "PCAN_USBBUS1"

    def __init__(self, parent=None):
        super().__init__("Connection", parent)

        self.channel_value_label = QLabel(self.DEFAULT_CHANNEL)

        self.baud_rate_combo = QComboBox()
        for baud_rate in self.BAUD_RATE_OPTIONS:
            self.baud_rate_combo.addItem(
                f"{baud_rate} kbit/s",
                baud_rate,
            )

        self.baud_rate_combo.setCurrentText(
            f"{self.DEFAULT_BAUD_RATE} kbit/s"
        )

        self.connect_button = QPushButton("Bağlan")

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Kanal:"))
        layout.addWidget(self.channel_value_label)
        layout.addSpacing(20)
        layout.addWidget(QLabel("Mevcut CAN Baud Rate:"))
        layout.addWidget(self.baud_rate_combo)
        layout.addStretch()
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def get_selected_baud_rate_kbit(self):
        return int(self.baud_rate_combo.currentData())

    def get_selected_baud_rate(self):
        return self.get_selected_baud_rate_kbit() * 1000

    def set_baud_rate(self, baud_rate_kbit):
        index = self.baud_rate_combo.findData(baud_rate_kbit)

        if index == -1:
            raise ValueError(
                f"Desteklenmeyen baud rate: {baud_rate_kbit} kbit/s"
            )

        self.baud_rate_combo.setCurrentIndex(index)

    def set_channel(self, channel):
        self.channel_value_label.setText(str(channel))

    def set_connected(self, connected):
        if connected:
            self.connect_button.setText("Bağlantıyı Kes")
            self.baud_rate_combo.setEnabled(False)
        else:
            self.connect_button.setText("Bağlan")
            self.baud_rate_combo.setEnabled(True)

        self.connect_button.setEnabled(True)

    def set_connecting(self):
        self.connect_button.setText("Bağlanıyor...")
        self.connect_button.setEnabled(False)
        self.baud_rate_combo.setEnabled(False)

    def set_enabled(self, enabled):
        self.connect_button.setEnabled(enabled)
        self.baud_rate_combo.setEnabled(enabled)