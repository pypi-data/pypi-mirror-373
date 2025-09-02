# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/3/5 01:04
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""
import numpy as np
import polars as pl

over = dict(
    partition_by=["date", "asset"],
    order_by=["time"]
)


def itd_mean(expr: pl.Expr, windows): return expr.rolling_mean(windows, min_samples=1).over(**over)


def itd_std(expr: pl.Expr, windows): return expr.rolling_std(windows, min_samples=1).over(**over)


def itd_sum(expr: pl.Expr, windows): return expr.rolling_sum(windows, min_samples=1).over(**over)


def itd_var(expr: pl.Expr, windows): return expr.rolling_var(windows, min_samples=1).over(**over)


def itd_skew(expr: pl.Expr, windows): return expr.rolling_skew(windows, ).over(**over)


def itd_ref(expr: pl.Expr, windows, dims):  # return expr.shift(int(abs(windows))).over(**over)
    return (
        expr
        .map_batches(
            lambda x: pl.DataFrame(
                x
                .to_numpy()
                .reshape(dims)
                .transpose((1, 0, 2))
                .reshape((dims[1], -1))
            )
            .shift(windows)
            .to_numpy()
            .reshape((dims[1], dims[0], dims[2]))
            .transpose((1, 0, 2))
            .ravel(),
            return_dtype=pl.self_dtype()
        )
        .replace(np.nan, None)
    )


def itd_mid(expr: pl.Expr, windows): return expr.rolling_median(windows, min_samples=1).over(**over)


def itd_mad(expr: pl.Expr, windows):
    return 1.4826 * (expr - expr.rolling_median(windows, min_samples=1)).abs().rolling_median(windows, min_samples=1).over(**over)


def itd_rank(expr: pl.Expr, windows, dims):
    return (
        expr
        .map_batches(
            lambda x: pl.DataFrame(
                x
                .to_numpy()
                .reshape(dims)
                .transpose((1, 0, 2))
                .reshape((dims[1], -1))
            )
            .with_row_index()
            .rolling("index", period=f"{windows}i")
            .agg(pl.all().exclude("index").rank().last())
            .drop("index")
            .to_numpy()
            .reshape((dims[1], dims[0], dims[2]))
            .transpose((1, 0, 2))
            .ravel(),
            return_dtype=pl.self_dtype()
        )
    )

def itd_prod(expr: pl.Expr, windows, dims):
    return (
        expr
        .map_batches(
            lambda x: pl.DataFrame(
                x
                .to_numpy()
                .reshape(dims)
                .transpose((1, 0, 2))
                .reshape((dims[1], -1))
            )
            .with_row_index()
            .rolling("index", period=f"{windows}i")
            .agg(pl.all().exclude("index").cum_prod())
            .drop("index")
            .to_numpy()
            .reshape((dims[1], dims[0], dims[2]))
            .transpose((1, 0, 2))
            .ravel(),
            return_dtype=pl.self_dtype()
        )
    )

def itd_max(expr: pl.Expr, windows): return expr.rolling_max(windows, min_samples=1).over(**over)


def itd_min(expr: pl.Expr, windows): return expr.rolling_min(windows, min_samples=1).over(**over)


def itd_ewmmean(expr: pl.Expr, com=None, span=None, half_life=None, alpha=None):
    return (expr
            .ewm_mean(com=com,
                      span=span,
                      half_life=half_life,
                      alpha=alpha,
                      adjust=False,
                      min_samples=1)
            .over(**over))


def itd_ewmstd(expr: pl.Expr, com=None, span=None, half_life=None, alpha=None):
    return (expr
            .ewm_std(com=com,
                     span=span,
                     half_life=half_life,
                     alpha=alpha,
                     adjust=False,
                     min_samples=1)
            .over(**over))


def itd_ewmvar(expr: pl.Expr, com=None, span=None, half_life=None, alpha=None):
    return (expr
            .ewm_var(com=com,
                     span=span,
                     half_life=half_life,
                     alpha=alpha,
                     adjust=False,
                     min_samples=1)
            .over(**over))


def itd_cv(expr: pl.Expr, windows): return itd_std(expr, windows) / itd_mean(expr, windows)


def itd_snr(expr: pl.Expr, windows): return itd_mean(expr, windows) / itd_std(expr,
                                                                              windows)  # 信噪比: signal_to_noise ratio


def itd_diff(expr: pl.Expr, windows=1): return expr.diff(windows).over(**over)


def itd_pct(expr: pl.Expr, windows=1): return expr.pct_change(windows).over(**over)


def itd_corr(left: pl.Expr, right: pl.Expr, windows): return pl.rolling_corr(left, right, window_size=windows,
                                                                             min_samples=1).over(**over)


def itd_cov(left: pl.Expr, right: pl.Expr, windows): return pl.rolling_cov(left, right, window_size=windows,
                                                                           min_samples=1).over(**over).replace(np.nan,
                                                                                                               None)

def itd_slope(left: pl.Expr, right: pl.Expr, windows): return (
            itd_mean(left * right, windows) - itd_mean(right, windows) * itd_mean(left, windows)) / itd_var(right,
                                                                                                            windows)


def itd_resid(left: pl.Expr, right: pl.Expr, windows): return right - itd_slope(left, right, windows) * right


def itd_quantile(expr: pl.Expr, windows, quantile):
    return expr.rolling_quantile(window_size=windows, quantile=quantile, min_samples=1).over(**over)

def itd_entropy(expr: pl.Expr, windows, dims):
    return (
        expr
        .map_batches(
            lambda x: pl.DataFrame(
                x
                .to_numpy()
                .reshape(dims)
                .transpose((1, 0, 2))
                .reshape((dims[1], -1))
            )
            .with_row_index()
            .rolling("index", period=f"{windows}i")
            .agg(pl.all().exclude("index").entropy())
            .drop("index")
            .to_numpy()
            .reshape((dims[1], dims[0], dims[2]))
            .transpose((1, 0, 2))
            .ravel(),
            return_dtype=pl.self_dtype()
        )
    )

def itd_zscore(expr: pl.Expr, windows):
    return (expr - itd_mean(expr, windows))/itd_std(expr, windows)

def itd_norm(expr: pl.Expr, windows):
    return (expr - itd_mid(expr, windows))/itd_mad(expr, windows)

def itd_fill_forward(expr: pl.Expr):
    return expr.fill_null(strategy="forward").over(**over)