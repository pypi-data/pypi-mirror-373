# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/10 17:43
@author: ZhangYundi
@email: yundi.xxii@outlook.com
@description: 
---------------------------------------------
"""

from quda.qdf.expr import Expr

if __name__ == '__main__':
    expr = "a>0?b:Null as d"
    res = Expr(expr)
    print(res)