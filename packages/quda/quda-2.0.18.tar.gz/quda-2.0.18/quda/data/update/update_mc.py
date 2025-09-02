# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/29 18:10
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""
import subprocess

import ygo
import lidb

from ._mc_sql import *
from .. import tables

CONFIG = {
    tables.TB_STOCK_KLINE_MINUTE: ygo.delay(sql_StockKlineMinute)(tb_name="cquote.stock_minute_distributed final"),
    tables.TB_STOCK_KLINE_DAY: ygo.delay(sql_StockKlineDay)(tb_name="cquote.stock_daily_distributed final"),
    tables.TB_INDEX_KLINE_MINUTE: ygo.delay(sql_IndexKlineMinute)(tb_name="cquote.index_minute_distributed final"),
    tables.TB_INDEX_KLINE_DAY: ygo.delay(sql_IndexKlineDay)(tb_name="cquote.index_daily_distributed final"),
}


def fetch_fn(tb_name, date, db_conf):
    file_path = lidb.tb_path(f"{tb_name}/date={date}/0.parquet")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    query = CONFIG.get(tb_name)(date=date)
    config_ck = lidb.get_settings().get(db_conf)
    urls = config_ck.get("urls")
    user = config_ck.get("user")
    password = config_ck.get("password")
    host, port = urls[0].split(":")
    cmd = [
        "clickhouse",
        "client",
        "--host",
        host,
        "--port",
        port,
        "--user",
        user,
        "--database",
        "cquote",
        "--password",
        password,
        "--query",
        f"""
        {query}
        INTO OUTFILE '{file_path}' TRUNCATE
        FORMAT Parquet
        """
    ]
    subprocess.run(cmd)
