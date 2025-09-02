# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/8 14:19
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""
import lidb
import pandas as pd
import polars as pl
import xcals

import quda.data
from quda.factor import DATE_FORMAT, Factor, INDEX
from .. import tables


def kline_minute(date, end_time):
    query = f"select * from {tables.TB_STOCK_KLINE_MINUTE} where date='{date}' and time='{end_time}'"
    return lidb.sql(query).cast({"date": pl.Utf8}).collect()


fac_kline_minute = Factor(fn=kline_minute)


def kline_day(date, ):
    query = f"select * from {tables.TB_STOCK_KLINE_DAY} where date='{date}'"
    return lidb.sql(query).cast({"date": pl.Utf8}).collect()


fac_kline_day = Factor(fn=kline_day)


def share(date, ):
    """
    股本信息
    Returns
    -------
    Notes
    -----
    - TotalShares: 总股本
    - AShares: A股股本
    - AFloats: A股流通股本
    """
    cols = ['TotalShares', 'AShares', 'AFloats']
    shares_info = quda.data.get_shares()
    res: pl.DataFrame = shares_info.filter(pl.col("InfoPublDate") <= date, pl.col("EndDate") <= date)["asset", *cols]

    return res.group_by("asset").tail(1)


fac_share = Factor(fn=share)


def cap(this: Factor, date, end_time):
    depend_val = this.get_value_depends(date, time=end_time)
    depend_val = depend_val.select(*INDEX,
                                   pl.sql_expr("`fac_kline_minute.close` * `fac_share.TotalShares` as total_cap"),
                                   pl.sql_expr("`fac_kline_minute.close` * `fac_share.AShares` as a_cap"),
                                   pl.sql_expr("`fac_kline_minute.close` * `fac_share.AFloats` as afloat_cap"))
    # 对数
    return depend_val.with_columns(total_cap_ln=pl.col("total_cap").log(),
                                   a_cap_ln=pl.col("a_cap").log(),
                                   afloat_cap_ln=pl.col("afloat_cap").log(), )


fac_cap = Factor(fac_kline_minute, fac_share, fn=cap)


def st(date):
    """
    st 股票: 1-st, 0-非st
    Parameters
    ----------
    Returns
    -------
    """
    df = quda.data.get_st()
    df = (
        df
        .filter(pl.col("SpecialTradeDate") <= date)
        .group_by("asset").tail(1)
        .filter(pl.col("SpecialTradeType").is_in([1, 3, 5, 7, 8, 9, 10, 12, 14]))
    )
    st_df = pl.DataFrame({"asset": df["asset"], "st": 1})
    codes = quda.data.get_codes(date)
    index = pl.DataFrame({"asset": codes})
    return index.join(st_df, on="asset", how="left").fill_null(0)


fac_st = Factor(fn=st)


def ipo(date, days: int):
    """
    ipo:

    - 1: ipo <= days
    - 0: ipo > days
    Parameters
    ----------
    Returns
    -------

    """
    secumain = quda.data.get_secumain()
    refer_date = pd.to_datetime(date) - pd.offsets.Day(days)
    refer_date = refer_date.strftime("%Y-%m-%d")
    df = secumain.filter(pl.col("ListedDate") > refer_date)
    ipo_df = pl.DataFrame({"asset": df["asset"], "ipo": 1})
    codes = quda.data.get_codes(date)
    index = pl.DataFrame({"asset": codes})
    return index.join(ipo_df, on="asset", how="left").fill_null(0)


fac_ipo = Factor(fn=ipo)


def industry(date):
    """
    申万行业
    Parameters
    ----------
    Returns
    -------

    """
    cols = ["Lv1", "Lv2", "Lv3"]
    df = quda.data.get_industry()
    df = df.filter(pl.col("InfoPublDate") <= date)["asset", *cols]
    return df.group_by("asset").tail(1)


fac_industry = Factor(fn=industry)


