# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/3/5 21:40
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""
from __future__ import annotations

from .qdf import QDF
from .lazy import LQDF



def from_polars(df, index: tuple[str] = ("date", "time", "asset"), align: bool = True, ) -> QDF:
    """polars dataframe 转为 表达式数据库"""
    return QDF(df, index, align,)

def to_lazy(df, index: tuple[str] = ("date", "time", "asset"), align: bool = False, ) -> LQDF:
    """polars dataframe 转为 表达式数据库"""
    return LQDF(df, index, align,)

