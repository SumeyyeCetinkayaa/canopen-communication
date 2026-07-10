"""
Simülasyon ortamında kullanılan CANopen Object Dictionary verilerini içerir.

Gerçek CANopen cihazı yerine kullanılacak örnek Index, Subindex ve
değerler bu dosyada tanımlanmaktadır.
"""
class FakeObjectDictionary:
    def __init__(self):
        self.objects = {
            (0x1000, 0): 0x00001234,   # Device Type
            (0x1018, 1): 0x0000009A,   # Vendor ID
            (0x1018, 2): 0x00003668,   # Product Code
            (0x1018, 4): 0xABCDEF12,   # Serial Number
        }

    def get_value(self, index, subindex):
        key = (index, subindex)

        if key not in self.objects:
            return None

        return self.objects[key]