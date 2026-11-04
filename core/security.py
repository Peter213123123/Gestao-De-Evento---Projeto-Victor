from passlib.context import CryptContext

# Configura o passlib para usar o algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Recebe a senha informada no cadastro e retorna o hash criptografado."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara a senha digitada no login com o hash salvo no Firestore."""
    return pwd_context.verify(plain_password, hashed_password)