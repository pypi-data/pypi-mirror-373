import base64
import gzip
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

nonce_length = 12  # AES-GCM nonce size
sealed_header = bytes([0x9e, 0x85, 0xdc, 0xed])  # Custom header for validation
tag_length = 16  # AES-GCM tag size (typically 16 bytes)

def import_key(base64_key: str) -> bytes:
    return base64.b64decode(base64_key)

def decompress(data: bytes) -> bytes:
    return gzip.decompress(data)

def unseal(sealed_base64: str, base64_key: str) -> dict:
    if not sealed_base64 or not isinstance(sealed_base64, str):
        raise ValueError('Invalid sealedBase64 input')
    if not base64_key or not isinstance(base64_key, str):
        raise ValueError('Invalid base64Key input')

    key = import_key(base64_key)

    try:
        sealed_result = base64.b64decode(sealed_base64)
    except Exception as e:
        raise ValueError('Invalid base64 string') from e

    # Verify the header
    if sealed_result[:len(sealed_header)] != sealed_header:
        raise ValueError('Invalid header')

    # Extract nonce, encrypted data, and authentication tag
    nonce = sealed_result[len(sealed_header):len(sealed_header) + nonce_length]
    encrypted_data_with_tag = sealed_result[len(sealed_header) + nonce_length:]
    encrypted_data = encrypted_data_with_tag[:-tag_length]
    tag = encrypted_data_with_tag[-tag_length:]

    # Decrypt the data using AES-GCM
    try:
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # Decompress the decrypted payload
        decompressed_payload = decompress(decrypted_data)

        # Convert the decompressed payload back to a string and parse as JSON
        decoded_payload = decompressed_payload.decode('utf-8')
        return json.loads(decoded_payload)
    except Exception as e:
        raise ValueError(f'Decryption failed: {e}') from e
