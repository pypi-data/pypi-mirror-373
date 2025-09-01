# coding=utf-8
from collections.abc import Callable, Iterator
from typing import Any

import os

from ut_log.log import LogEq

from ut_path.dodopath import DoDoPath

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


class AoDoDoPath:
    """
    Manage Array of Path-Dictionaries
    """
    @staticmethod
    def sh_aopath(aodod_path: TyAoD, kwargs: TyDic) -> TyAoPath:
        _aopath: TyAoPath = []
        LogEq.debug("aodod_path", aodod_path)
        if not aodod_path:
            LogEq.debug("_aopath", _aopath)
            return _aopath
        for _dod_path in aodod_path:
            _path: TnPath = DoDoPath.sh_path(_dod_path, kwargs)
            if not _path:
                continue
            _aopath.append(_path)
        LogEq.debug("_aopath", _aopath)
        return _aopath
