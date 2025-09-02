# coding=utf-8
# from collections.abc import Callable
from typing import Any

import os
import yaml
import jinja2
from logging import Logger

TyAny = Any
TyDic = dict[Any, Any]
TyLogger = Logger
TyPath = str
TyStr = str
TyJinja2Env = jinja2.environment.Environment
TyJinja2Tmpl = jinja2.environment.Template

TnDic = None | TyDic
TnStr = None | TyStr


class Jinja2_:
    """
    Manage Object to Json file affilitation
    """
    @staticmethod
    def read_template(path: TyPath) -> TyJinja2Tmpl:
        directory, file = os.path.split(path)
        env: TyJinja2Env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(directory))
        template: TyJinja2Tmpl = env.get_template(file)
        return template

    @classmethod
    def read(cls, path: TyPath, log: TyLogger, **kwargs) -> Any:
        try:
            # read jinja template from file
            template: TyJinja2Tmpl = cls.read_template(path)
            # render template as yaml string
            template_rendered: str = template.render(kwargs)
            # load yaml string into object
            return yaml.safe_load(template_rendered)
        except IOError as exc:
            log.critical(exc, exc_info=True)
            # log.error(f"No such file or directory: path='{path'}")
            raise
