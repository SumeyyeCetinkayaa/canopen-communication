# CANopen Encoder Configuration Project

Proje, PEAK PCAN-USB adaptörü üzerinden Baumer EAM360 CANopen encoder ile haberleşmek, veri okumak ve cihaz parametrelerini yapılandırmak amacıyla geliştirilmiştir.  

Uygulama Python dili ile yazılmış olup, alt yapıda `python-can` kütüphanesini ve özel geliştirilmiş CANopen protokol katmanlarını kullanmaktadır.  






## Projenin Amacı

Uygulama aşağıdaki işlemleri gerçekleştirir:

- Encoder ile CANopen üzerinden haberleşme
- SDO Read işlemleri
- SDO Write işlemleri
- Node ID değiştirme
- Baud rate değiştirme
- Producer Heartbeat Time ayarlama
- TPDO Transmission Type ayarlama
- TPDO Event Time ayarlama
- Ayarları kalıcı hafızaya kaydetme
- NMT Reset Communication gönderme
- Yeni Node ID ve baud rate ile bağlantıyı yeniden kurma
- Yazılan değerleri tekrar okuyarak doğrulama


## Projenin Amacı

Uygulama aşağıdaki işlemleri gerçekleştirir:

- Encoder ile CANopen üzerinden haberleşme
- SDO Read işlemleri
- SDO Write işlemleri
- Node ID değiştirme
- Baud rate değiştirme
- Producer Heartbeat Time ayarlama
- TPDO Transmission Type ayarlama
- TPDO Event Time ayarlama
- Ayarları kalıcı hafızaya kaydetme
- NMT Reset Communication gönderme
- Yeni Node ID ve baud rate ile bağlantıyı yeniden kurma
- Yazılan değerleri tekrar okuyarak doğrulama

## Kullanılan Donanım

- PEAK PCAN-USB CAN adaptörü
- Baumer EAM360 CANopen encoder
- 24 V DC güç kaynağı
- CAN hattı
- 120 ohm sonlandırma direnci

Test edilen encoder modeli: `EAM360-SWA.7NC6.14180.A`

## Kullanılan Yazılımlar

- Python
- python-can
- PEAK PCAN sürücüsü
- PCAN-View
- Visual Studio Code
- Git

## Proje Yapısı

```text
canopen-communication/
│
├── bus/                         # CAN haberleşme katmanı
│   ├── __init__.py
│   ├── can_bus.py               # Ortak CAN arayüzü / soyut sınıf
│   ├── can_message.py           # CAN mesaj modeli
│   └── real_can.py              # Gerçek PCAN-USB haberleşmesi
│
├── canopen/                     # CANopen protokol katmanı
│   ├── __init__.py
│   ├── client.py                # CANopen istemcisi
│   ├── encoder_configurator.py  # Encoder yapılandırma işlemleri
│   ├── encoder_reader.py        # Encoder veri okuma işlemleri
│   ├── nmt.py                   # NMT komutları
│   ├── node_scanner.py          # Ağ üzerindeki düğümleri tarama
│   ├── object_dictionary.py     # Object Dictionary sabitleri ve tanımları
│   └── sdo.py                   # SDO Read / Write işlemleri
│
├── services/                    # Servis katmanı
│   ├── __init__.py
│   └── encoder_controller.py    # Arayüz ve protokol arasındaki kontrolör
│
├── ui/                          # Grafik kullanıcı arayüzü (GUI)
│   ├── __init__.py
│   ├── configuration_panel.py   # Yapılandırma paneli
│   ├── connection_panel.py      # Bağlantı ayarları paneli
│   ├── encoder_info_panel.py    # Encoder bilgi paneli
│   ├── encoder_table_panel.py   # Encoder tablo / tarama paneli
│   ├── main_window.py           # Ana pencere
│   ├── status_panel.py          # Durum ve log paneli
│   └── styles.py                # Arayüz stilleri (CSS/QSS)
│
├── .gitignore
├── README.md
├── config.py                    # Genel yapılandırma
├── encoder_state.py             # Encoder durum modeli
├── gui_main.py                  # Arayüzlü uygulama başlangıç noktası
├── main.py                      # Konsol / temel başlangıç noktası
└── requirements.txt             # Gerekli Python paketleri
```



## Katmanlı Mimari

### Kullanıcı Arayüzü & Uygulama Katmanı

`gui_main.py`

Grafik kullanıcı arayüzünü (GUI) başlatır ve uygulamayı çalıştırır.

`main.py`

Uygulamanın konsol üzerinden çalışan başlangıç noktasıdır.

`ui/`

Kullanıcı arayüz panellerini (`main_window.py`, `configuration_panel.py`, `connection_panel.py`, `encoder_info_panel.py`, `encoder_table_panel.py`, `status_panel.py`) ve stil dosyalarını (`styles.py`) içerir.

`services/encoder_controller.py`

Arayüz ile CANopen katmanı arasında köprü görevi görerek encoder işlemlerini yönetir.

