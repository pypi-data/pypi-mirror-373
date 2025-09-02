from typing import Any

import smtplib
import msal
from email import encoders

from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ut_path.path import AoDoDoPath
from ut_log.log import Log, LogEq

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoD = list[dict[Any, Any]]
TnAny = None | Any


class MailSnd:
    """
    Send Email
    """
    @staticmethod
    def sh_token_with_msal(d_send) -> Any:
        """
        Authenticat with Microsoft Authentication library
        """
        # Define your Azure AD app details
        client_id = d_send.get('client_id', '')
        client_secret = d_send.get('client_secret', '')
        tenant_id = d_send.get('tenant_id', '')
        url_authority = d_send.get('url_authority', 'https://login.microsoftonline.com')
        authority = f'{url_authority}/{tenant_id}'
        url_scope = [d_send.get('url_scope', 'https://graph.microsoft.com/.default')]
        scope = url_scope

        # Create a confidential client application
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret
        )

        # Acquire a token
        result = app.acquire_token_for_client(scopes=scope)

        if 'access_token' in result:
            access_token = result['access_token']
            print("Token acquired successfully")
        else:
            error = result.get('error')
            error_description = result.get('error_description')
            a_msg = ['Failed to acquire token', error, error_description]
            msg = "\n".join(a_msg)
            raise Exception(msg)
        return access_token

    @staticmethod
    def add_attachements(msg, aopath, kwargs) -> None:
        for _path in aopath:
            LogEq.debug("_path", _path)

            # Attach the file
            _attachment = MIMEBase('application', 'octet-stream')
            with open(_path, 'rb') as fd:
                _attachment.set_payload(fd.read())
            encoders.encode_base64(_attachment)
            _attachment.add_header(
                    'Content-Disposition', f'attachment; filename={_path}')
            msg.attach(_attachment)

    @classmethod
    def send(cls, msg, d_send: TyDic) -> None:
        _from: str = d_send.get('from', '')
        _host: str = d_send.get('host', '')

        _authentication = d_send.get('authentication', 'base')
        match(_authentication):
            case 'oauth2', 'modern':
                _token = cls.sh_token_with_msal(d_send)
            case _:
                _token = d_send.get('password', '')

        _sw_ssl: bool = d_send.get('sw_ssl', True)
        if _sw_ssl:
            _port = d_send.get('ssl_port', 465)
            try:
                with smtplib.SMTP_SSL(_host, _port) as smtp:
                    smtp.login(_from, _token)
                    smtp.send_message(msg)
                    smtp.quit()
            except Exception:
                # print(f"An error occurred: {e}")
                raise
        else:
            _port = d_send.get('tls_port', 587)
            try:
                with smtplib.SMTP(_host, _port) as smtp:
                    smtp.starttls()
                    smtp.login(_from, _token)
                    smtp.send_message(msg)
                    smtp.quit()
            except Exception:
                # print(f"An error occurred: {e}")
                raise


class MailDoSnd:
    """
    Send Email
    """
    @staticmethod
    def create(d_snd: TyDic):
        _from = d_snd.get('from', '')
        _to = d_snd.get('to', '')
        _subject = d_snd.get('subject', '')
        _cc = d_snd.get('cc', '')
        _bcc = d_snd.get('bcc', '')
        # Create the email
        _msg = MIMEMultipart()
        _msg['From'] = _from
        _msg['To'] = _to
        _msg['Subject'] = _subject
        if _cc:
            _msg['Cc'] = _cc
        if _bcc:
            _msg['Bcc'] = _bcc
        return _msg

    @classmethod
    def send(cls, d_snd: TyDic, kwargs: TyDic) -> None:
        LogEq.debug("_d_snd", d_snd)
        _msg = cls.create(d_snd)

        _aodod_path: TyAoD = d_snd.get('paths', [])
        _aopath: TyArr = AoDoDoPath.sh_aopath(_aodod_path, kwargs)

        _a_body: TyArr = d_snd.get('body', [])
        LogEq.debug("_a_body", _a_body)
        _body: str = '\n'.join(_a_body)
        Log.debug(f"_body: {_body} before format")
        LogEq.debug("_aopath", _aopath)
        _body = _body.format(*_aopath)
        Log.debug(f"_body: {_body} after format")

        _msg.attach(MIMEText(_body, 'plain'))

        _sw_attachements: TyAoD = d_snd.get('sw_attachements', False)
        if _sw_attachements:
            MailSnd.add_attachements(_msg, _aopath, kwargs)

        # Send the email
        MailSnd.send(_msg, d_snd)
