# coding=utf-8
from typing import Any

import os

from ut_log.log import Log, LogEq
from ut_pac.pac import Pac

TyAny = Any
TyDic = dict[Any, Any]
TyPath = str
TyStr = str
TyAoStr = list[TyStr]
TyDoPath = dict[Any, TyPath]

TnPath = None | TyPath


class DoPath:

    @staticmethod
    def sh_a_part(d_path: TyDoPath, kwargs: TyDic) -> TyAoStr:
        LogEq.debug("d_path", d_path)
        _a_part: TyAoStr = []
        _package: TyStr = kwargs.get('package', '')
        LogEq.debug("_package", _package)

        for _k, _v in d_path.items():
            LogEq.debug("_k", _k)
            LogEq.debug("_v", _v)
            match _v:
                case 'key':
                    _val = kwargs.get(_k)
                    if _val:
                        _a_part.append(_val)
                case 'pac':
                    _val = Pac.sh_path_by_path(_package, _k, Log.log)
                    if _val:
                        _a_part.append(_val)
                case _:
                    _a_part.append(_k)

        return _a_part

    @classmethod
    def sh_path(cls, d_path: TyDoPath, kwargs: TyDic) -> TnPath:
        _a_part: TyAoStr = cls.sh_a_part(d_path, kwargs)
        LogEq.debug("_a_part", _a_part)
        if not _a_part:
            msg = f"_a_part for d_path = {d_path} is undefined or empty"
            Log.error(msg)
            # raise Exception(msg)
            return None
        return os.path.join(*_a_part)
