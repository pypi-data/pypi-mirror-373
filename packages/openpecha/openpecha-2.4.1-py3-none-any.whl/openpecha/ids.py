import random
from uuid import uuid4
import secrets


def generate_id(size: int = 16) -> str:
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz-"
    return "".join(secrets.choice(chars) for _ in range(size))


def get_uuid():
    return uuid4().hex


def get_id(prefix, length):
    return prefix + "".join(random.choices(uuid4().hex, k=length)).upper()


def get_annotation_id():
    return get_id("", length=10)


def get_base_id():
    return get_id("", length=4)


def get_layer_id():
    return generate_id()


def get_initial_pecha_id():
    return get_id(prefix="I", length=8)
