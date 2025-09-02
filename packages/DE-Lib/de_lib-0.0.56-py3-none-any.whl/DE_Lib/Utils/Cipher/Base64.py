import base64

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
