# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/6 15:56
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""

FIELD_DATE = "date"
FIELD_TIME = "time"
FIELD_ASSET = "asset"
FIELD_VERSION = "version"
FIELD_ENDTIME = "end_time"
TYPE_FIXEDTIME = 'fixed_time'  # 因子插入时间是固定的
TYPE_REALTIME = "real_time"  # 因子插入时间是实时的
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

INDEX = (FIELD_DATE, FIELD_TIME, FIELD_ASSET,)