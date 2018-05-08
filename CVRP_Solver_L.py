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

# 初始化工作，读取数据
def init():
    lp= np.array(pd.read_excel('Data/LP.xlsx'))

    hp_raw = np.array(pd.read_excel('Data/HP_raw.xlsx'))

    hp = np.array(pd.read_excel('Data/HP.xlsx'))

    lh_costmatrix = np.array(pd.read_excel('Data/LH_costmatrix.xlsx'))

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
        lh_costmatrix, class_type, routes


# 对于类i，提取所有包含的点（重件点和轻件点）
def PickP_class(i, lp, hp):
    class_l = np.where(lp[:, 4] == i)[0]
    class_h = np.where(hp[:, 3] == i)[0]
    return class_l, class_h


def Find_inRoutes(routes, hp_index):
    routes_num = len(routes)
    for i in range(0, routes_num):
        points_num = len(routes[i])
        for j in range(0, points_num):
            if routes[i][j] == hp_index:
                return i, j
    return -1, -1


def Find_inHP(classnum, class_h, hp):
    for ele in class_h:
        if hp[ele][4] == 1:
            return ele
    return -1


def hp_isinclass(hp_num, class_h):
    for ele in class_h:
        if hp_num == ele:
            return True
    else:
        return False


def CVRP_L(drone_num,UAV_capacity,classtype, routes, lp, hp, hp_raw, lh_costmatrix, lp_costmatrix, hp_costmatrix) :
    
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

    for i in range(0, class_num):

        depot1 = -1
        depot2 = -1

        class_l, class_h = PickP_class(i, lp, hp)

        hp_index = Find_inHP(i, class_h, hp)  # 当前等价重件点在HP表中的位置

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
    
        current_pointindexR = point_index
        current_pointindexL = point_index

        # 路径慢慢往右挪直到不在类内
        while hp_isinclass(routes[route_index][current_pointindexR], class_h):
            print "class :", i, "route :", route_index, "current_pointindexR :", routes[route_index][current_pointindexR]
            current_pointindexR = current_pointindexR + 1
            # print "class:",i,"route:" , route_index , "current_pointindexR" , routes[route_index][current_pointindexR]
        current_pointindexR = current_pointindexR - 1

        # 路径慢慢往左挪直到不在类内
        while hp_isinclass(routes[route_index][current_pointindexL], class_h):
            print "class :", i, "route :", route_index, "current_pointindexL :", routes[route_index][current_pointindexL]
            current_pointindexL = current_pointindexL - 1
            # print "class:",i,"route:" , route_index , "current_pointindexL" , routes[route_index][current_pointindexL]
        current_pointindexL = current_pointindexL + 1
        
        #最左边的L 最右边的R
        print "L:", routes[route_index][current_pointindexL], "R:", routes[route_index][current_pointindexR]
     

        Flag_L = hp_isinclass(front_hp , class_h)

        Flag_R = hp_isinclass(behind_hp , class_h)

        #第一种情况 ， 两头都有类内重件点
        if Flag_L and Flag_R == True :
            depot1 = routes[route_index][current_pointindexL]
            depot2 = routes[route_index][current_pointindexR]

            if lp_classlen <= drone_num :
                Type = "20"
                """
                两头重件点确定，中间轻件点点少直飞
                """
                temp_route = [0]
                for ele in class_l :
                    temp_route.append(ele)
                    temp_route.append(0)
                uav_routes.append(temp_route)

            else :
                Type = "21"
                """
                两头重件点确定，中间轻件点点多 CVRP
                """
                temp_route = TS_search(class_l, depot1, depot2, UAV_capacity)
                

        #第二种情况 ， 两头都没有重件
        elif Flag_L or Flag_R == False :
            if lp_classlen <= drone_num :
                Type = "00"
                depot1 = hp_index
                """
                两头都没重件点,点少，到等价重件点后直接单项环路配送
                """
            else :
                Type = "01"
                """
                两头都没重件点，点多，寻找等价重件点再进行类似第一种情况配送
                """
                
        #只有一个符合
        else :
            depot1 = routes[route_index][current_pointindexL]
            depot2 = routes[route_index][current_pointindexR]
            if Flag_L == True :
                new_hprow = hp[depot2][:]
                hp_new = np.row_stack((hp_new, new_hprow))
                """
                
                """

            
        

        classtype[i][0] = Type
        classtype[i][1] = depot1
        classtype[i][2] = depot2

        updateLH_costmatrix(lp,hp_new)
    




   
        #无重件点的情况
        # if current_pointindexL == point_index and current_pointindexR == point_index:
        
        # elif 





