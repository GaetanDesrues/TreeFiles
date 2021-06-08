import logging
import smtplib
import ssl
from email.message import Message


def register_treemails(uname: str, passwd: str):
    import keyring

    keyring.set_password("treemails", uname, passwd)


def send_mail(login: str, msg: Message, port: int = 465):
    import keyring

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(login, keyring.get_password("treemails", login))
        server.send_message(msg)
    log.info(f"Message sent to {msg['To']!r}")


logging.getLogger("keyring").setLevel(logging.ERROR)
log = logging.getLogger(__name__)
