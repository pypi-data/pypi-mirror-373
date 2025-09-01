# coding=utf-8
from collections.abc import Callable, Iterator
from typing import Any

import os

from ut_log.log import LogEq

from ut_path.path import Path
from ut_path.dopath import DoPath

TyAny = Any
TyArr = list[Any]
TyAoS = list[str]
TyAoA = list[TyArr]
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoA = dict[Any, TyArr]
TyDoAoA = dict[Any, TyAoA]
TyDoInt = dict[str, int]
TyDoDoInt = dict[str, TyDoInt]
TyIntStr = int | str
TyPath = str
TyPathLike = os.PathLike
TyAoPath = list[TyPath]
TyBasename = str
TyTup = tuple[Any, ...]
TyIterAny = Iterator[Any]
TyIterPath = Iterator[TyPath]
TyIterTup = Iterator[TyTup]
TyStr = str
TyToS = tuple[str, ...]

TnAny = None | TyAny
TnArr = None | TyArr
TnAoA = None | TyAoA
TnDic = None | TyDic
TnInt = None | int
TnPath = None | TyPath
TnStr = None | str
TnTup = None | TyTup


class DoDoPath:

    @classmethod
    def sh_path(cls, dodopath: TyDic, kwargs: TyDic) -> TnPath:
        LogEq.debug("dodopath", dodopath)
        if not dodopath:
            return ''
        _d_path: TyDic = dodopath.get('d_path', {})
        LogEq.debug("_d_path", _d_path)
        _path: TnPath = DoPath.sh_path(_d_path, kwargs)
        LogEq.debug("_path", _path)

        _datetype = dodopath.get('datetype')
        LogEq.debug("_datetype", _datetype)

        if _datetype:
            _path = Path.sh_path_by_datetype(_path, _datetype, kwargs)
        return _path
