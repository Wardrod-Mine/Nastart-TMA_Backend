import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

def send_email(to_email: str, content: str):
    subject = "Новый заказ"
    body = content

    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.yandex.ru', 587)
        server.starttls()
        server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)

        server.send_message(msg)

    except Exception as e:
        logging.error(f"Error while sending email: {e}")

    finally:
        server.quit() 

