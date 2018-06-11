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


def cal_UGVcost():
	def cal_UGVroutecost(route):  # 计算传入路径的总代价
	    route_cost = 0
	    route_length = np.size(route)
	    for i in range(0, route_length-1):
	        route_cost = route_cost + HPnew_costmatrix[route[i]][route[i+1]]
	    return route_cost

	with open("Data/New_routes.csv", "r") as csvfile:
		reader = csv.reader(csvfile)
		# 这里不需要readlines
		routes = []
		for line in reader:
			if line != []:
				routes.append(line)

	routes = [map(eval, ele) for ele in routes]
	# routes_len = np.shape(routes)[0]

	UGVcost_sum = 0

	for ele in routes :
	    UGVcost_sum = UGVcost_sum + cal_UGVroutecost(ele)

	print "UGV :" , UGVcost_sum

def cal_UAVcost() :
	def cal_UAVcost_normal(route,Depot1,Depot2):  # 计算传入路径的总代价
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




HP_data = np.array(pd.read_excel("Data/HP_raw.xlsx"))

HP_newdata = np.array(pd.read_excel("Data/HP_new.xlsx"))

LP_costmatrix = np.array(pd.read_excel("Data/LP_costmatrix.xlsx"))

HPnew_costmatrix = Generate_HPnewCostmatrix(HP_newdata)

LH_Costmatrix = np.array(pd.read_excel("Data/LH_costmatrix.xlsx"))

Class_type = np.array(pd.read_csv("Data/Classtype.csv"))


cal_UGVcost()

