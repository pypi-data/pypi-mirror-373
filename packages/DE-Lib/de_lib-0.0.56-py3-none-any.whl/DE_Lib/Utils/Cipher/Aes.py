from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
import base64

class AES_Cipher:
    """
    Esta classe faz criptografia de textos longos
    """
    def __init__(self):
        ...

    @staticmethod
    def encrypt(plaintext: str, rsa_public_key):
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


    @staticmethod
    def decrypt(encrypted_data: str, rsa_private_key):
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