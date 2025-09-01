# coding=utf-8
from collections.abc import Callable, Iterator
from typing import Any

import datetime
import glob
from importlib import resources
import os
import pathlib
import pandas as pd
import re
from string import Template

from ut_aod.aod import AoD
from ut_dic.dic import Dic
from ut_pac.pac import Pac
from ut_log.log import Log, LogEq
from ut_obj.str import Str

TyAny = Any
TyObj = Any
TyAoS = list[str]
TyArr = list[Any]
TyAoA = list[TyArr]
TyBasename = str
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoA = dict[Any, TyArr]
TyDoAoA = dict[Any, TyAoA]
TyDoD = dict[Any, TyDic]
TyDoInt = dict[str, int]
TyDoDoInt = dict[str, TyDoInt]
TyFnc = Callable[..., Any]
TyIntStr = int | str
TyIoS = Iterator[str]
TyPath = str
TyPathLike = os.PathLike
TyAoPath = list[str]
TyTup = tuple[Any, ...]
TyIterAny = Iterator[Any]
TyIterPath = Iterator[TyPath]
TyIterTup = Iterator[TyTup]
TyStr = str
TyToS = tuple[str, ...]

TnAny = None | TyAny
TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoPath = None | TyAoPath
TnBool = None | bool
TnDic = None | TyDic
TnFnc = None | TyFnc
TnInt = None | int
TnPath = None | TyPath
TnStr = None | str
TnTup = None | TyTup


