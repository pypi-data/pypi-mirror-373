# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/26 15:54
Email: yundi.xxii@outlook.com
Description: quda cli 入口
---------------------------------------------
"""

import typer

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        import quda
        typer.echo(f"Version: {quda.__version__}\n Run `quda --help` to get more information.")


@app.command()
def update(tasks: list[str] = ["jydata", "mc"]):
    """数据更新"""
    import quda

    quda.update(tasks=tasks)


@app.command()
def tick_clean(beg_date: str, end_date: str, freq: str = "3s", tb_name: str = "mc/stock_tick_cleaned", n_jobs: int = 5):
    """
    tick 行情数据清洗
    Parameters
    ----------
    beg_date: str
        开始日期
    end_date: str
        结束日期
    freq: str
        清洗后的行情级别，比如 '1min', 则清洗后的行情数据为 分钟频的 盘口数据
    tb_name
    n_jobs

    Returns
    -------

    """

    from quda.data.quote import save_ytick

    save_ytick(tb_name=tb_name, beg_date=beg_date, end_date=end_date, freq=freq, n_jobs=n_jobs)


if __name__ == '__main__':
    app()
