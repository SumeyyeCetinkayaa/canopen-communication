"""
CAN bağlantısı ve encoder durumunu gösteren panel.
"""

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class StatusItem(QWidget):
    """
    Durum panelindeki tek bir bilgi alanını temsil eder.
    """

    def __init__(
        self,
        title,
        value="--",
        value_object_name="statusValue",
        parent=None,
    ):
        super().__init__(parent)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statusTitle")

        self.value_label = QLabel(str(value))
        self.value_label.setObjectName(
            value_object_name
        )

        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))

    def set_value_object_name(self, object_name):
        """
        Duruma göre farklı stylesheet uygulanmasını sağlar.
        """

        self.value_label.setObjectName(object_name)

        # Qt stylesheet'in yeni objectName'i hemen algılaması için.
        self.value_label.style().unpolish(
            self.value_label
        )
        self.value_label.style().polish(
            self.value_label
        )


class StatusPanel(QGroupBox):
    """
    CAN bağlantısı ve encoder durumunu gösterir.
    """

    def __init__(self, parent=None):
        super().__init__("System Status", parent)

        self.connection_item = StatusItem(
            title="CAN CONNECTION",
            value="Disconnected",
            value_object_name="statusDisconnected",
        )

        self.encoder_state_item = StatusItem(
            title="ENCODER STATE",
            value="Not Detected",
            value_object_name="statusInactive",
        )

        self.node_id_item = StatusItem(
            title="NODE ID",
            value="--",
        )

        self.baud_rate_item = StatusItem(
            title="BAUD RATE",
            value="--",
        )

        self.heartbeat_item = StatusItem(
            title="HEARTBEAT",
            value="--",
        )

        self.last_communication_item = StatusItem(
            title="LAST COMMUNICATION",
            value="--",
        )

        self._create_layout()

    def _create_layout(self):
        layout = QGridLayout(self)

        layout.setContentsMargins(10, 12, 10, 8)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(4)

        items = [
            self.connection_item,
            self.encoder_state_item,
            self.node_id_item,
            self.baud_rate_item,
            self.heartbeat_item,
            self.last_communication_item,
        ]

        for column, item in enumerate(items):
            layout.addWidget(item, 0, column)

            if column < len(items) - 1:
                divider = QFrame()
                divider.setObjectName(
                    "statusVerticalDivider"
                )
                divider.setFrameShape(
                    QFrame.Shape.VLine
                )

                layout.addWidget(
                    divider,
                    0,
                    column,
                    1,
                    1,
                    Qt.AlignmentFlag.AlignRight,
                )

            layout.setColumnStretch(column, 1)

    def set_connecting(self):
        self.connection_item.set_value(
            "Connecting..."
        )
        self.connection_item.set_value_object_name(
            "statusWarning"
        )

        self.encoder_state_item.set_value(
            "Waiting"
        )
        self.encoder_state_item.set_value_object_name(
            "statusInactive"
        )

    def set_connected(self, baud_rate_kbit):
        self.connection_item.set_value(
            "Connected"
        )
        self.connection_item.set_value_object_name(
            "statusConnected"
        )

        self.baud_rate_item.set_value(
            f"{baud_rate_kbit} kbit/s"
        )

        self.update_last_communication()

    def set_disconnected(self):
        self.connection_item.set_value(
            "Disconnected"
        )
        self.connection_item.set_value_object_name(
            "statusDisconnected"
        )

        self.clear_encoder()

        self.baud_rate_item.set_value("--")
        self.last_communication_item.set_value("--")

    def set_scanning(self):
        self.encoder_state_item.set_value(
            "Scanning..."
        )
        self.encoder_state_item.set_value_object_name(
            "statusWarning"
        )

    def set_encoder_detected(
        self,
        node_id,
        baud_rate_kbit,
        heartbeat_time_ms=None,
    ):
        self.encoder_state_item.set_value(
            "Online"
        )
        self.encoder_state_item.set_value_object_name(
            "statusConnected"
        )

        self.node_id_item.set_value(
            f"0x{node_id:02X} ({node_id})"
        )

        self.baud_rate_item.set_value(
            f"{baud_rate_kbit} kbit/s"
        )

        if heartbeat_time_ms is not None:
            self.heartbeat_item.set_value(
                f"{heartbeat_time_ms} ms"
            )

        self.update_last_communication()

    def set_configuring(self):
        self.encoder_state_item.set_value(
            "Configuring..."
        )
        self.encoder_state_item.set_value_object_name(
            "statusWarning"
        )

    def set_restoring(self):
        self.encoder_state_item.set_value(
            "Restoring..."
        )
        self.encoder_state_item.set_value_object_name(
            "statusWarning"
        )

    def set_error(self):
        self.encoder_state_item.set_value(
            "Communication Error"
        )
        self.encoder_state_item.set_value_object_name(
            "statusDisconnected"
        )

    def set_heartbeat(self, heartbeat_time_ms):
        self.heartbeat_item.set_value(
            f"{heartbeat_time_ms} ms"
        )

    def update_last_communication(self):
        current_time = QDateTime.currentDateTime()

        self.last_communication_item.set_value(
            current_time.toString("HH:mm:ss")
        )

    def clear_encoder(self):
        self.encoder_state_item.set_value(
            "Not Detected"
        )
        self.encoder_state_item.set_value_object_name(
            "statusInactive"
        )

        self.node_id_item.set_value("--")
        self.heartbeat_item.set_value("--")