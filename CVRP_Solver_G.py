# -*- coding:utf-8 -*-

'''
@author 周昊天

初稿 3.11.2018

最后修改 5.8.2018 

'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
import csv
from scipy.special import comb

"""
初始化部分：
    init()
    read_costmatrix()
    init_route()
"""


def init_L(Maxiternum,Maxcapacity):  # 初始化

    global Max_iternum
    # global Neighbour_num
    # global Table_length
    global Max_capacity
    global Current_route
    global Best_route
    global Best_cost
    global Tabu_table

    # 读取并设置参数
    Max_iternum = Maxiternum
    # Neighbour_num = Neighbournum
    # Table_length = Tablelength
    Max_capacity = Maxcapacity

    # # 得到Node_num
    # rawData = pd.read_excel("data_C.xlsx")
    # Data = np.array(rawData)
    # Node_num = Data.shape[0]

    # # 读取代价矩阵（已经事先由generate_costmatrix.py计算出来）
    # Cost_matrix = read_costmatrix()

    # 初始化路径
    initroute = init_route()
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


def init_G(Maxiternum , Maxcapacity):

    global Max_iternum
    # global Neighbour_num
    # global Table_length
    global Max_capacity
    global Current_route
    global Best_route
    global Best_cost
    global Tabu_table

    # 读取并设置参数
    Max_iternum = Maxiternum
    # Neighbour_num = Neighbournum
    # Table_length = Tablelength
    Max_capacity = Maxcapacity

    # 初始化路径
    BestIndex = np.where(Best_G[:, 1] == np.min(Best_G[:, 1]))[0][0]
    initroute = Best_G[BestIndex][0]
    Current_route = initroute[:]
    initcost = Best_G[BestIndex][1]
    # 初始化最优解（一条随机路径）
    Best_route = initroute[:]
    Best_cost = initcost

    # 初始化禁忌表

    init_row = [initroute, initcost]
    Tabu_table = np.array(init_row)
    for i in range(1, Table_length):
        Tabu_table = np.row_stack((Tabu_table, init_row))


def read_costmatrix():  # 读取计算好的代价矩阵

    costmatrix = pd.read_excel("Data\HP_costmatrix.xlsx")
    costmatrix = np.array(costmatrix)
    return costmatrix


def init_route():  # 生成初始路径（随机产生）

    initroute = range(1, Node_num)
    np.random.shuffle(initroute)
    return initroute


def generate_realroute(route):
    current_capacity = 0
    real_route = np.insert(route, 0, 0)
    flag = 1
    # zeroindex = []
    for i in range(0, Node_num-1):
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
    route_length = np.size(real_route)
    for i in range(0, route_length-1):
        route_cost = route_cost + Cost_matrix[real_route[i]][real_route[i+1]]
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
    initroute = range(1, Node_num)
    np.random.shuffle(initroute)
    while is_inTabulist(initroute):
        np.random.shuffle(initroute)
    initcost = cal_routecost(initroute)
    Neighbour_route = [initroute, initcost]

    #0不算在里面所以用的Node_num-1
    exchange_matrix = np.random.randint(0, Node_num-1, (Neighbour_num, 2))

    for i in range(0, Neighbour_num):
        # Neighbour_route 内保存着新的邻域路线和代价（从1开始，0 为列标志）
        x1 = exchange_matrix[i][0]
        x2 = exchange_matrix[i][1]
        temp_route = Current_route[:]
        temp_route[x1], temp_route[x2] = temp_route[x2], temp_route[x1]
        while is_inTabulist(temp_route):
            # 当前路径在禁忌表中的话需要重新生成
            new_exchange = np.random.randint(0, Node_num-1, (1, 2))
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


def update_Tabulist(route):  # 更新禁忌表
    global Tabu_table

# #每次选取代价最大的去掉
#     tempcost = cal_routecost(route)
#     Max_index = np.where(Tabu_table[:, 1] == np.max(Tabu_table[:, 1]))[0][0]
#     Tabu_table[Max_index][0] = route
#     Tabu_table[Max_index][1] = tempcost

# 按迭代次数更新禁忌表
    tempcost = cal_routecost(route)
    Tabu_table = np.delete(Tabu_table, 0, 0)[:]
    new_row = [route, tempcost]
    Tabu_table = np.row_stack((Tabu_table, new_row))


def show_route():
    Best_real_route = generate_realroute(Best_route)
    # Best_real_route = np.array(Best_real_route)
    zero_index = np.where(Best_real_route[:] == 0)[0]
    route_num = np.shape(zero_index)[0] - 1

    with file("Data/Routes.csv", "w") as csvfile:
        writer = csv.writer(csvfile)

        for i in range(0, route_num):
            x1 = zero_index[i]
            x2 = zero_index[i+1]+1
            route_list = Best_real_route[x1:x2]
            # route_list = np.array(route_list)
            writer.writerow(route_list)

            x_show = []
            y_show = []
            for ele in route_list:
                x_show.append(Data[ele][0])
                y_show.append(Data[ele][1])
            # plt.plot(Data[:, 0], Data[:, 1], marker='.', linestyle='', color=color[i])
            plt.plot(x_show, y_show, marker='o', linewidth=2.0)

    plt.plot(Data[0][0], Data[0][1], marker='x', linestyle='', color='red')
    plt.show()


# 主函数，启动禁忌搜索
def TS_L():
    global Current_route
    global Best_cost
    global Best_route
    # global Bestroute_G
    # global Bestcost_G

    current_iternum = 0
    while current_iternum < Max_iternum:
        get_neighbours()
        current_mincost = np.min(Neighbour_route[:, 1])
        Min_index = np.where(Neighbour_route[:, 1] == current_mincost)[0]
        current_minroute = Neighbour_route[Min_index[0], 0]
        update_Tabulist(current_minroute)

        Current_route = current_minroute[:]
        if current_mincost < Best_cost:
            print "IterNum:", current_iternum+1, current_mincost
            Best_cost = current_mincost
            Best_route = current_minroute[:]

        current_iternum = current_iternum + 1


def TS_G(Maxiternum, Maxcapacity, Initnum , Maxiter_L ):
    global Neighbour_num
    global Table_length
    global Best_G
    global Current_route
    global Best_cost
    global Best_route
    global Data
    global Node_num
    global Cost_matrix


    # 读取Data 和 节点数量
    rawData = pd.read_excel("Data\HP.xlsx")
    Data = np.array(rawData)
    Node_num = Data.shape[0]
    Neighbour_num = int(np.sqrt(comb(Node_num,2)))+1
    Table_length = int(np.sqrt(Node_num))+1
    # Maxiter_L = pow(Table_length,2)
    # 读取代价矩阵（已经事先由generate_costmatrix.py计算出来）
    Cost_matrix = read_costmatrix()

    new_row = [[], 0]
    Best_G = new_row[:]

    for i in range(1, Initnum+1):
        Best_G = np.row_stack((Best_G, new_row))

    for i in range(0, Initnum+1):
        init_L(Maxiter_L, Maxcapacity)
        TS_L()
        print "Iter :", i, "Best :", Best_cost, ":", generate_realroute(Best_route)
        Best_G[i][0] = Best_route
        Best_G[i][1] = Best_cost

    init_G(Maxiternum , Maxcapacity)

    TS_L()
    print "Ult Best :", Best_cost, ":", generate_realroute(Best_route)


"""
全局变量清单

"""
Data = []  # 数据
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
Max_capacity = 0
Node_num = 0  # 节点数量，编码长度
Cost_matrix = []  # 代价矩阵
Current_route = []  # 当前路径
Best_route = []  # 最优路径
Current_cost = 0  # 当前路径花费代价
Best_cost = 0  # 最优代价
Tabu_table = []  # 禁忌表
Bestroute_G = []
Bestcost_G = 0
"""
    Tabu_list
            [
                    [route],cost;
            ]

"""

def Solver_G(Maxiternum , Maxcapacity, Initnum, Maxiter_L):
    start = time.clock()
    # 全局迭代次数，邻域大小，禁忌长度，车辆容量，局部解产生个数，局部迭代次数
    TS_G(Maxiternum , Maxcapacity, Initnum, Maxiter_L)
    end = time.clock()
    print('Running time: %s Seconds' % (end-start))
    show_route()