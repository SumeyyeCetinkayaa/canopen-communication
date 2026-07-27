"""
Encoder durumlarını JSON dosyasında saklar.

Birden fazla encoderın Node ID ve baud rate
bilgilerini destekler.
"""

import json
from pathlib import Path


STATE_FILE = Path("encoder_state.json")


def load_encoder_states():
    """
    Kayıtlı bütün encoder durumlarını döndürür.

    Dönüş biçimi:

    {
        "36": {
            "baud_rate": 250
        },
        "91": {
            "baud_rate": 250
        }
    }
    """

    if not STATE_FILE.exists():
        return {}

    try:
        with STATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {}

    # Yeni çoklu encoder biçimi
    encoders = data.get("encoders")

    if isinstance(encoders, dict):
        return encoders

    # Eski tek encoder biçimini yeni biçime dönüştür
    node_id = data.get("node_id")
    baud_rate = data.get("baud_rate")

    if (
        isinstance(node_id, int)
        and isinstance(baud_rate, int)
    ):
        return {
            str(node_id): {
                "baud_rate": baud_rate
            }
        }

    return {}


def save_encoder_state(
    node_id,
    baud_rate,
    old_node_id=None,
):
    """
    Bir encoderın durumunu kaydeder veya günceller.

    Node ID değiştirildiyse old_node_id verilerek
    eski kayıt silinir.
    """

    encoders = load_encoder_states()

    if (
        old_node_id is not None
        and old_node_id != node_id
    ):
        encoders.pop(
            str(old_node_id),
            None,
        )

    encoders[str(node_id)] = {
        "baud_rate": int(baud_rate),
    }

    data = {
        "encoders": encoders
    }

    with STATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def remove_encoder_state(node_id):
    """
    Belirtilen encoder kaydını dosyadan siler.
    """

    encoders = load_encoder_states()

    encoders.pop(
        str(node_id),
        None,
    )

    data = {
        "encoders": encoders
    }

    with STATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def clear_encoder_states():
    """
    Bütün kayıtlı encoder durumlarını temizler.
    """

    data = {
        "encoders": {}
    }

    with STATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )