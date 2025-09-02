# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/8 15:56
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Factor


@dataclass
class FactorGetError(Exception):
    fac_name: str
    end_time: str
    insert_time: str
    get_date: str
    get_time: str
    fac_params: dict
    error: Exception

    def __str__(self):
        return f"""
[因子名称]: {self.fac_name}({self.fac_params})
[因子时间]: {self.end_time}
[入库时间]: {self.insert_time}
[取值时间]: {self.get_date} {self.get_time}
[错误信息]: \n{self.error}
"""

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def new_error(fac: 'Factor', date, time, e):
        return FactorGetError(fac_name=fac.name,
                              end_time=fac.end_time,
                              insert_time=fac.insert_time,
                              fac_params=fac._params,
                              get_date=date,
                              get_time=time,
                              error=e)