# 为每个类内重新选择两个等价重件点使代价最小，另外更新路径
def Choose_depot(classtype, routes, lp, hp, hp_raw, lh_costmatrix, lp_costmatrix, hp_costmatrix):

    class_num = np.shape(classtype)[0]

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

    for i in range(0, class_num):

        class_l, class_h = PickP_class(i, lp, hp)

        hp_index = Find_inHP(i, class_h, hp)  # 当前等价重件点在HP表中的位置

        print "class:", i, "等价重件点：", hp_index

        route_index, point_index = Find_inRoutes(routes, hp_index)

        lp_classlen = len(class_l)

        # 路径上前一个重件索引
        front_hp = routes[route_index][point_index-1]
        # 路径上后一个重件索引
        behind_hp = routes[route_index][point_index+1]

        # 无重件点：选出两等价重件点使无人车在新的路径代价最短
        if classtype[i][0] == 0:
            mincost = 99999999
            depot1 = -1
            depot2 = -1

            # 如果类内只有一个轻件点，直接让前后重件点作为起飞停泊点
            if lp_classlen == 1:
                del(routes[route_index][point_index])
                print class_l[0]
                print front_hp
                print behind_hp
                classtype[i][1] = front_hp
                classtype[i][2] = behind_hp
                # 加入新的等价重件点到hp_raw
                # new_hprow = [lp[depot1][0], lp[depot1][1], lp[depot1][2], i, 1]
                # hp_raw = np.row_stack((hp_raw, new_hprow))
                # class_l = np.delete(class_l,)
                # routes[route_index][point_index] = current_hpindex

            else:
                # 遍历类内所有轻件点，找出阶段代价最小的的两个点设置成等价重件点
                for m in range(0, lp_classlen):
                    for n in range(0, lp_classlen):
                        if m != n:
                            lp1_index = class_l[m]
                            lp2_index = class_l[n]
                            tempcost = lh_costmatrix[lp1_index][front_hp] + \
                                lp_costmatrix[lp1_index][lp2_index] + \
                                lh_costmatrix[lp2_index][behind_hp]

                            if tempcost < mincost:
                                mincost = tempcost
                                depot1 = lp1_index
                                depot2 = lp2_index

                # print "depot1", depot1, "depot2", depot2, "mincost", mincost
                current_hpindex = np.shape(hp_raw)[0]

                lp[depot1][3] = 1
                lp[depot2][3] = 1
                class_l = np.delete(class_l, np.where(class_l[:] == depot1), 0)
                class_l = np.delete(class_l, np.where(class_l[:] == depot2), 0)
                # 加入新的等价重件点到hp_raw
                new_hprow1 = [lp[depot1][0], lp[depot1]
                              [1], lp[depot1][2], i, 1]
                hp_raw = np.row_stack((hp_raw, new_hprow1))
                new_hprow2 = [lp[depot2][0], lp[depot2]
                              [1], lp[depot2][2], i, 1]
                hp_raw = np.row_stack((hp_raw, new_hprow2))

                # 改变存储的Routes
                del(routes[route_index][point_index])
                routes[route_index].insert(
                    point_index, current_hpindex + 1)  # routes加入n
                routes[route_index].insert(
                    point_index, current_hpindex)  # routes加入m

                # 改变Classtype里存储的depot
                classtype[i][1] = current_hpindex
                classtype[i][2] = current_hpindex + 1

                # depot1 = int(classtype[i][1])
                # depot2 = int(classtype[i][2])
                # TS_search(class_l,depot1,depot2,100,2,2,30)
            # print "class:",i,"route:" , route_index , "depot1" , routes[route_index][current_pointindexR]
            print "L:", classtype[i][1], "R:" ,classtype[i][2]

        # 一个重件点，再找出一个轻件点设置成等价重件点使阶段路径代价最小
        elif classtype[i][0] == 1:
            mincost = 9999999
            depot = -1
            hp_inclass = class_h[0]

            for m in range(0, lp_classlen):
                lp_index = class_l[m]
                tempcost1 = lh_costmatrix[lp_index][front_hp] +\
                    lh_costmatrix[lp_index][hp_inclass] + \
                    hp_costmatrix[hp_inclass][behind_hp]
                tempcost2 = hp_costmatrix[front_hp][hp_inclass] + \
                    lh_costmatrix[lp_index][hp_inclass] + \
                    lh_costmatrix[lp_index][behind_hp]
                flag = -1  # 0 为轻在前 ，1 为轻在后

                if tempcost1 > tempcost2:
                    if tempcost2 < mincost:
                        mincost = tempcost2
                        # depot1 = hp_inclass
                        depot = lp_index
                        flag = 1

                else:
                    if tempcost1 < mincost:
                        mincost = tempcost1
                        depot = lp_index
                        # depot2 = hp_inclass
                        flag = 0

            current_hpindex = np.shape(hp_raw)[0]

            lp[depot][3] = 1
            class_l = np.delete(class_l, np.where(class_l[:] == depot), 0)

            # 将新生成的重件点加入hp_raw
            new_hprow = [lp[depot][0], lp[depot][1], lp[depot][2], i, 1]
            hp_raw = np.row_stack((hp_raw, new_hprow))

            # 更新路径表

            # del(routes[route_index][point_index])

            """
            这里需要加上搜索那一个重件点然后再判断往前加还是往后加
            问题：该重件点可能不在类内路径上
                解决方案：
                    1、照常规划
                        >如果在路径上--照常
                        >如果不在，加入当前等价点所在路径，删掉原重件点
                    2、开始阶段就将重件点归为一类（采用）
                        
            
            """
            if flag == 0:
                routes[route_index].insert(
                    point_index, current_hpindex)  # 等价重件点前加入选出的轻件点

                classtype[i][1] = current_hpindex
                classtype[i][2] = hp_inclass

            else:
                routes[route_index].insert(
                    point_index+1, current_hpindex)  # 等价重件点后加入选出的轻件点

                classtype[i][1] = hp_inclass
                classtype[i][2] = current_hpindex
            # routes[route_index].insert(point_index,current_hpindex + 1) #routes加入n
            # routes[route_index].insert(point_index,current_hpindex) #routes加入m

            # depot1 = int(classtype[i][1])
            # depot2 = int(classtype[i][2])

        else:

            # classtype(0)==2 大于两个点的情况
            #     如果除了当前的标记重件点另外的点不在路径上执行上面的单点情况
            #     如果有在路径上的就直接取重件点首末作为无人机中转站

            # current_routeindex = route_index
            current_pointindexR = point_index
            current_pointindexL = point_index

            # 路径慢慢往右挪直到不在类内
            while hp_isinclass(routes[route_index][current_pointindexR], class_h):
                print "class:", i, "route:", route_index, "current_pointindexR", routes[route_index][current_pointindexR]
                current_pointindexR = current_pointindexR + 1
                # print "class:",i,"route:" , route_index , "current_pointindexR" , routes[route_index][current_pointindexR]
            current_pointindexR = current_pointindexR - 1

            # 路径慢慢往左挪直到不在类内
            while hp_isinclass(routes[route_index][current_pointindexL], class_h):
                print "class:", i, "route:", route_index, "current_pointindexL", routes[route_index][current_pointindexL]
                current_pointindexL = current_pointindexL - 1
                # print "class:",i,"route:" , route_index , "current_pointindexL" , routes[route_index][current_pointindexL]
            current_pointindexL = current_pointindexL + 1

            print "L:", routes[route_index][current_pointindexL], "R:", routes[route_index][current_pointindexR]
            if current_pointindexL == point_index and current_pointindexR == point_index:
                # print "惨了，不是同一条路径"
                """
                重复上面的单重件部分
                """
                mincost = 9999999
                depot = -1
                hp_inclass = hp_index

                for m in range(0, lp_classlen):
                    lp_index = class_l[m]
                    tempcost1 = lh_costmatrix[lp_index][front_hp] +\
                        lh_costmatrix[lp_index][hp_inclass] + \
                        hp_costmatrix[hp_inclass][behind_hp]
                    tempcost2 = hp_costmatrix[front_hp][hp_inclass] + \
                        lh_costmatrix[lp_index][hp_inclass] + \
                        lh_costmatrix[lp_index][behind_hp]
                    flag = -1  # 0 为轻在前 ，1 为轻在后

                    if tempcost1 > tempcost2:
                        if tempcost2 < mincost:
                            mincost = tempcost2
                            # depot1 = hp_inclass
                            depot = lp_index
                            flag = 1

                    else:
                        if tempcost1 < mincost:
                            mincost = tempcost1
                            depot = lp_index
                            # depot2 = hp_inclass
                            flag = 0

                lp[depot][3] = 1
                class_l = np.delete(class_l, np.where(class_l[:] == depot), 0)

                current_hpindex = np.shape(hp_raw)[0]
                # 将新生成的重件点加入hp_raw
                new_hprow = [lp[depot][0], lp[depot][1], lp[depot][2], i, 1]
                hp_raw = np.row_stack((hp_raw, new_hprow))

                # 更新路径表

                # del(routes[route_index][point_index])

                """
                这里需要加上搜索那一个重件点然后再判断往前加还是往后加
                问题：该重件点可能不在类内路径上
                    解决方案：
                        1、照常规划
                            >如果在路径上--照常
                            >如果不在，加入当前等价点所在路径，删掉原重件点
                        2、开始阶段就将重件点归为一类（采用）
                            
                
                """
                if flag == 0:
                    routes[route_index].insert(
                        point_index, current_hpindex)  # 等价重件点前加入选出的轻件点

                    classtype[i][1] = current_hpindex
                    classtype[i][2] = hp_inclass

                else:
                    routes[route_index].insert(
                        point_index+1, current_hpindex)  # 等价重件点后加入选出的轻件点

                    classtype[i][1] = hp_inclass
                    classtype[i][2] = current_hpindex

            else:
                classtype[i][1] = routes[route_index][current_pointindexL]
                classtype[i][2] = routes[route_index][current_pointindexR]

            # depot1 = int(classtype[i][1])
            # depot2 = int(classtype[i][2])
            # TS_search(class_l,depot1,depot2,100,2,2,30)

    Generate_newHPCostmatrix(hp_raw)

    output1 = pd.DataFrame(
        data=hp_raw, columns=['x', 'y', 'capacity', 'class', 'type'])
    output2 = pd.DataFrame(data=classtype, columns=[
                           'type', 'depot1', 'depot2'])
    # output3 = pd.DataFrame(data=routes)
    output3 = pd.DataFrame(
        data=lp, columns=['x', 'y', 'capacity', 'type', 'class', 'A_num'])
    writer1 = pd.ExcelWriter('Data/HP_raw.xlsx')
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
    # writer2.close()
    # writer4.close()
    routes_num = len(routes)

    with file("Data/New_routes.csv", "w") as csvfile:
        writer = csv.writer(csvfile)

        for i in range(0, routes_num):
            # route_list = np.array(route_list)
            writer.writerow(routes[i])

    updateLH_costmatrix(lp, hp_raw)
    print routes
    print classtype


    # 有一个：选出一个等价重件点，使...最短

    # 有多个：如果存在连续的话选连续线段首末点作为停泊点，如果没连续的就选代价最短的回到一个点的问题解决

# def UAV_route_plan():
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
        LH_Costmatrix, Classtype, Routes = init()
    # Class_L , Class_H = PickP_class(i,LP,HP)
    CVRP_L(Drone_num, UAV_capacity ,Classtype, Routes, LP, HP, HP_raw,
                LH_Costmatrix, LP_Costmatrix, HP_Costmatrix)

