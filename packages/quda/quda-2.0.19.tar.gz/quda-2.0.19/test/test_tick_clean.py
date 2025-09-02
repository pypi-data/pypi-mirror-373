# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/7/11 11:24
Email: yundi.xxii@outlook.com
Description: 
---------------------------------------------
"""

from quda.data.quote import save_ytick
import time

def test_clean():
    start_t = time.time()
    beg_date = "2025-05-06"
    end_date = "2025-05-06"
    freq = "30s"
    save_ytick(beg_date, end_date, freq, "mc/stock_tick_cleaned", n_jobs=1)
    print(f"cost {(time.time() - start_t):.3f}s")

if __name__ == '__main__':
    test_clean()