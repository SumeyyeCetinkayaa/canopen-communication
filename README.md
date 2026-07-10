# CANopen Communication Project

## 1. Proje Hakkında

Bu proje, CANopen protokolü kullanan cihazlarla haberleşebilen modüler bir Python uygulaması geliştirmek amacıyla oluşturulmuştur.

İlk geliştirme aşamasında gerçek CAN donanımı kullanılmadan CANopen haberleşme altyapısı simüle edilmiş ve uygulamanın gerçek donanım ile çalışabilecek şekilde katmanlı bir mimari üzerine kurulması hedeflenmiştir.

---

## 2. Projenin Amacı

Bu projenin temel amaçları:

- CAN Bus haberleşmesini soyutlamak
- CANopen SDO haberleşmesini gerçekleştirmek
- Gerçek CAN donanımı olmadan geliştirme yapılabilecek bir simülasyon ortamı oluşturmak
- Gerçek donanım eklendiğinde uygulamanın geri kalanını değiştirmeden yalnızca haberleşme katmanını kullanarak sistemi çalıştırabilmek

---

## 3. Kullanılan Teknolojiler

- Python 3.14
- python-can
- canopen
- Visual Studio Code
- PEAK PCAN-USB (hedef donanım)

---

## 4. Proje Mimarisi

```
                main.py
                    │
                    ▼
            CANopenClient
                    │
                    ▼
               SDO Request
                    │
                    ▼
               CanMessage
                    │
                    ▼
                 CanBus
              ┌────┴────┐
              ▼         ▼
         FakeCan    RealCan
```

Proje üç temel katmandan oluşmaktadır.

- **Application Katmanı** uygulamanın genel akışını yönetir.
- **CANopen Katmanı** CANopen protokolüne ait haberleşme işlemlerini gerçekleştirir.
- **CAN Katmanı** CAN mesajlarının oluşturulması ve fiziksel haberleşme katmanına iletilmesinden sorumludur.

CAN katmanı içerisinde bulunan `CanBus` sınıfı, uygulamanın gerçek CAN donanımı (`RealCan`) veya simülasyon ortamı (`FakeCan`) arasında geçiş yapmasını sağlayan bir soyutlama katmanı olarak görev yapmaktadır.

---

## 5. Klasör Yapısı

```
CANOPEN_PROJECT
│
├── main.py
├── config.py
│
├── bus
│   ├── can_bus.py
│   ├── can_message.py
│   ├── fake_can.py
│   ├── fake_object_dictionary.py
│   └── real_can.py
│
└── canopen
    ├── client.py
    ├── node.py
    ├── object_dictionary.py
    ├── pdo.py
    └── sdo.py
```

---

## 6. Dosyaların Görevleri

### main.py

Uygulamanın başlangıç noktasıdır. Program akışını yönetir ve CANopen istemcisi üzerinden örnek haberleşme işlemlerini başlatır.

### config.py

Proje genelinde kullanılan yapılandırma bilgilerini içerir.

---

### bus/

#### can_bus.py

CAN haberleşmesi için ortak arayüzü sağlayan soyutlama katmanıdır. Uygulamanın gerçek veya simülasyon ortamında çalışmasını yönetir.

#### can_message.py

CAN Bus üzerinde gönderilen ve alınan mesajları temsil eden veri modelini içerir.

#### fake_can.py

Gerçek donanım bulunmadığında CAN haberleşmesini simüle eder ve CANopen cihazı gibi davranır.

#### fake_object_dictionary.py

Simülasyon ortamında kullanılan Object Dictionary verilerini içerir.

#### real_can.py

Gerçek PEAK PCAN-USB donanımı üzerinden CAN Bus haberleşmesini gerçekleştirir.

---

### canopen/

#### client.py

CANopen istemcisini temsil eder. SDO okuma işlemlerini yönetir ve CAN Bus ile haberleşmeyi gerçekleştirir.

#### sdo.py

CANopen SDO (Service Data Object) isteklerinin oluşturulması ve gelen cevapların çözümlenmesinden sorumludur.

#### object_dictionary.py

CANopen standardında kullanılan Object Dictionary index ve subindex tanımlarını içerir.

#### node.py

İlerleyen aşamalarda CANopen cihazını temsil edecek yapının geliştirileceği modüldür.

#### pdo.py

İlerleyen aşamalarda PDO (Process Data Object) haberleşmesinin gerçekleştirileceği modüldür.

---

## 7. Geliştirme Durumu

### Tamamlanan Çalışmalar

- [x] Proje mimarisi oluşturuldu.
- [x] CAN mesaj modeli geliştirildi.
- [x] Fake CAN haberleşmesi oluşturuldu.
- [x] SDO Read Request desteği eklendi.
- [x] SDO Response çözümleme desteği eklendi.
- [x] CANopen Client geliştirildi.
- [x] Fake Object Dictionary oluşturuldu.
- [x] Birden fazla Object Dictionary nesnesinin okunması sağlandı.

### Planlanan Çalışmalar

- [ ] Gerçek PEAK PCAN-USB entegrasyonu
- [ ] Gerçek Baumer EAM360 haberleşmesi
- [ ] PDO desteği
- [ ] NMT desteği
- [ ] Heartbeat desteği
- [ ] EMCY desteği

---

## 8. Haberleşme Akışı

```
main.py
      │
      ▼
CANopenClient.read_object()
      │
      ▼
SDO Request oluşturulur
      │
      ▼
CanMessage oluşturulur
      │
      ▼
CanBus.send()
      │
      ▼
FakeCan / RealCan
      │
      ▼
CANopen Device
      │
      ▼
SDO Response
      │
      ▼
CANopenClient
      │
      ▼
Uygulamaya sonuç döndürülür
```

---

## 9. Gerçek Donanım Entegrasyonu

Gerçek PEAK PCAN-USB adaptörü sisteme bağlandığında simülasyon katmanı yerine `real_can.py` kullanılacaktır.

Uygulamanın geri kalan katmanlarında herhangi bir değişiklik yapılmadan aynı CANopen istemcisi üzerinden haberleşmeye devam edilmesi hedeflenmektedir.