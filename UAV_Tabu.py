# -*- coding:utf-8 -*-
'''
UAV TS-CVRP Solver
Input:
    class_l
    classtype

Output:
    Routes

'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import csv
from scipy.special import comb

"""
全局变量清单

"""
Data = []  # 数据
HP_data = []     
Max_iternum = 0  # 迭代次数最大值
Neighbour_num = 0  # 每次搜索邻居个数
Neighbour_route = []  # 邻域路线矩阵

"""
    Neighbour_route 数据结构：
            [
                    [路径]
                    代价;
                    ...
            ]
"""
Table_length = 0  # 禁忌长度
Node_num = 0  # 节点数量，编码长度
Cost_matrix = []  # 代价矩阵
LH_Costmatrix = []
Current_route = []  # 当前路径
Best_route = []  # 最优路径
Current_cost = 0  # 当前路径花费代价
Best_cost = 0  # 最优代价
Tabu_table = []  # 禁忌表
Depot1 = 0
Depot2 = 0
Class_L = []
Class_type = []
"""
初始化部分：
    init()
    read_costmatrix()
    init_route()
"""


def init(class_l, depot1, depot2 , Maxcapacity):  # 初始化

    global Data
    global Max_iternum
    global Neighbour_num
    global Table_length
    global Max_capacity
    global Node_num
    global Cost_matrix
    global LH_Costmatrix
    global Current_route
    global Best_route
    global Best_cost
    global Tabu_table
    global Depot1
    global Depot2
    global Class_L

    # 读取并设置参数
    Max_capacity = Maxcapacity

    Class_L = class_l[:]

    # 得到Node_num
    rawData = pd.read_excel("Data/LP.xlsx")
    Data = np.array(rawData)
    # HP_data = pd.read_excel("Data/HP_raw.xlsx")
    # HP_data = np.array(HP_data)

    Node_num = len(class_l)

    Neighbour_num = int(np.sqrt(comb(Node_num,2)))+1
    Table_length = int(np.sqrt(Node_num))+1
    Max_iternum = Node_num*200

    Depot1 = depot1
    Depot2 = depot2
    # 读取代价矩阵（已经事先由generate_costmatrix.py计算出来）
    Cost_matrix, LH_Costmatrix = read_costmatrix()

    # 初始化路径
    initroute = init_route(class_l)
    initcost = cal_routecost(initroute)
    Current_route = initroute[:]

    # 初始化最优解（一条随机路径）
    Best_route = initroute[:]
    Best_cost = initcost

    # 初始化禁忌表

    init_row = [initroute, initcost]
    Tabu_table = np.array(init_row)
    for i in range(1, Table_length):
        Tabu_table = np.row_stack((Tabu_table, init_row))


def read_costmatrix():  # 读取计算好的代价矩阵

    lp_costmatrix = pd.read_excel("Data/LP_costmatrix.xlsx")
    lp_costmatrix = np.array(lp_costmatrix)
    lh_costmatrix = pd.read_excel("Data/LH_costmatrix.xlsx")
    lh_costmatrix = np.array(lh_costmatrix)
    return lp_costmatrix, lh_costmatrix


def init_route(class_l):  # 生成初始路径（随机产生）
    initroute = class_l[:]
    np.random.shuffle(initroute)
    return initroute


def generate_realroute(route):
    current_capacity = 0
    real_route = np.insert(route, 0, 0)
    flag = 1
    # zeroindex = []
    for i in range(0, Node_num):
        current_capacity = current_capacity + Data[route[i]][2]
        if current_capacity > Max_capacity:
            # zeroindex.append(i)
            real_route = np.insert(real_route, i+flag, 0)
            flag = flag + 1
            current_capacity = Data[route[i]][2]
    real_route = np.append(real_route, 0)
    return real_route


def cal_routecost(route):  # 计算传入路径的总代价
    # 没有加入重量限制
    # route_cost = 0
    # for i in range(0, Node_num-1):
    #     route_cost = route_cost + Cost_matrix[route[i]][route[i+1]]
    # return route_cost
    real_route = generate_realroute(route)
    route_cost = 0

    zero_index = np.where(real_route[:] == 0)[0]
    route_num = np.shape(zero_index)[0] - 1
    # sun_cost = 0

    # 循环计算每个小路径的
    for i in range(0, route_num):
        x1 = zero_index[i]+1
        x2 = zero_index[i+1]
        route_list = real_route[x1:x2]
        # route_list = np.array(route_list)
        route_length = np.size(route_list)

        for i in range(0, route_length-1):
            route_cost = route_cost + \
                Cost_matrix[real_route[i]][real_route[i+1]]

        front = int(route_list[0])
        behind = int(route_list[route_length-1])
        route_cost = route_cost + \
            LH_Costmatrix[front][Depot1] + \
            LH_Costmatrix[behind][Depot2]

    return route_cost


def get_neighbours():  # 获取邻域路径(随机交换俩)
    global Neighbour_route

    # # 邻域矩阵中的路径可重复：
    # init_exchange = np.random.randint(0, Node_num, (1, 2))
    # x1 = init_exchange[0][0]
    # x2 = init_exchange[0][1]
    # temp_route = Current_route[:]
    # temp_route[x1], temp_route[x2] = temp_route[x2], temp_route[x1]
    # tempcost = cal_routecost(temp_route)
    # Neighbour_route = [temp_route, tempcost]

    # 每个邻域矩阵生成一个随机列进一步提升前期收敛速度
    init_route = Class_L[:]
    
    np.random.shuffle(init_route)
    while is_inTabulist(init_route):
        np.random.shuffle(init_route)

    initcost = cal_routecost(init_route)
    Neighbour_route = [init_route, initcost]

    exchange_matrix = np.random.randint(0, Node_num, (Neighbour_num, 2))

    for i in range(0, Neighbour_num):
        # Neighbour_route 内保存着新的邻域路线和代价（从1开始，0 为列标志）
        x1 = exchange_matrix[i][0]
        x2 = exchange_matrix[i][1]
        temp_route = Current_route[:]
        temp_route[x1], temp_route[x2] = temp_route[x2], temp_route[x1]


        while is_inTabulist(temp_route):

            # 当前路径在禁忌表中的话需要重新生成
            new_exchange = np.random.randint(0, Node_num, (1, 2))
            x1 = new_exchange[0][0]
            x2 = new_exchange[0][1]
            temp_route = Current_route[:]
            temp_route[x1], temp_route[x2] = temp_route[x2], temp_route[x1]
        # 此处可以优化，不用计算所有长度，只需要考虑变化值
        temp_cost = cal_routecost(temp_route)
        new_row = [temp_route, temp_cost]
        Neighbour_route = np.row_stack((Neighbour_route, new_row))


def is_inTabulist(route):  # 判断路径是否在禁忌表中
    for ele in Tabu_table:
        if ele[0] == route:
            return True
    return False


def update_Tabulist(route, cost):  # 更新禁忌表
    global Tabu_table

# #每次选取代价最大的去掉
#     tempcost = cal_routecost(route)
#     Max_index = np.where(Tabu_table[:, 1] == np.max(Tabu_table[:, 1]))[0][0]
#     Tabu_table[Max_index][0] = route
#     Tabu_table[Max_index][1] = tempcost

# 按迭代次数更新禁忌表
    Tabu_table = np.delete(Tabu_table, 0, 0)[:]
    new_row = [route, cost]
    Tabu_table = np.row_stack((Tabu_table, new_row))




# 主函数，启动禁忌搜索
def TS_search(class_l, depot1, depot2, Maxcapacity):
    global Current_route
    global Best_cost
    global Best_route
    
    init(class_l, depot1, depot2 , Maxcapacity)

    current_iternum = 0
    while current_iternum < Max_iternum:
        get_neighbours()
        current_mincost = np.min(Neighbour_route[:, 1])
        Min_index = np.where(Neighbour_route[:, 1] == current_mincost)[0]
        current_minroute = Neighbour_route[Min_index[0], 0]
        update_Tabulist(current_minroute, current_mincost)

        Current_route = current_minroute[:]
        if current_mincost < Best_cost:
            print "IterNum:", current_iternum+1, current_mincost
            Best_cost = current_mincost
            Best_route = current_minroute[:]

        current_iternum = current_iternum + 1

    Best_realroute = generate_realroute(Best_route)
    print "Best:" , Best_cost , Best_realroute
    return Best_realroute


# class_l = [15,16,17,18,19,20,21]
# depot1 = 26
# depot2 = 30
# UAV_capacity = 20
# temp_route = TS_search(class_l, depot1, depot2, UAV_capacity)
