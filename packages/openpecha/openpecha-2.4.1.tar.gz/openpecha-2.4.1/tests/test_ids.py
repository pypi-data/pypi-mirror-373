import re

from openpecha.ids import (
    get_annotation_id,
    get_base_id,
    get_id,
    get_initial_pecha_id,
    get_layer_id,
    get_uuid,
)


def test_get_uuid():
    uuid = get_uuid()
    assert re.match(
        r"^[0-9a-fA-F]{32}$", uuid
    ), f"UUID {uuid} is not in the correct format"


def test_get_id():
    prefix = "T"
    length = 4
    generated_id = get_id(prefix, length)
    assert re.match(
        r"^T[0-9A-F]{4}$", generated_id
    ), f"ID {generated_id} is not in the correct format"


def test_get_base_id():
    base_id = get_base_id()
    assert re.match(
        r"^[0-9A-F]{4}$", base_id
    ), f"Base ID {base_id} is not in the correct format"


def test_get_layer_id():
    layer_id = get_layer_id()
    assert re.match(
        r"^[0-9A-Za-z_-]{16}$", layer_id
    ), f"Layer ID {layer_id} is not in the correct format"


def test_get_initial_pecha_id():
    initial_pecha_id = get_initial_pecha_id()
    assert re.match(
        r"^I[0-9A-F]{8}$", initial_pecha_id
    ), f"Initial Pecha ID {initial_pecha_id} is not in the correct format"


def test_get_annotation_id():
    ann_id = get_annotation_id()
    assert len(ann_id) == 10
