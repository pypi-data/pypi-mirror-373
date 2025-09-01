from argon2 import PasswordHasher

class ARGON2:
    # ----------------------------------
    def __init__(self):
        msg, result = None, True
        try:
            self.__ph = PasswordHasher()
        except Exception as error:
            msg = error
            result = msg

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

    # ----------------------------------
    def validHash(self, value, key):
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