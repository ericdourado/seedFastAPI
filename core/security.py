from passlib.context import CryptContext

CRIPTO = CryptContext(schemes=['bcrypt'], deprecated='auto')

def gerar_hash_senha(senha: str) -> str:
    return CRIPTO.hash(senha)