class Path:

    @staticmethod
    def count(path_pattern: TnPath) -> None | int:
        """
        count number of paths that match path pattern
        """
        if not path_pattern:
            return None
        return len(list(glob.iglob(path_pattern)))

    @staticmethod
    def ex_get_aod_by_fnc(
            path: TnPath, fnc: TyFnc, kwargs: TyDic) -> TyAoD:
        _aod: TyAoD = []
        if not path:
            return _aod
        _mode = kwargs.get('mode', 'r')
        with open(path, _mode) as _fd:
            for _line in _fd:
                _dic = Str.sh_dic(_line)
                _obj = fnc(_dic, kwargs)
                AoD.add(_aod, _obj)
        return _aod

    @staticmethod
    def ex_get_aod(path: TnPath, kwargs: TyDic) -> TyAoD:
        _aod: TyAoD = []
        if not path:
            return _aod
        _mode = kwargs.get('mode', 'r')
        with open(path, _mode) as _fd:
            for _line in _fd:
                _dic = Str.sh_dic(_line)
                AoD.add(_aod, _dic)
        return _aod

    @staticmethod
    def ex_get_dod_by_fnc(
            path: TnPath, fnc: TyFnc, key: str, kwargs: TyDic) -> TyDoD:
        """
        Create a dictionary of dictionaries by executing the following steps:
        1. read every line of the json file <path> into a dictionary
        2. If the function <obj_fnc> is not None:
             transform the dictionary by the function <obj_fnc>
             get value of the transformed dictionary for the key <key>
           else
             get value of the dictionary for the key <key>
        2. if the value is not None:
             insert the transformed dictionary into the new dictionary
             of dictionaries with the value as key.
        """
        _dod: TyDoD = {}
        if not path:
            return _dod
        _mode = kwargs.get('mode', 'r')
        with open(path, _mode) as _fd:
            for _line in _fd:
                _obj = Str.sh_dic(_line)
                _obj = fnc(_obj, kwargs)
                if _obj is not None:
                    _key = _obj.get(key)
                    if _key is not None:
                        _dod[_key] = _obj
        return _dod

    @staticmethod
    def ex_get_dod(
            path: TnPath, key: str, kwargs: TyDic) -> TyDoD:
        """
        Create a dictionary of dictionaries by executing the following steps:
        1. read every line of the json file <path> into a dictionary
        2. If the function <obj_fnc> is not None:
             transform the dictionary by the function <obj_fnc>
             get value of the transformed dictionary for the key <key>
           else
             get value of the dictionary for the key <key>
        2. if the value is not None:
             insert the transformed dictionary into the new dictionary
             of dictionaries with the value as key.
        """
        _dod: TyDoD = {}
        if not path:
            return _dod
        _mode = kwargs.get('mode', 'r')
        with open(path, _mode) as _fd:
            for _line in _fd:
                _obj = Str.sh_dic(_line)
                if _obj is not None:
                    _key = _obj.get(key)
                    _key = _obj[key]
                    if _key is not None:
                        _dod[_key] = _obj
        return _dod

    @classmethod
    def get_aod(cls, path: TnPath, fnc: TnFnc, kwargs: TyDic) -> TyAoD:
        # Timer.start(cls.get_aod, f"{path}")
        if fnc is not None:
            _aod = cls.ex_get_aod_by_fnc(path, fnc, kwargs)
        else:
            _aod = cls.ex_get_aod(path, kwargs)
        # Timer.end(cls.get_aod, f"{path}")
        return _aod

    @classmethod
    def get_first_dic(cls, path: TnPath, fnc: TnFnc, kwargs: TyDic) -> TyDic:
        # def get_dic(cls, path: TyPath, fnc: TnFnc, kwargs: TyDic) -> TyDic:
        aod = cls.get_aod(path, fnc, kwargs)
        if len(aod) > 1:
            msg = (f"File {path} contains {len(aod)} records; "
                   "it should contain only one record")
            raise Exception(msg)
        return aod[0]

    @classmethod
    def get_dod(
            cls, path: TnPath, fnc: TnFnc, key: str, kwargs: TyDic) -> TyDoD:
        """
        Create a dictionary of dictionaries by executing the following steps:
        1. read every line of the json file <path> into a dictionary
        2. If the function <obj_fnc> is not None:
             transform the dictionary by the function <obj_fnc>
             get value of the transformed dictionary for the key <key>
           else
             get value of the dictionary for the key <key>
        2. if the value is not None:
             insert the transformed dictionary into the new dictionary
             of dictionaries with the value as key.
        """
        if fnc is not None:
            _dod = cls.ex_get_dod_by_fnc(path, fnc, key, kwargs)
        else:
            _dod = cls.ex_get_dod(path, key, kwargs)
        return _dod

    @staticmethod
    def get_latest(path_pattern: TnPath) -> TnPath:
        """
        get latest path that match path pattern
        """
        if not path_pattern:
            return None
        _iter_path = glob.iglob(path_pattern)
        _a_path = list(_iter_path)
        if len(_a_path) <= 0:
            msg = f"No path exist for pattern: {path_pattern}"
            Log.error(msg)
            return None
        return max(_a_path, key=os.path.getmtime)

    @staticmethod
    def get_paths(
            path_pattern: TnPath, sw_recursive: TnBool = None) -> TyIoS:
        """
        get all paths that match path_pattern
        """
        if not path_pattern:
            return
        if sw_recursive is None:
            sw_recursive = False
        _paths: Iterator[str] = glob.iglob(path_pattern, recursive=sw_recursive)
        LogEq.debug("path_pattern", path_pattern)
        LogEq.debug("_paths", _paths)
        for _path in _paths:
            if os.path.isfile(_path):
                LogEq.debug("_path", _path)
                yield _path

    @staticmethod
    def io(obj: TyObj, path: TnPath, fnc: TyFnc) -> None:
        """
        execute io function
        """
        fnc(obj, path)

    @staticmethod
    def verify(path: TnPath) -> None:
        if path is None:
            raise Exception("path is None")
        elif path == '':
            raise Exception("path is empty")

    @classmethod
    def edit_path(cls, path: TnPath, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        _d_edit = kwargs.get('d_out_path_edit', {})
        _prefix = kwargs.get('dl_out_file_prefix', '')
        _suffix = kwargs.get('dl_out_file_suffix', '.csv')
        _edit_from = _d_edit.get('from')
        _edit_to = _d_edit.get('to')
        if _edit_from is not None and _edit_to is not None:
            _path_out = path.replace(_edit_from, _edit_to)
        else:
            _path_out = path
        _dir_out = os.path.dirname(_path_out)
        cls.mkdir_from_path(_dir_out)
        _basename_out = os.path.basename(_path_out)
        if _prefix:
            _basename_out = str(f"{_prefix}{_basename_out}")
        if _suffix:
            _basename_out = os.path.splitext(_basename_out)[0]
            _basename_out = str(f"{_basename_out}{_suffix}")
        _path_out = os.path.join(_dir_out, _basename_out)
        return _path_out

    @staticmethod
    def mkdir(path: TnPath) -> None:
        if not path:
            return
        if not os.path.exists(path):
            # Create the directory
            os.makedirs(path)

    @staticmethod
    def mkdir_from_path(path: TnPath) -> None:
        if not path:
            return
        _dir = os.path.dirname(path)
        if not os.path.exists(_dir):
            # Create the directory
            os.makedirs(_dir)

    @staticmethod
    def sh_aopath(path: TnPath) -> TyAoPath:
        if not path:
            raise Exception("Argument 'path' is empty")
        return glob.glob(path)

    @classmethod
    def sh_aopath_mtime_gt_threshold(
            cls, path: TnPath, mtime_threshhold: float) -> TnAoPath:
        return AoPath.sh_aopath_mtime_gt_threshold(
                cls.sh_aopath(path), mtime_threshhold)

    @staticmethod
    def sh_basename(path: TnPath) -> None | TyBasename:
        """
        Extracts basename of a given path.
        Should Work with any OS Path on any OS
        """
        if not path:
            return path
        raw_string = r'[^\\/]+(?=[\\/]?$)'
        basename = re.search(raw_string, path)
        if basename:
            return basename.group(0)
        return path

    @classmethod
    def sh_components(
            cls, path: TnPath, d_ix: TyDic, separator: str = "-") -> TnPath:
        if not path:
            return path
        ix_start = d_ix.get("start")
        ix_add = d_ix.get("add", 0)
        if not ix_start:
            return None
        _a_dir: TyArr = cls.split_to_array(path)
        _ix_end = ix_start + ix_add + 1
        _component = separator.join(_a_dir[ix_start:_ix_end])
        _a_component = os.path.splitext(_component)
        return _a_component[0]

    @classmethod
    def sh_component_by_field_name(
        # def sh_component_at_start(
            cls, path: TnPath, d_path_ix: TyDoDoInt, field_name: str) -> TnPath:
        if not path:
            return path
        _d_ix: TyDoInt = d_path_ix.get(field_name, {})
        if not _d_ix:
            msg = f"field_name: {field_name} is not defined in dictionary: {d_path_ix}"
            raise Exception(msg)
        _start = _d_ix.get('start')
        if not _start:
            msg = f"'start' is not defined in dictionary: {_d_ix}"
            raise Exception(msg)
        _a_dir: TyAoS = cls.split_to_array(path)
        if _start < len(_a_dir):
            return _a_dir[_start]
        msg = f"index: {_start} is out of range of list: {_a_dir}"
        raise Exception(msg)

    @classmethod
    def sh_data_type(cls, path: TnPath, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        _d_in_path_ix: TyDoDoInt = kwargs.get("d_in_path_ix", {})
        _d_data_type_ix: TyDoInt = _d_in_path_ix.get("data_type", {})
        return cls.sh_components(path, _d_data_type_ix)

    @classmethod
    def sh_rundatetime_ms(cls, dl_in_dir: TnPath, kwargs: TyDic) -> None | pd.Timestamp:
        if not dl_in_dir:
            return None
        _d_in_path_ix: TyDoDoInt = kwargs.get("d_in_path_ix", {})
        _rundatetime_iso8601: TnPath = cls.sh_component_by_field_name(
                dl_in_dir, _d_in_path_ix, 'rundatetime')
        if not _rundatetime_iso8601:
            return None
        _rundatetime_iso8601 = _rundatetime_iso8601.replace("_", ".")
        _rundatetime_ms: pd.Timestamp = pd.to_datetime(
                _rundatetime_iso8601, utc=True, format='ISO8601')
        LogEq.debug("_rundatetime_ms", _rundatetime_ms)
        return _rundatetime_ms

    @staticmethod
    def sh_fnc_name_by_pathlib(path: TnPath) -> TnPath:
        if not path:
            return path
        # def sh_fnc_name(path: TyPath) -> str:
        _purepath = pathlib.PurePath(path)
        dir_: str = _purepath.parent.name
        stem_: str = _purepath.stem
        return f"{dir_}-{stem_}"

    @staticmethod
    def sh_fnc_name_by_os_path(path: TnPath) -> TnPath:
        if not path:
            return path
        # def sh_os_fnc_name(path: TyPath) -> str:
        split_ = os.path.split(path)
        dir_ = os.path.basename(split_[0])
        stem_ = os.path.splitext(split_[1])[0]
        return f"{dir_}-{stem_}"

    @classmethod
    def sh_last_part(cls, path: TnPath) -> TnPath:
        if not path:
            return path
        # def sh_last_component(cls, path: TyPath) -> TyPath:
        a_dir: TyArr = cls.split_to_array(path)
        _path: TyPath = a_dir[-1]
        return _path

    @staticmethod
    def sh_path_by_d_path(path: TnPath, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        _d_path = kwargs.get('d_path', {})
        if not _d_path:
            return path
        return Template(path).safe_substitute(_d_path)

    @staticmethod
    def sh_path_by_tpl(path: TnPath, kwargs: TyDic) -> TnPath:
        """
        Apply template function to replace variables in path and show result
        """
        if not path:
            return path
        # Extract variables starting with '$'
        _a_key = re.findall(r'\$(\w+)', path)
        LogEq.debug("_a_key", _a_key)
        _dic = {}
        for _key in _a_key:
            _val = kwargs.get(_key)
            if _val:
                _dic[_key] = _val
        LogEq.debug("_dic", _dic)
        if not _dic:
            return path
        LogEq.debug("path", path)
        _template = Template(path)
        return _template.safe_substitute(**_dic)

    @staticmethod
    def sh_path_by_pac(path: TnPath, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        # Define the regex pattern
        _pattern = r"package_path\(\'([a-zA-Z0-9_]+)\'\)"
        # Use re.search to find the first match
        match = re.search(_pattern, path)
        if match:
            Log.debug(f"match with _pattern = {_pattern} succesfull")
            _package_string: TnStr = match.group()  # Extract the matched string
            if not _package_string:
                return path
            _package: TnStr = match.group(1)        # Extract the package name
            if not _package:
                return path
            LogEq.debug("_package", _package)
            _package_path: TnPath = Pac.sh_path((_package))
            if not _package_path:
                return _package_string
            _path: TnStr = path.replace(_package_string, _package_path)
            LogEq.debug("_path", _path)
            return _path
        else:
            _pattern = r"package_path"
            # Use re.search to find the first match
            match = re.search(_pattern, path)
            if match:
                Log.debug(f"match with _pattern = {_pattern} succesfull")
                _package_string = match.group()  # Extract the matched string
                _package = os.__package__
                LogEq.debug("_package", _package)
                _package_path = Pac.sh_path((_package))
                if not _package_path:
                    return path
                _path = path.replace(_package_string, _package_path)
                LogEq.debug("_path", _path)
                return _path
        return path

    @classmethod
    def sh_path_by_tpl_pac(
            cls, path: TnPath, kwargs: TyDic, sep: str = "|") -> TnPath:
        if not path:
            raise Exception("The parameter 'path' is udefined or empty")
        _path: TnPath = cls.sh_path_by_tpl(path, kwargs)
        return cls.sh_path_by_pac(_path, kwargs)

    @classmethod
    def sh_path_by_tpl_pac_sep(
            cls, path: TnPath, kwargs: TyDic, sep: str = "|") -> TnPath:
        _path: TnPath = cls.sh_path_by_tpl_pac(path, kwargs)
        if not _path:
            return _path
        _a_path: TyArr = _path.split(sep)
        return AoPath.sh_path_by_tpl_first_exist(_a_path, kwargs)

    # @classmethod
    # def sh_path_by_tpl_and_pac(cls, path: TyPath, kwargs: TyDic) -> TyPath:
    #     if not path:
    #         msg = "The parameter 'path' is udefined or empty"
    #         raise Exception(msg)
    #     _a_part: TyArr = list(pathlib.Path(path).parts)
    #     LogEq.debug("_a_part", _a_part)
    #     if not _a_part:
    #         return ''
    #     _a_path = AoPath.sh_aopath_by_pac(_a_part, kwargs)
    #     print("=========================================")
    #     print(f"_a_part = {_a_part}")
    #     print(f"_a_path = {_a_path}")
    #     print("=========================================")
    #     return AoPath.sh_path_by_tpl_first_exist(_a_path, kwargs)

    @classmethod
    def sh_path_by_tpl_and_d_pathnm2datetype(
           cls,  path: TnPath, pathnm: str, kwargs: TyDic) -> TnPath:
        LogEq.debug("path", path)
        _path: TnPath = cls.sh_path_by_tpl(path, kwargs)
        LogEq.debug("_path", _path)
        return cls.sh_path_by_d_pathnm2datetype(_path, pathnm, kwargs)

    @classmethod
    def sh_path_by_d_pathnm2datetype(
            cls, path: TnPath, pathnm: str, kwargs: TyDic) -> TnPath:
        LogEq.debug("pathnm", pathnm)
        _d_pathnm2datetype: TyDic = kwargs.get('d_pathnm2datetype', {})
        LogEq.debug("_d_pathnm2datetype", _d_pathnm2datetype)
        if not _d_pathnm2datetype:
            return path
        _datetype: TyStr = _d_pathnm2datetype.get(pathnm, '')
        return cls.sh_path_by_datetype(path, _datetype, kwargs)

    @classmethod
    def sh_path_by_datetype(
            cls, path: TnPath, datetype: str, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        LogEq.debug("path", path)
        LogEq.debug("datetype", datetype)
        match datetype:
            case 'last':
                path_new = cls.sh_path_last(path)
            case 'first':
                path_new = cls.sh_path_first(path)
            case 'now':
                path_new = cls.sh_path_now(path, **kwargs)
            case _:
                path_new = cls.sh_path_first(path)
        LogEq.debug("path_new", path_new)
        return path_new

    @classmethod
    def sh_path(cls, path: TnPath) -> TyPath:
        return cls.sh_path_first(path)

    @classmethod
    def sh_path_first(cls, path: TnPath) -> TyPath:
        _a_path: TyAoPath = cls.sh_aopath(path)
        if not _a_path:
            msg = f"glob.glob find no paths for template: {path}"
            raise Exception(msg)
        return sorted(_a_path)[0]

    @classmethod
    def sh_path_last(cls, path: TnPath) -> TyPath:
        _a_path: TyAoPath = cls.sh_aopath(path)
        if not _a_path:
            msg = f"glob.glob find no paths for template: {path}"
            raise Exception(msg)
        return sorted(_a_path)[-1]

    @staticmethod
    def sh_path_now(path: TnPath, **kwargs) -> TyPath:
        if not path:
            raise Exception("Argument 'path' is empty")
        now_var = kwargs.get('now_var', 'now')
        now_fmt = kwargs.get('now_fmt', '%Y%m%d')
        _current_date: str = datetime.datetime.now().strftime(now_fmt)
        _dic = {now_var: _current_date}
        return Template(path).safe_substitute(_dic)

    @staticmethod
    def split_to_array(path: TyPath) -> TyArr:
        """
        Convert path to normalized pyth
        Should Work with any OS Path on any OS
        """
        _normalized_path = os.path.normpath(path)
        return _normalized_path.split(os.sep)


class AoPath:

    @staticmethod
    def join(aopath: TyAoPath) -> TyPath:
        return ''.join([os.sep + _path.strip(os.sep) for _path in aopath if _path])

    @staticmethod
    def mkdirs(aopath: TyAoPath, **kwargs) -> None:
        if not aopath:
            return
        for _path in aopath:
            os.makedirs(_path, **kwargs)

    @classmethod
    def sh_aopath_by_tpl(
            cls, a_path_tpl_key: TyAoPath, kwargs: TyDic) -> TyAoPath:
        # _a_path_tpl: TyAoPath = cls.sh_items_in_dic(a_path_tpl_key, kwargs)
        aopath: TyAoPath = Path.sh_aopath(
                cls.join(Dic.sh_values_by_keys(kwargs, a_path_tpl_key)))
        return aopath

    @staticmethod
    def sh_aopath_by_glob(aopath: TyAoPath) -> TyAoPath:
        _aopath: TyAoPath = []
        if not aopath:
            return _aopath
        for _path in aopath:
            _aopath = _aopath + Path.sh_aopath(_path)
        return _aopath

    @staticmethod
    def sh_aopart_by_pac(a_part: TyArr, kwargs: TyDic) -> TyAoPath:
        LogEq.debug("a_part", a_part)
        _a_part: TyArr = []
        for _part in a_part:
            LogEq.debug("_part", _part)
            if _part == 'package':
                _package = kwargs.get('package', '')
                # _dir_package: TyPath = str(importlib.resources.files(_package))
                _dir_package: TyPath = str(resources.files(_package))
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
