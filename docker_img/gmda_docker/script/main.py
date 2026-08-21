import argparse
import numpy as np
import json
import os
from inits import load_data
from trainGcn import train_gcn
from trainNN import train_nn
from evaluation import get_results, evaluate_performance_two, evaluate_performance, get_max_avg_results
import pandas as pd  ###

from pandas import DataFrame

import csv  ###
import xlrd  ###
import xlsxwriter as xw
from scipy import io
import os

os.environ['KMP_WARNINGS'] = '0'


def main():
    ########
    # 存入输入的药物名csv文件
    headers = ['Drug_name']
    rows = ['Sulfadoxine']
    save_path1 = os.path.join("input")  # 用于路径拼接文件路径，可以传入多个路径
    with open("results/" + save_path1 + ".csv", 'w+', encoding='utf8', newline='') as f1:

        writer = csv.writer(f1)
        writer.writerow(headers)
        writer.writerows([rows])
        f1.close()
        my_matrix = pd.read_csv('results/input.csv')
        print(my_matrix)
        print(my_matrix.shape)
        #print(matrix.shape)

    # 读取excel文件并存为列表
    def read_excel():
        wb = xlrd.open_workbook('../data/MDAD/drugs.xlsx')  # 打开Excel文件
        sheet = wb.sheet_by_name('Sheet1')  # 通过excel表格名称(rank)获取工作表
        dat = []
        for r in range(sheet.nrows):  # 将表中数据按行逐步添加到列表中，最后转换为list结构
            dat1 = []
            for c in range(sheet.ncols):
                dat1.append(sheet.cell_value(r, c))
            dat.append(list(dat1))
        return dat
    a = read_excel()
    print(a)


    str_match = [s for s in a if "Sorbitol" in s]
    print(str_match)
    idx = int(str_match[0][0])
    print(idx)

    def read_excel1():
        wb = xlrd.open_workbook('../data/MDAD/microbes.xlsx')  # 打开Excel文件
        sheet = wb.sheet_by_name('Sheet1')  # 通过excel表格名称(rank)获取工作表
        dat = []
        for i in range(173):
            if i == 0:
                continue
            dat.append(sheet.cell_value(rowx=i, colx=1))
        return  dat
    b=read_excel1()
    print(b)

    ##############

    parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)  # 创建一个解析器——创建 ArgumentParser() 对象，ArgumentDefaultsHelpFormatter自动添加默认的值的信息到每一个帮助信息的参数中
    # global parameters 全局参数
    parser.add_argument('--graphs', type=lambda s: [item for item in s.split(",")], default=('interaction', 'net2'),
                        help="lists of graphs to use.")  # 添加参数——调用 add_argument() 方法添加参数
    # name or flags - 选项字符串的名字或者列表，例如foo或者 - f, --foo。  default - 不指定参数时的默认值。help - 参数的帮助信息，当指定为 argparse.SUPPRESS 时表示不显示该参数的帮助信息.
    parser.add_argument('--attributes', type=lambda s: [item for item in s.split(",")],
                        default=('features', 'similarity'), help=" attributes ： features similarity")
    parser.add_argument('--data_path', type=str, default='MDAD', help="lists of dataset : MDAD  , DrugVirus, aBiofilm")
    # parameters for traing GCN
    parser.add_argument('--lr', type=float, default=0.0005, help="Initial learning rate. best 0.0005")
    parser.add_argument('--epochs_net1', type=int, default=1, help="Number of epochs to train interaction. best 150")

    parser.add_argument('--epochs_net', type=int, default=200, help="Number of epochs to train net.")  # default 200
    parser.add_argument('--hidden1', type=int, default=800, help="Number of units in hidden layer 1. best 800 400")
    parser.add_argument('--hidden2', type=int, default=400, help="Number of units in hidden layer 2.")
    parser.add_argument('--weight_decay', type=float, default=0, help="Weight for L2 loss on embedding matrix.")
    parser.add_argument('--dropout', type=float, default=0.5, help="Dropout rate (1 - keep probability).")
    parser.add_argument('--threshold', type=float, default=0.02, help="threshold for two classes.")  # 默认阈值
    parser.add_argument('--k_folds', type=int, default=10, help="kflod")
    parser.add_argument('--model', type=str, default="gcn_vae", help="Model string.")
    args = parser.parse_args()  # 解析参数——使用 parse_args() 解析添加的参数
    print(args)

    print("Training", args.data_path)
    dataset = args.data_path  ##

    for time in range(1):  # 5
        print("#############################")
        graph = 'interaction'
        # for dataset in args.data_path:  ##
        print("data_path", args.data_path)
        print("#############################")
        print("Training", graph)
        adj, features, labels, num_drug, num_microbe = load_data(graph, args)  ###数据源分析，加载数据

        # save_path = os.path.join("embeddings")  ###
        #
        embeddings = train_gcn(features, adj, args, graph, num_drug, num_microbe)  # 训练  1546*173
        #
        # io.savemat("results/" + save_path + ".mat",{'embeddings':embeddings}) ###

        #print(embeddings)
        k_folds = args.k_folds

        # split data into train and test   将数据拆分为训练和测试
        num_test = int(np.floor(labels.shape[0] / k_folds))  # 测试  137
        num_train = labels.shape[0] - num_test  # 训练（全部-测试）  1373-137=1236
        all_idx = list(range(labels.shape[0]))  # 全部 1373
        print(num_test,num_train,all_idx)
        # print(len(embeddings[1545]))
        perf_list = []
        #print(all_idx)
        print("###################################")



        # 交叉验证
        for k in range(k_folds):
            print("------this is %dth cross validation------" % (k + 1))
            #np.random.seed(k)  #生成随机数，()不同，则随机数不同
            #np.random.shuffle(all_idx)   #1373，shuffle直接在原来的数组上进行操作，改变原来数组的顺序，无返回值(是对列表x中的所有元素随机打乱顺序，若x不是列表，则报错)。
            #python list 索引+遍历

            #num_test=137，num_train=1236

            train_idx = all_idx[:num_train]  # 前1236
            print(train_idx)
            test_idx = all_idx[num_train:(num_train + num_test)]  #后137
            print(test_idx)

            #train_idx = all_idx[num_test:1373]  ##137到1373
            #test_idx = all_idx[:num_test]  ##前137

            Y_train = labels[train_idx]   #1236*173
            Y_test = labels[test_idx]     #137*173
            X_train = embeddings[train_idx]   #1236*173
            X_test = embeddings[test_idx]     #137*173

            print('....train_nn....')
            y_score = train_nn(X_train, Y_train, X_test, Y_test)  #已知的和训练的结果的index前1236X173 训练模型，预测训练结果的后137的样本属于每一个类别的概率

            print("---------------------------------")
            print('....evalution....')
            #print(y_score)


            y_pred = [int(item > args.threshold) for item in y_score.flatten()]#预测训练结果的后137的值 >0.02 ?1 :0

            print("*************")
            #print(len(y_pred))
            #print(y_pred)

            for i in range(137):
                print(i+1237,end = " ")
                for j in range(173):
                    print(y_pred[i*173 + j], end = " ")
                print()
            a = []
            for i in range(173):
                if y_pred[i + (idx-1237) * 173] == 1:
                    print(b[i])
                    a.append(b[i])

            print("+++++++++++++++++++++++")
            #print(len(Y_test))
            # print(Y_test)
            perf = evaluate_performance_two(Y_test.flatten(), y_pred, y_score.flatten())
            print(perf)
            perf_list.append(perf)


        save_path2 = os.path.join("output")
        with open("results/" + save_path2 + ".json", "w") as f2:
            json.dump(perf, f2)

        save_path3 = os.path.join("output1")
        with open("results/" + save_path3 + ".json", "w") as f3:
            json.dump(a, f3)



        print("###################################")
        # print("1",args.model)  ##  gcn_vae
        perf_result = get_max_avg_results(perf_list)

        save_path = os.path.join("results_" + str(args.model))
        print("save:", save_path)
        version = '0506'
        with open("results/" + version + '/' + save_path + "_" + version + ".json", "w") as f:
            #  print("results/" + version + '/' + save_path + "_" + version + ".json")  #
            json.dump(perf_result, f)
        # f.close()  ##


if __name__ == '__main__':
    main()