### CANopen Katmanı

`canopen/client.py`

SDO ve NMT işlemlerini yönetir.

`canopen/sdo.py`

SDO Read ve SDO Write mesajlarını oluşturur ve gelen cevapları işler.

`canopen/nmt.py`

NMT komutlarını (Reset, Start vb.) oluşturur ve yönetir.

`canopen/object_dictionary.py`

Kullanılan CANopen Object Dictionary adreslerini ve dizin tanımlarını içerir.

`canopen/encoder_configurator.py`

Encoder ayarlarını yazar, geri okur, doğrular ve kalıcı hafızaya kaydeder.

`canopen/encoder_reader.py`

Encoder üzerindeki pozisyon ve durum verilerini okur.

`canopen/node_scanner.py`

Ağ üzerindeki aktif CANopen düğümlerini (Node) tarar ve tespit eder.

### CAN Haberleşme Katmanı

`bus/can_bus.py`

CAN adaptörleri için soyut (abstract) temel arayüzü tanımlar.

`bus/real_can.py`

PEAK PCAN-USB üzerinden gerçek CAN haberleşmesini gerçekleştirir.

`bus/can_message.py`

CAN mesaj yapısını ve veri modelini temsil eder.




## CANopen Haberleşme Bilgileri

CANopen SDO COB-ID değerleri Node ID kullanılarak hesaplanır.

```text
SDO Request COB-ID  = 0x600 + Node ID
SDO Response COB-ID = 0x580 + Node ID
Heartbeat COB-ID    = 0x700 + Node ID
```

Örnek olarak Node ID `0x5B` için:

```text
SDO Request COB-ID  = 0x65B
SDO Response COB-ID = 0x5DB
Heartbeat COB-ID    = 0x75B
```

## Kullanılan Object Dictionary Nesneleri

| İşlem                       | Index    | Subindex |
|---                          |---:      |---:      |
| Device Type                 | `0x1000` | `0`      |
| Store Parameters            | `0x1010` | `1`      |
| Producer Heartbeat Time     | `0x1017` | `0`      |
| TPDO1 Transmission Type     | `0x1800` | `2`      |
| TPDO1 Event Time            | `0x1800` | `5`      |
| Baud Rate                   | `0x2100` | `0`      |
| Node ID                     | `0x2101` | `0`      |
| Position Value              | `0x6004` | `0`      |

## Sabit Yapılandırma Değerleri

Proje gereksinimine göre aşağıdaki değerler kullanılır:

```text
Producer Heartbeat Time = 100 ms
Transmission Type       = 255
Event Time              = 80 ms
```

Node ID ve baud rate kullanıcı tarafından girilir.

## Desteklenen Baud Rate Değerleri

```text
10 kbit/s
20 kbit/s
50 kbit/s
100 kbit/s
125 kbit/s
250 kbit/s
500 kbit/s
800 kbit/s
1000 kbit/s
```

Encoder baud rate kodları:

| Baud Rate | Kod |
|---:|---:|
| 10 kbit/s | 0 |
| 20 kbit/s | 1 |
| 50 kbit/s | 2 |
| 100 kbit/s | 3 |
| 125 kbit/s | 4 |
| 250 kbit/s | 5 |
| 500 kbit/s | 6 |
| 800 kbit/s | 7 |
| 1000 kbit/s | 8 |


## Kurulum

### 1. Proje klasörüne geçiş

```powershell
cd canopen-communication

```

### 2. Sanal ortam oluşturma

```powershell
python -m venv venv

```

### 3. Sanal ortamı etkinleştirme

```powershell
.\venv\Scripts\Activate.ps1

```

### 4. Gerekli paketleri yükleme

```powershell
pip install -r requirements.txt

```

## PCAN Ayarları

`config.py` dosyasında varsayılan bağlantı ve zaman aşımı değerleri tanımlıdır:

```python
CHANNEL = "PCAN_USBBUS1"
BITRATE = 250000
READ_TIMEOUT = 1.0

```

Program, arayüz üzerinden yapılandırma yapılırken veya baud rate değiştirildiğinde PCAN bağlantısını otomatik olarak yeni ayarlar ile yeniden başlatır.

## Programı Çalıştırma

PCAN-View veya diğer CAN araçları kapatıldıktan sonra grafik arayüzü başlatmak için:

```powershell
python gui_main.py

```

*(Not: İstenirse `python main.py` ile konsol sürümü de çalıştırılabilir.)*

## Kullanıcı Arayüzü (GUI) Kullanımı

Uygulama açıldığında tüm işlemler ekran üzerindeki panellerden gerçekleştirilir:

1. **Bağlantı Paneli (Connection Panel):** PCAN kanalı ve mevcut Baud Rate seçilerek encoder bağlantısı kurulur.
2. **Düğüm Tarama (Node Scanner):** Ağdaki aktif encoder'ları tespit etmek için tarama başlatılır.
3. **Yapılandırma Paneli (Configuration Panel):**
* Yeni **Node ID** ve **Baud Rate** değerleri girilir.
* **Producer Heartbeat Time**, **TPDO Transmission Type** ve **Event Time** parametreleri belirlenir.


