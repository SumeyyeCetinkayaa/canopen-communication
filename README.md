# CANopen Encoder Configuration Project

Bu proje, PEAK PCAN-USB adaptörü üzerinden Baumer EAM360 CANopen encoder ile haberleşmek ve encoder ayarlarını yapılandırmak amacıyla geliştirilmiştir.

Uygulama Python ile yazılmıştır ve `python-can` kütüphanesini kullanır.

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
CANOPEN_PROJECT/
│
├── bus/                         # CAN haberleşme katmanı
│   ├── can_bus.py               # Ortak CAN arayüzü
│   ├── can_message.py           # CAN mesaj modeli
│   ├── real_can.py              # Gerçek PCAN-USB haberleşmesi
│   ├── fake_can.py              # Simülasyon CAN arayüzü
│   └── fake_object_dictionary.py
│
├── canopen/                     # CANopen protokol katmanı
│   ├── client.py                # CANopen istemcisi
│   ├── sdo.py                   # SDO Read / Write
│   ├── nmt.py                   # NMT komutları
│   ├── pdo.py                   # PDO yapıları
│   ├── node.py                  # CANopen node işlemleri
│   ├── object_dictionary.py     # Object Dictionary sabitleri
│   └── encoder_configurator.py  # Encoder yapılandırma işlemleri
│
├── venv/                        # Python sanal ortamı
│
├── config.py                    # Genel yapılandırma
├── main.py                      # Uygulamanın başlangıç noktası
├── requirements.txt             # Gerekli Python paketleri
├── README.md
└── .gitignore
```
## Katmanlı Mimari

### Uygulama Katmanı

`main.py`

Kullanıcıdan mevcut ve yeni Node ID ile baud rate bilgilerini alır. Yapılandırma sürecini başlatır ve sonuçları ekrana yazdırır.

### CANopen Katmanı

`canopen/client.py`

SDO ve NMT işlemlerini yönetir.

`canopen/sdo.py`

SDO Read ve SDO Write mesajlarını oluşturur ve gelen cevapları işler.

`canopen/nmt.py`

NMT komutlarını oluşturur.é

`canopen/object_dictionary.py`

Kullanılan CANopen Object Dictionary adreslerini içerir.

`canopen/encoder_configurator.py`

Encoder ayarlarını yazar, geri okur, doğrular ve kalıcı hafızaya kaydeder.

### CAN Haberleşme Katmanı

`bus/real_can.py`

PEAK PCAN-USB üzerinden gerçek CAN haberleşmesini gerçekleştirir.

`bus/fake_can.py`

Donanım olmadan test yapılabilmesi için sahte CAN ortamı sağlar.

`bus/can_bus.py`

Gerçek veya sahte CAN adaptörünü ortak bir arayüz üzerinden kullanır.

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
cd C:\CANOPEN_PROJECT
```

### 2. Sanal ortam oluşturma

```powershell
python -m venv venv
```

### 3. Sanal ortamı etkinleştirme

```powershell
.\venv\Scripts\Activate.ps1
```

PowerShell çalıştırma politikası nedeniyle hata alınırsa:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Ardından sanal ortam tekrar etkinleştirilir:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Gerekli paketi yükleme

```powershel
pip install python-can
```

## PCAN Ayarları

`config.py` dosyasında gerçek CAN kullanımı etkin olmalıdır.

```python
USE_REAL_CAN = True
CHANNEL = "PCAN_USBBUS1"
BITRATE = 250000
READ_TIMEOUT = 1.0
```

Program çalışma sırasında gerekli olduğunda PCAN bağlantısını yeni baud rate ile yeniden açar.

## Programı Çalıştırma

PCAN-View kapatıldıktan sonra aşağıdaki komut çalıştırılır:

```powershell
python main.py
```

Program kullanıcıdan şu bilgileri ister:

```text
Mevcut Node ID:
Yeni Node ID:
Mevcut baud rate:
Yeni baud rate:
```

Node ID decimal veya hexadecimal olarak girilebilir.

Geçerli örnekler:

```text
90
0x5A
5A
```

Bir alanı mevcut varsayılan değerle kullanmak için doğrudan Enter tuşuna basılabilir.

