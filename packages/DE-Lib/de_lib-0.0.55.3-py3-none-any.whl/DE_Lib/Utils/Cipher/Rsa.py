from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

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

    def getChavePrivada(self, value_bytes=2048):
        msg, result = None, True
        try:
            self.__private_key = RSA.generate(2048)
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