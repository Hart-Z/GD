# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
from UAV_Tabu import TS_search

"""
>轻件点处理（起飞点着陆点选取，轻重件点转换)
    >先判断当前等价重件点前后的两个重件点与当前等价重件点的距离是否在规定距离的一半内
        >符合要求【2】 ： 一直往两边延伸直到最远满足条件的点 ， 设置两端的重件点为起飞点和着陆点【2】
            >点少于车载无人机数量【20】：每个点直接进行单无人机进行配送
            >点大于车载无人机数量【21】：运行局部的CVRP算法得出解
        
        >不符合要求 ： 
            >两个都不符合【0】：
                >点少 【00】：
                    直飞当前等价重件点进行单点环路配送（<=无人机数量 + 1）
                >点多 【01】：
                    选取两个轻件点使前后路径代价最小（遍历）生成等价重件点，置为起飞着陆点加入车的路径中
                    >剩余点少：单飞
                    >剩余点多：CVRP             
            
            >就一个点不符合【1】：
                >当前等价重件点和符合的重件点往外扩展的最远重件点作为起飞着陆点
                    >点少【10】：单个配送
                    >点多【11】：CVRP
                
       

    >无人机路径规划
        *类似单程的CVRP问题求解
        *大于车载无人机数量的路径从最短的开始由无人机在起飞点环形运输，

"""

