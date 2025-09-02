import os
#from operator import truediv
# -----------------------------------
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
# -----------------------------------
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import rsa
from argon2 import PasswordHasher

KEYS_RSA = rsa.newkeys(512)

class RSA_Cipher:
    """
    Esta classe faz criptografia de pequenos textos
    """
    def __init__(self):
        self.__private_key = None
        self.__public_key = None
        self.__path_keys = ""

    def setInit(self, path, word:str=""):
            msg, result = None, True
            try:
                self.setPathKeys(path)
                self.setWord(word)
                self.__private_key = self.getFileKey(os.path.join(self.PATH_KEYS, "private.pem"))
                self.__public_key = self.getFileKey(os.path.join(self.PATH_KEYS, "public.pem"))
            except Exception as error:
                msg = error
                result = msg
            finally:
                return result

    def CIPHER(self, word, action: str = "E"):
            msg, result = None, True
            try:
                if action == "E":
                    result = self.encrypt(word, self.PUBLIC_KEY)
                else:
                    result = self.decrypt(word, self.PRIVATE_KEY)
            except Exception as error:
                msg = error
                result = msg
            finally:
                return result

    def encrypt(self, word, key):
            msg, result = None, True
            try:
                __cifra = PKCS1_OAEP.new(key)
                result = __cifra.encrypt(word.encode())
                result = result.hex()
            except Exception as error:
                msg = error
                result = msg
            finally:
                return result

    def decrypt(self, word, key):
            msg, result = None, True
            try:
                __decifra = PKCS1_OAEP.new(key)
                result = __decifra.decrypt(bytes.fromhex(word))
            except Exception as error:
                msg = error
                result = msg
            finally:
                return result

    def getChavePublica(self):
        msg, result = None, True
        try:
            self.__public_key = self.PRIVATE_KEY.publickey()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getChavePrivada(self, value_bytes: int = 2048):
        msg, result = None, True
        try:
            self.__private_key = RSA.generate(value_bytes)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def setFileKey(self, key: hex, filename: str = "private.pem"):
        msg, result = None, True
        try:
            with open(filename, "wb") as f:
                f.write(key.export_key())
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def getFileKey(self, filename):
        msg, result = None, True
        try:
            x = os.getcwd()
            with open(filename, "r") as f:
                result = RSA.import_key(f.read())
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    def setPathKeys(self, path:str):
            msg, result = None, True
            try:
                self.__path_keys = path
            except Exception as error:
                msg = error
                result = msg
            finally:
                return result

    def setWord(self, word):
            msg, result = None, True
            try:
                self.__word = word
            except Exception as error:
                msg = error
                result = msg
            finally:
                return result

    @property
    def PRIVATE_KEY(self):
        return self.__private_key

    @property
    def PUBLIC_KEY(self):
        return self.__public_key

    @property
    def PATH_KEYS(self):
        return self.__path_keys

    @property
    def WORD(self):
        return self.__word

class AES_Cipher:
    """
    Esta classe faz criptografia de textos longos
    """
    def __init__(self):
        ...

    def encrypt(self, plaintext: str, rsa_public_key):
        msg, result = None, True
        try:
            # Gerar uma chave AES aleatória (16 bytes)
            aes_key = get_random_bytes(16)

            # Criar cifra AES em modo CBC
            cipher_aes = AES.new(aes_key, AES.MODE_CBC)
            iv = cipher_aes.iv  # Vetor de Inicialização

            # Adicionar padding ao texto para que seja múltiplo de 16
            ciphertext = cipher_aes.encrypt(pad(plaintext.encode(), AES.block_size))

            # Criptografar a chave AES com RSA
            cipher_rsa = PKCS1_OAEP.new(rsa_public_key)
            encrypted_aes_key = cipher_rsa.encrypt(aes_key)
            result = base64.b64encode(encrypted_aes_key + iv + ciphertext).decode()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result


    def decrypt(self, encrypted_data: str, rsa_private_key):
        msg, result = None, True
        try:
            # Converter de base64 para bytes
            encrypted_data = base64.b64decode(encrypted_data)

            # Extrair partes (chave AES criptografada + IV + texto criptografado)
            key_size = rsa_private_key.size_in_bytes()
            encrypted_aes_key = encrypted_data[:key_size]
            iv = encrypted_data[key_size:key_size + 16]
            ciphertext = encrypted_data[key_size + 16:]

            # Descriptografar a chave AES com RSA
            cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
            aes_key = cipher_rsa.decrypt(encrypted_aes_key)

            # Descriptografar o texto com AES
            cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
            plaintext = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)

            result = plaintext.decode()

        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

class B64_Cipher:
    def __init__(self):
        ...

    @staticmethod
    def base64_encrypt(word: str, encode_pattern: str = "utf-8"):
        encoded = (base64.b64encode(word.encode(encode_pattern)))
        encoded_ascii = encoded.decode(encode_pattern)
        return encoded_ascii

    @staticmethod
    def base64_decrypt(word: str, encode_pattern: str = "utf-8"):
        try:
            word = word.encode(encode_pattern)
            decoded = base64.b64decode(word).decode(encode_pattern)
            # decoded_ascii = decoded.decode()
        except Exception as error:
            decoded = error
        finally:
            return decoded

    @staticmethod
    def token_get() -> str:
        # key = Fernet.generate_key()
        # cipher_suite = Fernet(key)
        cipher_suite = True
        # return key.decode("ascii")
        return cipher_suite

    @staticmethod
    def CRYPTOGRAPHY(word: str, token: str = None, action: str = "E"):
        msg, result = None, None
        try:
            if action == "E":
                if isinstance(word, str):
                    word = word.encode()
                result = token.encrypt(word).decode()
            else:
                if isinstance(word, str):
                    word = word.encode()
                result = token.decrypt(word).decode()
        except Exception as error:
            msg = error.args[0]
            result = msg
        finally:
            return result

class ARGON:
    # ----------------------------------
    def __init__(self):
        msg, result = None, True
        try:
            self.__ph = PasswordHasher()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    # ----------------------------------
    def hash(self, value):
        msg, result = None, True
        try:
            result = self.HASH.hash(value)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @staticmethod
    # ----------------------------------
    def unHash(self, value, key):
        msg, result = None, True
        try:
            result = self.HASH.verify(key, value)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @property
    def HASH(self):
        return self.__ph




