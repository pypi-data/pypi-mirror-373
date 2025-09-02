# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/7/10 17:36
Email: yundi.xxii@outlook.com
Description: 更新tick数据
---------------------------------------------
"""

import subprocess

import ygo
import lidb

from ._mc_sql import *
from .. import tables

CONFIG = {
    tables.TB_STOCK_TICK: ygo.delay(sql_StockTick)(tb_name="cquote.stock_tick_distributed final")
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
