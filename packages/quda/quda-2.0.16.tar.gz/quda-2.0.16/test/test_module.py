# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/7/21 11:15
# Description:

import ygo
from pandas import DataFrame
from pydoc import locate

if __name__ == '__main__':
    df = locate("DataFrame")({"a": [1, 2, 3]})
    print(df)