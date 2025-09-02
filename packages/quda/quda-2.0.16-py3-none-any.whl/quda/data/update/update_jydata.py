# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/24 19:02
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

from ._jy_sql import *
from .. import tables
import lidb


CONFIG = {
    tables.TB_CALENDAR: sql_calendar,
    tables.TB_SECU_MAIN: sql_secumain,
    tables.TB_SHARES_INFO: sql_shares,
    tables.TB_LIST_STATUS: sql_liststatus,
    tables.TB_SPECIAL_TRADE: sql_st,
    tables.TB_INDUSTRY_SW: sql_industry,
    tables.TB_ADJ_FACTOR: sql_adj_factor,
}


def fetch_fn(tb_name, db_conf):
    query = CONFIG.get(tb_name)
    return lidb.read_mysql(query, db_conf=db_conf)
