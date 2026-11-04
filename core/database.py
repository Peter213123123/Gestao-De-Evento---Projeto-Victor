import firebase_admin
from firebase_admin import credentials, firestore
from core.config import settings

# Garante que o Firebase não seja inicializado duas vezes
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)

# Exporta o db para ser usado nas rotas
db = firestore.client()
