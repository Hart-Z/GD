# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from UAV_Tabu import TS_search

def Generate_LHCostmatrix_raw(lp, hp):
    # 矩阵行轻列重
    Node_numH = np.shape(hp)[0]
    Node_numL = np.shape(lp)[0]
    LH_costmatrix = np.zeros((Node_numL, Node_numH))

    def cal_distance(i, j):
        xd = lp[i][0]-hp[j][0]
        yd = lp[i][1]-hp[j][1]
        distance = np.sqrt(np.square(xd)+np.square(yd))
        return distance

    for i in range(0, Node_numL):
        for j in range(0, Node_numH):
            LH_costmatrix[i][j] = cal_distance(i, j)

    output = pd.DataFrame(data=LH_costmatrix)
    # output.to_csv('costmatrix.xlsx', index=False)
    writer = pd.ExcelWriter('Data/LH_costmatrix_raw.xlsx')

    output.to_excel(writer, 'Sheet1')
    writer.close()

lp= np.array(pd.read_excel('Data/LP.xlsx'))


hp = np.array(pd.read_excel('Data/HP.xlsx'))

Generate_LHCostmatrix_raw(lp,hp)