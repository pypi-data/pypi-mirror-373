# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/8 14:29
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""
import time

import polars as pl
import xcals

from quda.data.zoo import base
import logair
import ygo

from quda.data.zoo.base import fac_components

pl.Config.set_tbl_cols(20)
pl.Config.set_tbl_width_chars(1000)

logger = logair.get_logger("test")

def test_components():
    test_date = "2025-05-06"
    w = fac_components(index_code="000852").get_value(test_date)
    logger.info(w)

def test_base_quote():
    test_date1 = "2025-05-06"
    test_date2 = "2025-07-04"
    data1 = base.fac_base_quote.get_value(test_date1)
    data2 = base.fac_base_quote(env="rt").get_value(test_date2)
    logger.info(data1.head())
    logger.info(data2.head())

def test_filter():
    test_date = "2025-05-06"
    data = base.fac_filter.get_value(test_date)
    logger.info(data.filter(pl.col("cond") > 0))

def test_filter_notindex():
    test_date = "2025-05-06"
    data = base.fac_filter_notindex(index_codes=["000016", ]).get_value(test_date)
    logger.info(data.filter(pl.col("cond").is_null()))

def test_get_value():
    test_date = "2025-05-06"
    data = base.fac_kline_minute.get_value(date=test_date, time="09:31:00")
    # data = base.fac_filter.get_value(date=test_date, time="09:00:00")
    logger.info(data)

def test_get_history():
    test_date = "2025-05-06"
    fac = base.fac_kline_day
    # data = base.fac_filter.get_history(date=test_date,
    #                                    period="-2d",
    #                                    beg_date="2025-01-01",
                                       # time="09:31:00")
    data = fac.get_history(date=test_date, period="-2d", time="09:30:00")
    logger.info(data.filter(date=test_date))
    prev_date = xcals.shift_tradeday(test_date, -1)
    data = fac.get_value(date=prev_date)
    logger.info(data)

def test_ipo():
    test_date = "2025-05-30"
    data = base.fac_ipo(days=90).get_value(date=test_date)
    logger.info(data)

def test_st():
    test_date = "2025-05-30"
    data = base.fac_st.get_value(date=test_date)
    logger.info(data)



if __name__ == '__main__':
    # test_st()
    test_get_history()
    # import quda
    # print(FactorContext.__dataclass_fields__.keys())
    # print(ygo.fn_info(ygo.delay(base.fac_prev_close.fn)(env="rt")))
    # test_base_quote()
    # test_filter()
    # test_components()
    # test_filter_notindex()
    # test_get_value()
    # test_get_history()
    # test_ipo()
    # data = quda.sql("select * from mc/stock_kline_minute where date='2025-05-30';")
    # ylog.info(data.collect())