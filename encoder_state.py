import json
from pathlib import Path


STATE_FILE = Path(__file__).parent / "encoder_state.json"

DEFAULT_NODE_ID = 0x5B
DEFAULT_BAUD_RATE = 250


def load_encoder_state():
    """
    Encoder'ın son bilinen Node ID ve baud rate değerlerini yükler.
    Dosya yoksa varsayılan değerleri döndürür.
    """

    if not STATE_FILE.exists():
        return DEFAULT_NODE_ID, DEFAULT_BAUD_RATE

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            state = json.load(file)

        node_id = int(state["node_id"])
        baud_rate = int(state["baud_rate"])

        return node_id, baud_rate

    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        print(
            "Encoder durum dosyası okunamadı. "
            "Varsayılan değerler kullanılacak."
        )

        return DEFAULT_NODE_ID, DEFAULT_BAUD_RATE


def save_encoder_state(node_id, baud_rate):
    """
    Başarıyla uygulanan encoder ayarlarını dosyaya kaydeder.
    """

    state = {
        "node_id": node_id,
        "baud_rate": baud_rate
    }

    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)

    print(
        f"Encoder durumu kaydedildi: "
        f"Node ID 0x{node_id:02X}, "
        f"Baud Rate {baud_rate} kbit/s"
    )