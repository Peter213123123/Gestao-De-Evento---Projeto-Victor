from datetime import datetime, timezone

class InscricaoModel:
    def __init__(self, id_usuario: str, id_evento: str, status: str = "confirmada"):
        self.id_usuario = id_usuario
        self.id_evento = id_evento
        self.status = status
        self.data_inscricao = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        """Converte o objeto para dicionário para ser armazenado no Firestore"""
        return {
            "id_usuario": self.id_usuario,
            "id_evento": self.id_evento,
            "status": self.status,
            "data_inscricao": self.data_inscricao
        }