def base_quote(this: Factor, date, end_time, env="dev"):
    """盘前能够获取的基本行情信息：昨收/涨跌停/开盘"""
    if date < xcals.today():
        return (
            this
            .get_value_depends(date, time="15:00:00")
            .select("asset",
                    pl.sql_expr("`fac_kline_day.prev_close` as prev_close"),
                    pl.sql_expr("`fac_kline_day.limit_up` as limit_up"),
                    pl.sql_expr("`fac_kline_day.limit_down` as limit_down"))
        )
    tb = "stock_tick_rt_distributed" if env == "rt" else "stock_tick_distributed"
    rt_query = f"""
        SELECT replaceRegexpAll(order_book_id, '[^0-9]', '') as asset,
               max(prev_close)                               as prev_close,
               max(limit_up)                                 as limit_up,
               max(limit_down)                               as limit_down
        FROM cquote.{tb} final
        WHERE EventDate = '{date}'
          AND formatDateTime(datetime, '%T') <= '{end_time}'
        GROUP BY asset
        ORDER BY asset;
    """
    return lidb.read_ck(rt_query, db_conf="DATABASES.ck")


fac_base_quote = Factor(fac_kline_day, fn=base_quote).set_end_time("09:00:00").set_insert_time("09:00:00")


def components(this: Factor, date, index_code):
    """指数成分股: 使用昨收价来计算权重"""
    ts = pd.to_datetime(date)
    beg_date = (ts - pd.offsets.MonthEnd() - pd.offsets.MonthBegin()).strftime(DATE_FORMAT)

    sql = f"""
    SELECT A.InnerCode,
            EndDate
    FROM gildata.LC_IndexComponentsWeight A
             JOIN
         gildata.SecuMain B
         ON A.IndexCode = B.InnerCode
             AND B.SecuCategory = 4
             AND B.SecuMarket in (83, 90)
             AND B.SecuCode='{index_code}'
    WHERE EndDate >= '{beg_date}'
        AND EndDate < '{date}';
    """
    time_ = "09:00:00"
    iw = lidb.read_mysql(sql, db_conf="DATABASES.jy")
    secu_main = quda.data.get_secumain()
    iw = (iw
          .join(secu_main["InnerCode", "asset"], on="InnerCode", how="inner")
          .filter(pl.col("EndDate") == pl.col("EndDate").max())
          .drop("InnerCode", "EndDate"))
    codes = iw["asset"]
    depend_val = this.get_value_depends(date=date, codes=codes, time=time_)
    depend_val = depend_val.select(*INDEX,
                                   pl.sql_expr("`fac_base_quote.prev_close` * `fac_share.AFloats` as afloat_cap"), )
    w = depend_val.with_columns(weight=pl.col("afloat_cap") / pl.col("afloat_cap").sum()).drop("afloat_cap")
    return w


fac_components = Factor(fac_base_quote, fac_share, fn=components).set_end_time("09:00:00").set_insert_time(
    "09:00:00")


def filter(this: Factor, date, end_time, env="dev"):
    """默认过滤因子：过滤 st | ipo <= 90d | limit_up | limit_down"""
    depend_val = this.get_value_depends(date, time=end_time)
    cond_df = (
        depend_val
        .select("asset",
                st=pl.col("fac_st.st"),
                ipo=pl.col("fac_ipo.ipo"),
                limit_up=pl.when(pl.col("fac_kline_minute.close") >= pl.col("fac_base_quote.limit_up")).then(
                    1).otherwise(0),
                limit_down=pl.when(pl.col("fac_kline_minute.close") <= pl.col("fac_base_quote.limit_down")).then(
                    1).otherwise(0)
                )
        .select("asset",
                cond=pl.sum_horizontal(pl.all().exclude("asset")).sign().fill_null(1))
    )
    return cond_df


fac_filter = Factor(fac_st,
                         fac_kline_minute,
                         fac_ipo(days=90),
                         fac_base_quote,
                         fn=filter,
                         share_params=["env", ])


def filter_notindex(date, end_time, index_codes: list[str], env="dev"):
    """
    过滤非成份股：过滤 not index
    0 - 不要过滤，成分股
    1 - 非成份股，需要过滤
    """
    res = fac_base_quote.get_value(date, time=end_time).select("asset")
    codes = res["asset"]
    res = res.with_columns(cond=pl.lit(None))
    for index_code in index_codes:
        w = fac_components(index_code=index_code).get_value(date, codes)["weight"]
        res = res.fill_null(w)
    # 有权重的是不要过滤的，标记为0
    res = (
        res
        .select("asset", cond=pl.when(pl.col("cond") > 0).then(0).otherwise(1))
    )
    return res


fac_filter_notindex = Factor(fac_base_quote,
                                  fac_components,
                                  fn=filter_notindex,
                                  share_params=["env"]).set_end_time("09:00:00").set_insert_time("09:00:00")
