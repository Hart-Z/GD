# -*- coding:utf-8 -*-
import numpy as np

import matplotlib.pyplot as plt
import pandas as pd
import time
import csv

def Generate_HPnewCostmatrix(hp):
    Node_num = np.shape(hp)[0]
    HP_costmatrix = np.zeros((Node_num, Node_num))

    def cal_distance(i, j):
        xd = hp[i][0]-hp[j][0]
        yd = hp[i][1]-hp[j][1]
        distance = np.sqrt(np.square(xd)+np.square(yd))
        return distance

    for i in range(0, Node_num):
        for j in range(0, Node_num):
            HP_costmatrix[i][j] = cal_distance(i, j)

    output = pd.DataFrame(data=HP_costmatrix)
    # output.to_csv('costmatrix.xlsx', index=False)
    writer = pd.ExcelWriter('Data/HP_newcostmatrix.xlsx')

    output.to_excel(writer, 'Sheet1')
    writer.close()

    return HP_costmatrix


def cal_UGVcost(route):  # 计算传入路径的总代价
    
    route_cost = 0
    route_length = np.size(route)
    for i in range(0, route_length-1):
        route_cost = route_cost + HPnew_costmatrix[route[i]][route[i+1]]
    return route_cost

def cal_Dronecost(route,Depot1,Depot2):  # 计算传入路径的总代价
    # 没有加入重量限制
    # route_cost = 0
    # for i in range(0, Node_num-1):
    #     route_cost = route_cost + Cost_matrix[route[i]][route[i+1]]
    # return route_cost
    route_cost = 0
    route = np.array(route)
    zero_index = np.where(route[:] == 0)[0]
    route_num = np.shape(zero_index)[0] - 1
    # sun_cost = 0

    # 循环计算每个小路径的
    for i in range(0, route_num):
        x1 = zero_index[i]+1
        x2 = zero_index[i+1]
        route_list = route[x1:x2]
        # route_list = np.array(route_list)
        route_length = np.size(route_list)

        for i in range(0, route_length-1):
            route_cost = route_cost + \
                LP_costmatrix[route[i]][route[i+1]]

        front = int(route_list[0])
        behind = int(route_list[route_length-1])
        route_cost = route_cost + \
            LH_Costmatrix[front][Depot1] + \
            LH_Costmatrix[behind][Depot2]

    return route_cost




def cal_Time(UAVcost , routes , v1 ,v2):
    
    time_sum = UAVcost/v1

    def longest_inclass(route,Depot1,Depot2):
        maxcost = 0

        route = np.array(route)
        zero_index = np.where(route[:] == 0)[0]
        route_num = np.shape(zero_index)[0] - 1
        # sun_cost = 0

        # 循环计算每个小路径的
        for i in range(0, route_num):
            tempcost = 0
            x1 = zero_index[i]+1
            x2 = zero_index[i+1]
            route_list = route[x1:x2]
            # route_list = np.array(route_list)
            route_length = np.size(route_list)

            for i in range(0, route_length-1):
                tempcost = tempcost + \
                    LP_costmatrix[route[i]][route[i+1]]

            front = int(route_list[0])
            behind = int(route_list[route_length-1])
            tempcost = tempcost + \
                LH_Costmatrix[front][Depot1] + \
                LH_Costmatrix[behind][Depot2]
            if tempcost > maxcost :
                maxcost = tempcost
        return maxcost

    # def cal_routecostinclass(depot1 , depot2):
    #     routelen = np.shape(routes[0])[0]
    #     for i in range(0,routelen):
    #         if routes[0][i] == 45:
    #             index_1 = i
    #         if routes[0][i] == 73:
    #             index_2 = i
    #     if index_1 < index_2 :
            

    #     print index_1 , index_2

    Class_num = np.shape(Class_type)[0]
    for i in range(0,Class_num) :
        depot1 = int(Class_type[i][1])
        depot2 = int(Class_type[i][2])
        #计算类内无人车路径
        maxcost_inclass = longest_inclass(routes[i],depot1,depot2)
        UAVcost_inclass = HPnew_costmatrix[depot1][depot2]
        if maxcost_inclass/v2 > UAVcost_inclass/v1 :
            time_sum += maxcost_inclass/v2 - UAVcost_inclass/v1
    return time_sum

# def Generate_newHPCostmatrix(hp):
#     Node_num = np.shape(hp)[0]
#     HPnew_costmatrix = np.random.randint(0, 1, (Node_num, Node_num))

#     def cal_distance(i, j):
#         xd = hp[i][0]-hp[j][0]
#         yd = hp[i][1]-hp[j][1]
#         distance = np.sqrt(np.square(xd)+np.square(yd))
#         return distance

#     for i in range(0, Node_num):
#         for j in range(0, Node_num):
#             HPnew_costmatrix[i][j] = cal_distance(i, j)

#     output = pd.DataFrame(data=HPnew_costmatrix)
#     # output.to_csv('costmatrix.xlsx', index=False)
#     writer = pd.ExcelWriter('Data/HPnew_costmatrix.xlsx')

#     output.to_excel(writer, 'Sheet1')
#     writer.close()

#     return HPnew_costmatrix

HP_data = np.array(pd.read_excel("Data/HP_raw.xlsx"))

HP_newdata = np.array(pd.read_excel("Data/HP_new.xlsx"))

LP_costmatrix = np.array(pd.read_excel("Data/LP_costmatrix.xlsx"))

HPnew_costmatrix = Generate_HPnewCostmatrix(HP_newdata)

LH_Costmatrix = np.array(pd.read_excel("Data/LH_costmatrix.xlsx"))

Class_type = np.array(pd.read_csv("Data/Classtype.csv"))



with open("Data/New_routes.csv", "r") as csvfile:
    reader = csv.reader(csvfile)
    # 这里不需要readlines
    routes = []
    for line in reader:
        if line != []:
            routes.append(line)
routes = [map(eval, ele) for ele in routes]
routes_len = np.shape(routes)[0]

UAVcost_sum = 0

for ele in routes :
    UAVcost_sum = UAVcost_sum + cal_UGVcost(ele)

print "UAV :" , UAVcost_sum

#无人机计算
with open("Data/UAV_Routes.csv", "r") as csvfile:
    reader = csv.reader(csvfile)
    # 这里不需要readlines
    routes = []
    for line in reader:
        if line != []:
            routes.append(line)
routes = [map(eval, ele) for ele in routes]
routes_len = np.shape(routes)[0]
Dronecost_sum = 0

for i in range(0,routes_len):
    depot1 = int(Class_type[i][1])
    depot2 = int(Class_type[i][2])
    Dronecost_sum = Dronecost_sum + cal_Dronecost(routes[i],depot1,depot2)

print "Drone :" , Dronecost_sum

total_time = cal_Time(UAVcost_sum , routes , 1.0 ,2.0)
print "Time :" , total_time
