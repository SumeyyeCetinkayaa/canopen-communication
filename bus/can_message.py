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
        self.arbitration_id = arbitration_id #mesaj ID'sini saklar
        self.data = data #mesajın veri içeriğini saklar
        self.dlc = len(data) #mesajın veri uzunluğunu saklar (DLC: Data Length Code)

    def __str__(self):
        data_text = " ".join(f"{byte:02X}" for byte in self.data)

        return (
            f"ID: 0x{self.arbitration_id:X} | "
            f"DLC: {self.dlc} | "
            f"DATA: {data_text}"
        )

#ileride mesaj formatlama işlemlerini kolaylaştırmak için kullanılacak bir yardımcı fonksiyon.
def format_can_message(msg):
    return str(msg)