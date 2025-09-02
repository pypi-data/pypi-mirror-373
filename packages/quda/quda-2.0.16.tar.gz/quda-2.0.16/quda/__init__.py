# Copyright (c) ZhangYundi.
# Licensed under the MIT License.

__version__ = "2.0.16"

from typing import Iterable


def update(tasks: tuple[str] = ("jydata", "mc")):
    """
    通过全局配置文件中的`UPDATES`配置项来更新数据，需要遵循统一编写标准。每个数据源需要定义 `CONFIG` 字典和 `fetch_fn` 方法。

    添加新的更新任务步骤：

    - **Step 1**: 实现具体的数据更新逻辑

    创建一个新的 Python 文件（如：`my_project/data/update/update_news.py`），

    并在其中定义如下内容：

    >>> import lidb
    >>>
    >>> CONFIG = {'news/tb1': 'SELECT * FROM source_table'}  # SQL 查询语句或其它来源标识
    >>>
    >>> def fetch_fn(tb_name, db_conf):
    ...     query = CONFIG.get(tb_name)
    ...     return lidb.read_mysql(query, db_conf=db_conf)

    - **Step 2**: 在配置文件中添加配置

    在 {quda.DB_PATH}/conf/settings.toml 添加配置

    [UPDATES.news_data]

    mod = "my_project.data.update.update_news"

    update_time = "16:30"

    db_conf = "DATABASES.mysql"

    mode = "auto"

    beg_date = "2020-01-01"

    """

    from . import updater
    import ygo
    import logair
    import lidb

    logger = logair.get_logger("quda.update")

    update_settings = lidb.get_settings().get("UPDATES")
    if not update_settings:
        logger.warning(f"Missing provider update configuration. Initialize jydata/mc configs from quda.data.init.")
        import quda.data
        quda.data.init()
        update_settings = lidb.get_settings().get("UPDATES")
    for task, task_conf in update_settings.items():
        if task not in tasks:
            continue
        logger.info(f"{task} config: {task_conf}")
        mod = ygo.module_from_str(task_conf["mod"])
        for tb_name in mod.CONFIG.keys():
            ygo.delay(updater.submit)(tb_name=tb_name,
                                      fetch_fn=ygo.delay(mod.fetch_fn)(db_conf=task_conf.get("db_conf")),
                                      **task_conf)()
    updater.do(debug_mode=True)


def from_polars(df, index: Iterable[str] = ("date", "time", "asset"), align: bool = False):
    from .qdf import QDF
    return QDF(data=df, index=index, align=align)


def to_lazy(df, index: Iterable[str] = ("date", "time", "asset"), align: bool = False):
    from .qdf import LQDF
    return LQDF(data=df, index=index, align=align)
