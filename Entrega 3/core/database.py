import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
from core.config import settings

# Garante que o Firebase não seja inicializado duas vezes
if not firebase_admin._apps:
    cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if cred_json:
        cred = credentials.Certificate(json.loads(cred_json))
    elif settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    else:
        raise RuntimeError(
            "Credenciais do Firebase não configuradas. "
            "Defina FIREBASE_CREDENTIALS_PATH ou FIREBASE_CREDENTIALS_JSON."
        )
    firebase_admin.initialize_app(cred)

# Exporta o db para ser usado nas rotas
db = firestore.client()
