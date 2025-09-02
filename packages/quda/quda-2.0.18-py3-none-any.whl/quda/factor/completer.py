# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/6 17:15
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 因子数据补齐模块
---------------------------------------------
"""
from collections import defaultdict
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import unquote

import pandas as pd
import polars as pl
import xcals
import ygo
import logair

from .consts import *
from .errors import FactorGetError
import lidb

if TYPE_CHECKING:
    from .core import Factor

logger = logair.get_logger("quda")


class MissingChecker:
    @staticmethod
    def check_date(fac: 'Factor', beg_date, end_date) -> list[str]:
        """检验数据缺失的日期"""
        dateList = xcals.get_tradingdays(beg_date=beg_date, end_date=end_date)
        if not lidb.has(fac.tb_name):
            return dateList
        # 查询本地有数据的日期
        fac_path = lidb.tb_path(fac.tb_name)
        schema = pl.scan_parquet(fac_path).collect_schema()
        columns = schema.names()
        cond = " OR ".join([f"'{col}' IS NOT NULL" for col in columns])
        sql = f"""SELECT date
                    FROM {fac.tb_name}
                WHERE date BETWEEN '{beg_date}' AND '{end_date}'
                    AND ({cond})
                GROUP BY date 
                HAVING count() > 0;"""
        exist_dateList = lidb.sql(sql).collect()["date"].cast(pl.Utf8).to_list()
        return set(dateList) - set(exist_dateList)

    @staticmethod
    def check_times(fac: 'Factor', date: str, beg_time: str, end_time: str, freq: str) -> set:
        """
        获取指定日期缺失的时间段
        Parameters
        ----------

        Returns
        -------

        """
        tb_name = fac.tb_name
        tb_path = lidb.tb_path(tb_name) / f"date={date}"
        partition_dirs = glob(str(tb_path / "time=*" / "*.parquet"))
        exists_times = set()
        for p in partition_dirs:
            rel_path = Path(p).relative_to(tb_path)
            parts = dict(part.split("=", 1) for part in rel_path.parts if "=" in part)
            exists_times.add(unquote(parts["time"]))
        if beg_time == end_time:
            need_times = [beg_time, ]
        else:
            need_times = xcals.get_tradingtime(beg_time, end_time, freq)
        return set(need_times) - set(exists_times)

    @staticmethod
    def check_datetimes(fac: 'Factor',
                        beg_date: str,
                        end_date: str,
                        beg_time: str,
                        end_time: str,
                        freq: str) -> defaultdict[set]:
        """
        获取本地已存在的日期时间
        Parameters
        ----------

        Returns
        -------

        """
        missing_datetimes = defaultdict(set)
        for date in xcals.get_tradingdays(beg_date, end_date):
            missing_times = MissingChecker.check_times(fac, date=date, beg_time=beg_time,
                                                       end_time=end_time, freq=freq)
            if missing_times:
                missing_datetimes[date] = missing_times
        return missing_datetimes


class DataCompleter:
    """数据补齐器"""

    @staticmethod
    def _get_value_firsttime(fac: 'Factor', date: str, ) -> pl.DataFrame:
        """
        第一次落数据: 当本地没有数据或者数据都为空


        Parameters
        ----------
        fac : Factor
            因子对象，包含因子计算函数和其他相关信息。
        date : str
            日期，用于指定因子计算的日期，格式为 yyyy-mm-dd

        Returns
        -------
        data : pl.DataFrame | None
            处理后的因子计算结果数据

        Raises
        ------
        Exception
            如果因子计算函数返回的数据为空或数据类型不符合要求，则抛出异常。
        Exception
            如果因子计算结果中缺少必要的 `asset` 列，则抛出异常。
        """

        try:
            data = ygo.delay(fac.fn)(this=fac, date=date)()
        except Exception as e:
            raise FactorGetError.new_error(fac, date, fac.end_time, e) from e
        e = FactorGetError.new_error(fac, date, fac.end_time, "Empty Value.")
        if data is None:
            return fac.tb_name, None, e
        if not (isinstance(data, (pl.DataFrame, pd.Series, pd.DataFrame))):
            raise Exception("因子计算函数需要返回 polars.DataFrame | pandas.Series | pandas.DataFrame")
        if isinstance(data, (pd.DataFrame, pd.Series)):
            index_levs = data.index.nlevels
            if index_levs == 1:
                assert FIELD_ASSET == data.index.name, f"因子计算结果index中必须包含`{FIELD_ASSET}`"
            else:
                assert FIELD_ASSET in data.index.names, f"因子计算结果index中必须包含`{FIELD_ASSET}`"
            data = pl.from_pandas(data.reset_index())
        if FIELD_ASSET not in data.columns:
            if data.is_empty():
                return fac.tb_name, None, e
            raise Exception(f"因子计算函数返回值中必须包含`{FIELD_ASSET}`列")
        val_fields = data.drop(INDEX, strict=False).columns

        data = data.unique().fill_nan(None)
        if data.drop_nulls().is_empty():
            return fac.tb_name, None, e
        if FIELD_DATE not in data.columns:
            data = data.with_columns(pl.lit(date).alias(FIELD_DATE))
        data = data.with_columns(pl.lit(fac.end_time).alias(FIELD_TIME))
        data = data.select(*INDEX, *val_fields, )
        return fac.tb_name, data.sort(INDEX), None

    @staticmethod
    def complete(missing_config: list[tuple['Factor', dict[str, set]]], n_jobs: int):
        if missing_config:
            with ygo.pool(n_jobs=n_jobs) as go:
                for (fac, missing_datetimes) in missing_config:
                    for date, timeset in missing_datetimes.items():
                        for time_ in timeset:
                            job_name = f"[{fac.name} completing]"
                            if fac.type == TYPE_REALTIME:
                                fac = fac(end_time=time_)
                            go.submit(DataCompleter._get_value_firsttime, job_name=job_name)(fac=fac,
                                                                                             date=date, )

                dataset = defaultdict(list)
                for (tb_name, data, e) in go.do():
                    if data is None:
                        logger.warning(e)
                        continue
                    dataset[tb_name].append(data)
                if dataset:
                    for tb_name, data_list in dataset.items():
                        data = pl.concat(data_list)
                        lidb.put(data, tb_name=tb_name, partitions=[FIELD_DATE, FIELD_TIME])
