import base64


def btoa(value: str) -> str:
    binary = value.encode("latin-1")
    return base64.b64encode(binary).decode()


def atob(value: str) -> str:
    binary = base64.b64decode(value.encode())
    return binary.decode("latin-1")
