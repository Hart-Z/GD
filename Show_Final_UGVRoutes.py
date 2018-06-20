# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv

"""
显示物流车路径
"""
def show_route():
    with open("Data/New_routes.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        # 这里不需要readlines
        routes = []
        for line in reader:
            if line != []:
                routes.append(line)
    routes = [map(eval, ele) for ele in routes]
    

    routes_len = np.shape(routes)[0]

    # for i in range(0,routes_len) :
    #     line = routes[i]
    #     line_len = np.shape(line)[0]

    #     for j in range(0,line_len) :
    #         if routes[i][j] > 200 :
    #             routes[i][j] -= 100

    for i in range(0,routes_len) :
        x_show = []
        y_show = []
        for ele in routes[i] :
            x_show.append(HP_data[int(ele)][0])
            y_show.append(HP_data[int(ele)][1])
        # plt.plot(Data[:, 0], Data[:, 1], marker='.', linestyle='', color=color[i])
        plt.plot(x_show, y_show, marker='o', linewidth=2.0)
    
    plt.show()

HP_data = np.array(pd.read_excel("Data/HP_new.xlsx"))
show_route()