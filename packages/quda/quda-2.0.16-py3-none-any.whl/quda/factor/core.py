# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/26 08:47
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

from __future__ import annotations

import inspect as inspect_
import os
from dataclasses import dataclass
from functools import wraps

import xcals
import ygo
from varname import varname

from .consts import *
from .errors import FactorGetError
from .evaluator import Evaluator
from .resolver import VersionResolver


@dataclass
class FactorContext:
    """
    参数上下文
    """
    date: str = ''
    beg_date: str = ''
    end_date: str = ''
    beg_time: str = ''
    end_time: str = ''
    codes: list[str] | None = None
    time: str = "15:00:00"
    avoid_future: bool = True
    show_progress: bool = True
    n_jobs: int = 10
    freq: str = '1min'


def factor_context(func: callable, ):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        # 获取函数签名
        sig = inspect_.signature(func)
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()
        period = bound_args.arguments.get("period")
        context_fields = set(FactorContext.__dataclass_fields__.keys())
        filtered = {
            k: v for k, v in bound_args.arguments.items()
            if k in context_fields and k != "self"
        }
        if period:
            date = bound_args.arguments.get("date")
            beg_date = bound_args.arguments.get("beg_date")
            if not beg_date:
                date_shifted, _ = xcals.shift_tradedt(date, self.end_time, period)
                beg_date, end_date = min([date, date_shifted]), max([date, date_shifted])
            else:
                beg_date, end_date = min([date, beg_date]), max([date, beg_date])
            filtered.update({"beg_date": beg_date, "end_date": end_date})

        ctx = FactorContext(**filtered)
        fn_name = func.__name__
        if "depend" in fn_name:
            Evaluator.prepare(self._depends, ctx)
        else:
            Evaluator.prepare([self, ], ctx)
        try:
            return getattr(Evaluator, fn_name)(self, ctx=ctx)
        except Exception as e:
            raise FactorGetError.new_error(self, ctx.date, ctx.time, e) from e

    return wrapper


