# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/5 16:56
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

from .api import (
    get_industry,
    get_liststatus,
    get_shares,
    get_st,
    get_secumain,
    get_codes,
)
from .tables import (
    TB_STOCK_KLINE_DAY,
    TB_STOCK_KLINE_MINUTE,
    TB_INDEX_KLINE_DAY,
    TB_INDEX_KLINE_MINUTE,
    TB_STOCK_TICK,
)

def init():
    import lidb
    import logair
    import toml

    logger = logair.get_logger("quda.data")

    settings = lidb.get_settings()
    if (not settings.get("UPDATES.jydata")) or (not settings.get("UPDATES.mc")):
        logger.warning(f"Missing jydata/mc configuration. writing update config to {lidb.CONFIG_PATH}")
        update_conf = {
            "updates": {
                "jydata": {
                    "mod": "quda.data.update.update_jydata",
                    "update_time": "16:30",
                    "db_conf": "DATABASES.jy",
                    "mode": "auto",
                },
                "mc": {
                    "mod": "quda.data.update.update_mc",
                    "update_time": "22:00",
                    "db_conf": "DATABASES.ck",
                    "mode": "auto",
                    "beg_date": "2020-01-01",
                },
            }
        }
        settings.update(update_conf)
        with open(lidb.CONFIG_PATH, 'w') as f:
            toml.dump(settings.as_dict(), f)
            logger.info("Init success.")


__all__ = [
    "get_st",
    "get_industry",
    "get_liststatus",
    "get_shares",
    "get_secumain",
    "get_codes",
    "TB_STOCK_KLINE_MINUTE",
    "TB_INDEX_KLINE_DAY",
    "TB_STOCK_KLINE_DAY",
    "TB_INDEX_KLINE_MINUTE",
    "TB_STOCK_TICK",
]
