from typing import Any
import warnings

warnings.filterwarnings("ignore")

TyDic = dict[Any, Any]
TyDoD = dict[Any, TyDic]
TyDoEq = dict[str, str | dict[str, str]]


class Parms:
    """
    Define valid Parameters with default values
    """
    d_eq: TyDoEq = {
        'mailsnd': {
            'cmd': 'str',

            'app_home': 'str',
            'app_data': 'str',

            'in_path_mail_snd': 'str',

            'log_sw_mkdirs': 'bool',
            'log_sw_single_dir': 'bool',
            'log_type': 'str',
            'log_ts_type': 'str',

            'sw_debug': 'bool',
            'tenant': 'str',
        },
        'mailrcv': {
            'cmd': 'str',

            'app_home': 'str',
            'app_data': 'str',

            'in_path_mail_rcv': 'str',

            'log_sw_mkdirs': 'bool',
            'log_sw_single_dir': 'bool',
            'log_type': 'str',
            'log_ts_type': 'str',

            'sw_debug': 'bool',
            'tenant': 'str',
        },
    }
