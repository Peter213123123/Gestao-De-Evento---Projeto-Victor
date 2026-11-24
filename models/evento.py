from datetime import date

class EventoModel:
    def __init__(self, titulo: str, descricao: str, data_evento: date, capacidade: int):
        self.titulo = titulo
        self.descricao = descricao
        self.data_evento = data_evento
        self.capacidade = capacidade

    def to_dict(self):
        """Converte o objeto para dicionário (formato que o Firestore armazena)"""
        return {
            "titulo": self.titulo,
            "descricao": self.descricao,
            "data_evento": self.data_evento.isoformat(), 
            "capacidade": self.capacidade
        }