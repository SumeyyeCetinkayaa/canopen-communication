"""
Encoder kimlik, pozisyon ve preset bilgilerinin gösterildiği panel.
"""

from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel


class EncoderInfoPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Encoder Information", parent)
        self.setFixedWidth(230)
        self.vendor_label = QLabel("-")
        self.product_label = QLabel("-")
        self.revision_label = QLabel("-")
        self.serial_label = QLabel("-")
        self.position_label = QLabel("-")
        self.preset_value_label = QLabel("-")

        layout = QFormLayout()
        layout.addRow("Vendor ID:", self.vendor_label)
        layout.addRow("Product Code:", self.product_label)
        layout.addRow("Revision Number:", self.revision_label)
        layout.addRow("Serial Number:", self.serial_label)
        layout.addRow("Position Value:", self.position_label)
        layout.addRow("Preset Value:", self.preset_value_label)

        self.setLayout(layout)

    @staticmethod
    def _format_hex(value):
        if value is None:
            return "-"

        return f"0x{value:08X}"

    def set_information(self, information):
        self.vendor_label.setText(
            self._format_hex(information.vendor_id)
        )
        self.product_label.setText(
            self._format_hex(information.product_code)
        )
        self.revision_label.setText(
            self._format_hex(information.revision_number)
        )
        self.serial_label.setText(
            self._format_hex(information.serial_number)
        )

        if information.position is None:
            self.position_label.setText("-")
        else:
            self.position_label.setText(
                str(information.position)
            )

        preset_value = getattr(
            information,
            "preset_value",
            None,
        )

        if preset_value is None:
            self.preset_value_label.setText("-")
        else:
            self.preset_value_label.setText(
                str(preset_value)
            )

    def clear(self):
        self.vendor_label.setText("-")
        self.product_label.setText("-")
        self.revision_label.setText("-")
        self.serial_label.setText("-")
        self.position_label.setText("-")
        self.preset_value_label.setText("-")

    def set_position(self, position):
        if position is None:
            self.position_label.setText("-")
        else:
            self.position_label.setText(str(position))        

    def set_preset_value(self, preset_value):
        if preset_value is None:
            self.preset_value_label.setText("-")
        else:
            self.preset_value_label.setText(str(preset_value))