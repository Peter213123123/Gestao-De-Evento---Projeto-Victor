from core.permissoes import PARTICIPANTE, PERFIS_VALIDOS


class UsuarioModel:
    def __init__(self, nome: str, email: str, senha: str, tipo_perfil: str = PARTICIPANTE):
        tipo_perfil = str(tipo_perfil).lower()
        if tipo_perfil not in PERFIS_VALIDOS:
            raise ValueError(f"tipo_perfil inválido. Use um destes: {', '.join(PERFIS_VALIDOS)}.")
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
