# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from Pre_Process import Pre_Process
from CVRP_Solver_G import Solver_G
from CVRP_Solver_L import Solver_L
"""
预处理模块
Pre_Process(file_position , l_limit , max_d , max_num)
"""
# Pre_Process("Data/Dataset1.xlsx" , [1500, 1500, 0, -1, 0] , 20 , 800 , 20)

"""
所有重件点CVRP初步求解
Solver_G( 总迭代次数 , 载重量, 初始解个数 , 初始解迭代次数 )
"""
# Solver_G(7000, 500, 10, 1000)

Solver_L(3 , 20)

