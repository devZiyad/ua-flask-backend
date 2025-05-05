import os
import logging
import smtplib

from typing import Literal
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# SMTP Configuration
SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

FROM_NAME: str = "فريق 2"
FROM_EMAIL: str = SMTP_USERNAME


def contains_non_ascii(text: str) -> bool:
    """Check if text contains non-ASCII characters."""
    try:
        text.encode("ascii")
        return False
    except UnicodeEncodeError:
        return True


def send_confirmation_email(
    recipient_email: str, lang: Literal["ar", "en"] = "en"
) -> None:
    """Send a confirmation email in Arabic or English."""
    logging.info(f"Preparing confirmation email to {recipient_email}")

    if lang == "ar":
        subject = "الاشتراك"
        body_text = "شكرًا لاشتراكك في منصتنا لدعم القبول الشامل."
    else:
        subject = "Subscription"
        body_text = (
            "Thank you for subscribing to our platform supporting Universal Acceptance."
        )

    # Build MIME message
    msg = MIMEText(body_text, _charset="utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((str(Header(FROM_NAME, "utf-8")), FROM_EMAIL))
    msg["To"] = recipient_email
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()

    # Detect encoding requirements
    requires_smtputf8 = contains_non_ascii(FROM_EMAIL) or contains_non_ascii(
        recipient_email
    )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

            if requires_smtputf8:
                logging.info("Detected non-ASCII characters. Using SMTPUTF8 extension.")
                server.sendmail(
                    FROM_EMAIL,
                    [recipient_email],
                    msg.as_string(),
                    mail_options=["SMTPUTF8"],
                )
            else:
                logging.info("No non-ASCII characters. Sending normally.")
                server.sendmail(FROM_EMAIL, [recipient_email], msg.as_string())

        logging.info(f"Confirmation email successfully sent to {recipient_email}")

    except Exception as e:
        logging.error(f"Failed to send confirmation email to {recipient_email}: {e}")
        raise
