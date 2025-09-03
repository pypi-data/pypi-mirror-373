from cryptography.fernet import Fernet

class CryptoPassService:
    def __init__(self, key: bytes | None = None):
        # Se a chave não for passada, gera uma nova
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_password(self, password: str) -> bytes:
        # Recebe a senha em texto e retorna a senha criptografada em bytes
        password_bytes = password.encode()
        encrypted = self.cipher.encrypt(password_bytes)
        return encrypted

    def decrypt_password(self, token: bytes) -> str:
        # Recebe o token criptografado e retorna a senha em texto
        decrypted_bytes = self.cipher.decrypt(token)
        return decrypted_bytes.decode()