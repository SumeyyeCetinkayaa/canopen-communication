"""
CANopen ağı üzerindeki aktif Node ID'leri SDO isteği göndererek tarar.

Her Node ID için Device Type nesnesi (0x1000:00) okunur.
Geçerli SDO cevabı veren cihazlar aktif node olarak kabul edilir.
"""

from dataclasses import dataclass

from canopen.client import CANopenClient
from canopen.object_dictionary import ObjectDictionary


@dataclass
class ScannedNode:
    node_id: int
    device_type: int


class NodeScanner:
    def __init__(self, can_bus):
        self.can_bus = can_bus

    def scan(
        self,
        start_node_id=1,
        end_node_id=127,
        timeout=0.01,
    ):
        """
        Belirtilen Node ID aralığını tarar.

        Tarama sırasında cevap vermeyen node'lar için hata mesajı
        gösterilmez. Bulunan cihazlar ScannedNode listesi olarak döner.
        """

        if not 1 <= start_node_id <= 127:
            raise ValueError(
                "Başlangıç Node ID 1 ile 127 arasında olmalıdır."
            )

        if not 1 <= end_node_id <= 127:
            raise ValueError(
                "Bitiş Node ID 1 ile 127 arasında olmalıdır."
            )

        if start_node_id > end_node_id:
            raise ValueError(
                "Başlangıç Node ID, bitiş Node ID'den büyük olamaz."
            )

        found_nodes = []

        print(
            f"\nCANopen ağı taranıyor "
            f"({start_node_id}-{end_node_id})..."
        )

        for node_id in range(
            start_node_id,
            end_node_id + 1,
        ):
            client = CANopenClient(
                can_bus=self.can_bus,
                node_id=node_id,
            )

            response = client.read_object(
                index=ObjectDictionary.DEVICE_TYPE,
                subindex=0,
                timeout=timeout,
                silent=True,
            )

            if response is None:
                continue

            node = ScannedNode(
                node_id=node_id,
                device_type=response.value,
            )

            found_nodes.append(node)

            print(
                f"✓ Node bulundu: "
                f"0x{node_id:02X} ({node_id}) | "
                f"Device Type: 0x{response.value:08X}"
            )

        if not found_nodes:
            print("✗ Aktif CANopen node bulunamadı.")
        else:
            print(
                f"\nToplam {len(found_nodes)} aktif node bulundu."
            )

        return found_nodes