4. **Uygula ve Kaydet:** Yapılan ayarlar encoder'a yazılır, doğrulanır ve kalıcı hafızaya (EEPROM) kaydedilir.
5. **Durum ve Log Paneli:** Tüm SDO/NMT işlemleri ve yanıtları canlı olarak log ekranından takip edilebilir.


## Yapılandırma Akışı

Kullanıcı arayüz üzerinden yapılandırma işlemini başlattığında arka planda aşağıdaki sıra izlenir:

1. Mevcut Node ID ve baud rate ile CAN bağlantısı açılır.
2. Producer Heartbeat Time değeri yazılır.
3. Transmission Type değeri yazılır.
4. Event Time değeri yazılır.
5. Yeni Node ID değeri yazılır.
6. Yeni baud rate kodu yazılır.
7. Yazılan her değer geri okunarak doğrulanır.
8. Ayarlar kalıcı hafızaya kaydedilir.
9. NMT Reset Communication komutu gönderilir.
10. PCAN bağlantısı yeni baud rate ile yeniden açılır.
11. Encoder heartbeat mesajı beklenir.
12. CANopen istemcisi yeni Node ID ile güncellenir.
13. Yeni bağlantı bilgileri üzerinden SDO haberleşmesi doğrulanır.
14. Node ID ve baud rate değerleri tekrar okunarak son kontrol yapılır.


## Kalıcı Hafızaya Kaydetme

Ayarların kalıcı olması için CANopen Store Parameters nesnesi kullanılır:

```text
Index    : 0x1010
Subindex : 1
Değer    : 0x65766173

```

Bu değer little-endian olarak CAN mesajına aşağıdaki şekilde yerleştirilir:

```text
73 61 76 65

```

Bu veri ASCII olarak `save` ifadesine karşılık gelir.

## NMT Reset Communication

Yeni Node ID ve baud rate değerlerinin aktif olması için NMT Reset Communication komutu gönderilir:

```text
CAN-ID  : 0x000
DATA[0] : 0x82
DATA[1] : Mevcut Node ID

```

Reset komutu mevcut Node ID üzerinden gönderilir. Encoder yeniden başladıktan sonra yeni Node ID ve yeni baud rate kullanılır.


## Test Sonuçları

Gerçek donanım üzerinde aşağıdaki işlemler başarıyla doğrulanmıştır:

* SDO Read
* SDO Write
* Producer Heartbeat Time yazma ve okuma
* Transmission Type yazma ve okuma
* Event Time yazma ve okuma
* Node ID değişimi
* Baud rate değişimi
* Kalıcı hafızaya kayıt
* NMT Reset Communication
* Yeni baud rate ile PCAN bağlantısını yeniden açma
* Yeni Node ID üzerinden heartbeat alma
* Yeni Node ID üzerinden SDO haberleşmesi
* Reset sonrasında Node ID ve baud rate doğrulaması


Başarılı gerçek testlerden biri:

```text
Eski Node ID   : 0x5A
Yeni Node ID   : 0x5B
Eski Baud Rate : 500 kbit/s
Yeni Baud Rate : 250 kbit/s

```

Test sonunda encoder aşağıdaki değerlerle doğrulanmıştır:

```text
Node ID                 : 0x5B
Baud Rate               : 250 kbit/s
Producer Heartbeat Time : 100 ms
Transmission Type       : 255
Event Time              : 80 ms

```

## Dikkat Edilmesi Gerekenler

* PCAN-View veya başka bir uygulama ile Python programı aynı anda PCAN kanalını kullanmamalıdır.
* Mevcut Node ID doğru girilmelidir.
* Mevcut baud rate doğru girilmelidir.
* Yanlış baud rate seçilirse CAN controller bus-off durumuna geçebilir.
* Baud rate değişiminden sonra PCAN bağlantısı yeni hızla yeniden açılmalıdır.
* Node ID değişiminden sonra SDO ve heartbeat COB-ID değerleri değişir.
* CAN hattında uygun sonlandırma direnci bulunmalıdır.
* Encoder güç bağlantısı ve CAN-H / CAN-L bağlantıları kontrol edilmelidir.

## Güncel Encoder Durumu

Son başarılı testten sonra encoder:

```text
Node ID   : 0x5B
Baud Rate : 250 kbit/s

```

değerleriyle çalışmaktadır.


## Geliştirme Durumu

Projenin temel fonksiyonları ve kullanıcı arayüzü tamamlanmıştır.

Tamamlanan özellikler:

* CAN bağlantısı
* SDO Read / SDO Write
* NMT komutları
* Encoder parametre yapılandırması
* Kalıcı hafızaya kayıt
* Node ID değişimi
* Baud rate değişimi
* Otomatik düğüm (node) tarama
* Grafik kullanıcı arayüzü (GUI)
* Reset sonrası doğrulama