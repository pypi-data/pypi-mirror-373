# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/6 16:01
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 因子调用执行器
---------------------------------------------
"""

import datetime
from typing import TYPE_CHECKING

import polars as pl
import xcals

from .completer import MissingChecker, DataCompleter
from .consts import (
    FIELD_ASSET,
    FIELD_DATE,
    FIELD_TIME,
    FIELD_VERSION,
    TYPE_FIXEDTIME,
    TYPE_REALTIME,
    INDEX,
    DATE_FORMAT,
)
from .resolver import TimeResolver
import lidb

if TYPE_CHECKING:
    from .core import Factor, FactorContext


class Evaluator:

    @staticmethod
    def read_data(fac: 'Factor', date_cond: str, time_cond: str, eager: bool = True):
        """
        读取本地数据
        Returns
        -------
        polars.DataFrame | polars.LazyFrame
        """
        conds = []
        if date_cond:
            conds.append(date_cond)
        if time_cond:
            conds.append(time_cond)
        query_cond = "" if not conds else f"where {' and '.join(conds)}"
        query = f"select * from {fac.tb_name} {query_cond};"
        data = lidb.sql(query).drop(FIELD_VERSION).cast({FIELD_DATE: pl.Utf8})
        if eager:
            return data.collect()
        return data

    @staticmethod
    def get_value(fac: 'Factor', ctx: 'FactorContext') -> pl.DataFrame | None:
        """
        获取指定日期和时间的最新数据。

        Parameters
        ----------
        fac : Factor
            因子对象，包含因子的相关信息。
        ctx: FactorContext
            参数定制
        Returns
        -------
        polars.DataFrame
        """
        date = ctx.date
        if isinstance(date, (datetime.date, datetime.datetime)):
            date = date.strftime(DATE_FORMAT)
        # 如果avoid_future 为 True, 且查询时间早于因子的结束时间，使用上一个交易日的数据
        val_date = TimeResolver.resolve_date(date=date,
                                             time=ctx.time,
                                             insert_time=fac.insert_time,
                                             avoid_future=ctx.avoid_future,
                                             fac_type=fac.type)
        val_time = fac.end_time if fac.type == TYPE_FIXEDTIME else ctx.time
        data = Evaluator.read_data(fac, f"date='{val_date}'", f"time='{val_time}'", eager=True)
        data = data.with_columns(date=pl.lit(ctx.date), time=pl.lit(ctx.time))
        if ctx.codes is None:
            return data
        cols = data.columns
        codes = pl.DataFrame({FIELD_ASSET: ctx.codes})
        return data.join(codes, on=FIELD_ASSET, how='right')[cols]

    @staticmethod
    def prepare(facs: list['Factor'], ctx: 'FactorContext'):
        """准备数据：检查缺失数据并补齐"""
        beg_date = ctx.beg_date if ctx.beg_date else ctx.date
        end_date = ctx.end_date if ctx.end_date else ctx.date
        beg_time = ctx.beg_time if ctx.beg_time else ctx.time
        end_time = ctx.end_time if ctx.end_time else ctx.time
        timeList = xcals.get_tradingtime(beg_time, end_time, ctx.freq)
        if timeList:
            beg_time, end_time = timeList[0], timeList[-1]

        missing_configs = list()
        for fac in facs:
            check_beg_date = TimeResolver.resolve_date(date=beg_date,
                                                       time=end_time,
                                                       insert_time=fac.insert_time,
                                                       avoid_future=ctx.avoid_future,
                                                       fac_type=fac.type)
            check_end_date = TimeResolver.resolve_date(date=end_date,
                                                       time=end_time,
                                                       insert_time=fac.insert_time,
                                                       avoid_future=ctx.avoid_future,
                                                       fac_type=fac.type)
            # 补齐缺失数据
            check_beg_time = beg_time if fac.type == TYPE_REALTIME else fac.end_time
            check_end_time = end_time if fac.type == TYPE_REALTIME else fac.end_time
            missing_datetimes = MissingChecker.check_datetimes(fac, check_beg_date, check_end_date, check_beg_time,
                                                               check_end_time, freq=ctx.freq)
            if missing_datetimes:
                missing_configs.append((fac, missing_datetimes))
        if missing_configs:
            DataCompleter.complete(missing_configs, n_jobs=ctx.n_jobs)

    @staticmethod
    def get_values(fac: 'Factor', ctx: 'FactorContext') -> pl.DataFrame:
        """
        取值: 指定日期 beg_time -> end_time 的全部值
        """

        beg_time = ctx.beg_time if ctx.beg_time else ctx.time
        end_time = ctx.end_time if ctx.end_time else ctx.time
        timeList = xcals.get_tradingtime(beg_time, end_time, ctx.freq)
        beg_time, end_time = timeList[0], timeList[-1]
        beg_date = ctx.beg_date if ctx.beg_date else ctx.date
        end_date = ctx.end_date if ctx.end_date else ctx.date
        dateList = xcals.get_tradingdays(beg_date, end_date)

        def fill_forward(val: pl.DataFrame, beg_time_: str, end_time_: str):
            timeList_ = xcals.get_tradingtime(beg_time_, end_time_, ctx.freq)
            time_df = pl.DataFrame({FIELD_TIME: timeList_})
            full_index = val.select(FIELD_DATE, FIELD_ASSET)
            cols = val.columns[3:]
            full_index = full_index.join(time_df, how="cross")
            over_spec = {"partition_by": [FIELD_ASSET], "order_by": [FIELD_DATE, FIELD_TIME]}
            val = full_index.join(val.drop(FIELD_TIME), on=[FIELD_DATE, FIELD_ASSET], how="left")
            val = val.with_columns(pl.all().exclude(INDEX).forward_fill().over(**over_spec))
            return val.select(*INDEX, *cols).sort(INDEX)

        if fac.type == TYPE_FIXEDTIME:
            fn = Evaluator.get_value if len(dateList) < 2 else Evaluator.get_history
            if ctx.avoid_future and beg_time < fac.insert_time <= end_time:
                # beg_time -> self.insert_time中的需要取上一天的
                prev_need_times = xcals.get_tradingtime(beg_time, fac.insert_time)[:-1]
                ctx.time = beg_time
                prev_val = fn(fac, ctx)
                prev_val = fill_forward(prev_val, beg_time, prev_need_times[-1])
                ctx.time = fac.insert_time
                cur_val = fn(fac, ctx)
                cur_val = fill_forward(cur_val, fac.insert_time, end_time)
                return pl.concat([prev_val, cur_val])
            else:
                # 所有值都只能取同一天的
                ctx.time = beg_time
                val = fn(fac, ctx)
                return fill_forward(val, beg_time, end_time)
        else:
            data = Evaluator.read_data(fac,
                                       date_cond=f"{FIELD_DATE} between '{dateList[0]}' and '{dateList[-1]}'",
                                       time_cond=f"{FIELD_TIME} between '{beg_time}' and '{end_time}'")
            cols = data.columns
            if ctx.codes is not None:
                data = data.join(pl.DataFrame({FIELD_ASSET: ctx.codes}), on=FIELD_ASSET, how="right")
            # 调整列的顺序
            return data[cols].sort(INDEX)

    @staticmethod
    def depends_getter(fac: 'Factor', ctx: 'FactorContext', fn) -> pl.DataFrame | None:
        if not fac._depends:
            return
        depend_vals = list()
        for depend in fac._depends:
            val = fn(fac=depend, ctx=ctx)
            # 重命名columns
            if val is None:
                continue
            columns = val.columns
            if len(columns) >= 4:
                new_columns = [
                    col_name if col_name in INDEX else f'{depend.name}.{col_name}' for
                    col_name in
                    columns]
                val.columns = new_columns
            depend_vals.append(val)
        return pl.concat(depend_vals, how="align").sort(INDEX)

    @staticmethod
    def get_value_depends(fac: 'Factor', ctx: 'FactorContext') -> pl.DataFrame:
        return Evaluator.depends_getter(fac, ctx, Evaluator.get_value)

    @staticmethod
    def get_history(fac: 'Factor', ctx: 'FactorContext') -> pl.DataFrame:

        beg_date = xcals.get_recent_tradeday(ctx.beg_date)
        val_time = ctx.time if fac.type == TYPE_REALTIME else fac.end_time

        data = Evaluator.read_data(fac, date_cond=f"date BETWEEN '{beg_date}' AND '{ctx.end_date}'",
                                   time_cond=f"time = '{val_time}'")
        cols = data.columns
        if ctx.avoid_future and ctx.time < fac.insert_time:
            dateList = xcals.get_tradingdays(beg_date, ctx.end_date)
            next_dateList = xcals.get_tradingdays(xcals.shift_tradeday(beg_date, 1),
                                                  xcals.shift_tradeday(ctx.end_date, 1))
            shift_date_map = {old_date: next_dateList[i] for i, old_date in enumerate(dateList)}
            data = data.group_by(FIELD_DATE).map_groups(
                lambda df: df.with_columns(pl.lit(shift_date_map[df[FIELD_DATE][0]]).alias(FIELD_DATE)))
        if data is not None and ctx.codes is not None:
            target_index = pl.DataFrame({FIELD_ASSET: ctx.codes})
            data = target_index.join(data, on=FIELD_ASSET, how="left")
        data = data.with_columns(pl.lit(ctx.time).alias(FIELD_TIME)).filter(pl.col(FIELD_DATE) >= ctx.beg_date, pl.col(FIELD_DATE) <= ctx.end_date)
        return data[cols].sort(INDEX)

    @staticmethod
    def get_history_depends(fac: 'Factor', ctx: 'FactorContext'):
        return Evaluator.depends_getter(fac, ctx, Evaluator.get_history)

    @staticmethod
    def get_values_depends(fac: 'Factor', ctx: 'FactorContext'):
        return Evaluator.depends_getter(fac, ctx, Evaluator.get_values)

    @staticmethod
    def get_history_values(fac: 'Factor', ctx: 'FactorContext'):
        return Evaluator.get_values(fac, ctx)

    @staticmethod
    def get_history_values_depends(fac: 'Factor', ctx: 'FactorContext'):
        return Evaluator.depends_getter(fac, ctx, Evaluator.get_history_values)
