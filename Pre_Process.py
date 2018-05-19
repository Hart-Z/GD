# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans

"""
Input : Dataset1.xlsx
Output : 
    Classtype.csv 类信息[种类 起飞点 着陆点]
    HP_costmatrix.xlsx
    HP_raw.xlsx
    HP.xlsx
    LP.xlsx
    LH_costmatrix.xlsx
    LP_costmatrix.xlsx

>LP_Process
    >Split_LH           : 剥离轻重件 分别生成轻重件数据表

            原数据：[x , y , capacity]
            处理后：
                轻件点：[x,y,capacity,type(是否为等价重件点 0否 1 是),class(初始都是0),A_num(无人机号 初始-1)]
                重件点：[x,y,capacity,
                        class(在类中为类号，都不在为-1),
                        type(是否为等价重件点0 否 1是)]

    >Generate_Costmatrix：生成可能的几种代价矩阵
    >LP_Cluster         : 所有轻件聚类
    >Generate_Center    : 初步处理轻件点，生成等价重件点
        Classtype：
            [type , depot1 ,  depot2]
"""

# 分离轻重件，单独生成对应文件并返回LP HP
def Split_LH(depotposition,data,weight):
    LP = [0, 0, 0, 0, 0, 0]
    HP = depotposition

    for ele in data:
        if ele[2] <= weight and ele[2] > 0:
            new_LProw = np.append(ele, [0, 0, -1])
            LP = np.row_stack((LP, new_LProw))
        elif ele[2] > weight:
            new_HProw = np.append(ele, [-1, 0])
            HP = np.row_stack((HP, new_HProw))

    LP = np.delete(LP, 0, 0)
    # HP = np.delete(HP, 0, 0)

    output1 = pd.DataFrame(
        data=LP, columns=['x', 'y', 'capacity', 'type', 'class', 'A_num'])
    output2 = pd.DataFrame(
        data=HP, columns=['x', 'y', 'capacity', 'class', 'V_num'])
    writer1 = pd.ExcelWriter('Data/LP.xlsx')
    writer2 = pd.ExcelWriter('Data/HP.xlsx')
    # writer3 = pd.ExcelWriter('Data/HP_raw.xlsx')
    output1.to_excel(writer1, 'Sheet1')
    output2.to_excel(writer2, 'Sheet1')
    # output2.to_excel(writer3, 'Sheet1')
    writer1.close()
    writer2.close()
    # writer3.close()

    return LP, HP


# 生成后续算法要用到的轻件的代价矩阵
def Generate_LPCostmatrix(lp):
    Node_num = np.shape(lp)[0]
    LP_costmatrix = np.random.randint(0, 1, (Node_num, Node_num))

    def cal_distance(i, j):
        xd = lp[i][0]-lp[j][0]
        yd = lp[i][1]-lp[j][1]
        distance = np.sqrt(np.square(xd)+np.square(yd))
        return distance

    for i in range(0, Node_num):
        for j in range(0, Node_num):
            LP_costmatrix[i][j] = cal_distance(i, j)

    output = pd.DataFrame(data=LP_costmatrix)
    # output.to_csv('costmatrix.xlsx', index=False)
    writer = pd.ExcelWriter('Data/LP_costmatrix.xlsx')

    output.to_excel(writer, 'Sheet1')
    writer.close()

    return LP_costmatrix


#生成重件代价矩阵
def Generate_HPCostmatrix(hp):
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
    writer = pd.ExcelWriter('Data/HP_costmatrix.xlsx')

    output.to_excel(writer, 'Sheet1')
    writer.close()

    return HP_costmatrix

#生成轻重件混合代价矩阵
def Generate_LHCostmatrix(lp, hp):
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

    return LH_costmatrix

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

    return LH_costmatrix


# 轻件聚类最大直径 max_d 最大点数 max_num
def LP_Cluster(lp, lp_c, max_d, max_num, hp):
    INF = 9999

    # Node_num = np.shape(lp)[0]

    def show():
        plt.scatter(lp[:, 0], lp[:, 1], c=lp[:, 4])
        plt.plot(hp[:, 0], hp[:, 1], marker='x', linestyle='', color='red')
        plt.show()

    #判断是否符合聚类要求
    def is_meetreq(class_num):

        for i in range(0, class_num):
            contents = np.where(lp[:, 4] == i)[0]
            contents_len = len(contents)
            Max_len = 0
            for i in range(0, contents_len-1):
                for j in range(i+1, contents_len):
                    x1 = contents[i]
                    x2 = contents[j]
                    if lp_c[x1][x2] > Max_len:
                        Max_len = lp_c[x1][x2]

            contents_len = np.shape(contents)[0]
            if Max_len > max_d or contents_len > max_num:
                return True

        return False

    for i in range(1, INF):
        if is_meetreq(i):
            # print "class_num :", i
            lp[:, 4] = KMeans(n_clusters=i).fit_predict(lp)
        else:
            break

    lp[0][4] = -1
    output = pd.DataFrame(
        data=lp, columns=['x', 'y', 'capacity', 'type', 'class', 'A_num'])
    writer = pd.ExcelWriter('Data/LP.xlsx')
    output.to_excel(writer, 'Sheet1')
    writer.close()
    show()
    return lp

