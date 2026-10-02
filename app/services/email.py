import logging
from email.message import EmailMessage
from typing import Optional
import aiosmtplib

from app.core.config import settings

logger = logging.getLogger("app.email")


def _is_placeholder_credential(val: Optional[str]) -> bool:
    if not val:
        return True
    lower = val.lower().strip()
    return "tu_correo" in lower or "tu_contrasena" in lower or "example" in lower or "change_me" in lower


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> bool:
    """
    Envía un correo electrónico asíncrono utilizando el servidor SMTP configurado (Gmail).
    """
    if _is_placeholder_credential(settings.SMTP_USER) or _is_placeholder_credential(settings.SMTP_PASSWORD):
        logger.warning(
            "⚠️ [SMTP NO CONFIGURADO] Detectadas credenciales por defecto o vacías en .env.\n"
            f"   Destinatario: {to_email}\n"
            f"   Asunto: {subject}\n"
            f"   Contenido texto:\n{text_content or 'Ver contenido HTML'}\n"
        )
        return False

    message = EmailMessage()
    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
    if settings.SMTP_FROM_NAME:
        message["From"] = f"{settings.SMTP_FROM_NAME} <{from_email}>"
    else:
        message["From"] = from_email

    message["To"] = to_email
    message["Subject"] = subject

    if text_content:
        message.set_content(text_content)
    else:
        message.set_content("Por favor visualiza este correo en un cliente compatible con HTML.")

    message.add_alternative(html_content, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=(settings.SMTP_PORT == 587 and settings.SMTP_TLS),
            use_tls=(settings.SMTP_PORT == 465),
            timeout=30,
        )
        logger.info(f"✅ Correo enviado con éxito a {to_email} (Asunto: '{subject}')")
        return True
    except Exception as e:
        logger.error(
            f"❌ Error al enviar correo vía SMTP ({settings.SMTP_HOST}:{settings.SMTP_PORT}) a {to_email}: {e}",
            exc_info=True,
        )
        return False


