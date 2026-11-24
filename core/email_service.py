"""Serviço de envio de e-mails transacionais via SMTP e geração de certificado personalizado."""
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
import html
import io
import logging
import os
import smtplib

from PIL import Image, ImageDraw, ImageFont

from core.config import settings

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERTIFICADO_MODELO_PATH = os.path.join(BASE_DIR, "static", "certificado_modelo.jpg")

# Coordenadas exatas da linha em static/certificado_modelo.jpg (1024x724)
_LINHA_CENTRO_X = 574
_LINHA_BASE_Y = 423
_LINHA_LARGURA_MAX = 400


def _carregar_fonte(tamanho: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    candidatos = [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for caminho in candidatos:
        if os.path.exists(caminho):
            try:
                return ImageFont.truetype(caminho, tamanho)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


def gerar_certificado_personalizado(
    nome_participante: str,
    titulo_evento: str = "",
    codigo_validacao: str = "",
) -> tuple[bytes, bytes] | None:
    """Preenche o nome do participante no modelo oficial e retorna (jpg_bytes, pdf_bytes)."""
    if not os.path.exists(CERTIFICADO_MODELO_PATH):
        logger.warning("Modelo de certificado não encontrado em %s.", CERTIFICADO_MODELO_PATH)
        return None

    img = Image.open(CERTIFICADO_MODELO_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    nome = (nome_participante or "Participante").strip()
    tamanho = 28
    fonte = _carregar_fonte(tamanho)
    while tamanho > 14:
        bbox = draw.textbbox((0, 0), nome, font=fonte)
        largura = bbox[2] - bbox[0]
        if largura <= _LINHA_LARGURA_MAX:
            break
        tamanho -= 2
        fonte = _carregar_fonte(tamanho)

    draw.text((_LINHA_CENTRO_X, _LINHA_BASE_Y), nome, fill="#1f2937", font=fonte, anchor="ms")

    if titulo_evento or codigo_validacao:
        rodape_partes = []
        if titulo_evento:
            rodape_partes.append(f"Evento: {titulo_evento}")
        if codigo_validacao:
            rodape_partes.append(f"Validação: {codigo_validacao}")
        rodape = "  |  ".join(rodape_partes)
        fonte_rodape = _carregar_fonte(13)
        draw.text((512, 692), rodape, fill="#6b7280", font=fonte_rodape, anchor="ms")

    jpg_buf = io.BytesIO()
    img.save(jpg_buf, format="JPEG", quality=95)

    pdf_buf = io.BytesIO()
    img.save(pdf_buf, format="PDF", resolution=150.0)

    return jpg_buf.getvalue(), pdf_buf.getvalue()


def _smtp_configurado() -> bool:
    return bool(
        settings.SMTP_HOST
        and settings.SMTP_USER
        and settings.SMTP_PASSWORD
        and settings.SMTP_FROM_EMAIL
    )


def enviar_email(
    destinatario: str,
    assunto: str,
    corpo_texto: str,
    corpo_html: str,
    anexos: list[tuple[str, bytes, str, str]] | None = None,
) -> bool:
    """Envia e-mail multipart (texto plano + HTML + anexos opcionais) com cabeçalhos antispam."""
    if not destinatario or not _smtp_configurado():
        logger.info("Envio de e-mail ignorado (SMTP não configurado ou destinatário vazio).")
        return False

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM_EMAIL))
    msg["To"] = destinatario
    msg["Reply-To"] = settings.SMTP_FROM_EMAIL
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=settings.SMTP_FROM_EMAIL.split("@")[-1])

    msg.set_content(corpo_texto, subtype="plain", charset="utf-8")
    msg.add_alternative(corpo_html, subtype="html", charset="utf-8")

    for filename, data, maintype, subtype in anexos or []:
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

    try:
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        logger.info("E-mail enviado com sucesso para %s.", destinatario)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar e-mail para %s: %s", destinatario, exc)
        return False


