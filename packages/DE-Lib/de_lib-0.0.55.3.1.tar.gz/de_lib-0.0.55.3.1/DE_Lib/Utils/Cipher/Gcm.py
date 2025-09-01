# criptografia funcionou normalmente
# tem que utulizar a biblioteca "pip install cryptography==41.0.7"

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64

from docutils.io import error_string


class GCM:
    def __init__(self):
        ...

    def __buildKey(self, token: str, salt: bytes) -> bytes:
        msg, result = None, None
        try:
            result = PBKDF2HMAC(algorithm=hashes.SHA256(),
                                length=32,
                                salt=salt,
                                iterations=100000
                                )
            result = result.derive(token.encode())
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ----------------------------------
    def Encrypt(self, token:str, word:str):
        msg, result = None, True
        try:
            salt = os.urandom(16)
            key = self.__buildKey(token=token, salt=salt)

            iv = os.urandom(12)
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
            encryptor = cipher.encryptor()

            text_bytes = word.encode()
            text_cryptography = encryptor.update(text_bytes) + encryptor.finalize()
            result = base64.b64encode(salt + iv + encryptor.tag + text_cryptography).decode()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ----------------------------------
    def Decrypt(self, word:str, token: str):
        msg, result = None, True
        try:
            data = base64.b64decode(word)


            salt = data[:16]
            iv = data[16:28]
            tag = data[28:44]
            __text = data[44:]

            key = self.__buildKey(token, salt)
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            result = decryptor.update(__text) + decryptor.finalize()

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result.decode("utf-8")





