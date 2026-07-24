STYLE = """
QMainWindow {
    background-color: #171a1f;
}

QWidget {
    color: #d8dde5;
    font-family: "Segoe UI";
    font-size: 13px;
}


/* -------------------------------------------------- */
/* GroupBox (Sadeleştirilmiş Başlıklar) */
/* -------------------------------------------------- */

QGroupBox {
    background-color: #20242b;
    border: 1px solid #3a404a;
    border-radius: 4px;

    margin-top: 18px;
    padding: 16px 12px 12px 12px;

    font-size: 13px;
    font-weight: 500;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;

    left: 12px;
    padding: 0 6px;

    color: #8fb7e8;
    background-color: #20242b;

    font-size: 13px;
    font-weight: 500;
}


/* -------------------------------------------------- */
/* Label */
/* -------------------------------------------------- */

QLabel {
    background-color: transparent;
    color: #c7ccd4;
}


/* -------------------------------------------------- */
/* Encoder Information Özel Alanları */
/* -------------------------------------------------- */

QLabel#informationName {
    color: #9da6b2;
    font-size: 12px;
    font-weight: 500;
    padding: 2px 0;
}

QLabel#informationValue {
    color: #dce2ea;
    font-size: 12px;
    font-family: "Consolas";
    font-weight: 600;
}

QLabel#positionTitle {
    color: #8fa0b5;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Pozisyon Değeri - Öne Çıkarılmış Endüstriyel Dijital Ekran */
QLabel#positionValue {
    color: #00e5ff;
    background-color: #0d1117;
    font-family: "Consolas", "Courier New";
    font-size: 26px;
    font-weight: 700;

    border: 1px solid #00b0ff;
    border-radius: 3px;

    padding: 8px 12px;
    min-height: 36px;
}

QLabel#presetTitle {
    color: #8fa0b5;
    font-size: 11px;
    font-weight: 600;
}

QLabel#presetValue {
    color: #e6edf3;
    font-family: "Consolas";
    font-size: 15px;
    font-weight: 600;

    background-color: #151921;
    border: 1px solid #30363d;
    border-radius: 2px;

    padding: 6px 10px;
    min-height: 20px;
}

QFrame#informationDivider {
    background-color: #30363d;
    border: none;
    min-height: 1px;
    max-height: 1px;
}


/* -------------------------------------------------- */
/* LineEdit */
/* -------------------------------------------------- */

QLineEdit {
    background-color: #121519;
    color: #e5e9ef;

    border: 1px solid #3c444f;
    border-radius: 2px;

    padding: 3px 6px;
    min-height: 22px;

    selection-background-color: #2b5278;
}

QLineEdit:hover {
    border-color: #525c6a;
}

QLineEdit:focus {
    border: 1px solid #4b86c5;
}

QLineEdit:read-only {
    background-color: #191c22;
    color: #7d8590;
    border-color: #2e343d;
}


/* -------------------------------------------------- */
/* ComboBox (Aşağı Ok İkonlu) */
/* -------------------------------------------------- */

QComboBox {
    background-color: #121519;
    color: #e5e9ef;

    border: 1px solid #3c444f;
    border-radius: 2px;

    padding: 3px 24px 3px 8px;
    min-height: 22px;
}

QComboBox:hover {
    border-color: #525c6a;
}

QComboBox:focus {
    border-color: #4b86c5;
}

QComboBox:disabled {
    background-color: #191c22;
    color: #6e7681;
    border-color: #2e343d;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;

    border-left-width: 1px;
    border-left-color: #2a3038;
    border-left-style: solid;
    border-top-right-radius: 2px;
    border-bottom-right-radius: 2px;
    background-color: #1a1e24;
}

QComboBox::drop-down:hover {
    background-color: #252b34;
}

QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;

    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8fa0b5;

    margin-right: 1px;
}

QComboBox::down-arrow:hover {
    border-top-color: #00e5ff;
}

QComboBox QAbstractItemView {
    background-color: #20242b;
    color: #d8dde5;

    border: 1px solid #3c444f;
    selection-background-color: #2b5278;
    selection-color: #ffffff;

    outline: none;
}


/* -------------------------------------------------- */
/* Genel Butonlar */
/* -------------------------------------------------- */

QPushButton {
    background-color: #2a3038;
    color: #d8dde5;

    border: 1px solid #454d58;
    border-radius: 2px;

    padding: 4px 10px;
    min-height: 24px;

    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #343b46;
    border-color: #5a6472;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1e2228;
    border-color: #363d47;
}

QPushButton:disabled {
    background-color: #1d2127;
    color: #57606a;
    border-color: #2d333b;
}


/* -------------------------------------------------- */
/* Ana İşlem Butonları (Yapılandır & Fabrika Ayarları) */
/* -------------------------------------------------- */

QPushButton#primaryButton {
    background-color: #1f4e79;
    color: #ffffff;
    border: 1px solid #2d689c;
}

QPushButton#primaryButton:hover {
    background-color: #265d8f;
    border-color: #387bba;
}

QPushButton#primaryButton:pressed {
    background-color: #183e61;
}

QPushButton#dangerButton {
    background-color: #5c282b;
    color: #ffffff;
    border: 1px solid #7d373b;
}

QPushButton#dangerButton:hover {
    background-color: #703135;
    border-color: #964247;
}

QPushButton#dangerButton:pressed {
    background-color: #471f21;
}


/* -------------------------------------------------- */
/* Log Alanı (Genişletilmiş Konsol) */
/* -------------------------------------------------- */

QPlainTextEdit {
    background-color: #0d1117;
    color: #c9d1d9;

    border: 1px solid #30363d;
    border-radius: 3px;

    padding: 10px;

    font-family: "Consolas", "Courier New";
    font-size: 12px;
    line-height: 1.4;

    selection-background-color: #2b5278;
}


/* -------------------------------------------------- */
/* ScrollBar */
/* -------------------------------------------------- */

QScrollBar:vertical {
    background-color: #171a1f;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #3a414d;
    border-radius: 2px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4e5766;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #171a1f;
    height: 8px;
}

QScrollBar::handle:horizontal {
    background-color: #3a414d;
    border-radius: 2px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4e5766;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}


/* -------------------------------------------------- */
/* Mesaj Kutuları */
/* -------------------------------------------------- */

QMessageBox {
    background-color: #20242b;
}

QMessageBox QLabel {
    color: #d8dde5;
}

QMessageBox QPushButton {
    min-width: 68px;
    min-height: 22px;
}


/* -------------------------------------------------- */
/* Sistem Durum Paneli */
/* -------------------------------------------------- */

QLabel#statusTitle {
    color: #768390;
    font-family: "Segoe UI";
    font-size: 10px;
    font-weight: 600;
}

QLabel#statusValue {
    color: #d8dee9;
    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 600;
}

QLabel#statusConnected {
    color: #3ddc97;
    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 700;
}

QLabel#statusDisconnected {
    color: #f47067;
    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 700;
}

QLabel#statusWarning {
    color: #e3b341;
    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 700;
}

QLabel#statusInactive {
    color: #8b949e;
    font-family: "Segoe UI";
    font-size: 13px;
    font-weight: 600;
}

QFrame#statusVerticalDivider {
    background-color: #30363d;
    border: none;
    min-width: 1px;
    max-width: 1px;
}


/* -------------------------------------------------- */
/* Connection Panel Özel Alanları */
/* -------------------------------------------------- */

QLabel#channelValue {
    color: #58a6ff;
    font-family: "Consolas";
    font-weight: 600;
}

QPushButton#connectButton {
    min-width: 105px;
    background-color: #1f4e79;
    border-color: #2d689c;
}

QPushButton#connectButton:hover {
    background-color: #265d8f;
    border-color: #387bba;
}

QPushButton#connectButton[connected="true"] {
    background-color: #5c282b;
    border-color: #7d373b;
}

QPushButton#connectButton[connected="true"]:hover {
    background-color: #703135;
    border-color: #964247;
}

QPushButton#scanButton {
    min-width: 145px;
}
"""


