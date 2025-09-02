import hashlib
import os

class PBKDF2:
    # ----------------------------------
    def __init__(self):
        msg, result = None, True
        try:
            self.__saltAleatorio = 16
        except Exception as error:
            msg = error
            result = msg

    # ----------------------------------
    def hash(self, value, salt=None):
        msg, result = None, True
        try:
            if salt is None:
                salt = os.urandom(self.SALT)
            hash_value = hashlib.pbkdf2_hmac("sha256", value.encode(), salt, 100000)
            result = salt + hash_value
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ----------------------------------
    def validHash(self, value, key):
        msg, result = None, True
        try:
            salt = key[:self.SALT]
            new_hash = self.hash(value, salt)
            result = (new_hash == key)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    @property
    def SALT(self):
        return self.__saltAleatorio
