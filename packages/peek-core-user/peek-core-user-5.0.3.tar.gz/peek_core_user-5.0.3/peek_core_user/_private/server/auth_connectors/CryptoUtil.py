import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def decryptAES256GCM(encodedBase64String: str, passphrase: str) -> str:
    concatBinaryString = base64.b64decode(encodedBase64String)

    # salt [16bytes] |
    # iv [12bytes] |
    # ciphertext (ciphertext [variable length] | tag [16bytes] )
    receivedSalt = concatBinaryString[0:16]
    receivedIv = concatBinaryString[16 : 16 + 12]
    receivedCiphertext = concatBinaryString[16 + 12 : -16]
    receivedTag = concatBinaryString[-16:]
    # Derive the key from the received salt and password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=receivedSalt,
        iterations=100000,
        backend=default_backend(),
    )
    key = kdf.derive(passphrase.encode("utf-8"))
    # Decrypt the ciphertext using AES-GCM mode
    backend = default_backend()
    cipher = Cipher(
        algorithms.AES256(key), modes.GCM(receivedIv), backend=backend
    )
    decryptor = cipher.decryptor()
    decryptedData = decryptor.update(
        receivedCiphertext
    ) + decryptor.finalize_with_tag(receivedTag)

    return decryptedData.decode("utf-8")
