"""
Ağda bulunan encoderları tablo halinde gösterir.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QGroupBox,
    QHeaderView,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)


class EncoderTablePanel(QGroupBox):
    encoder_selected = Signal(int)

    SELECT_COLUMN = 0
    NODE_COLUMN = 1
    SERIAL_COLUMN = 2
    POSITION_COLUMN = 3
    STATUS_COLUMN = 4

    def __init__(self, parent=None):
        super().__init__("Encoder Monitor", parent)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.table = QTableWidget(0, 5)

        self.table.setHorizontalHeaderLabels(
            [
                "Seç",
                "Node ID",
                "Serial Number",
                "Position",
                "Status",
            ]
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectItems
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.setAlternatingRowColors(True)

        self.table.setMinimumHeight(90)
        self.table.setMaximumHeight(125)

        self.table.verticalHeader().setVisible(False)

        self.table.verticalHeader().setDefaultSectionSize(
            30
        )

        self.table.horizontalHeader().setFixedHeight(
            30
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            self.SELECT_COLUMN,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            self.NODE_COLUMN,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            self.SERIAL_COLUMN,
            QHeaderView.ResizeMode.Stretch,
        )

        header.setSectionResizeMode(
            self.POSITION_COLUMN,
            QHeaderView.ResizeMode.Stretch,
        )

        header.setSectionResizeMode(
            self.STATUS_COLUMN,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.table.itemSelectionChanged.connect(
            self._selection_changed
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            8,
            10,
            8,
            8,
        )

        layout.setSpacing(4)

        layout.addWidget(
            self.table
        )

        self.setMaximumHeight(155)

    @staticmethod
    def _node_text(node_id):
        return f"0x{node_id:02X} ({node_id})"

    @staticmethod
    def _serial_text(serial_number):
        if serial_number is None:
            return "-"

        return f"0x{serial_number:08X}"

    def clear(self):
        self.table.setRowCount(0)

        for button in self.button_group.buttons():
            self.button_group.removeButton(
                button
            )

    def add_encoder(
        self,
        node_id,
        serial_number=None,
        position=None,
        status="Online",
    ):
        row = self.table.rowCount()

        self.table.insertRow(row)

        # -----------------------------------------
        # Seçim radyo butonu
        # -----------------------------------------

        radio_button = QRadioButton()

        radio_button.setProperty(
            "node_id",
            node_id,
        )

        radio_button.clicked.connect(
            lambda checked, current_node_id=node_id:
            self._radio_selected(
                current_node_id
            )
        )

        self.button_group.addButton(
            radio_button
        )

        radio_container = QWidget()

        radio_layout = QHBoxLayout(
            radio_container
        )

        radio_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        radio_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        radio_layout.addWidget(
            radio_button
        )

        self.table.setCellWidget(
            row,
            self.SELECT_COLUMN,
            radio_container,
        )

        # -----------------------------------------
        # Diğer hücreler
        # -----------------------------------------

        node_item = QTableWidgetItem(
            self._node_text(node_id)
        )

        node_item.setData(
            Qt.ItemDataRole.UserRole,
            node_id,
        )

        serial_item = QTableWidgetItem(
            self._serial_text(serial_number)
        )

        position_item = QTableWidgetItem(
            (
                "-"
                if position is None
                else str(position)
            )
        )

        status_item = QTableWidgetItem(
            status
        )

        node_item.setTextAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        serial_item.setTextAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        position_item.setTextAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        status_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.table.setItem(
            row,
            self.NODE_COLUMN,
            node_item,
        )

        self.table.setItem(
            row,
            self.SERIAL_COLUMN,
            serial_item,
        )

        self.table.setItem(
            row,
            self.POSITION_COLUMN,
            position_item,
        )

        self.table.setItem(
            row,
            self.STATUS_COLUMN,
            status_item,
        )

        self.table.setRowHeight(
            row,
            30,
        )

    def _find_row(self, node_id):
        for row in range(
            self.table.rowCount()
        ):
            item = self.table.item(
                row,
                self.NODE_COLUMN,
            )

            if (
                item is not None
                and item.data(
                    Qt.ItemDataRole.UserRole
                )
                == node_id
            ):
                return row

        return -1

    def update_position(
        self,
        node_id,
        position,
        status="Online",
    ):
        row = self._find_row(
            node_id
        )

        if row == -1:
            return

        position_item = self.table.item(
            row,
            self.POSITION_COLUMN,
        )

        status_item = self.table.item(
            row,
            self.STATUS_COLUMN,
        )

        if position_item is not None:
            position_item.setText(
                (
                    "-"
                    if position is None
                    else str(position)
                )
            )

        if status_item is not None:
            status_item.setText(
                status
            )

    def set_offline(self, node_id):
        row = self._find_row(
            node_id
        )

        if row == -1:
            return

        status_item = self.table.item(
            row,
            self.STATUS_COLUMN,
        )

        if status_item is not None:
            status_item.setText(
                "Offline"
            )

    def select_node(self, node_id):
        row = self._find_row(
            node_id
        )

        if row == -1:
            return

        radio_container = self.table.cellWidget(
            row,
            self.SELECT_COLUMN,
        )

        if radio_container is not None:
            radio_button = (
                radio_container.findChild(
                    QRadioButton
                )
            )

            if radio_button is not None:
                radio_button.setChecked(
                    True
                )

        self.table.blockSignals(
            True
        )

        self.table.selectRow(
            row
        )

        self.table.blockSignals(
            False
        )

    def update_node_id(
        self,
        old_node_id,
        new_node_id,
    ):
        row = self._find_row(
            old_node_id
        )

        if row == -1:
            return

        node_item = self.table.item(
            row,
            self.NODE_COLUMN,
        )

        if node_item is not None:
            node_item.setText(
                self._node_text(
                    new_node_id
                )
            )

            node_item.setData(
                Qt.ItemDataRole.UserRole,
                new_node_id,
            )

        radio_container = self.table.cellWidget(
            row,
            self.SELECT_COLUMN,
        )

        if radio_container is not None:
            radio_button = (
                radio_container.findChild(
                    QRadioButton
                )
            )

            if radio_button is not None:
                radio_button.setProperty(
                    "node_id",
                    new_node_id,
                )

                try:
                    radio_button.clicked.disconnect()
                except TypeError:
                    pass

                radio_button.clicked.connect(
                    lambda checked, current_node_id=new_node_id:
                    self._radio_selected(
                        current_node_id
                    )
                )

    def _radio_selected(self, node_id):
        row = self._find_row(
            node_id
        )

        if row != -1:
            self.table.blockSignals(
                True
            )

            self.table.selectRow(
                row
            )

            self.table.blockSignals(
                False
            )

        self.encoder_selected.emit(
            int(node_id)
        )

    def _selection_changed(self):
        selected_rows = (
            self.table
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            return

        row = selected_rows[0].row()

        node_item = self.table.item(
            row,
            self.NODE_COLUMN,
        )

        if node_item is None:
            return

        node_id = node_item.data(
            Qt.ItemDataRole.UserRole
        )

        if node_id is None:
            return

        radio_container = self.table.cellWidget(
            row,
            self.SELECT_COLUMN,
        )

        if radio_container is not None:
            radio_button = (
                radio_container.findChild(
                    QRadioButton
                )
            )

            if radio_button is not None:
                radio_button.setChecked(
                    True
                )

        self.encoder_selected.emit(
            int(node_id)
        )