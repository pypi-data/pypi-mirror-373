# coding=utf-8
import yaml


from typing import Any
TyAny = Any
TyArr = list[Any]
TyDic = dict[Any, Any]
TyPath = str
TyYaml = int | str | float | TyDic | TyArr
TnYaml = None | TyYaml

TnAny = None | Any


class Yaml_:
    """ Manage Object to Yaml file affilitation
    """
    @staticmethod
    def read_with_safeloader(path: TyPath) -> TnAny:
        try:
            with open(path) as fd:
                # The Loader parameter handles the conversion from YAML
                # scalar values to Python object format
                obj = yaml.load(fd, Loader=yaml.SafeLoader)
                return obj
        except FileNotFoundError:
            msg = f"No such file or directory: path='{path}'"
            raise Exception(msg)
        except IOError:
            raise
        return None

    @staticmethod
    def write(path: TyPath, obj: Any) -> None:
        with open(path, 'w') as fd:
            yaml.dump(
                obj, fd,
                Dumper=yaml.SafeDumper,
                sort_keys=False,
                indent=4,
                default_flow_style=False
            )
