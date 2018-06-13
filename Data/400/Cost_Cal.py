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

	def Find_inRoutes(routes, hp_index):
	    routes_num = len(routes)
	    for i in range(0, routes_num):
	        points_num = len(routes[i])
	        for j in range(0, points_num):
	            if routes[i][j] == hp_index:
	                return i, j
	    return -1, -1

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

	for i in range(0,classnum):
		start = Class_type[i][1]
		end = Class_type[i][2]

		start_r , start_p = Find_inRoutes(routes,start)
		end_r , end_p = Find_inRoutes(routes,end)

		if start_r != end_r :
			print "UGV local wrong"
			break
		elif Class_type[i][0] == 30:
			UGV_inclass = 0
		else:
			UGV_inclass = 0
			for j in range(start_p,end_p):
				UGV_inclass += HPnew_costmatrix[routes[start_r][j]][routes[start_r][j+1]]
		
		UGV_routelen[i] = UGV_inclass


	UGVcost_sum = 0

	for ele in routes :
	    UGVcost_sum = UGVcost_sum + cal_UGVroutecost(ele)

	print "UGV :" , UGVcost_sum
	return UGVcost_sum

def cal_UAVcost() :
	def cal_UAVcost_normal(class_num,route,Depot1,Depot2):  # 计算传入路径的总代价
		# 没有加入重量限制
		# route_cost = 0
		# for i in range(0, Node_num-1):
		#     route_cost = route_cost + Cost_matrix[route[i]][route[i+1]]
		# return route_cost
		route_cost = 0
		route = np.array(route)
		zero_index = np.where(route[:] == 0)[0]
		route_num = np.shape(zero_index)[0] - 1
		max_cost = 0
		# sun_cost = 0

		# 循环计算每个小路径的
		for i in range(0, route_num):
			x1 = zero_index[i]+1
			x2 = zero_index[i+1]
			routecost_l = 0
			route_list = route[x1:x2]
			# route_list = np.array(route_list)
			route_length = np.size(route_list)

			for i in range(0, route_length-1):
				routecost_l = routecost_l + \
					LP_costmatrix[route[i]][route[i+1]]

			front = int(route_list[0])
			behind = int(route_list[route_length-1])
			
			

			routecost_l = routecost_l + \
				LH_Costmatrix[front][Depot1] + \
				LH_Costmatrix[behind][Depot2]

			if routecost_l >= max_cost :
				max_cost = routecost_l

			route_cost +=  routecost_l
			
		UAV_maxlist[class_num] = max_cost
		return route_cost
	
	def cal_UAVcost_special(class_num,route,Depot):
		route_cost = 0
		route = np.array(route)
		zero_index = np.where(route[:] == 0)[0]
		route_num = np.shape(zero_index)[0] - 1
		# sun_cost = 0
		max_cost = 0
		routecost_l = 0
		# 循环计算每个小路径的
		for i in range(0, route_num):
			x1 = zero_index[i]+1
			routecost_l = 2*(LH_Costmatrix[route[x1]][Depot])
			if routecost_l > max_cost:
				max_cost = routecost_l
			route_cost +=  routecost_l

		UAV_maxlist[class_num] = max_cost
		return route_cost

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
	# print routes_len
	UAVcost_sum = 0

	for i in range(0,routes_len):	
		depot1 = int(Class_type[i][1])
		depot2 = int(Class_type[i][2])
		if Class_type[i][0] == 30 :
			UAVcost_sum = UAVcost_sum + cal_UAVcost_special(i,routes[i],depot1)
		# print "current class:",i
		UAVcost_sum = UAVcost_sum + cal_UAVcost_normal(i,routes[i],depot1,depot2)

	print "UAV :" , UAVcost_sum
	return UAVcost_sum



def cal_Timecost(v1,v2):
	Timecost = 0
	UGV_timecost = UGVcost/v1
	UGV_costinclass = UGV_routelen/v1
	UAV_maxinclass = UAV_maxlist/v2
	UGV_inclass_sum = np.sum(UGV_costinclass)
	Timecost = UGV_timecost - UGV_inclass_sum
	for i in range (0,classnum):
		if UAV_maxinclass[i] > UGV_costinclass[i] :
			Timecost += UAV_maxinclass[i]
		else:
			Timecost += UGV_costinclass[i]
	print "Timecost:" , Timecost
	return Timecost

HP_data = np.array(pd.read_excel("Data/HP_raw.xlsx"))

HP_newdata = np.array(pd.read_excel("Data/HP_new.xlsx"))

LP_costmatrix = np.array(pd.read_excel("Data/LP_costmatrix.xlsx"))

HPnew_costmatrix = Generate_HPnewCostmatrix(HP_newdata)

LH_Costmatrix = np.array(pd.read_excel("Data/LH_costmatrix.xlsx"))

Class_type = np.array(pd.read_csv("Data/Classtype.csv"))

classnum = np.shape(Class_type)[0]

UAV_maxlist = np.zeros(classnum)
UGV_routelen = np.zeros(classnum)

UGVcost = cal_UGVcost()
UAVcost = cal_UAVcost()

Total_Timecost = cal_Timecost(1,5)

print  "Total cost : ",UGVcost+UAVcost/5