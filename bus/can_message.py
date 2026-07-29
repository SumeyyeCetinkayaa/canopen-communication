"""
CAN Bus üzerinde gönderilen veya alınan bir CAN mesajını temsil eder.

Bir CAN mesajı;
- Arbitration ID
- Data Length Code (DLC)
- Data
bilgilerinden oluşur.

Projedeki tüm CANopen mesajları bu sınıf kullanılarak taşınmaktadır.
"""


class CanMessage:
    def __init__(self, arbitration_id, data):
        if not 0 <= arbitration_id <= 0x7FF:
            raise ValueError("Standart CAN ID 0x000-0x7FF arasında olmalıdır.")

        if len(data) > 8:
            raise ValueError("Klasik CAN mesajı en fazla 8 byte olabilir.")

        if any(not 0 <= byte <= 0xFF for byte in data):
            raise ValueError("Her veri elemanı 0-255 arasında olmalıdır.")

        self.arbitration_id = arbitration_id
        self.data = list(data)
        self.dlc = len(data)

#ileride mesaj formatlama işlemlerini kolaylaştırmak için kullanılacak bir yardımcı fonksiyon.
def format_can_message(msg):
    return str(msg)