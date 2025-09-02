from typing import Any, Generator

import imaplib

from ut_log.log import LogEq

TyAny = Any
TyBool = bool
TyIMAP4 = imaplib.IMAP4 | imaplib.IMAP4_SSL
TyDic = dict[Any, Any]
TyGenStr = Generator[str, None, None]
TyMsg = bytes | Any
TyStr = str
TnAny = None | Any


class MailRcv:
    """ Receive Email
    """
    @staticmethod
    def connect(d_rcv: TyDic) -> TyIMAP4:
        _sw_ssl: TyBool = d_rcv.get('sw_ssl', True)
        _host = d_rcv.get('host', 'imap.gmail.com')
        # Connect to the server
        if _sw_ssl:
            _mail: TyIMAP4 = imaplib.IMAP4_SSL(_host)
        else:
            _mail = imaplib.IMAP4(_host)
        return _mail

    @staticmethod
    def login(mail: TyIMAP4, d_rcv: TyDic) -> None:
        _from = d_rcv.get('from', 'bernd.stroehle@gmail.com')
        _password = d_rcv.get('password', '')
        mail.login(_from, _password)

    @staticmethod
    def yield_body(mail: TyIMAP4, message: TyStr) -> TyGenStr:
        import email
        _email_ids = message.split()
        for email_id in _email_ids:
            # Fetch the email by ID
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            if not isinstance(msg_data, tuple):
                continue

            # Get the email content
            msg = msg_data[0][1]
            if not isinstance(msg, (bytes, bytearray)):
                continue

            # Parse the email
            email_message = email.message_from_bytes(msg)

            # Print the subject
            LogEq.debug("email_message['subject']", email_message['subject'])
            # Print the sender
            LogEq.debug("email_message['from']", email_message['from'])

            # Print the email body
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain':
                        _payload_part: bytes | Any = part.get_payload(decode=True)
                        _body = _payload_part.decode()
                        yield _body
            else:
                _payload_msg: TyMsg = email_message.get_payload(decode=True)
                _body = _payload_msg.decode()
                yield _body
