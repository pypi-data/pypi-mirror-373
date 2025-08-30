from base64 import b64decode, b64encode
from io import BytesIO


def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        file_bytes = file.read()
        encoded_string = b64encode(file_bytes)
        return encoded_string.decode("utf-8")


def decode_base64_to_bytesio(encoded_string):
    decoded_bytes = b64decode(encoded_string)
    return BytesIO(decoded_bytes)
