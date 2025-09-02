# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/7/9 15:40
Email: yundi.xxii@outlook.com
Description: tick数据清洗
---------------------------------------------
"""
import lidb
import logair
import polars as pl
import xcals
import ygo
from pandas import Timedelta

from quda.data.tables import TB_STOCK_TICK
from quda.factor import INDEX, TIME_FORMAT

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
END_CALL_AUC = "09:25:00"
END_AM = "11:30:00"
END_PM = "15:00:00"

BEG_AM = "09:30:00"
BEG_PM = "13:00:00"
END_TICK = "16:00:00"

logger = logair.get_logger("quda")


def read_tick(date: str, beg_time: str = None, end_time: str = None, ) -> pl.LazyFrame:
    beg_time = beg_time if beg_time else "09:14:00"
    end_time = end_time if end_time else END_TICK
    sql = f"""
    SELECT *
    FROM {TB_STOCK_TICK}
    WHERE date = '{date}'
        AND time BETWEEN '{beg_time}' AND '{end_time}';
    """
    df = lidb.sql(sql).with_columns(pl.col("close").alias("price")).drop("close")
    return df.collect()


def _to_kline(date, beg_time: str = "09:23:00", end_time: str = "16:00:00", freq: str = "1min") -> pl.LazyFrame:
    """合成分钟kline"""
    beg_time = beg_time if beg_time is not None else "09:23:00"
    end_time = end_time if end_time is not None else END_TICK
    df = read_tick(date, beg_time, end_time).select("date", "time", "asset", "high", "low", "price", "volume",
                                                    "amount", "prev_close", "limit_up", "limit_down")
    secs = Timedelta(freq).seconds
    over_spec = {"partition_by": "asset", "order_by": "time"}
    df = (
        df
        .with_columns(pl.lit(date).alias("date"),
                      _time_=pl.col("time").str.to_datetime(TIME_FORMAT).dt.truncate(f"{secs}s"), )
        .with_columns(diff_v=pl.col("volume").diff().over(**over_spec),
                      diff_p=pl.col("price").diff().over(**over_spec))
        .with_columns(time_str=pl.col("_time_").dt.time().cast(pl.Utf8), )
        .with_columns(pl.when(pl.col("time_str").is_in([END_CALL_AUC, END_AM, END_PM]))
                      .then(pl.col("time_str"))
                      .otherwise((pl.col("_time_") + pl.duration(seconds=secs)).dt.time().cast(pl.Utf8))
                      .alias("time"))
    )
    # 合成分钟kline: 最高价、最低价、开盘价、收盘价、成交量、成交额
    df = df.select("date", "time", "asset", "prev_close", "limit_up", "limit_down", "price", "volume", "amount",
                   pl.col("high").alias("cum_h"),
                   pl.col("low").alias("cum_l"),
                   pl.col("diff_v"),
                   pl.col("diff_p"))
    kline = (
        df
        .with_columns(price=pl.when(pl.col("price") > 0).then(pl.col("price")).otherwise(None))
        .with_columns(
            price=pl.when((pl.col("diff_v") > 0) | (pl.col("diff_p").abs() > 0)).then(pl.col("price")).otherwise(None))
        .group_by(INDEX)
        .agg(prev_close=pl.col("prev_close").max(),
             limit_up=pl.col("limit_up").max(),
             limit_down=pl.col("limit_down").max(),
             open=pl.col("price").drop_nulls().first(),
             high=pl.col("cum_h").last(),
             low=pl.col("cum_l").last(),
             close=pl.col("price").drop_nulls().last(),
             cum_vol=pl.col("volume").last(),
             cum_amt=pl.col("amount").last(),
             max_p=pl.col("price").max(),
             min_p=pl.col("price").min(), )
        .sort(INDEX)
        .with_columns(diff_h=pl.col("high").diff().over(**over_spec),
                      diff_l=pl.col("low").diff().over(**over_spec),
                      )
        .with_columns(high=pl.when(pl.col("diff_h") > 0).then(pl.col("high")).otherwise("max_p"),
                      low=pl.when(pl.col("diff_l") < 0).then(pl.col("low")).otherwise("min_p"), )
        .drop("max_p", "min_p", "diff_h", "diff_l", )
    )
    # if beg_time <= END_CALL_AUC <= end_time:
    if end_time < BEG_AM:
        kline = (
            kline
            .with_columns(*[
                pl.when(pl.col("time") == END_CALL_AUC).then(pl.col(field).fill_null(pl.col("prev_close"))).otherwise(
                    pl.col(field)) for field in ["open", "high", "low", "close"]])
            .with_columns(
                *[pl.col(field).forward_fill().over(**over_spec) for field in ["open", "high", "low", "close"]])
        )
    return kline


def agg_kline(kline: pl.LazyFrame, kline_time: str | None = None) -> pl.LazyFrame:
    """kline聚合：由多个K线聚合成一条kline"""
    kline = (
        kline
        .sort(INDEX)
        .group_by("date", "asset")
        .agg(time=pl.col("time").last(),
             prev_close=pl.col("prev_close").max(),
             limit_up=pl.col("limit_up").max(),
             limit_down=pl.col("limit_down").max(),
             open=pl.col("open").drop_nulls().first(),
             high=pl.col("high").max(),
             low=pl.col("low").min(),
             close=pl.col("close").drop_nulls().last(),
             cum_vol=pl.col("cum_vol").last(),
             cum_amt=pl.col("cum_amt").last())
    )
    if kline_time is not None:
        kline = (
            kline
            .with_columns(time=pl.lit(kline_time))
        )
    return kline.select(*INDEX, "prev_close", "limit_up", "limit_down", "open", "high", "low", "close", "cum_vol",
                        "cum_amt")


def to_kline_oneday(date, freq: str = "1min"):
    """一次性合成一天的所有kline"""
    kline_all = _to_kline(date, beg_time="09:23:00", end_time="16:00:00", freq=freq)
    # 集合竞价
    kline_beg = kline_all.filter(pl.col("time") < BEG_AM)
    kline_beg = agg_kline(kline_beg, kline_time=BEG_AM)
    # 上午
    kline_am = kline_all.filter(pl.col("time") > BEG_AM, pl.col("time") < END_AM)
    # 中午盘
    kline_skip = kline_all.filter(pl.col("time") >= END_AM, pl.col("time") <= BEG_PM)
    kline_skip = agg_kline(kline_skip, kline_time=END_AM)
    # 下午
    kline_pm = kline_all.filter(pl.col("time") > BEG_PM, pl.col("time") < END_PM)
    # 尾盘
    kline_end = kline_all.filter(pl.col("time") >= END_PM)
    # 收盘后
    kline_end = agg_kline(kline_end, kline_time=END_PM)
    klines = [kline_beg, kline_am, kline_skip, kline_pm, kline_end, ]
    kline = pl.concat(klines, how="vertical").sort(INDEX)
    # 对齐所有symbol(由于某些symbol不活跃而导致某些时段没有tick数据，需要修复)
    full_index_t = kline.select("date", "time").unique()
    full_index_a = kline.select("asset").unique()
    full_index = full_index_t.join(full_index_a, how="cross")
    over_spec = {"partition_by": "asset", "order_by": "time"}
    kline = (
        full_index
        .join(kline, on=INDEX, how="left")
        .sort(INDEX)
        .with_columns(pl.all().exclude("open", "high", "low").forward_fill().over(**over_spec))
    )
    # 调整 volume / amount / 以及其他一些价格字段
    kline = (
        kline
        .with_columns(volume=pl.col("cum_vol").diff().over(**over_spec).fill_null(pl.col("cum_vol")),
                      amount=pl.col("cum_amt").diff().over(**over_spec).fill_null(pl.col("cum_amt")),
                      last_close=pl.col("close").shift(1).forward_fill().over(**over_spec))
        .with_columns(
            *[pl.when(pl.col("volume") == 0).then(pl.col("close").fill_null(pl.col("last_close"))).otherwise(
                pl.col(field)).alias(field) for
              field in ["open", "high", "low", "close"]])
        .with_columns(
            *[pl.col(field).fill_null(pl.col("last_close")).alias(field) for field in ["open", "high", "low", "close"]])
    )
    kline = kline.sort(INDEX).select(*INDEX, "prev_close", "limit_up", "limit_down", "open", "high", "low", "close",
                                     "cum_vol", "cum_amt", "volume", "amount", )
    kline = kline.with_columns(pl.col(pl.Decimal).cast(pl.Decimal(16, 4)))
    return kline.drop("cum_vol", "cum_amt")


def _to_tick(date: str, beg_time: str, end_time: str, freq: str) -> pl.LazyFrame:
    tick = read_tick(date, beg_time, end_time).drop("high", "low", "price", "volume", "amount")
    secs = Timedelta(freq).seconds
    tick = (
        tick
        .with_columns(pl.lit(date).alias("date"),
                      _time_=pl.col("time").str.to_datetime(TIME_FORMAT).dt.truncate(f"{secs}s"), )
        .with_columns(time_str=pl.col("_time_").dt.time().cast(pl.Utf8), )
        .with_columns(pl.when(pl.col("time_str").is_in([END_CALL_AUC, END_AM, END_PM]))
                      .then(pl.col("time_str"))
                      .otherwise((pl.col("_time_") + pl.duration(seconds=secs)).dt.time().cast(pl.Utf8))
                      .alias("time"))
        .select("date", "time", "asset",
                "ask_p1", "ask_p2", "ask_p3", "ask_p4", "ask_p5",
                "ask_v1", "ask_v2", "ask_v3", "ask_v4", "ask_v5",
                "bid_p1", "bid_p2", "bid_p3", "bid_p4", "bid_p5",
                "bid_v1", "bid_v2", "bid_v3", "bid_v4", "bid_v5")
        .sort(INDEX)
    )
    return (
        tick
        .group_by(INDEX)
        .agg(pl.all().last().cast(pl.Decimal(16, 4)))
    )


def agg_tick(ticks: pl.DataFrame, tick_time: str) -> pl.LazyFrame:
    """tick聚合：由多个tick聚合成一个tick"""
    fields = ["time", "ask_p1", "ask_p2", "ask_p3", "ask_p4", "ask_p5",
              "ask_v1", "ask_v2", "ask_v3", "ask_v4", "ask_v5",
              "bid_p1", "bid_p2", "bid_p3", "bid_p4", "bid_p5",
              "bid_v1", "bid_v2", "bid_v3", "bid_v4", "bid_v5"]
    tick = (
        ticks
        .sort(INDEX)
        .group_by("date", "asset")
        .agg(*[pl.col(field).last() for field in fields])
    )
    if tick_time is not None:
        tick = (
            tick
            .with_columns(time=pl.lit(tick_time))
        )
    return tick.select(*INDEX, *fields[1:])


def to_tick_oneday(date, freq: str = "1min"):
    """一次性合成一天的所有tick"""
    tick_all = _to_tick(date, beg_time="09:23:00", end_time="16:00:00", freq=freq)
    # 集合竞价
    tick_beg = tick_all.filter(pl.col("time") < BEG_AM)
    tick_beg = agg_tick(tick_beg, tick_time=BEG_AM)
    # 上午
    tick_am = tick_all.filter(pl.col("time") > BEG_AM, pl.col("time") < END_AM)
    # 中午盘
    tick_skip = tick_all.filter(pl.col("time") >= END_AM, pl.col("time") <= BEG_PM)
    tick_skip = agg_tick(tick_skip, tick_time=END_AM)
    # 下午
    tick_pm = tick_all.filter(pl.col("time") > BEG_PM, pl.col("time") < END_PM)
    # 尾盘
    tick_end = tick_all.filter(pl.col("time") >= END_PM)
    # 收盘后
    tick_end = agg_tick(tick_end, tick_time=END_PM)
    ticks = [tick_beg, tick_am, tick_skip, tick_pm, tick_end]
    tick = pl.concat(ticks, how="vertical").sort(INDEX)
    # 对齐所有symbol(由于某些symbol不活跃而导致某些时段没有tick数据，需要修复)
    full_index_t = tick.select("date", "time").unique()
    full_index_a = tick.select("asset").unique()
    full_index = full_index_t.join(full_index_a, how="cross")
    over_spec = {"partition_by": "asset", "order_by": "time"}
    return (
        full_index
        .join(tick, on=INDEX, how="left")
        .sort(INDEX)
        .with_columns(pl.all().forward_fill().over(**over_spec))
    )


def save_ytick_oneday(date: str, tb_name: str, freq: str = "3s"):
    """tick数据清洗, 时间对齐, ohlc 修复"""
    from pathlib import Path
    tb_name = Path(tb_name) / f"freq={freq}"
    try:
        cnt = lidb.sql(f"select count(distinct date) from {tb_name} where date='{date}';").collect().item()
        if cnt > 0:
            return
    except Exception as e:
        logger.error(e)
        pass
    # 合成3s kline
    kline_3s = to_kline_oneday(date, freq=freq)
    tick_3s = to_tick_oneday(date, freq=freq)
    ytick = (
        kline_3s
        .join(tick_3s, on=INDEX, how="left")
        .sort(INDEX)
    )
    lidb.put(ytick, tb_name=tb_name, partitions=["date"], )
    return


def save_ytick(beg_date: str, end_date: str, freq: str, tb_name: str, n_jobs: int = 5):
    """保存ytick数据"""
    trade_days = xcals.get_tradingdays(beg_date, end_date)
    with ygo.pool(n_jobs=n_jobs, backend="threading") as go:
        for date in trade_days:
            go.submit(save_ytick_oneday, job_name="Cleaning tick")(tb_name=tb_name, date=date, freq=freq)
        go.do()
