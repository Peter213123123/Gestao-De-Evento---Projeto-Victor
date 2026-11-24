import base64
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from core.config import settings


def _load_firebase_credentials() -> credentials.Certificate:
    """Carrega as credenciais do Firebase via variável de ambiente ou arquivo local."""
    cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON", "").strip()
    cred_b64 = os.getenv("FIREBASE_CREDENTIALS_BASE64", "").strip()

    if cred_b64 and not cred_json:
        cred_json = base64.b64decode(cred_b64).decode("utf-8")

    if cred_json:
        try:
            cred_dict = json.loads(cred_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "FIREBASE_CREDENTIALS_JSON inválido: verifique se o JSON está completo."
            ) from exc
        if isinstance(cred_dict.get("private_key"), str):
            cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
        return credentials.Certificate(cred_dict)

    if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        return credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)

    raise RuntimeError(
        "Credenciais do Firebase não configuradas. "
        "Defina FIREBASE_CREDENTIALS_JSON, FIREBASE_CREDENTIALS_BASE64 ou FIREBASE_CREDENTIALS_PATH."
    )


# Garante que o Firebase não seja inicializado duas vezes
if not firebase_admin._apps:
    firebase_admin.initialize_app(_load_firebase_credentials())

# Exporta o db para ser usado nas rotas
db = firestore.client()
