# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/3/5 21:40
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""
from __future__ import annotations

import importlib.util
import sys
from functools import lru_cache
from functools import partial
from pathlib import Path
import inspect

import polars as pl
import logair

from .errors import CalculateError, CompileError, PolarsError, FailError
from .expr import Expr

# 动态加载模块
module_name = "udf"
module_path = Path(__file__).parent / "udf" / "__init__.py"
spec = importlib.util.spec_from_file_location(module_name, module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)


@lru_cache(maxsize=512)
def parse_expr(expr: str) -> Expr:
    return Expr(expr)

logger = logair.get_logger("quda.qdf")

class LQDF:

    def __init__(self,
                 data: pl.LazyFrame | pl.DataFrame,
                 index: tuple[str] = ("date", "time", "asset"),
                 align: bool = True, ):
        assert isinstance(data, (pl.LazyFrame, pl.DataFrame)), "data must be a polars DataFrame or LazyFrame"
        self.data: pl.LazyFrame = data.lazy().cast({pl.Decimal: pl.Float32}).drop_nulls(subset=index)
        self._index = self.data.select(index).collect()
        self.index = index
        self.dims = [self._index[name].n_unique() for name in index]
        if align:
            lev_vals: list[pl.DataFrame] = [self._index.select(name).unique().lazy() for name in index]
            full_index = lev_vals[0]
            for lev_val in lev_vals[1:]:
                full_index = full_index.join(lev_val, how="cross")
            self.data = full_index.join(self.data, on=index, how='left')
        self.data = self.data.sort(index)
        self.failed = list()
        self._cols = set(self.data.collect_schema().names())
        self._expr_cache = dict()  # type: dict[Expr, str]
        self._cur_expr_cache = dict()

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__str__()

    def register_udf(self, func: callable, name: str = None):
        name = name if name is not None else func.__name__
        setattr(module, name, func)

    def _compile_expr(self, expr: str):
        """str表达式 -> polars 表达式"""
        try:
            expr_parsed = Expr(expr)
            alias = expr_parsed.alias  # if expr_parsed.alias is not None else str(expr_parsed)
            if alias in self._cols:
                return pl.col(alias), alias
            # 如果该表达式已有对应列，直接复用
            if expr_parsed in self._expr_cache:
                expr_pl: pl.Expr = pl.col(self._expr_cache[expr_parsed]).alias(alias)
                self.data = self.data.with_columns(expr_pl)
                return pl.col(alias), alias
            elif expr_parsed in self._cur_expr_cache:
                expr_pl: pl.Expr = pl.col(self._cur_expr_cache[expr_parsed]).alias(alias)
                self.data = self.data.with_columns(expr_pl)
                return pl.col(alias), alias

            def recur_compile(expr_: Expr):
                """递归编译"""
                alias_ = expr_.alias
                if alias_ in self._cols:
                    # 已存在：直接select数据源
                    return pl.col(alias_)
                if expr_ in self._expr_cache:
                    return pl.col(self._expr_cache[expr_]).alias(alias_)
                elif expr_ in self._cur_expr_cache:
                    return pl.col(self._cur_expr_cache[expr_]).alias(alias_)
                func = getattr(module, expr_.fn_name)
                _params = sorted(list(inspect.signature(func).parameters.keys()))
                if "dims" in _params:
                    func = partial(func, dims=self.dims)
                args = list()
                kwargs = dict()
                for arg in expr_.args:
                    if isinstance(arg, Expr):
                        args.append(recur_compile(arg))
                    elif isinstance(arg, dict):
                        kwargs.update(arg)
                    elif isinstance(arg, str):
                        if arg.lower() == "null":
                            args.append(None)
                        else:
                            args.append(pl.col(arg))
                    else:
                        args.append(arg)  # or args.append(pl.lit(arg))
                try:
                    expr_pl: pl.Expr = func(*args, **kwargs)
                    self.data = self.data.with_columns(expr_pl.alias(alias_))
                    self._cur_expr_cache[expr_] = alias_
                    return pl.col(alias_)
                except Exception as e:
                    raise CompileError(message=f"{expr_.fn_name}({', '.join([str(arg) for arg in args])})\n{e}") from e

            return recur_compile(expr_parsed), alias
        except (CalculateError, CompileError, PolarsError) as e:
            raise e
        except Exception as e:
            # 所有未处理的错误统一抛出为 CompileError
            raise CompileError(message=f"[编译器外层]\n{e}") from e

    def sql(self, *exprs: str, ):
        """
        表达式查询
        Parameters
        ----------
        exprs: str
            表达式，比如 "ts_mean(close, 5) as close_ma5"
        Returns
        -------
            polars.LazyFrame
        """
        self.failed = list()
        exprs_select = list()
        self._cur_expr_cache = {}
        deps_lv1 = set()
        def get_dependencies(expr: Expr) -> set[Expr]:
            deps = set()
            for arg in expr.args:
                if isinstance(arg, Expr):
                    deps.update(get_dependencies(arg))
                elif isinstance(arg, str):
                    if arg.lower() != "null":
                        deps.add(arg)
            return deps

        for expr in exprs:
            expr = parse_expr(expr)
            deps_lv1.update(get_dependencies(expr))
        deps_lv1 = deps_lv1.intersection(self._cols)
        self.data = self.data.select(*self.index, *deps_lv1)

        for expr in exprs:
            try:
                compiled, alias = self._compile_expr(expr)
                if compiled is not None:
                    exprs_select.append(alias)
            except Exception as e:
                self.failed.append(FailError(expr, e))
        if self.failed:
            logger.warning(f"sql failed num：{len(self.failed)}/{len(exprs)}: \n {self.failed}")
        self.data = self.data.fill_nan(None)
        new_expr_cache = dict()
        try:
            current_cols = set(self.data.collect_schema().names())
            # 缓存整理：只保留当前表达式的缓存
            self._expr_cache.update(self._cur_expr_cache)
            for k, v in self._expr_cache.items():
                if v in current_cols:
                    new_expr_cache[k] = v
            self._expr_cache = new_expr_cache
            final_df = self.data.select(*self.index, *exprs_select)
            return final_df
        except Exception as e:
            # 缓存整理：只保留当前表达式的缓存
            for k, v in self._expr_cache.items():
                if v in self._cols:
                    new_expr_cache[k] = v
            self._expr_cache = new_expr_cache
            raise PolarsError(message=f"LazyFrame.collect() step error:\n{e}") from e
