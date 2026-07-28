STYLE = """
/* ================================================== */
/* GENEL UYGULAMA */
/* ================================================== */

QMainWindow {
    background-color: #15181d;
}

QWidget {
    color: #d6dbe3;
    font-family: "Segoe UI";
    font-size: 13px;
}

QToolTip {
    color: #f0f3f6;
    background-color: #252a32;
    border: 1px solid #484f5a;
    padding: 5px 8px;
}


/* ================================================== */
/* GROUP BOX */
/* ================================================== */

QGroupBox {
    background-color: #1e2229;

    border: 1px solid #363d47;
    border-radius: 6px;

    margin-top: 17px;
    padding: 18px 14px 14px 14px;

    font-size: 13px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;

    left: 13px;
    padding: 0 7px;

    color: #78aee8;
    background-color: #1e2229;

    font-size: 13px;
    font-weight: 600;
}


/* ================================================== */
/* LABEL */
/* ================================================== */

QLabel {
    color: #c8ced8;
    background-color: transparent;
}

QLabel:disabled {
    color: #68717e;
}

/* ================================================== */
/* ENCODER INFORMATION */
/* ================================================== */
QLabel#informationName {
    color: #929dab;
    font-size: 12px;
    font-weight: 500;
    padding: 2px 0;
}

QLabel#informationValue {
    color: #e1e6ed;
    font-family: "Segoe UI";
    font-size: 12px;
    font-weight: 600;
    padding: 2px 0;
}

QLabel#highlightInformationValue {
    color: #65c7f3;
    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 700;
    padding: 2px 0;
}QLabel#informationName {
    color: #929dab;
    font-size: 12px;
    font-weight: 500;
    padding: 2px 0;
}

QLabel#informationValue {
    color: #e1e6ed;
    font-family: "Segoe UI";
    font-size: 12px;
    font-weight: 600;
    padding: 2px 0;
}

QLabel#highlightInformationValue {
    color: #65c7f3;
    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 700;
    padding: 2px 0;
}
/* ================================================== */
/* LINE EDIT */
/* ================================================== */

QLineEdit {
    color: #e4e9ef;
    background-color: #11151a;

    border: 1px solid #3b444f;
    border-radius: 4px;

    padding: 4px 8px;
    min-height: 24px;

    selection-background-color: #315e8b;
    selection-color: #ffffff;
}

QLineEdit:hover {
    border-color: #566270;
}

QLineEdit:focus {
    border: 1px solid #4d91d4;
    background-color: #12171d;
}

QLineEdit:read-only {
    color: #7f8996;
    background-color: #191d23;
    border-color: #303741;
}

QLineEdit:disabled {
    color: #69727f;
    background-color: #191d23;
    border-color: #2c333c;
}


/* ================================================== */
/* COMBO BOX */
/* ================================================== */

QComboBox {
    color: #e4e9ef;
    background-color: #11151a;

    border: 1px solid #3b444f;
    border-radius: 4px;

    padding: 4px 34px 4px 8px;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #566270;
}

QComboBox:focus {
    border-color: #4d91d4;
}

QComboBox:disabled {
    color: #69727f;
    background-color: #191d23;
    border-color: #2c333c;
}

QComboBox::drop-down {
    subcontrol-origin: border;
    subcontrol-position: top right;

    width: 28px;

    background-color: #20262e;

    border-left: 1px solid #3b444f;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

QComboBox::drop-down:hover {
    background-color: #2b333d;
}

QComboBox::down-arrow {
    image: none;

    width: 8px;
    height: 8px;

    border-right: 2px solid #9fb2c8;
    border-bottom: 2px solid #9fb2c8;

    transform: rotate(45deg);

    margin-top: -4px;
}

QComboBox::down-arrow:hover {
    border-color: #ffffff;
}

/* ================================================== */
/* GENEL BUTONLAR */
/* ================================================== */

QPushButton {
    color: #dce2e9;
    background-color: #292f37;

    border: 1px solid #424b56;
    border-radius: 4px;

    padding: 5px 13px;
    min-height: 24px;

    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    color: #ffffff;
    background-color: #343c46;
    border-color: #596575;
}

QPushButton:pressed {
    background-color: #20252c;
    border-color: #353d47;
}

QPushButton:disabled {
    color: #626c78;
    background-color: #1d2127;
    border-color: #2d343d;
}


/* ================================================== */
/* ANA İŞLEM BUTONLARI */
/* ================================================== */

QPushButton#primaryButton {
    color: #ffffff;
    background-color: #245d8f;

    border: 1px solid #3479b4;
    border-radius: 4px;

    min-height: 25px;
}

QPushButton#primaryButton:hover {
    background-color: #2b6da5;
    border-color: #4692d2;
}

QPushButton#primaryButton:pressed {
    background-color: #1d4d77;
}

QPushButton#dangerButton {
    color: #ffffff;
    background-color: #6b2e32;

    border: 1px solid #8a3e43;
    border-radius: 4px;

    min-height: 25px;
}

QPushButton#dangerButton:hover {
    background-color: #7e373c;
    border-color: #a24c52;
}

QPushButton#dangerButton:pressed {
    background-color: #552428;
}


/* ================================================== */
/* CONNECTION PANEL */
/* ================================================== */

QLabel#channelValue {
    color: #64a8ef;

    font-family: "Segoe UI";
    font-size: 12px;
    font-weight: 600;
}

QPushButton#connectButton {
    min-width: 104px;

    color: #ffffff;
    background-color: #245d8f;
    border-color: #3479b4;
}

QPushButton#connectButton:hover {
    background-color: #2b6da5;
    border-color: #4692d2;
}

QPushButton#connectButton[connected="true"] {
    background-color: #6b2e32;
    border-color: #8a3e43;
}

QPushButton#connectButton[connected="true"]:hover {
    background-color: #7e373c;
    border-color: #a24c52;
}

QPushButton#scanButton {
    min-width: 140px;
}


/* ================================================== */
/* SYSTEM STATUS */
/* ================================================== */

QLabel#statusTitle {
    color: #758293;

    font-family: "Segoe UI";
    font-size: 10px;
    font-weight: 600;
}

QLabel#statusValue {
    color: #d8dee7;

    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 500;
}

QLabel#statusConnected {
    color: #42d39c;

    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 600;
}

QLabel#statusDisconnected {
    color: #ef6b67;

    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 600;
}

QLabel#statusWarning {
    color: #ddb454;

    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 600;
}

QLabel#statusInactive {
    color: #8b96a4;

    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 500;
}

QFrame#statusVerticalDivider {
    background-color: #333a44;
    border: none;

    min-width: 1px;
    max-width: 1px;
}


/* ================================================== */
/* ENCODER MONITOR TABLOSU */
/* ================================================== */

QTableWidget {
    color: #dce2e9;
    background-color: #15191f;

    alternate-background-color: #191e25;

    border: 1px solid #343b45;
    border-radius: 5px;

    gridline-color: #303741;

    selection-background-color: #294f74;
    selection-color: #ffffff;

    outline: none;
}

QTableWidget::item {
    padding: 6px;
    border: none;
}

QTableWidget::item:hover {
    background-color: #222933;
}

QTableWidget::item:selected {
    background-color: #294f74;
    color: #ffffff;
}

QHeaderView {
    background-color: #292e35;
}

QHeaderView::section {
    color: #d7dde5;
    background-color: #292e35;

    border: none;
    border-right: 1px solid #3a414b;
    border-bottom: 1px solid #3a414b;

    padding: 6px 8px;

    font-size: 12px;
    font-weight: 600;
}

QHeaderView::section:hover {
    background-color: #333a44;
}

QTableCornerButton::section {
    background-color: #292e35;

    border: none;
    border-right: 1px solid #3a414b;
    border-bottom: 1px solid #3a414b;
}


/* ================================================== */
/* CHECKBOX */
/* ================================================== */

QCheckBox {
    color: #d4dae2;
    spacing: 7px;
}

QCheckBox::indicator {
    width: 15px;
    height: 15px;

    background-color: #12161b;

    border: 1px solid #49535f;
    border-radius: 3px;
}

QCheckBox::indicator:hover {
    border-color: #6595c4;
}

QCheckBox::indicator:checked {
    background-color: #3478b4;
    border-color: #4c94d0;
}


/* ================================================== */
/* LOG ALANI */
/* ================================================== */

QPlainTextEdit {
    color: #cbd4df;
    background-color: #0d1117;

    border: 1px solid #303842;
    border-radius: 5px;

    padding: 10px;

    font-family: "Segoe UI";
    font-size: 12px;

    selection-background-color: #315e8b;
    selection-color: #ffffff;
}

QPlainTextEdit:focus {
    border-color: #3f5872;
}


/* ================================================== */
/* SCROLL BAR */
/* ================================================== */

QScrollBar:vertical {
    background-color: #171b21;

    width: 9px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #3a424d;

    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #535e6c;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollBar:horizontal {
    background-color: #171b21;

    height: 9px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #3a424d;

    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #535e6c;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
}

/* ================================================== */
/* MESAJ KUTULARI */
/* ================================================== */

QMessageBox {
    background-color: #1e2229;
}

QMessageBox QLabel {
    color: #dce2e9;
    font-size: 13px;
    padding: 3px 5px;
}

QMessageBox QPushButton {
    min-width: 82px;
    min-height: 25px;
    padding: 4px 14px;
}

QMessageBox QPushButton:hover {
    background-color: #343c46;
    border-color: #596575;
}

QMessageBox QPushButton:pressed {
    background-color: #20252c;
}

/* ================================================== */
/* SEPARATOR */
/* ================================================== */

QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #333a44;
    background-color: #333a44;
}

/* ================================================== */
/* RADIO BUTTON */
/* ================================================== */

QRadioButton {
    color: #d4dae2;
    spacing: 6px;
}

QRadioButton::indicator {
    width: 14px;
    height: 14px;

    background-color: #11151a;

    border: 1px solid #5a6572;
    border-radius: 7px;
}

QRadioButton::indicator:hover {
    border-color: #6fa8dc;
}

QRadioButton::indicator:checked {
    background-color: #4d91d4;
    border: 1px solid #7cb7ee;
}

QRadioButton::indicator:checked:hover {
    background-color: #3787c9;
    border-color: #a4d3fa;
}

QRadioButton::indicator:disabled {
    background-color: #1b2026;
    border-color: #343b44;
}






"""