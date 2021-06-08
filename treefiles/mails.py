import logging
import os.path
import smtplib
import ssl
from email.message import Message


def register_treemails(uname: str, passwd: str):
    import keyring

    keyring.set_password("treemails", uname, passwd)


def send_mail(login: str, msg: Message, port: int = 465, passwd: str = None):
    if passwd is None:
        import keyring

        logging.getLogger("keyring").setLevel(logging.ERROR)

        passwd = keyring.get_password("treemails", login)
    else:
        if os.path.isfile(passwd):
            with open(passwd) as f:
                passwd = f.read().strip()

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(login, passwd)
        server.send_message(msg)
    log.info(f"Message sent to {msg['To']!r}")


log = logging.getLogger(__name__)
