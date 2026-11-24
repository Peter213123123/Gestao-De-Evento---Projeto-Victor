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

    # Configurações de E-mail (SMTP transacional: Gmail App Password, Brevo, Resend, etc.)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USER", ""))
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Gestão de Eventos Acadêmicos")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

# Instancia as configurações para serem importadas em outros arquivos
settings = Settings()
