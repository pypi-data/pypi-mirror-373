# coding=utf-8
from collections.abc import Callable, Iterator
from typing import Any

import glob
import importlib
import os
import pathlib

from ut_dic.dic import Dic
from ut_log.log import Log, LogEq

from ut_path.path import Path

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
TyAoPath = list[str]
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


class AoPath:

    @staticmethod
    def join(aopath: TyAoPath) -> TyPath:
        _sep = os.sep
        return ''.join([_sep+_path.strip(_sep) for _path in aopath if _path])

    @staticmethod
    def mkdirs(aopath: TyAoPath, **kwargs) -> None:
        if not aopath:
            return
        for _path in aopath:
            os.makedirs(_path, **kwargs)

    @staticmethod
    def sh_a_path(path: TyPath) -> TyAoPath:
        a_path: TyAoPath = glob.glob(path)
        return a_path

    @classmethod
    def sh_aopath_by_tpl(
            cls, a_path_tpl_key: TyAoPath, kwargs: TyDic) -> TyAoPath:
        # _a_path_tpl: TyAoPath = cls.sh_items_in_dic(a_path_tpl_key, kwargs)
        _a_path_tpl: TyAoPath = Dic.sh_values_by_keys(kwargs, a_path_tpl_key)
        _path_tpl: TyPath = cls.join(_a_path_tpl)
        return cls.sh_a_path(_path_tpl)

    @staticmethod
    def sh_aopath_by_glob(aopath: TyAoPath) -> TyArr:
        if not aopath:
            return []
        _aopath: TyArr = []
        for _path in aopath:
            _aopath = _aopath + glob.glob(_path)
        return _aopath

    @staticmethod
    def sh_aopart_by_pac(a_part: TyArr, kwargs: TyDic) -> TyAoPath:
        LogEq.debug("a_part", a_part)
        _a_part: TyArr = []
        for _part in a_part:
            LogEq.debug("_part", _part)
            if _part == 'package':
                _package = kwargs.get('package', '')
                _dir_package: TyPath = str(importlib.resources.files(_package))
                _a_part.append(_dir_package)
            else:
                _a_part.append(_part)
        LogEq.debug("_a_part", _a_part)
        return _a_part

    @classmethod
    def sh_aopath_by_pac(cls, a_part: TyArr, kwargs: TyDic) -> TyAoPath:
        if a_part[0] == os.sep:
            _a_part = a_part[1:]
        else:
            _a_part = a_part
        _part0 = a_part[0]
        LogEq.debug("_part0", _part0)
        _a_part0 = _part0.split("|")
        _a_part0_new = cls.sh_aopart_by_pac(_a_part0, kwargs)
        LogEq.debug("_a_part0_new", _a_part0_new)

        _a_path: TyArr = []
        for _part in _a_part0_new:
            LogEq.debug("_part", _part)
            # _a_part_new = [os.sep, _part] + _a_part[1:]
            _a_part_new = [_part] + _a_part[1:]
            LogEq.debug("_a_part_new", _a_part_new)
            _path_new = str(pathlib.Path(*_a_part_new))
            LogEq.debug("_path_new", _path_new)
            _a_path.append(_path_new)
        return _a_path

    @staticmethod
    def sh_aopath_mtime_gt_threshold(
            aopath: TyAoPath, mtime_threshold_s: float) -> TyAoPath:
        _aopath: TyAoPath = []
        if not aopath:
            return _aopath
        for _path in aopath:
            # Get file's last modified time in micro seconds
            _mtime_µs = os.path.getmtime(_path)
            _mtime_s = _mtime_µs / 1_000_000
            LogEq.debug("_path", _path)
            LogEq.debug("_mtime_µs", _mtime_µs)
            LogEq.debug("_mtime_s", _mtime_s)
            LogEq.debug("mtime_threshold", mtime_threshold_s)
            if _mtime_s > mtime_threshold_s:
                msg = (f"mtime_s: {_mtime_s} of _path: {_path} ",
                       f"is greater than: {mtime_threshold_s}")
                Log.debug(msg)
                _aopath.append(_path)
        LogEq.debug("_aopath", _aopath)
        return _aopath

    # @staticmethod
    # def sh_items_in_dic(arr: TnArr, dic: TnDic) -> TyArr:
    #     # def sh_values(arr: TnArr, dic: TnDic) -> TyArr:
    #     a_new: TyArr = []
    #     if not arr:
    #         return a_new
    #     if not dic:
    #         return a_new
    #     for _key in arr:
    #         if _key in dic:
    #             a_new.append(dic[_key])
    #     return a_new

    @staticmethod
    def sh_path_by_tpl_first_exist(a_path: TyArr, kwargs: TyDic) -> TyPath:
        LogEq.debug("a_path", a_path)
        _a_path_new = []
        for _path in a_path:
            LogEq.debug("_path", _path)
            _path_new: TnPath = Path.sh_path_by_tpl(_path, kwargs)
            if not _path_new:
                continue
            if os.path.exists(_path_new):
                return _path_new
            _a_path_new.append(_path_new)
        msg = f"No path of the path-list with resolved variables {_a_path_new} exists"
        raise Exception(msg)

    @classmethod
    def yield_path_kwargs_over_path(
        # def yield_over_a_path(
            cls, a_path_tpl_key: TyAoPath, kwargs: TyDic
    ) -> TyIterTup:
        _a_path: TyAoPath = cls.sh_aopath_by_tpl(a_path_tpl_key, kwargs)
        for _path in _a_path:
            yield (_path, kwargs)

    @classmethod
    def yield_path_kwargs_over_dir_path(
        # def yield_path_kwargs_new(
        # def yield_over_a_dir_a_path(
            cls,
            a_dir_tpl_key: TyAoPath,
            a_path_tpl_key: TyAoPath,
            sh_kwargs_new: TyCallable,
            kwargs: TyDic
    ) -> TyIterTup:
        _a_dir: TyAoPath = cls.sh_aopath_by_tpl(a_dir_tpl_key, kwargs)
        for _dir in _a_dir:
            _kwargs_new: TyDic = sh_kwargs_new([_dir, kwargs])
            _a_path: TyAoPath = cls.sh_aopath_by_tpl(
                    a_path_tpl_key, _kwargs_new)
            for _path in _a_path:
                yield (_path, _kwargs_new)

    @classmethod
    def yield_path_item_kwargs_over_path_arr(
        # def yield_path_item_kwargs(
        # def yield_over_a_path_arr(
            cls, a_path_tpl_key: TyAoPath, arr_key: str, kwargs: TyDic
    ) -> TyIterTup:
        _a_path: TyAoPath = cls.sh_aopath_by_tpl(a_path_tpl_key, kwargs)
        _arr: TyAoPath = kwargs.get(arr_key, [])
        for _path in _a_path:
            for _item in _arr:
                yield (_path, _item, kwargs)

    @classmethod
    def yield_path_item_kwargs_over_dir_path_arr(
        # def yield_path_item_kwargs_new(
        # def yield_over_a_dir_a_path_arr(
            cls,
            a_dir_tpl_key: TyAoPath,
            a_path_tpl_key: TyAoPath,
            arr_key: str,
            sh_kwargs_new: TyCallable,
            kwargs: TyDic
    ) -> TyIterTup:
        _a_dir: TyAoPath = cls.sh_aopath_by_tpl(a_dir_tpl_key, kwargs)
        _arr: TyAoPath = kwargs.get(arr_key, [])
        for _dir in _a_dir:
            _kwargs_new: TyDic = sh_kwargs_new([_dir, kwargs])
            _a_path: TyAoPath = cls.sh_aopath_by_tpl(
                    a_path_tpl_key, _kwargs_new)
            for _path in _a_path:
                for _item in _arr:
                    yield (_path, _item, _kwargs_new)
