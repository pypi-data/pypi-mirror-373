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
    
# print(unseal("noXc7Sa/kj4AnWSgu9EnRHb6KQ0jA467onca00AnnD0TAG54xMmaI7ztHOV015mav3wG3z5GN8/iLCYdIQdQ2C3oe9Nlb+Sa9C3gbHpfoth/vQysmwYpe0VDElodytaL0j4791vm+V89e5DvdvAEqD5nMKRO/2lM/QgRKh9CO19iKF3kFCJ5cOvBl2xA2BJWrZZkHmrBWtd6u+unOiA+nFFrL4X+en0lsfTvhsw8JLDIsHwVmkVnIChuL5PcJvDpfpFBUXkLKYbAE4xQKvOmlU1gcW1q6stLeEjYxEk00rTa54ie1fDR61hsYVBAM8HxctaymiTBw5/JtxqGbUY9J7HPMt0LhRPrl/x+3zcAFRyTifqO5g61EJnCG5UuNRuu+rJD8ZrKW25clz7+Mstf66IXKz2CLXL97LorTgWMZTaIsvKXRGO+sOPZZlJD3B1awVTyPoK+lslqtUM3cwSv8sz/egryOIR3RJJKza2UaVVyF8YJ4Oa9vOLJL5vjlWYaw9JoLXI0ZPY+1Um2YTNTJNyimPNHsrkp6tj9iDlQ0tzgQgEgqI0Z/Z7TxPzdobwmrEZmcUCtip8gr+PRs/rPTP15qMRxJjD65vYg9cuLdGResNuttCCeugvCsOdAK9/f0BNtSklHOoe5tnbY+HR7NZ/B2bn77VjWUDqRd6vG+5MBc1sXCYW0DLK+rlIA5pxBVCTDrxMyQa6jHQF/d2gdxsJe4U0IjIGDoZG9YM3Jj3KuynA8Es0FVmGqzbBXcZJenirYiyRHP7tUTF+0tdeWvNH1ynebEIfW7ZULkw+bWEQRji5xntPYzvC5zVSWoJFwkjeqam5HRJxVrFAwM5XYeFqhk+Vm7lShhbz4lgAfMMSwfjXfUozHYduploQ8pyKeGt+90kkNsX6rsKZ1ex11MCk+j/S+hU1lgYAtBq7yMq6OreazJwtaIxpCUfQA/kvQe1mAZ5DMXnONAOzD2Lsr1y5cVmemdz6uIvH2rPFsddQ5vWjF2j6cd11IZVAksxgw5dJAsUmVygyS9f3hEysr3EGQUqE3rG4uFrMKvL5V2cfDm6XR3FQ9bBbqDFB/THczinLOHBfpHOCboUFZuBJrqbNA2qyzAbuH/yzH8N5F+sg=", "p0vvl4wrgILNH8rl6Tv8EC2TMuWIRisuteb9cjA3exU="))
