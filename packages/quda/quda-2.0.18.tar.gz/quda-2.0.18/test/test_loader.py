# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/21 01:42
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""

from quda.data import DataLoader, DatasetLoader
import quda
import xcals
from sklearn.pipeline import Pipeline
from quda.ml import transformer


simple_loader = DataLoader(fn=lambda iter_date, ds_path: quda.sql(f"select * from {ds_path} where date='{iter_date}';"),
                           shuffle=False,)

def change_pipe():
    new_pipe = Pipeline([
        ("imputer", transformer.Imputer()),
        ("target", transformer.Target(target="1min", frequency="1s", price_tag="price"))
    ])
    with DatasetLoader.set_params(pipe=new_pipe):
        print(DatasetLoader)
        DatasetLoader.pipe.set_params(target__target="5min")
        print(DatasetLoader)


if __name__ == '__main__':
    # beg_date = "2025-01-01"
    # end_date = "2025-05-06"
    # for df in simple_loader.fetch(xcals.get_tradingdays(beg_date, end_date), ds_path="mc/stock_kline_day"):
        # print(df.head())
        # print(df.tail())
    # print(DatasetLoader)
    change_pipe()
    # print(DatasetLoader)
