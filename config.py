"""
Proje genelinde kullanılan yapılandırma ayarlarını içerir.

Bu dosyada;
- CAN arayüzü
- Bitrate
- Gerçek veya simülasyon modu
gibi uygulama boyunca ortak kullanılacak ayarlar tutulur.
"""

USE_REAL_CAN = False

CHANNEL = "PCAN_USBBUS1"
BITRATE = 250000
READ_TIMEOUT = 1.0