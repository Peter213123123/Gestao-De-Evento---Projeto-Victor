"""Perfis de usuário e Matriz de Permissões (README, seção 10) traduzidos em código.

Para mudar quem pode fazer o quê, edite SOMENTE o dicionário MATRIZ abaixo.
Os endpoints usam  Depends(permissao("nome_da_acao"))  e nunca citam perfis diretamente.

Erros:
  401 -> sem token / token inválido ou expirado (tratado em core/auth.py)
  403 -> usuário autenticado, mas o perfil dele não tem permissão (tratado aqui)
"""
from fastapi import Depends, HTTPException, status

from core.auth import get_current_user

# Perfis existentes no sistema
ADMIN = "admin"
ORGANIZADOR = "organizador"
PARTICIPANTE = "participante"
PERFIS_VALIDOS = (ADMIN, ORGANIZADOR, PARTICIPANTE)

# ação -> perfis autorizados
MATRIZ = {
    # ---- Linhas da matriz da 1ª Unidade ----
    "criar_editar_eventos": (ADMIN, ORGANIZADOR),
    "excluir_eventos": (ADMIN,),
    "listar_eventos": PERFIS_VALIDOS,
    "inscrever_se": (PARTICIPANTE,),
    "listar_inscritos": (ADMIN, ORGANIZADOR),
    "cancelar_inscricao_propria": (PARTICIPANTE,),
    # ---- Complementos: recursos que existem na API e não estavam na matriz ----
    "gerenciar_usuarios": (ADMIN,),
    "registrar_presenca": (ADMIN, ORGANIZADOR),
    "listar_certificados": PERFIS_VALIDOS,
    "emitir_certificados": (ADMIN, ORGANIZADOR),
}


def perfil_do_usuario(usuario: dict) -> str:
    return str(usuario.get("tipo_perfil", "")).lower()


def tem_permissao(usuario: dict, acao: str) -> bool:
    return perfil_do_usuario(usuario) in MATRIZ[acao]


def exigir_permissao(usuario: dict, acao: str) -> dict:
    """Levanta 403 se o perfil do usuário não está autorizado para a ação."""
    if not tem_permissao(usuario, acao):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Ação restrita aos perfis: " + ", ".join(MATRIZ[acao]) + ".",
        )
    return usuario


def permissao(acao: str):
    """Dependência do FastAPI: exige token válido (401) e perfil autorizado (403)."""
    if acao not in MATRIZ:
        raise KeyError(f"Ação '{acao}' não existe em MATRIZ (core/permissoes.py).")

    def verificador(usuario: dict = Depends(get_current_user)) -> dict:
        return exigir_permissao(usuario, acao)

    return verificador
