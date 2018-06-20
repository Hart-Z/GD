# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
"""
显示无人机路径
"""
def show_route():
    with open("Data/UAV_Routes.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        # 这里不需要readlines
        routes = []
        for line in reader:
            if line != []:
                routes.append(line)
    routes = [map(eval, ele) for ele in routes]

    routes_len = np.shape(routes)[0]
    for i in range(0,routes_len) :
        # Best_real_route = np.array(Best_real_route)
        zero_index = np.where(np.array(routes[i][:]) == 0)[0]
        route_num = np.shape(zero_index)[0] - 1


        for j in range(0, route_num):
            x1 = zero_index[j]+1
            x2 = zero_index[j+1]
            route_list = routes[i][x1:x2]
            # route_list = np.array(route_list)

            x_show = []
            y_show = []
            x_show.append(HP_data[int(Class_type[i][1])][0])
            y_show.append(HP_data[int(Class_type[i][1])][1])

            for ele in route_list:
                x_show.append(Data[ele][0])
                y_show.append(Data[ele][1])

            x_show.append(HP_data[int(Class_type[i][2])][0])
            y_show.append(HP_data[int(Class_type[i][2])][1])

            # plt.plot(Data[:, 0], Data[:, 1], marker='.', linestyle='', color=color[i])
            plt.plot(x_show, y_show, marker='.', linewidth=2.0)
    
    x_depot = []
    y_depot = []    
    for ele in Class_type :
        x_depot.append(HP_data[int(ele[1])][0])
        y_depot.append(HP_data[int(ele[1])][1])
        x_depot.append(HP_data[int(ele[2])][0])
        y_depot.append(HP_data[int(ele[2])][1])

    plt.plot(x_depot, y_depot, marker='x', linestyle='')
    plt.show()

Data = np.array(pd.read_excel("Data/LP.xlsx"))
HP_data = np.array(pd.read_excel("Data/HP_new.xlsx"))
Class_type = np.array(pd.read_csv("Data/Classtype.csv"))
show_route()