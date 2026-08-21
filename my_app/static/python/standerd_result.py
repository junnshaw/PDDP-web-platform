# from matplotlib import pyplot as plt
# import matplotlib.ticker as ticker
# import numpy as np
from numpy.core.fromnumeric import size
# import re
import json
import csv

def csvTojson():
    filename = 'data/output.csv'
    result = []
    # 相比open(),with open()不用手动调用close()方法
    with open(filename, 'r') as f:
        next(f)
        # 将csv中的数据逐行存到列表lines里 lines的每一个元素对应于txt中的一行。然后将每个元素中的不同信息提取出来
        lines = f.readlines()
        # i变量，由于这个txt存储时有空行，所以增只读偶数行，主要看txt文件的格式，一般不需要
        # j用于判断读了多少条，step为画图的X轴
        # i = 0
        j = 0
        for line in lines:
        # if i % 2 == 0:
        # 分割每一行
            temp = line.split(',')
            # print(temp)
            # print(temp[0])
            # print(temp[1])
            t = temp[2].split('\n')
            # print(t[0])
    #         print(t[1])
    #         score = temp[1].split('\n')
            item = {
                'smiles':temp[0],
                'protein':temp[1],
                'pred':t[0]
                }
            result.append(item)
        # print(result)
        # print(type(result))

    with open('data/output_csvTojson.json','w') as dump_f:
        json.dump(result,dump_f)


if __name__ == '__main__':
    csvTojson()