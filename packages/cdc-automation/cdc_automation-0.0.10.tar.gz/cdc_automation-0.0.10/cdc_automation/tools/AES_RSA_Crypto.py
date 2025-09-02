import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
from Crypto.Signature import pss
from Crypto import Random


def generate_rsa_key(bits: int):
    key = RSA.generate(bits)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key.decode(), private_key.decode()


def rsa_encrypt(public_key: str, text: bytes):
    """
    Encrypt aes key with the public RSA key
    :param public_key:
    :param text:
    :return:
    """
    public_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key=public_key, hashAlgo=SHA256, mgfunc=lambda x, y: pss.MGF1(x, y, SHA256))
    ciphertext = cipher.encrypt(text)
    return ciphertext


def rsa_decrypt(private_key: str, text: bytes):
    """
    Decrypt ase key with the private RSA key
    :param private_key:
    :param text:
    :return:
    """
    private_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(key=private_key, hashAlgo=SHA256, mgfunc=lambda x, y: pss.MGF1(x, y, SHA256))
    ciphertext = cipher.decrypt(text)
    return ciphertext


class AESCipher:

    def __init__(self, key: bytes, iv: bytes):
        # self.bs = AES.block_size
        self.iv = iv
        self.key = key

    def encrypt(self, raw: str):
        # raw = self._pad(raw)
        # iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(pad(raw.encode(), AES.block_size, style="pkcs7"))
        # return cipher.encrypt(pad(bytearray(raw, 'utf-8'), AES.block_size))
        # return iv + cipher.encrypt(raw.encode())

    def decrypt(self, enc: bytes):
        # iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return unpad(cipher.decrypt(enc), AES.block_size).decode()
        # return AESCipher._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


if __name__ == "__main__":
    # generate aes, iv, get sender, receiver rsa public key
    # aes_key = str_gen(size=32).encode()
    # _IV = str_gen(size=16).encode()
    aes_key = hashlib.sha256("this is aes key".encode()).digest()
    _IV = Random.new().read(AES.block_size)
    # generate sender rsa keys
    sender_rsa_pub, sender_rsa_pri = generate_rsa_key(2048)

    # encrypt sender msg by aes and iv
    AES_CRYPTO = AESCipher(aes_key, _IV)
    enc_text_by_aes_iv = AES_CRYPTO.encrypt("hi this is test message")
    # encrypt sender msg by base64 and then to str
    en_b64_sender_msg_str = base64.b64encode(enc_text_by_aes_iv).decode()
    # encrypt sender iv by base64 and then to str
    en_b64_sender_iv_str = base64.b64encode(_IV).decode()
    # encrypt sender aes by receiver RSA public key
    enc_aes_by_rsa_pub = rsa_encrypt(open('../ignoreFolder/trial/digital_envelope/receiver/public.bin').read(), aes_key)
    # encrypt sender aes with receiver RSA public key by base64 encode and then str
    en_b64_sender_aes_str = base64.b64encode(enc_aes_by_rsa_pub).decode()
    # combine b64_sender_msg % b64_sender_aes % b64_sender_iv
    request_msg = en_b64_sender_msg_str+"%"+en_b64_sender_aes_str+"%"+en_b64_sender_iv_str

    # receiver split msg by %
    receiver_msg = request_msg.split("%")
    # decrypt sender aes with receiver RSA public key by base64 decode
    de_b64_aes = base64.b64decode(receiver_msg[1])
    # decrypt sender aes by receiver RSA private key
    dec_aes_by_rsa_pri = rsa_decrypt(open("../ignoreFolder/trial/digital_envelope/receiver/private.bin").read(), de_b64_aes)
    # decrypt sender iv by base64 decode
    de_b64_iv = base64.b64decode(receiver_msg[2])
    # decrypt sender msg by base64 decode
    de_b64_msg = base64.b64decode(receiver_msg[0])
    # decrypt sender msg by aes and iv
    dec_text_by_aes_iv = AES_CRYPTO.decrypt(de_b64_msg)
    print(dec_text_by_aes_iv)