"""
重复重件点路径处理解决方案：
    对routes的改动会让后续的操作不知道目前操作的是老重件点还是新重件点，
    所以在添加新重件点的时候人为先额外加上100以便检索、区分
"""
# 初始化工作，读取数据
def init():
    lp= np.array(pd.read_excel('Data/LP.xlsx'))

    hp_raw = np.array(pd.read_excel('Data/HP_raw.xlsx'))

    hp = np.array(pd.read_excel('Data/HP.xlsx'))

    lh_costmatrix = np.array(pd.read_excel('Data/LH_costmatrix.xlsx'))

    # lh_costmatrix_raw = np.array(pd.read_excel('Data/LH_costmatrix_raw.xlsx'))

    lp_costmatrix = np.array(pd.read_excel('Data/LP_costmatrix.xlsx'))

    hp_costmatrix = np.array(pd.read_excel('Data/HP_costmatrix.xlsx'))

    with open("Data/Routes.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        # 这里不需要readlines
        routes = []
        for line in reader:
            if line != []:
                routes.append(line)
    routes = [map(eval, ele) for ele in routes]

    class_type = np.array(pd.read_csv('Data/Classtype.csv'))

    return lp, hp_raw, hp, lp_costmatrix, hp_costmatrix,\
        lh_costmatrix , class_type, routes


# 对于类i，提取所有包含的点（重件点和轻件点）
def PickP_class(i, lp, hp):
    class_l = np.where(lp[:, 4] == i)[0].tolist()
    class_h = np.where(hp[:, 3] == i)[0].tolist()
    return class_l, class_h


def Find_inRoutes(routes, hp_index):
    routes_num = len(routes)
    for i in range(0, routes_num):
        points_num = len(routes[i])
        for j in range(0, points_num):
            if routes[i][j] == hp_index:
                return i, j
    return -1, -1


def Find_inHP(classnum , hp):
    hp_len = np.shape(hp)[0]
    for i in range(0,hp_len) :
        if hp[i][4] == 1 and hp[i][3] == classnum:
            return i
    return -1


def hp_isinclass(hp_num, class_h):
    for ele in class_h:
        if hp_num == ele:
            return True
    else:
        return False


def CVRP_L(drone_num,UAV_capacity,classtype, routes, lp, hp, hp_raw, lh_costmatrix , lp_costmatrix, hp_costmatrix) :
    
    class_num = np.shape(classtype)[0]
    hp_new = hp_raw
    uav_routes = [[-1]]
    
    def updateLH_costmatrix(lp, hp):
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
        writer = pd.ExcelWriter('Data/LH_costmatrix.xlsx')

        output.to_excel(writer, 'Sheet1')
        writer.close()

    def cal_ugvrouteinclass(front_hp , behind_hp , class_l) : 
       
        def cal_distance(cord1, cord2):
            xd = cord1[0]-cord2[0]
            yd = cord1[1]-cord2[1]
            distance = np.sqrt(np.square(xd)+np.square(yd))
            return distance 
        
        hp_len = np.shape(hp)[0]
        if front_hp >= hp_len :
            front_hp = front_hp - 100
            x_f , y_f = hp_new[front_hp][0] , hp_new[front_hp][1]
        else :
            x_f , y_f = hp[front_hp][0] , hp[front_hp][1]
        if behind_hp >= hp_len :
            behind_hp = behind_hp - 100
            x_b , y_b = hp_new[behind_hp][0] , hp_new[behind_hp][1]
        else :
            x_b , y_b = hp[behind_hp][0] , hp[behind_hp][1]
        cord_f = [x_f , y_f ] 
        cord_b = [x_b , y_b ]
        classl_len = len(class_l)
        
        min_cost = 99999999
        depot1 = -1
        depot2 = -1

        for m in range(0, classl_len):
            for n in range(0, classl_len):
                if m != n:
                    lp1_index = class_l[m]
                    lp2_index = class_l[n]
                    cord_l1 = [ lp[lp1_index][0] , lp[lp1_index][1] ]
                    cord_l2 = [ lp[lp2_index][0] , lp[lp2_index][1] ]
                    tempcost1 = cal_distance(cord_f , cord_l1)
                    tempcost2 = cal_distance(cord_l1 , cord_l2)
                    tempcost3 = cal_distance(cord_l2 , cord_b)
                    tempsum = tempcost1 + tempcost2 + tempcost3
                    
                    if tempsum < min_cost :
                        min_cost = tempsum
                        depot1 = lp1_index
                        depot2 = lp2_index
        
        return depot1 , depot2

        

    for i in range(0, class_num):
        depot1 = -1
        depot2 = -1

        class_l, class_h = PickP_class(i, lp, hp_raw)

        hp_index = Find_inHP(i, hp)  # 当前等价重件点在HP表中的位置

        print "class:", i, "等价重件点：", hp_index

        route_index, point_index = Find_inRoutes(routes, hp_index)

        lp_classlen = len(class_l)


        #Type 20 21 00 01 10 11
        Type = -1

        Flag_L = -1
        Flag_R = -1

        # 路径上前一个重件索引
        front_hp = routes[route_index][point_index-1]
        # 路径上后一个重件索引
        behind_hp = routes[route_index][point_index+1]
        
        print "class_l:" , class_l
        print "class_h:" , class_h
        print "等价点：" , hp_index
        print "current_index:" , route_index, point_index
        print "front_hp:" , front_hp , "behind_hp :" , behind_hp
        current_pointindexR = point_index
        current_pointindexL = point_index

        # 路径慢慢往右挪直到不在类内
        while hp_isinclass(routes[route_index][current_pointindexR], class_h) or routes[route_index][current_pointindexR] == hp_index :
            # print "class :", i, "route :", route_index, "current_pointindexR :", routes[route_index][current_pointindexR]
            current_pointindexR = current_pointindexR + 1
            # print "class:",i,"route:" , route_index , "current_pointindexR" , routes[route_index][current_pointindexR]
        current_pointindexR = current_pointindexR - 1

        # 路径慢慢往左挪直到不在类内
        while hp_isinclass(routes[route_index][current_pointindexL], class_h) or routes[route_index][current_pointindexL] == hp_index :
            # print "class :", i, "route :", route_index, "current_pointindexL :", routes[route_index][current_pointindexL]
            current_pointindexL = current_pointindexL - 1
            # print "class:",i,"route:" , route_index , "current_pointindexL" , routes[route_index][current_pointindexL]
        current_pointindexL = current_pointindexL + 1
        
        #最左边的L 最右边的R
        print "L:", routes[route_index][current_pointindexL], "R:", routes[route_index][current_pointindexR]
     

        Flag_L = hp_isinclass(front_hp , class_h)

        Flag_R = hp_isinclass(behind_hp , class_h)
        print "F_L :", Flag_L , "F_R : " ,Flag_R

        #第一种情况 ， 两头都有类内重件点

        if Flag_L and Flag_R == True :
            depot1 = routes[route_index][current_pointindexL]
            depot2 = routes[route_index][current_pointindexR]

            if lp_classlen <= drone_num :
                Type = "20"
                print "Type:" , Type
                """
                两头重件点确定，中间轻件点点少直飞
                """
                #更新UGV路径
                del(routes[route_index][point_index])
                
                #不需要添加重件点

                #计算该类的UAV路径
                temp_route = [0]
                for ele in class_l :
                    temp_route.append(ele)
                    temp_route.append(0)
                uav_routes.append(temp_route)

            else :
                Type = "21"
                print "Type:" , Type
                """
                两头重件点确定，中间轻件点点多 CVRP
                """

                #生成局部无人机路径，加入无人机路径表中
                temp_route = TS_search(class_l, depot1, depot2, UAV_capacity)
                uav_routes.append(temp_route)

                # #重件表加入新点
                # new_hprow1 = [lp[depot1][0], lp[depot1]
                #               [1], lp[depot1][2], i, 1]
                # hp_new = np.row_stack((hp_raw, new_hprow1))
                # new_hprow2 = [lp[depot2][0], lp[depot2]
                #               [1], lp[depot2][2], i, 1]
                # hp_new = np.row_stack((hp_raw, new_hprow2))

                # 改变存储的Routes


                del(routes[route_index][point_index])

                # current_hpindex = np.shape(hp_new)[0]
                # routes[route_index].insert(
                #     point_index, current_hpindex + 1)  # routes加入n
                # routes[route_index].insert(
                #     point_index, current_hpindex)  # routes加入m
        #第二种情况 ， 两头都没有重件
        elif Flag_L or Flag_R == False :
            if lp_classlen <= drone_num + 1 :
                Type = "30"
                print "Type:" , Type

                """
                两头都没重件点,点少，到等价重件点后直接单项环路配送
                """ 
                #删除轻件点中的等价重件点
                for ele in class_l :
                    if lp[ele][3] == 1 :
                        lpspecial_index = ele
                class_l = np.delete(class_l, np.where(class_l[:] == lpspecial_index), 0)

                class_l = class_l.tolist()
                #计算该类的UAV路径
                temp_route = [0]
                for ele in class_l :
                    temp_route.append(ele)
                    temp_route.append(0)
                uav_routes.append(temp_route)

                #等价重件点加入
                current_hpindex = np.shape(hp_new)[0]
                new_hprow = hp[hp_index][:]
                hp_new = np.row_stack((hp_new, new_hprow))
                updateLH_costmatrix(lp,hp_new)
                
                depot1 = current_hpindex
                depot2 = current_hpindex

                #更新路径中的重件点为hp_new中的索引
                del(routes[route_index][point_index]) #删除等价重件点
                routes[route_index].insert(
                    point_index, current_hpindex+100)  # routes加入n
                
            else :

                """
                两头都没重件点，点多，寻找等价重件点再进行类似第一种情况配送
                """


                # 遍历类内所有轻件点，找出阶段代价最小的的两个点设置成等价重件点
                """
                换用方法解出最短解
                """

                depot1 , depot2 = cal_ugvrouteinclass(front_hp , behind_hp , class_l)
                print "depot1:" , depot1 , "depot2" , depot2
                # for m in range(0, lp_classlen):
                #     for n in range(0, lp_classlen):
                #         if m != n:
                #             lp1_index = class_l[m]
                #             lp2_index = class_l[n]
                #             tempcost = lh_costmatrix_raw[lp1_index][front_hp] + \
                #                 lp_costmatrix[lp1_index][lp2_index] + \
                #                 lh_costmatrix_raw[lp2_index][behind_hp]

                #             if tempcost < mincost:
                #                 mincost = tempcost
                #                 depot1 = lp1_index
                #                 depot2 = lp2_index

                # print "depot1", depot1, "depot2", depot2, "mincost", mincost

                #更新轻件点数据结构
                lp[depot1][3] = 1
                lp[depot2][3] = 1
                class_l = np.delete(class_l, np.where(class_l[:] == depot1), 0)
                class_l = np.delete(class_l, np.where(class_l[:] == depot2), 0)
                class_l = class_l.tolist()
                lp_classlen = len(class_l)

                # 加入新的等价重件点到hp_new
                current_hpindex = np.shape(hp_new)[0]
                new_hprow1 = [lp[depot1][0], lp[depot1]
                                [1], lp[depot1][2], i, 1]
                hp_new = np.row_stack((hp_new, new_hprow1))
                new_hprow2 = [lp[depot2][0], lp[depot2]
                                [1], lp[depot2][2], i, 1]
                hp_new = np.row_stack((hp_new, new_hprow2))

                # 改变存储的Routes
                del(routes[route_index][point_index]) #删除等价重件点
                routes[route_index].insert(
                    point_index, current_hpindex + 1 + 100)  # routes加入n
                routes[route_index].insert(
                    point_index, current_hpindex + 100)  # routes加入m

                # 改变Classtype里存储的depot
                depot1 = current_hpindex
                depot2 = current_hpindex + 1
                # print "class:",i,"route:" , route_index , "depot1" , routes[route_index][current_pointindexR]
                print "D1:", depot1, "D2:" ,depot2

                if lp_classlen <= drone_num :
                    Type = "310"
                    print "Type:" , Type
                    """
                    两头选好等价重件点，但是剩下点少
                    """
                    #计算该类的UAV路径
                    temp_route = [0]
                    for ele in class_l :
                        temp_route.append(ele)
                        temp_route.append(0)
                    uav_routes.append(temp_route)
                
                else : 
                    """
                    否则进行CVRP
                    """
                    Type = "311"
                    print "Type:" , Type
                    updateLH_costmatrix(lp,hp_new)
                    # class_l = class_l.tolist()
                    temp_route = TS_search(class_l, depot1, depot2, UAV_capacity)
                    uav_routes.append(temp_route)

                
        #只有一个符合
        else : 
            depot1 = routes[route_index][current_pointindexL]
            depot2 = routes[route_index][current_pointindexR]

            #删除轻件点中的等价重件点
            for ele in class_l :
                if lp[ele][3] == 1 :
                    lpspecial_index = ele
            class_l = np.delete(class_l, np.where(class_l[:] == lpspecial_index), 0)
            class_l = class_l.tolist()

            if Flag_L == True :
                """
                左边是真实重件点，右边是等价重件点
                """
                #添加等价重件点到hp_new
                current_hpindex = np.shape(hp_new)[0]
                new_hprow = hp[depot2][:]
                hp_new = np.row_stack((hp_new, new_hprow))
                depot2 = current_hpindex
                #路径上的等价重件点更新为hp_new中的索引
                del(routes[route_index][point_index])
                routes[route_index].insert(
                    point_index, current_hpindex+100)
            
            else : 
                """
                右边是真实重件点，左边是等价重件点
                """
                #添加等价重件点到hp_new
                current_hpindex = np.shape(hp_new)[0]
                new_hprow = hp[depot1][:]
                hp_new = np.row_stack((hp_new, new_hprow))
                depot1 = current_hpindex
                
                #路径上的等价重件点更新为hp_new中的索引
                del(routes[route_index][point_index])
                routes[route_index].insert(
                    point_index, current_hpindex+100)

            if lp_classlen <= drone_num : 
                Type = "10"
                print "Type:" , Type
                #计算该类的UAV路径
                temp_route = [0]
                for ele in class_l :
                    temp_route.append(ele)
                    temp_route.append(0)
                uav_routes.append(temp_route)

            else : 
                Type = "11"
                print "Type:" , Type
                """
                两头重件点确定，中间轻件点点多 CVRP
                """

                #生成局部无人机路径，加入无人机路径表中
                updateLH_costmatrix(lp,hp_new)
                temp_route = TS_search(class_l, depot1, depot2, UAV_capacity)
                uav_routes.append(temp_route)

        classtype[i][0] = Type
        classtype[i][1] = depot1
        classtype[i][2] = depot2

        updateLH_costmatrix(lp,hp_new)

    routes_num = len(routes)
    hp_len = np.shape(hp)[0]
    # routes_len = np.shape(routes)[0]

    for i in range(0,routes_num) :
        line = routes[i]
        line_len = np.shape(line)[0]

        for j in range(0,line_len) :
            if routes[i][j] > hp_len :
                routes[i][j] -= 100

    with file("Data/New_routes.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        for i in range(0, routes_num):
            # route_list = np.array(route_list)
            writer.writerow(routes[i])
    
    del(uav_routes[0])
    uav_routes_num = len(uav_routes)

    with file("Data/UAV_routes.csv", "w") as csvfile:
        writer = csv.writer(csvfile)

        for i in range(0, uav_routes_num):
            # route_list = np.array(route_list)
            writer.writerow(uav_routes[i])

    output1 = pd.DataFrame(
    data=hp_new, columns=['x', 'y', 'capacity', 'class', 'type'])
    output2 = pd.DataFrame(data=classtype, columns=[
                           'type', 'depot1', 'depot2'])
    # output3 = pd.DataFrame(data=routes)
    output3 = pd.DataFrame(
        data=lp, columns=['x', 'y', 'capacity', 'type', 'class', 'A_num'])
    writer1 = pd.ExcelWriter('Data/HP_new.xlsx')
    writer2 = pd.ExcelWriter('Data/LP.xlsx')
    # writer4 = pd.ExcelWriter('Data/HP_raw.xlsx')
    output1.to_excel(writer1, 'Sheet1')
    # output2.to_excel(writer2, 'Sheet1')
    # output4.to_excel(writer4, 'Sheet1')
    output2.to_csv('Data/Classtype.csv', index=False)
    output3.to_excel(writer2, 'Sheet1')
    # output3.to_csv('Data/New_routes.csv', index=False)
    writer1.close()
    writer2.close()


   
def Generate_newHPCostmatrix(hp):
    Node_num = np.shape(hp)[0]
    HPnew_costmatrix = np.random.randint(0, 1, (Node_num, Node_num))

    def cal_distance(i, j):
        xd = hp[i][0]-hp[j][0]
        yd = hp[i][1]-hp[j][1]
        distance = np.sqrt(np.square(xd)+np.square(yd))
        return distance

    for i in range(0, Node_num):
        for j in range(0, Node_num):
            HPnew_costmatrix[i][j] = cal_distance(i, j)

    output = pd.DataFrame(data=HPnew_costmatrix)
    # output.to_csv('costmatrix.xlsx', index=False)
    writer = pd.ExcelWriter('Data/HPnew_costmatrix.xlsx')

    output.to_excel(writer, 'Sheet1')
    writer.close()

    return HPnew_costmatrix


def Solver_L(Drone_num , UAV_capacity):

    LP, HP_raw, HP, LP_Costmatrix, HP_Costmatrix,\
        LH_Costmatrix , Classtype, Routes = init()
    # Class_L , Class_H = PickP_class(i,LP,HP)
    CVRP_L(Drone_num, UAV_capacity ,Classtype, Routes, LP, HP, HP_raw,
                LH_Costmatrix , LP_Costmatrix, HP_Costmatrix)
