from cryptography.fernet import Fernet
import os
import json

class FERNET:
    def __init__(self):
        self.__token = None
        self.__cipher = None

    # -----------------------------------
    def encrypt(self, word:str):
        msg, result = None, None
        try:
            #x = Fernet(key)
            result = self.CIPHER.encrypt(word.encode()).hex()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ----------------------------------
    def decrypt(self, word):
        msg, result = None, True
        try:
            bytes_word = bytes.fromhex(word).decode()
            result = self.CIPHER.decrypt(bytes_word).decode()
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result


    # ----------------------------------
    def setBuildToken(self):
        # normalmente sera gerado apenas uma unica vez
        # armazenar a chave. Caso seja gerado uma outra
        # todas as criptografias geraradas anteriormente
        # serao perdidas.
        msg, result = None, True
        try:
            self.__token = Fernet.generate_key().hex()
            result = self.TOKEN
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result

    # ----------------------------------
    def setToken(self, token):
        msg, result = None, True
        try:
            self.__token = bytes.fromhex(token)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result


    # ----------------------------------
    def __setCipher(self, key):
        msg, result = None, True
        try:
            self.__cipher = Fernet(key)
        except Exception as error:
            msg = error
            result = msg
        finally:
            return result


    @property
    def TOKEN(self) -> str:
        return self.__token

    @property
    def CIPHER(self):
        return Fernet(self.TOKEN)


if __name__ == "__main__":
    x = FERNET()
    token = x.setBuildToken()

    # __token =  "cXBRJulOb_arFkWjsOZF0JprhAb0FjsC5xRTcn63WQE="
    # x.setToken(__token)
    # print("Token: ",x.TOKEN)
    #
    # __root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",".."))
    # __file = os.path.join(__root, "config", "tokens", "base_conexao.json")
    # __buffer = open(__file, "r").read()
    # __word = __buffer
    #
    # #__word = "teste "*1000
    # print("__word:" ,__word)
    # __ENCRYPT = x.encrypt(word=__word)
    # print("Encrypt: ",__ENCRYPT)
    # __DECRYPT = x.decrypt(__ENCRYPT)
    # print("Decrypt: ", __DECRYPT)