## Örnek Kullanım

Encoder mevcut durumda Node ID `0x5A` ve baud rate `500 kbit/s` kullanıyorsa ve yeni değerler Node ID `0x5B`, baud rate `250 kbit/s` olacaksa:

```text
Mevcut Node ID: 5A
Yeni Node ID: 5B
Mevcut baud rate: 500
Yeni baud rate: 250
```

Program kullanıcıdan onay aldıktan sonra yapılandırmayı uygular.

## Yapılandırma Akışı

Program aşağıdaki sırayı izler:

1. Mevcut Node ID ve baud rate ile CAN bağlantısını açar.
2. Producer Heartbeat Time değerini yazar.
3. Transmission Type değerini yazar.
4. Event Time değerini yazar.
5. Yeni Node ID değerini yazar.
6. Yeni baud rate kodunu yazar.
7. Yazılan her değeri geri okuyarak doğrular.
8. Ayarları kalıcı hafızaya kaydeder.
9. NMT Reset Communication komutu gönderir.
10. PCAN bağlantısını yeni baud rate ile yeniden açar.
11. Encoder heartbeat mesajını bekler.
12. CANopen istemcisini yeni Node ID ile günceller.
13. Yeni bağlantı bilgileri üzerinden SDO haberleşmesini doğrular.
14. Node ID ve baud rate değerlerini tekrar okuyarak kontrol eder.

## Kalıcı Hafızaya Kaydetme

Ayarların kalıcı olması için CANopen Store Parameters nesnesi kullanılır.

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

Yeni Node ID ve baud rate değerlerinin aktif olması için NMT Reset Communication komutu gönderilir.

```text
CAN-ID  : 0x000
DATA[0] : 0x82
DATA[1] : Mevcut Node ID
```

Reset komutu mevcut Node ID üzerinden gönderilir. Encoder yeniden başladıktan sonra yeni Node ID ve yeni baud rate kullanılır.

## Test Sonuçları

Gerçek donanım üzerinde aşağıdaki işlemler başarıyla doğrulanmıştır:

- SDO Read
- SDO Write
- Producer Heartbeat Time yazma ve okuma
- Transmission Type yazma ve okuma
- Event Time yazma ve okuma
- Node ID değişimi
- Baud rate değişimi
- Kalıcı hafızaya kayıt
- NMT Reset Communication
- Yeni baud rate ile PCAN bağlantısını yeniden açma
- Yeni Node ID üzerinden heartbeat alma
- Yeni Node ID üzerinden SDO haberleşmesi
- Reset sonrasında Node ID ve baud rate doğrulaması

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

- PCAN-View ve Python programı aynı anda PCAN kanalını kullanmamalıdır.
- Mevcut Node ID doğru girilmelidir.
- Mevcut baud rate doğru girilmelidir.
- Yanlış baud rate seçilirse CAN controller bus-off durumuna geçebilir.
- Baud rate değişiminden sonra PCAN bağlantısı yeni hızla yeniden açılmalıdır.
- Node ID değişiminden sonra SDO ve heartbeat COB-ID değerleri değişir.
- CAN hattında uygun sonlandırma direnci bulunmalıdır.
- Encoder güç bağlantısı ve CAN-H/CAN-L bağlantıları kontrol edilmelidir.

## Güncel Encoder Durumu

Son başarılı testten sonra encoder:

```text
Node ID   : 0x5B
Baud Rate : 250 kbit/s
```

değerleriyle çalışmaktadır.

## Geliştirme Durumu

Projenin temel fonksiyonları tamamlanmıştır.

Tamamlanan özellikler:

- CAN bağlantısı
- SDO Read
- SDO Write
- NMT komutları
- Encoder parametre yapılandırması
- Kalıcı hafızaya kayıt
- Node ID değişimi
- Baud rate değişimi
- Kullanıcıdan terminal üzerinden giriş alma
- Reset sonrası doğrulama

Gelecekte eklenebilecek özellikler:

- Grafik kullanıcı arayüzü
- Otomatik cihaz tarama
- Birden fazla encoder desteği
- Log dosyasına kayıt
- Hata kodlarının daha ayrıntılı açıklanması
- Position Value verisinin sürekli okunması