class Factor:
    """
    因子类
    Examples
    --------

    日频因子

    >>> def fac1(date, ):
    ...     ...
    >>> fac_DayFac1 = Factor(fn=fac1)
    >>> fac_DayFac1.name
    DayFac1

    分钟频因子

    >>> def fac2(date, end_time):
    ...     ...
    >>> fac_MinuteFac = Factor(fn=fac2)
    >>> fac_MinuteFac(end_time="09:31:00").name
    MinuteFac

    多依赖因子

    >>> def fac3(this: Factor, date, ):
    ...     depend_big_df = this.get_history_depends(date, )
    ...     ...
    >>> fac_MultiFac = Factor(fac_DayFac1, fac_MinuteFac, fn=fac3)

    """

    def __init__(self, *depends: Factor, fn: callable, name: str = None, frame: int = 1, share_params: list = None):
        """
        初始化Factor类的实例。
        Parameters
        ----------
        *depends : Factor
            可变数量的Factor实例，表示当前函数依赖的因子。
        fn : callable
            可调用对象，每天的因子计算逻辑的具体实现
        name : str | None
            因子的名称，默认为None。如果未提供名称，将尝试从调用栈中获取。
        frame : int
            调用栈的层级，默认为1。
        share_params: list
            共享参数: 顶层的Factor的参数会传递到底层的依赖因子

        Notes
        -----
        - 如果提供了依赖因子，会根据依赖因子的版本号和当前因子的版本号重新计算版本号。
        - 如果没有提供名称，会尝试从调用栈中获取名称。
        - 根据因子计算逻辑函数中是否带有 `end_time` 形参来确定因子的类型(日频还是分钟频)
        """
        self._frame = frame
        self.fn = fn
        self.__doc__ = fn.__doc__
        self._fn_info = ygo.fn_info(fn)
        self.fn_params = ygo.fn_params(fn)
        self._depends = [depend for depend in depends]
        if self._depends:
            if share_params is not None:
                depend_params = {k: v for k, v in self.fn_params if k in share_params}
                self._depends = [depend(**depend_params) for depend in depends]
        self.version = VersionResolver.resolve_version(fn, self._depends)
        self._params = {k: v for k, v in self.fn_params}
        default_insettime = "15:00:00"
        self.end_time = self._params.get(FIELD_ENDTIME, default_insettime)
        self.insert_time = self._params.get(FIELD_ENDTIME, default_insettime)
        self.name = name
        if self.name is None:
            try:
                self.name = varname(self._frame, strict=False)
            except:
                pass
        self._name = self.name
        self.type = TYPE_FIXEDTIME
        if FIELD_ENDTIME in list(inspect_.signature(self.fn).parameters.keys()):
            self.type = TYPE_REALTIME

    def __call__(self, **kwargs):
        """
        当实例被调用时，创建并返回一个新的Factor对象。
        该方法通过更新当前实例的状态，并使用延迟调用封装原始函数，创建一个新的Factor实例。
        如果新实例的类型为TYPE_D，则设置其结束时间为 15:00:00。

        Parameters
        ----------
        **kwargs : dict
            关键字参数，将传递给因子计算逻辑函数的参数

        Returns
        -------
        Factor
            一个新的Factor对象，其属性根据当前实例和调用参数初始化。
        """
        if not kwargs:
            return self
        frame = self._frame + 1
        newFactor = Factor(*self._depends,
                           fn=ygo.delay(self.fn)(**kwargs),
                           name=self._name,
                           frame=frame)
        newFactor.name = self.name
        newFactor.type = self.type
        if newFactor.type == TYPE_FIXEDTIME:
            newFactor.end_time = newFactor._params.get(FIELD_ENDTIME, self.end_time)
            newFactor.insert_time = self.insert_time
        return newFactor

    def astype(self, _type: str):
        """有些因子因为没有实时数据的缘故，然而计算函数中使用了形参:`end_time`需要声明为日频因子"""
        self.type = _type
        return self

    def __repr__(self):
        # inspect(self, title=f"{self.name}", help=True)

        params = ygo.fn_params(self.fn)
        all_define_params = sorted(list(inspect_.signature(self.fn).parameters.keys()))

        default_params = {k: v for k, v in params}
        params_infos = list()
        for p in all_define_params:
            if p in default_params:
                params_infos.append(f'{p}={default_params[p]}')
            else:
                params_infos.append(p)
        params_infos = ', '.join(params_infos)
        mod = ygo.fn_path(self.fn)

        return f"""{mod}.{self.fn.__name__}({params_infos})"""

    @property
    def tb_name(self, ) -> str:
        tb_name = os.path.join("factors", self._name, f"version={self.version}")
        return tb_name

    def alias(self, name):
        """重新命名因子"""
        self.name = name
        return self

    def set_insert_time(self, insert_time):
        """
        设置因子的入库时间, 注意，设置了插入时间后，factor.type == "fixed_time"
        Parameters
        ----------
        insert_time: str
            入库时间，格式为 `hh:mm:ss`
        Returns
        -------
        Factor
            其他设置和原始因子一致，只是入库时间不同
        """
        insert_time = "13:00:00" if "11:30:00" < insert_time < "13:00:00" else insert_time
        frame = self._frame + 1
        newFactor = Factor(*self._depends, fn=self.fn, name=self._name, frame=frame).astype(TYPE_FIXEDTIME)
        newFactor.insert_time = insert_time
        newFactor.end_time = self.end_time
        return newFactor

    def set_end_time(self, end_time: str):
        """
        设置因子的结束时间
        Parameters
        ----------
        end_time: str
            结束时间，格式为 `hh:mm:ss`
        Returns
        -------
        Factor
            其他设置和原始因子一致，只是结束时间不同
        """
        frame = self._frame + 1
        newFactor = Factor(*self._depends, fn=ygo.delay(self.fn)(end_time=end_time), name=self._name, frame=frame)
        newFactor.end_time = end_time
        newFactor.insert_time = self.insert_time
        return newFactor

    @factor_context
    def get_value(self,
                  date: str,
                  codes: list[str] | None = None,
                  time: str = '15:00:00',
                  avoid_future: bool = True,
                  ):
        """
        获取指定日期和时间的最新数据。

        Parameters
        ----------
        date : str
            日期字符串，格式为 yyyy-mm-dd。
        codes : Iterable[str]
            证券代码列表，可选，默认为 None。
        time : str
            时间字符串，默认为 '15:00:00'。
        avoid_future: bool
            是否避免未来数据，默认 True
            - True: 当取值time < fac.insert_time 时，取不到当天的数据，只能取上一个交易日的数据
            - False: 当取值 time < fac.insert_time 时, 可以取到当天的数据

        Returns
        -------
        polars.DataFrame
        """

    @factor_context
    def get_values(self,
                   date: str,
                   beg_time: str,
                   end_time: str,
                   freq: str = "1min",
                   codes: list[str] | None = None,
                   complete_n_workers: int = 5):
        """
        取值: 指定日期 beg_time -> end_time 的全部值

        Returns
        -------
        polars.DataFrame
        """

    @factor_context
    def get_value_depends(self,
                          date: str,
                          codes: list[str] | None = None,
                          time: str = '15:00:00',
                          avoid_future: bool = True, ):
        """
        获取依赖因子的值，并合并成一张宽表。

        Parameters
        ----------
        date : str
            日期字符串，用于获取因子值的日期, 格式为'yyyy-mm-dd'。
        codes : Iterable[str]
            可选的证券代码列表，默认为 None。
        time : str
            时间字符串，默认为 '15:00:00'。
        avoid_future: bool
            是否避免未来数据，默认 True
            - True: 当取值time < fac.insert_time 时，取不到当天的数据，只能取上一个交易日的数据
            - False: 当取值 time < fac.insert_time 时, 可以取到当天的数据

        Returns
        -------
        polars DataFrame | None
            包含所有依赖因子值的宽表。

        Notes
        -----
        - 如果该因子不依赖于其他因子，则直接返回 None。
        - 函数会为每个因子获取其值，并将这些值合并成一个宽表。
        - 如果某个因子的值为 None，则跳过该因子。
        - 存在多列的因子，列名会被重命名，便于阅读与避免冲突, 命名规则为 {fac.name}.<columns>。
        """

    @factor_context
    def get_history(self,
                    date,
                    codes: list[str] | None = None,
                    period: str = '-5d',
                    beg_date: str = None,
                    time='15:00:00',
                    avoid_future: bool = True,
                    show_progress: bool = True,
                    n_jobs: int = 7):
        """
        回看period(包含当天), period最小单位为d, 小于d的周期向上取整，比如1d1s,视为2d

        Parameters
        ----------
        date : str
            结束日期, 格式 'yyyy-mm-dd'。
        codes : Iterable[str] | None
            可选的证券代码列表，默认为None。
        time : str
            时间，默认为'15:00:00', 格式 hh:mm:ss
        period: str
            回看周期, 最小单位为d, 小于d的周期向上取整，比如1d1s,视为2d
        beg_date: str
            开始日期，如果赋值，则period参数失去作用
        n_jobs : int, optional
            并发任务数，默认为7。
        avoid_future: bool
            是否避免未来数据，默认 True
            - True: 当取值time < fac.insert_time 时，取不到当天的数据，只能取上一个交易日的数据
            - False: 当取值 time < fac.insert_time 时, 可以取到当天的数据
        show_progress: bool
            是否显示进度，默认True

        Returns
        -------
        polars.DataFrame | None

        Notes
        -----
        - 如果`avoid_future`=True 并且 指定的时间早于因子的结束时间，则将开始和结束日期都向前移动一个交易日。
        - 如果数据不完整，会自动补齐缺失的数据。
        - 最终结果会按日期和证券代码排序。
        """

    @factor_context
    def get_history_depends(self,
                            date,
                            codes: list[str] | None = None,
                            period: str = '-5d',
                            beg_date: str = None,
                            time="15:00:00",
                            avoid_future: bool = True,
                            show_progress: bool = True,
                            n_jobs=7):
        """
        回看依赖period(包含当天), period最小单位为d, 小于d的周期向上取整，比如1d1s,视为2d

        Parameters
        ----------
        date : str
            结束日期，格式为 'yyyy-mm-dd'。
        codes : Iterable[str]
            股票代码列表，默认为 None。
        period: str
            回看周期, 最小单位为d, 小于d的周期向上取整，比如1d1s,视为2d
        beg_date: str
            开始日期，如果赋值，则period参数失去作用
        time : str
        show_progress : bool, optional
            是否显示进度条，默认为 True。
        n_jobs : int, optional
            并行任务数，默认为 7。
        avoid_future: bool
            是否避免未来数据，默认 True
            - True: 当取值time < fac.insert_time 时，取不到当天的数据，只能取上一个交易日的数据
            - False: 当取值 time < fac.insert_time 时, 可以取到当天的数据
        show_progress : bool
            是否显示进度条，默认为 True。

        Returns
        -------
        polars.DataFrame | None

        Notes
        -----
        - 最终结果会按日期和股票代码排序。
        """

    @factor_context
    def get_values_depends(self,
                           date: str,
                           beg_time: str,
                           end_time: str,
                           freq: str = "1min",
                           codes: list[str] | None = None,
                           avoid_future: bool = True,
                           n_jobs: int = 5):
        """
        获取底层依赖因子 date: beg_time -> end_time 的值

        Returns
        -------
        polars.DataFrame
        """

    @factor_context
    def get_history_values(self,
                           date: str,
                           period: str,
                           beg_time: str,
                           end_time: str,
                           freq: str = "1min",
                           codes: list[str] | None = None,
                           avoid_future: bool = True,
                           n_jobs: int = 5):
        """
        获取 beg_date->end_date: beg_time -> end_time 取值

        Returns
        -------
        polars.DataFrame
        """

    @factor_context
    def get_history_values_depends(self,
                                   date: str,
                                   period: str,
                                   beg_time: str,
                                   end_time: str,
                                   freq: str = "1min",
                                   codes: list[str] | None = None,
                                   avoid_future: bool = True,
                                   n_jobs: int = 5):
        """
        获取底层依赖因子 beg_date->end_date: beg_time -> end_time 的值

        Returns
        -------
        polars.DataFrame
        """

    def doc(self):
        """
        使用 rich 以更紧凑的方式打印因子信息，在 Jupyter Notebook 中展示更美观。
        """
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich import inspect

        console = Console()
        # 标题部分
        title = Text(f"{self.name}", style="bold magenta")
        console.print(Panel(title, expand=False))
        console.print(self.fn.__doc__)
        inspect(self, help=True)

        # 示例调用
        test_date = "2025-05-06"
        test_time = "10:00:00"
        example_call = f"`{self.name}.get_value(date='{test_date}', time='{test_time}')`"
        console.print(f"🧪 **示例调用**: {example_call}", style="bold magenta")

        # 数据样例
        try:
            sample = self.get_value(test_date, time=test_time).head()
            console.print("📊 **数据样例**: ", style="bold magenta")
            console.print(sample)
        except Exception as e:
            console.print(f"[red]⚠️ 获取数据样例失败: {str(e)}[/red]")
        self.show_dependency()

    def show_dependency(self):
        """
        生成因子依赖关系的 DOT 字符串，并调用 polars 的 display_dot_graph 显示。
        支持 Jupyter / IPython 环境内联显示。

        示例:
            fac.show_dependency()
        """
        from polars._utils.various import display_dot_graph

        dot_lines = ['digraph G {', 'rankdir=TB;', 'node [shape=box, style=solid, color=black, fillcolor=white];']

        visited = set()

        def add_node(fac):
            if not hasattr(fac, "name") or fac.name is None or fac.name in visited:
                return
            visited.add(fac.name)
            for dep in getattr(fac, "_depends", []):
                if dep.name:
                    dot_lines.append(f'"{dep.name}" -> "{fac.name}";')
                    add_node(dep)

        add_node(self)

        dot_lines.append("}")
        dot_source = "\n".join(dot_lines)

        # 使用 Polars 的 display_dot_graph 渲染图形
        display_dot_graph(dot=dot_source)