# 每个类生成等价重件点
def Generate_Center(lp, hp, lp_c):

    classnum = int(np.max(lp[:, 4])+1)
    hp_raw_lenth = np.shape(hp)[0]
    Classtype = np.zeros((classnum, 3))

    #判断是否在长方形区域内
    def is_inClass(ele1, boundcord):
        if ele1[0] > boundcord[2] and ele1[0] < boundcord[3] \
                and ele1[1] > boundcord[1] and ele1[1] < boundcord[0]:
            return True
        else:
            return False

    def show():
        plt.scatter(lp[:, 0], lp[:, 1], c=lp[:, 4])
        plt.scatter(hp[:, 0], hp[:, 1], c=hp[:, 3], marker='x')
        plt.show()

    def find_center(lp_class, num, lp_c):
        measure = np.zeros(num)

        for i in range(0, num):
            for j in range(0, num):
                measure[i] = measure[i] + \
                    np.square(lp_c[lp_class[i], lp_class[j]])

        minindex = np.where(measure[:] == np.min(measure[:]))[0][0]

        min_lpindex = lp_class[minindex]

        return min_lpindex

    def cal_classcost(lp_class, lp):
        cost_sum = 0
        for ele in lp_class:
            cost_sum = cost_sum + lp[ele][2]
        return cost_sum

    for i in range(0, classnum):
        # 循环所有class
        contents = np.where(lp[:, 4] == i)[0]
        contents_len = len(contents)
        init_index = contents[0]

        # top bottom left right
        init_cord = [lp[init_index][1], lp[init_index][1],
                     lp[init_index][0], lp[init_index][0]]

        # 循环所有类内点找出边界
        for j in range(1, contents_len):
            if lp[contents[j]][1] > init_cord[0]:
                init_cord[0] = lp[contents[j]][1]

            if lp[contents[j]][1] < init_cord[1]:
                init_cord[1] = lp[contents[j]][1]

            if lp[contents[j]][0] < init_cord[2]:
                init_cord[2] = lp[contents[j]][0]

            if lp[contents[j]][0] > init_cord[3]:
                init_cord[3] = lp[contents[j]][0]

        # 判断类内有无重件点，有就赋值，没有需要创建新等价重件点
        hp[0][3] = -1
        HP_num = np.shape(hp)[0]
        hp_inclass_num = 0
        for m in range(1, HP_num):
            if is_inClass(hp[m], init_cord):
                hp_inclass_num = hp_inclass_num + 1
                hp[m][3] = i
                # tempx = hp[m][0]
                # tempy = hp[m][1]
                tempindex = m

        center_index = find_center(contents, contents_len, lp_c)

        class_cost = cal_classcost(contents, lp)


        if hp_inclass_num == 0:
            Classtype[i][0] = 0
            Classtype[i][1] = -1
            Classtype[i][2] = -1

            lp[center_index][3] = 1
            new_hprow = [lp[center_index][0], lp[center_index]
                     [1], class_cost , i, 1]
            hp = np.row_stack((hp, new_hprow))


        elif hp_inclass_num == 1:
            Classtype[i][0] = 1
            Classtype[i][1] = -1
            Classtype[i][2] = -1
            # hp[tempindex][4] = 1
            # hp[tempindex][2] = hp[tempindex][2] + class_cost

            lp[center_index][3] = 1
            new_hprow = [lp[center_index][0], lp[center_index]
                     [1], class_cost , i, 1]
            hp = np.row_stack((hp, new_hprow))
            
        else:
            Classtype[i][0] = 2
            Classtype[i][1] = -1
            Classtype[i][2] = -1
            # hp[tempindex][4] = 1
            # hp[tempindex][2] = hp[tempindex][2] + class_cost
            lp[center_index][3] = 1
            new_hprow = [lp[center_index][0], lp[center_index]
                     [1], class_cost , i, 1]
            hp = np.row_stack((hp, new_hprow))
    
    hp_raw = hp[0:hp_raw_lenth, :]

    output1 = pd.DataFrame(
        data=lp, columns=['x', 'y', 'capacity', 'type', 'class', 'A_num'])
    output2 = pd.DataFrame(
        data=hp, columns=['x', 'y', 'capacity', 'class', 'type'])
    # output3 = pd.DataFrame(data=Classtype, columns=['type', 'depot1','depot2'])
    output4 = pd.DataFrame(data=hp_raw, columns=[
                           'x', 'y', 'capacity', 'class', 'type'])
    writer1 = pd.ExcelWriter('Data/LP.xlsx')
    writer2 = pd.ExcelWriter('Data/HP.xlsx')
    writer4 = pd.ExcelWriter('Data/HP_raw.xlsx')
    output1.to_excel(writer1, 'Sheet1')
    output2.to_excel(writer2, 'Sheet1')
    output4.to_excel(writer4, 'Sheet1')
    # output3.to_csv('Data/Classtype.csv', index=False)
    writer1.close()
    writer2.close()
    writer4.close()

    show()

    return lp, hp

def Pre_Process(file_position ,depotposition , l_limit , max_d , max_num):   
    rawData = pd.read_excel(file_position)
    rawData = np.array(rawData)

    LP, HP = Split_LH(depotposition,rawData,l_limit)

    LP_cost = Generate_LPCostmatrix(LP)
    # HP_cost_raw = Generate_HPCostmatrix_Raw(HP)

    # LH_costmatrix = Generate_LHCostmatrix(LP, HP)


    LP = LP_Cluster(LP, LP_cost, max_d, max_num, HP)

    LP, HP = Generate_Center(LP, HP, LP_cost)

    LH_costmatrix = Generate_LHCostmatrix(LP, HP)

    LH_costmatrix_raw = Generate_LHCostmatrix_raw(LP, HP)
    
    HP_cost = Generate_HPCostmatrix(HP)