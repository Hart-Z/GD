# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from Pre_Process import Pre_Process


"""
预处理模块
Pre_Process(file_position ,depotpositionn, l_limit , max_d , max_num)
"""
Pre_Process("Data/Dataset1.xlsx" , [1000, 1000, 0, -1, 0] , 20 , 800 , 12)

"""
所有重件点CVRP初步求解

Solver_G( 总迭代次数 , 载重量, 初始解个数 , 初始解迭代次数 )
"""

from CVRP_Solver_G import Solver_G
Solver_G(10000, 500, 10, 800)


"""
CVRP局部解模块

Solver_L(无人机数量,无人机载重)
"""

from CVRP_Solver_L import Solver_L
Solver_L(4 , 20)



