# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/6 15:41
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 因子依赖/时间/版本解析
---------------------------------------------
"""
import hashlib

import xcals
from .utils import version_hash
from .consts import TYPE_REALTIME, TYPE_FIXEDTIME

class TimeResolver:

    @staticmethod
    def resolve_date(date: str, time: str, insert_time: str, avoid_future: bool, fac_type: str) -> str:
        if fac_type == TYPE_REALTIME:
            return date
        val_date = xcals.get_recent_tradeday(date)
        if avoid_future and time < insert_time:
            val_date = xcals.shift_tradeday(val_date, -1)
        return val_date

    @staticmethod
    def resolve_time(time: str, end_time: str, fac_type: str) -> str:
        val_time = end_time if fac_type == TYPE_FIXEDTIME else time
        return val_time


class VersionResolver:

    @staticmethod
    def resolve_version(fn: callable, depends: list | tuple | None = None):
        assert isinstance(depends, (list, tuple, None)), f"depends must be list/tuple/None."
        base_version = version_hash(fn)
        deps_version = [base_version, ]
        if depends:
            for depend in depends:
                if hasattr(depend, "version"):
                    deps_version.append(getattr(depend, "version"))
        deps_version.sort()
        return hashlib.md5(f"{'|'.join(deps_version)}".encode()).hexdigest()

