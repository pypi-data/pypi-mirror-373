# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/29 18:10
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

def sql_StockKlineDay(date, tb_name):
    return f"""
    select date,
           replaceRegexpAll(order_book_id, '[^0-9]', '')                          as asset,
           total_turnover                                                         as amount,
           volume,
           prev_close,
           open,
           high,
           low,
           close,
           limit_up,
           limit_down,
           if(num_trades < 0, 0, if(num_trades > toInt64(volume), 0, num_trades)) as num_trades
    from {tb_name}
        prewhere date = '{date}'
    order by asset
    """


def sql_StockKlineMinute(date, tb_name):
    return f"""
    select EventDate                                                              as date,
           replaceRegexpAll(order_book_id, '[^0-9]', '')                          as asset,
           formatDateTime(datetime, '%T')                                         as time,
           total_turnover                                                         as amount,
           volume,
           open,
           high,
           low,
           close,
           if(num_trades < 0, 0, if(num_trades > toInt64(volume), 0, num_trades)) as num_trades
    from {tb_name}
        prewhere EventDate = '{date}'
    order by asset
    """

def sql_StockTick(date, tb_name):
    return f"""
    SELECT EventDate as date,
               formatDateTime(datetime, '%T') as time,
               replaceRegexpAll(order_book_id, '[^0-9]', '') AS asset,
               prev_close, 
               limit_up, 
               limit_down,
               total_turnover AS amount,
               volume,
               high,
               low,
               close,
               a1 AS ask_p1,
               a2 AS ask_p2,
               a3 AS ask_p3,
               a4 AS ask_p4,
               a5 AS ask_p5,
               a1_v AS ask_v1,
               a2_v AS ask_v2,
               a3_v AS ask_v3,
               a4_v AS ask_v4,
               a5_v AS ask_v5,
               b1 AS bid_p1,
               b2 AS bid_p2,
               b3 AS bid_p3,
               b4 AS bid_p4,
               b5 AS bid_p5,
               b1_v AS bid_v1,
               b2_v AS bid_v2,
               b3_v AS bid_v3,
               b4_v AS bid_v4,
               b5_v AS bid_v5
        FROM {tb_name}
        WHERE EventDate = '{date}'
        AND time >= '09:14:00'
        ORDER BY
            order_book_id ASC,
            datetime ASC
    """


def sql_IndexKlineMinute(date, tb_name):
    return f"""
    select EventDate                                     as date,
           replaceRegexpAll(order_book_id, '[^0-9]', '') as asset,
           formatDateTime(datetime, '%T')                as time,
           total_turnover                                as amount,
           volume,
           open,
           high,
           low,
           close
    from {tb_name}
        prewhere EventDate = '{date}'
    order by asset
    """


def sql_IndexKlineDay(date, tb_name):
    return f"""
    select date,
           replaceRegexpAll(order_book_id, '[^0-9]', '') as asset,
           total_turnover                                as amount,
           volume,
           prev_close,
           open,
           high,
           low,
           close
    from {tb_name}
        prewhere date = '{date}'
    order by asset
    """
