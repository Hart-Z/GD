# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from Pre_Process import Pre_Process

#Pre_Process(file_position , l_limit , max_d , max_num)
Pre_Process("Data/Dataset1.xlsx" , [1500, 1500, 0, -1, 0] , 20 , 800 , 20)
