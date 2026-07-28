"""
Encoder kimlik, pozisyon ve preset bilgilerinin gösterildiği panel.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
)


class EncoderInfoPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Encoder Information", parent)

        self.setFixedWidth(250)

        self.vendor_label = self._create_value_label()
        self.product_label = self._create_value_label()
        self.revision_label = self._create_value_label()
        self.serial_label = self._create_value_label()
        self.position_label = self._create_value_label(
            object_name="highlightInformationValue"
        )
        self.preset_value_label = self._create_value_label(
            object_name="highlightInformationValue"
        )

        layout = QGridLayout()
        layout.setContentsMargins(16, 18, 16, 16)
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(10)

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        self._add_row(
            layout,
            0,
            "Vendor ID:",
            self.vendor_label,
        )
        self._add_row(
            layout,
            1,
            "Product Code:",
            self.product_label,
        )
        self._add_row(
            layout,
            2,
            "Revision Number:",
            self.revision_label,
        )
        self._add_row(
            layout,
            3,
            "Serial Number:",
            self.serial_label,
        )
        self._add_row(
            layout,
            4,
            "Position Value:",
            self.position_label,
        )
        self._add_row(
            layout,
            5,
            "Preset Value:",
            self.preset_value_label,
        )

        layout.setRowStretch(6, 1)

        self.setLayout(layout)

    @staticmethod
    def _create_value_label(object_name="informationValue"):
        label = QLabel("-")
        label.setObjectName(object_name)
        label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        return label

    @staticmethod
    def _add_row(
        layout,
        row,
        title,
        value_label,
    ):
        title_label = QLabel(title)
        title_label.setObjectName("informationName")

        layout.addWidget(
            title_label,
            row,
            0,
        )
        layout.addWidget(
            value_label,
            row,
            1,
        )

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

        self.set_position(information.position)

        preset_value = getattr(
            information,
            "preset_value",
            None,
        )
        self.set_preset_value(preset_value)

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
            self.preset_value_label.setText(
                str(preset_value)
            )