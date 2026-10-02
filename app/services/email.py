import logging
from email.message import EmailMessage
from pathlib import Path
from typing import Optional
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger("app.email")

# Directorio base para las plantillas de correo
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Configuración de Jinja2 para renderizado seguro de HTML
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


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
    Envía el correo de verificación de cuenta utilizando la plantilla emails/verification.html.
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

    template = jinja_env.get_template("emails/verification.html")
    html_content = template.render(
        app_name=settings.SMTP_FROM_NAME,
        verification_url=verification_url,
        token=token,
    )

    return await send_email(
        to_email=email,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )


async def send_reset_password_email(email: str, token: str) -> bool:
    """
    Envía el correo de recuperación de contraseña utilizando la plantilla emails/reset_password.html.
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

    template = jinja_env.get_template("emails/reset_password.html")
    html_content = template.render(
        app_name=settings.SMTP_FROM_NAME,
        email=email,
        reset_url=reset_url,
        token=token,
    )

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
