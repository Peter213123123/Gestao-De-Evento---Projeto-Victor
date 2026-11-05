class UsuarioModel:
    def __init__(self, nome: str, email: str, senha: str, tipo_perfil: str = "participante"):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo_perfil = tipo_perfil

    def to_dict(self):
        """Converte o objeto para dicionário para ser armazenado no Firestore"""
        return {
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "tipo_perfil": self.tipo_perfil
        }
