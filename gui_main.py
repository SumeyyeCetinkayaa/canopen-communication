"""
PySide6 tabanlı CANopen Encoder Configuration Tool.

Bu dosya uygulamanın giriş noktasıdır.
Ana pencereyi oluşturur ve çalıştırır.
"""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()