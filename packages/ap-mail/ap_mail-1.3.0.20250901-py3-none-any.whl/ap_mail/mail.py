from typing import Any

from ut_log.log import LogEq
from ut_path.path import Path
from ut_ioc.yaml_ import Yaml_

from ap_mail.mailrcv import MailRcv
from ap_mail.mailsnd import MailDoSnd

TyAny = Any
TyDic = dict[Any, Any]
TyPath = str
TnAny = None | TyAny


class Mail:

    @staticmethod
    def snd(kwargs: TyDic) -> None:
        _in_path_mail_snd: TyPath = kwargs.get('in_path_mail_snd', '')
        LogEq.debug("_in_path_mail_snd", _in_path_mail_snd)
        _path: TyPath = Path.sh_path_by_tpl_pac_sep(_in_path_mail_snd, kwargs)
        LogEq.debug("_path", _path)
        _aod_snd: TnAny = Yaml_.read_with_safeloader(_path)
        if not _aod_snd:
            raise Exception(f"Content of yaml file = {_path} is undefined or empty")
        LogEq.debug("_aod_snd", _aod_snd)

        for _d_snd in _aod_snd:
            MailDoSnd.send(_d_snd, kwargs)

    @staticmethod
    def rcv(kwargs: TyDic) -> None:
        _in_path_mail_rcv = kwargs.get('in_path_mail_rcv', '')
        LogEq.debug("_in_path_mail_rcv", _in_path_mail_rcv)
        _path: TyPath = Path.sh_path_by_tpl_pac_sep(_in_path_mail_rcv, kwargs)
        LogEq.debug("_path", _path)
        _d_rcv: TnAny = Yaml_.read_with_safeloader(_path)
        if not _d_rcv:
            raise Exception(f"Content of yaml file = {_path} is undefined or empty")
        # Connect to the server
        _mail = MailRcv.connect(_d_rcv)
        # Login to your account
        MailRcv.login(_mail, _d_rcv)

        # Select the mailbox you want to check
        _mail.select("inbox")
        # Search for all emails in the inbox
        # status, messages = _mail.search(None, "ALL")
        # Search for unread emails
        status, messages = _mail.search(None, 'UNSEEN')
        # Convert messages to a list of email IDs

        # Reading Emails
        # Now that you have the email IDs, you can fetch and read the emails.
        # Here’s how to do it:
        # Fetch the latest email
        # latest_email_id = _email_ids[-1]
        MailRcv.yield_body(_mail, messages[0])

        # Logout
        _mail.logout()
