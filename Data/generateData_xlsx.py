# -*- coding:utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# test whether these center points distinct enough
def isDistinct(means, criteria):
    k = np.shape(means)[0]

    # test whether distinct amout is below criteria ;
    # np.linalg.norm    : calculate the norm of (...)
    for i in range(k):
        for j in range(i + 1, k):
            if np.linalg.norm(means[i] - means[j]) < criteria:
                return False
    return True


"""
 generate all the data points (local clustering)
 K is the number of center points ; random center points' range : (0,0)~(X,Y) ; minimun length between center points :criteria
"""


def generateData(K, X, Y, criteria):
    means = np.zeros((K, 2))
    while (isDistinct(means, criteria) == False):  # 随机生成中心点，避免靠的太近
        means = np.random.random_sample((K, 2))
        means[:, 0] = X * means[:, 0]
        means[:, 1] = Y * means[:, 1]
    nums = np.random.random_integers(19, 20, K)  # 随机生成每个类的数据个数
    cov = [[17000, 0], [0, 17000]]  # 设置高斯分布协方差
    data = np.random.multivariate_normal(means[0], cov, nums[0])
    for i in range(1, K):  # 生成数据
        data = np.append(data, np.random.multivariate_normal(
            means[i], cov, nums[i]), axis=0)

    # randtype=np.random.randint(2,size=nums.sum()) #生成随机快递种类
    # data=np.c_[data,randtype]
    capacity =np.random.randint(1,50,nums.sum())
    data=np.c_[data,capacity]

    return data


# np.random.seed(np.random.randint(0, 9999))
X = 3000
Y = 3000
data = generateData(15, X, Y,5)
# des=np.array([[0,0],[X,Y]])
# ult = np.random.randint(21, size=2)

output = pd.DataFrame(data=data, columns=['x', 'y','capacity'])
# output=pd.DataFrame(data=data, columns=['x','y','e_type','c_type'])

# output.to_csv('pointsData_class.csv', index=False)


# output.to_csv('costmatrix.xlsx', index=False)
writer = pd.ExcelWriter('Dataset1.xlsx')

output.to_excel(writer,'Sheet1')
writer.close()


plt.axis([-1, X+1, -1, Y+1])
plt.plot(data[:, 0], data[:, 1], marker='.', linestyle='')
# plt.plot(des[:,0], des[:,1], marker='o', linestyle='', color='black')
# plt.plot(ult[0], ult[1], marker='x', linestyle='', color='green')
plt.show()