async def send_verification_email(email: str, token: str) -> bool:
    """
    Envía el correo de verificación de cuenta con el enlace y el token correspondiente.
    """
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    subject = f"Verifica tu cuenta - {settings.SMTP_FROM_NAME}"

    text_content = f"""Hola,

¡Gracias por registrarte en {settings.SMTP_FROM_NAME}!

Para completar la activación de tu cuenta y confirmar tu correo electrónico, haz clic en el siguiente enlace:
{verification_url}

Si tu aplicación te solicita ingresar el token directamente, copia este código:
{token}

Nota: Este enlace tiene una validez de 24 horas.
Si no has creado una cuenta con nosotros, puedes ignorar este mensaje.

Atentamente,
El equipo de {settings.SMTP_FROM_NAME}
"""

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f8fafc;
      margin: 0;
      padding: 0;
      color: #1e293b;
    }}
    .wrapper {{
      width: 100%;
      background-color: #f8fafc;
      padding: 40px 0;
    }}
    .card {{
      max-width: 560px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
      border: 1px solid #e2e8f0;
    }}
    .header {{
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #ffffff;
      padding: 32px 24px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .body {{
      padding: 36px 32px;
    }}
    .body h2 {{
      color: #0f172a;
      font-size: 20px;
      margin-top: 0;
      margin-bottom: 16px;
    }}
    .body p {{
      color: #475569;
      font-size: 15px;
      line-height: 1.6;
      margin: 0 0 16px 0;
    }}
    .btn-container {{
      text-align: center;
      margin: 28px 0;
    }}
    .btn {{
      background-color: #2563eb;
      color: #ffffff !important;
      padding: 14px 32px;
      font-size: 15px;
      font-weight: 600;
      text-decoration: none;
      border-radius: 8px;
      display: inline-block;
    }}
    .token-box {{
      background-color: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 12px 16px;
      font-family: monospace;
      font-size: 13px;
      word-break: break-all;
      color: #0f172a;
      margin-top: 8px;
    }}
    .subtext {{
      font-size: 13px !important;
      color: #64748b !important;
    }}
    .footer {{
      background-color: #f8fafc;
      padding: 24px;
      text-align: center;
      font-size: 12px;
      color: #94a3b8;
      border-top: 1px solid #e2e8f0;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="card">
      <div class="header">
        <h1>{settings.SMTP_FROM_NAME}</h1>
      </div>
      <div class="body">
        <h2>¡Te damos la bienvenida!</h2>
        <p>Gracias por unirte a nuestra plataforma. Para verificar tu dirección de correo electrónico y activar tu cuenta, haz clic en el siguiente botón:</p>
        <div class="btn-container">
          <a href="{verification_url}" class="btn" target="_blank">Verificar mi correo electrónico</a>
        </div>
        <p class="subtext">Si el botón no funciona en tu cliente de correo, copia y pega el siguiente enlace en tu navegador:</p>
        <p class="subtext" style="word-break: break-all;"><a href="{verification_url}" style="color: #2563eb;">{verification_url}</a></p>
        
        <p class="subtext" style="margin-top: 24px;">O si tu pantalla de verificación solicita el token directo:</p>
        <div class="token-box">{token}</div>

        <p class="subtext" style="margin-top: 28px; border-top: 1px solid #f1f5f9; padding-top: 16px;">
          ⏱️ Este enlace es válido durante <strong>24 horas</strong>.<br>
          Si tú no creaste esta cuenta, puedes desestimar este mensaje de forma segura.
        </p>
      </div>
      <div class="footer">
        © {settings.SMTP_FROM_NAME}. Todos los derechos reservados.
      </div>
    </div>
  </div>
</body>
</html>"""

    return await send_email(
        to_email=email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )


async def send_reset_password_email(email: str, token: str) -> bool:
    """
    Envía el correo de recuperación de contraseña con el enlace y el token correspondiente.
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = f"Recupera tu contraseña - {settings.SMTP_FROM_NAME}"

    text_content = f"""Hola,

Recibimos una solicitud para restablecer la contraseña asociada a tu cuenta ({email}) en {settings.SMTP_FROM_NAME}.

Para elegir una nueva contraseña, haz clic en el siguiente enlace:
{reset_url}

Si tu aplicación te solicita ingresar el token directamente, copia este código:
{token}

Nota: Este enlace tiene una validez de 1 hora.
Si tú no realizaste esta solicitud, puedes ignorar este correo; tu cuenta continuará protegida y tu contraseña actual no será modificada.

Atentamente,
El equipo de {settings.SMTP_FROM_NAME}
"""

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f8fafc;
      margin: 0;
      padding: 0;
      color: #1e293b;
    }}
    .wrapper {{
      width: 100%;
      background-color: #f8fafc;
      padding: 40px 0;
    }}
    .card {{
      max-width: 560px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
      border: 1px solid #e2e8f0;
    }}
    .header {{
      background: linear-gradient(135deg, #dc2626, #b91c1c);
      color: #ffffff;
      padding: 32px 24px;
      text-align: center;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .body {{
      padding: 36px 32px;
    }}
    .body h2 {{
      color: #0f172a;
      font-size: 20px;
      margin-top: 0;
      margin-bottom: 16px;
    }}
    .body p {{
      color: #475569;
      font-size: 15px;
      line-height: 1.6;
      margin: 0 0 16px 0;
    }}
    .btn-container {{
      text-align: center;
      margin: 28px 0;
    }}
    .btn {{
      background-color: #dc2626;
      color: #ffffff !important;
      padding: 14px 32px;
      font-size: 15px;
      font-weight: 600;
      text-decoration: none;
      border-radius: 8px;
      display: inline-block;
    }}
    .token-box {{
      background-color: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 12px 16px;
      font-family: monospace;
      font-size: 13px;
      word-break: break-all;
      color: #0f172a;
      margin-top: 8px;
    }}
    .subtext {{
      font-size: 13px !important;
      color: #64748b !important;
    }}
    .footer {{
      background-color: #f8fafc;
      padding: 24px;
      text-align: center;
      font-size: 12px;
      color: #94a3b8;
      border-top: 1px solid #e2e8f0;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="card">
      <div class="header">
        <h1>{settings.SMTP_FROM_NAME}</h1>
      </div>
      <div class="body">
        <h2>Restablecer contraseña</h2>
        <p>Hemos recibido una solicitud para restablecer la contraseña asociada a tu cuenta (<strong>{email}</strong>).</p>
        <p>Haz clic en el botón siguiente para definir una nueva contraseña:</p>
        <div class="btn-container">
          <a href="{reset_url}" class="btn" target="_blank">Restablecer mi contraseña</a>
        </div>
        <p class="subtext">Si el botón no funciona en tu cliente de correo, copia y pega el siguiente enlace en tu navegador:</p>
        <p class="subtext" style="word-break: break-all;"><a href="{reset_url}" style="color: #dc2626;">{reset_url}</a></p>
        
        <p class="subtext" style="margin-top: 24px;">O si tu formulario de reseteo solicita el token directo:</p>
        <div class="token-box">{token}</div>

        <p class="subtext" style="margin-top: 28px; border-top: 1px solid #f1f5f9; padding-top: 16px;">
          ⏱️ Este enlace es válido durante <strong>1 hora</strong>.<br>
          Si no solicitaste este cambio, no te preocupes, puedes ignorar este mensaje de forma segura. Tu contraseña no cambiará.
        </p>
      </div>
      <div class="footer">
        © {settings.SMTP_FROM_NAME}. Todos los derechos reservados.
      </div>
    </div>
  </div>
</body>
</html>"""

    return await send_email(
        to_email=email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )


if __name__ == "__main__":
    import asyncio
    import sys

    async def main():
        logging.basicConfig(level=logging.INFO)
        target = sys.argv[1] if len(sys.argv) > 1 else settings.SMTP_USER
        if not target or _is_placeholder_credential(target):
            print("Uso: python -m app.services.email <correo_destino_real>")
            print("Ejemplo: python -m app.services.email tu_correo_personal@gmail.com")
            return
        print(f"Probando envío de correo a {target} vía {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        res = await send_email(
            to_email=target,
            subject="Prueba de configuración SMTP Gmail",
            html_content="<h1>¡Prueba exitosa!</h1><p>Tu backend en FastAPI está enviando correos correctamente mediante Gmail SMTP.</p>",
            text_content="¡Prueba exitosa! Tu backend en FastAPI está enviando correos correctamente mediante Gmail SMTP.",
        )
        print(f"Resultado del envío: {'Éxito' if res else 'Falló (Revisa logs arriba)'}")

    asyncio.run(main())
