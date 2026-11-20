import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o sistema
load_dotenv()

class Settings:
    # Puxa os valores do .env usando os.getenv("NOME_DA_VARIAVEL", "valor_padrao")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave_padrao_para_desenvolvimento")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")

# Instancia as configurações para serem importadas em outros arquivos
settings = Settings()
