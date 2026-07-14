from dataclasses import dataclass

from canopen.client import CANopenClient
from canopen.object_dictionary import ObjectDictionary


@dataclass
class EncoderSettings:
    current_node_id: int
    new_node_id: int
    baud_rate: int

    heartbeat_time_ms: int = 100
    transmission_type: int = 255
    event_time_ms: int = 80


class EncoderConfigurator:
    """
    Encoder'a ait CANopen yapılandırma işlemlerini yönetir.

    Ayarları Object Dictionary kayıtlarına yazar,
    geri okuyarak doğrular ve kalıcı hafızaya kaydeder.
    """

    # Kullanıcının girdiği kbit/s değerini encoder'ın
    # 0x2100:00 nesnesinde beklediği seçim koduna dönüştürür.
    BAUD_RATE_CODES = {
        10: 0,
        20: 1,
        50: 2,
        100: 3,
        125: 4,
        250: 5,
        500: 6,
        800: 7,
        1000: 8,
    }

    def __init__(self, client: CANopenClient):
        self.client = client

    def _write_and_verify(
        self,
        title,
        index,
        subindex,
        value,
        size
    ):
        """
        Object Dictionary kaydına değer yazar ve aynı kaydı
        tekrar okuyarak yazma işlemini doğrular.
        """

        print(f"\n{title} ayarlanıyor...")

        written = self.client.write_object(
            index=index,
            subindex=subindex,
            value=value,
            size=size,
            timeout=3.0
        )

        if not written:
            print(f"{title} yazılamadı.")
            return False

        response = self.client.read_object(
            index=index,
            subindex=subindex,
            timeout=3.0
        )

        if response is None:
            print(f"{title} tekrar okunamadı.")
            return False

        if response.value != value:
            print(
                f"{title} doğrulanamadı. "
                f"Beklenen: {value}, "
                f"Okunan: {response.value}"
            )
            return False

        print(f"{title} başarıyla doğrulandı.")
        return True

    def configure_node_id(self, new_node_id):
        """
        Encoder'ın yeni Node ID değerini yazar.

        Node ID 1 ile 127 arasında olmalıdır.
        Yeni değer kalıcı kayıt ve yeniden başlatma sonrasında
        aktif hâle gelir.
        """

        if not 1 <= new_node_id <= 127:
            print(
                "\nGeçersiz Node ID. "
                "Node ID 1 ile 127 arasında olmalıdır."
            )
            return False

        return self._write_and_verify(
            title="Node ID",
            index=ObjectDictionary.NODE_ID,
            subindex=0,
            value=new_node_id,
            size=1
        )

    def configure_baud_rate(self, baud_rate):
        """
        Kullanıcının verdiği kbit/s değerini encoder'ın
        baud rate seçim koduna dönüştürür ve 0x2100:00
        nesnesine yazar.
        """

        if baud_rate not in self.BAUD_RATE_CODES:
            supported_rates = ", ".join(
                str(rate)
                for rate in self.BAUD_RATE_CODES
            )

            print(
                f"\nDesteklenmeyen baud rate: "
                f"{baud_rate} kbit/s"
            )
            print(
                f"Desteklenen baud rate değerleri: "
                f"{supported_rates} kbit/s"
            )

            return False

        baud_rate_code = self.BAUD_RATE_CODES[baud_rate]

        print(
            f"\nSeçilen baud rate: {baud_rate} kbit/s"
        )
        print(
            f"Encodera yazılacak baud rate kodu: "
            f"{baud_rate_code}"
        )

        return self._write_and_verify(
            title=f"Baud Rate ({baud_rate} kbit/s)",
            index=ObjectDictionary.BAUD_RATE,
            subindex=0,
            value=baud_rate_code,
            size=1
        )

    def configure(self, settings: EncoderSettings):
        """
        Encoder'ın bütün yapılandırma parametrelerini uygular.
        """

        heartbeat_ok = self._write_and_verify(
            title="Producer Heartbeat Time",
            index=ObjectDictionary.PRODUCER_HEARTBEAT_TIME,
            subindex=0,
            value=settings.heartbeat_time_ms,
            size=2
        )

        if not heartbeat_ok:
            return False

        transmission_ok = self._write_and_verify(
            title="Transmission Type",
            index=ObjectDictionary.TPDO1_COMMUNICATION_PARAMETER,
            subindex=(
                ObjectDictionary
                .TPDO1_TRANSMISSION_TYPE_SUBINDEX
            ),
            value=settings.transmission_type,
            size=1
        )

        if not transmission_ok:
            return False

        event_time_ok = self._write_and_verify(
            title="Event Time",
            index=ObjectDictionary.TPDO1_COMMUNICATION_PARAMETER,
            subindex=ObjectDictionary.TPDO1_EVENT_TIMER_SUBINDEX,
            value=settings.event_time_ms,
            size=2
        )

        if not event_time_ok:
            return False

        node_id_ok = self.configure_node_id(
            new_node_id=settings.new_node_id
        )

        if not node_id_ok:
            return False

        baud_rate_ok = self.configure_baud_rate(
            baud_rate=settings.baud_rate
        )

        if not baud_rate_ok:
            return False

        return True

    def save(self):
        """
        Yapılandırma parametrelerini encoder'ın kalıcı
        hafızasına kaydeder.
        """

        print("\nAyarlar kalıcı hafızaya kaydediliyor...")

        saved = self.client.write_object(
            index=ObjectDictionary.STORE_PARAMETERS,
            subindex=(
                ObjectDictionary
                .STORE_ALL_PARAMETERS_SUBINDEX
            ),
            value=ObjectDictionary.SAVE_SIGNATURE,
            size=4,
            timeout=5.0
        )

        if not saved:
            print("EEPROM kayıt işlemi başarısız.")
            return False

        print(
            "EEPROM kayıt komutu encoder tarafından kabul edildi."
        )

        return True

    def read_settings(self):
        """
        Encoder'ın mevcut yapılandırma değerlerini okur.
        """

        node_id = self.client.read_object(
            index=ObjectDictionary.NODE_ID,
            subindex=0,
            timeout=3.0
        )

        baud_rate = self.client.read_object(
            index=ObjectDictionary.BAUD_RATE,
            subindex=0,
            timeout=3.0
        )

        heartbeat = self.client.read_object(
            index=ObjectDictionary.PRODUCER_HEARTBEAT_TIME,
            subindex=0,
            timeout=3.0
        )

        transmission = self.client.read_object(
            index=ObjectDictionary.TPDO1_COMMUNICATION_PARAMETER,
            subindex=(
                ObjectDictionary
                .TPDO1_TRANSMISSION_TYPE_SUBINDEX
            ),
            timeout=3.0
        )

        event_time = self.client.read_object(
            index=ObjectDictionary.TPDO1_COMMUNICATION_PARAMETER,
            subindex=ObjectDictionary.TPDO1_EVENT_TIMER_SUBINDEX,
            timeout=3.0
        )

        return {
            "node_id": (
                node_id.value if node_id else None
            ),
            "baud_rate_code": (
                baud_rate.value if baud_rate else None
            ),
            "heartbeat_time_ms": (
                heartbeat.value if heartbeat else None
            ),
            "transmission_type": (
                transmission.value if transmission else None
            ),
            "event_time_ms": (
                event_time.value if event_time else None
            ),
        }