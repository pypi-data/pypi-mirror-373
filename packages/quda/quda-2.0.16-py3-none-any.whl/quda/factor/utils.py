# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/6/5 20:34
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

import ast
import hashlib
import re
from inspect import getsource

import ygo


def remove_end_time_default(fn):
    # 获取源码并解析为 AST
    source = getsource(fn)
    module = ast.parse(source)

    # 找到函数定义节点
    func_node = next(node for node in module.body if isinstance(node, ast.FunctionDef))

    # 移除 end_time 参数
    new_args = []
    defaults = []

    arg_names = [arg.arg for arg in func_node.args.args]
    default_values = func_node.args.defaults

    # 记录有多少个参数有默认值
    num_defaults = len(default_values)
    offset = len(arg_names) - num_defaults

    for i, arg in enumerate(func_node.args.args):
        if arg.arg == 'end_time':
            continue  # 跳过 end_time 参数

        new_args.append(arg)
        # 如果该参数有默认值
        if i >= offset:
            defaults.append(default_values[i - offset])

    # 更新函数参数
    func_node.args.args = new_args
    func_node.args.defaults = defaults

    # 可选：如果 kwonlyargs 中还有 end_time，也移除
    new_kwonlyargs = []
    new_kwonlydefaults = []
    for arg, default in zip(func_node.args.kwonlyargs, func_node.args.kw_defaults):
        if arg.arg == 'end_time':
            continue
        new_kwonlyargs.append(arg)
        new_kwonlydefaults.append(default)

    func_node.args.kwonlyargs = new_kwonlyargs
    func_node.args.kw_defaults = new_kwonlydefaults

    # 重新生成源码
    new_source = ast.unparse(func_node)
    return new_source


def fn_code(fn: callable) -> str:
    """
    返回清洗后的函数定义字符串：
    - 移除 end_time 参数

    Parameters
    ----------
    fn : callable
        需要获取定义代码的callable对象

    Returns
    -------
    str
        清洗后的函数定义字符串
    """
    # 使用 AST 解析并修改函数定义
    try:
        return remove_end_time_default(fn)
    except Exception as e:
        # 如果 AST 解析失败，退回到原始方式
        return getsource(fn)


def clean_source(source):
    # 移除注释
    source = re.sub(r'#.*$', '', source, flags=re.MULTILINE)
    # 移除空行
    source = re.sub(r'\n\s*\n', '\n', source)
    return source.strip()


def fn_code_hash(fn):
    source = fn_code(fn)
    cleaned = clean_source(source)
    return hashlib.md5(cleaned.encode()).hexdigest()


def fn_params_hash(fn, ignore_params=None):
    if ignore_params is None:
        ignore_params = []
    params = ygo.fn_params(fn)
    filtered = [f'{k}={v}' for k, v in params if k not in ignore_params]
    filtered_str = f"({','.join(filtered)})"
    return hashlib.md5(filtered_str.encode()).hexdigest()


def version_hash(fn, ):
    code_hash = fn_code_hash(fn)
    param_hash = fn_params_hash(fn, ignore_params=["end_time"])
    combined = f"{code_hash}|{param_hash}"
    return hashlib.md5(combined.encode()).hexdigest()
