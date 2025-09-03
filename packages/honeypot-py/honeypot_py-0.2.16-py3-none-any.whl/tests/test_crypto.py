import os
from honeypot_server_api import unseal
from dotenv import load_dotenv

load_dotenv()

def test_decryption():
    encrypted_text = os.getenv("ENCRYPTED_TEXT")
    encryption_key = os.getenv("ENCRYPTION_KEY")
    expected_output = os.getenv("EXPECTED_OUTPUT")

    assert encrypted_text is not None, "ENCRYPTED_TEXT not set"
    assert encryption_key is not None, "ENCRYPTION_KEY not set"
    assert expected_output is not None, "EXPECTED_OUTPUT not set"

    result = unseal(encrypted_text, encryption_key)
    assert result == expected_output, "Decryption output did not match expected result"