def enviar_email_confirmacao_inscricao(
    email_destino: str,
    nome_participante: str,
    titulo_evento: str,
    data_evento: str,
    inscricao_id: str,
) -> bool:
    """Envia e-mail de confirmação de inscrição em evento."""
    assunto = f"Confirmação de inscrição: {titulo_evento}"
    corpo_texto = (
        f"Olá, {nome_participante}.\n\n"
        f"Sua inscrição no evento '{titulo_evento}' foi confirmada.\n"
        f"Data do evento: {data_evento}\n"
        f"Código da inscrição: {inscricao_id}\n"
        f"Status: Confirmada\n\n"
        f"Atenciosamente,\n"
        f"{settings.SMTP_FROM_NAME}"
    )

    nome_esc = html.escape(nome_participante)
    titulo_esc = html.escape(titulo_evento)
    data_esc = html.escape(str(data_evento))
    id_esc = html.escape(inscricao_id)
    remetente_esc = html.escape(settings.SMTP_FROM_NAME)

    corpo_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<body style="font-family: Arial, sans-serif; color: #1e293b; background-color: #f8fafc; padding: 24px;">
  <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 24px;">
    <h2 style="margin-top: 0; color: #312e81;">Inscrição Confirmada</h2>
    <p>Olá, <strong>{nome_esc}</strong>.</p>
    <p>Sua inscrição no evento acadêmico foi registrada com sucesso:</p>
    <table style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px;">
      <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #64748b;">Evento</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;"><strong>{titulo_esc}</strong></td></tr>
      <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #64748b;">Data</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{data_esc}</td></tr>
      <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #64748b;">Código</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-family: monospace;">{id_esc}</td></tr>
      <tr><td style="padding: 8px; color: #64748b;">Status</td><td style="padding: 8px; color: #059669;"><strong>Confirmada</strong></td></tr>
    </table>
    <p style="font-size: 12px; color: #64748b; margin-top: 24px;">
      Mensagem automática enviada por {remetente_esc}.
    </p>
  </div>
</body>
</html>"""

    return enviar_email(email_destino, assunto, corpo_texto, corpo_html)


def enviar_email_certificado(
    email_destino: str,
    nome_participante: str,
    titulo_evento: str,
    codigo_validacao: str,
    emitido_em: str,
) -> bool:
    """Envia e-mail com o certificado personalizado (PDF e JPG) em anexo."""
    assunto = f"Certificado emitido: {titulo_evento}"
    corpo_texto = (
        f"Olá, {nome_participante}.\n\n"
        f"Seu certificado de participação no evento '{titulo_evento}' foi emitido e está anexado a este e-mail.\n"
        f"Código de validação: {codigo_validacao}\n"
        f"Data de emissão: {emitido_em}\n\n"
        f"Atenciosamente,\n"
        f"{settings.SMTP_FROM_NAME}"
    )

    nome_esc = html.escape(nome_participante)
    titulo_esc = html.escape(titulo_evento)
    codigo_esc = html.escape(codigo_validacao)
    emissao_esc = html.escape(str(emitido_em))
    remetente_esc = html.escape(settings.SMTP_FROM_NAME)

    corpo_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<body style="font-family: Arial, sans-serif; color: #1e293b; background-color: #f8fafc; padding: 24px;">
  <div style="max-width: 560px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 24px;">
    <h2 style="margin-top: 0; color: #312e81;">Certificado Emitido</h2>
    <p>Olá, <strong>{nome_esc}</strong>.</p>
    <p>Parabéns pela conclusão da sua participação! Seu certificado personalizado segue anexado em PDF e imagem.</p>
    <table style="width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px;">
      <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #64748b;">Evento</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;"><strong>{titulo_esc}</strong></td></tr>
      <tr><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: #64748b;">Código de Validação</td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-family: monospace; font-size: 16px; color: #4338ca;"><strong>{codigo_esc}</strong></td></tr>
      <tr><td style="padding: 8px; color: #64748b;">Emitido em</td><td style="padding: 8px;">{emissao_esc}</td></tr>
    </table>
    <p style="font-size: 12px; color: #64748b; margin-top: 24px;">
      Mensagem automática enviada por {remetente_esc}.
    </p>
  </div>
</body>
</html>"""

    anexos = []
    arquivos = gerar_certificado_personalizado(nome_participante, titulo_evento, codigo_validacao)
    if arquivos:
        jpg_bytes, pdf_bytes = arquivos
        slug = codigo_validacao or "evento"
        anexos.append((f"certificado_{slug}.pdf", pdf_bytes, "application", "pdf"))
        anexos.append((f"certificado_{slug}.jpg", jpg_bytes, "image", "jpeg"))

    return enviar_email(email_destino, assunto, corpo_texto, corpo_html, anexos=anexos)
