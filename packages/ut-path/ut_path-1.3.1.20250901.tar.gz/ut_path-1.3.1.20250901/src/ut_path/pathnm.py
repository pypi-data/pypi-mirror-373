from typing import Any

from ut_log.log import LogEq

from ut_path.path import Path

TyDic = dict[Any, Any]
TyPath = str

TnDic = None | TyDic
TnPath = None | TyPath


class PathNm:

    @staticmethod
    def sh_path(pathnm: str, kwargs: TyDic) -> TnPath:
        _path: TnPath = kwargs.get(pathnm, '')
        LogEq.debug("_path", _path)
        _path = Path.sh_path_by_tpl_and_d_pathnm2datetype(
                _path, pathnm, kwargs)
        return _path
