import argparse
import csv
import sys
import numpy as np
import json
import os
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from scipy import io
from inits import load_data
from trainGcn import train_gcn
from trainNN import train_nn
from evaluation import get_results, evaluate_performance_two, evaluate_performance,get_max_avg_results,get_metrics

import xlrd  ###
import pandas as pd
from scipy import io


##############

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#global parameters
parser.add_argument('--graphs', type=lambda s: [item for item in s.split(",")], default=('interaction', 'net2'), help="lists of graphs to use.")
parser.add_argument('--attributes', type=lambda s: [item for item in s.split(",")], default=('features','similarity'),help=" attributes ： features similarity")

parser.add_argument('--data_path', type=str, default='MDAD', help="lists of dataset : MDAD  , DrugVirus, aBiofilm")
#parameters for traing GCN
parser.add_argument('--lr', type=float, default=0.0005, help="Initial learning rate. best 0.0005")
parser.add_argument('--epochs_net1', type=int, default=1, help="Number of epochs to train interaction. best 150")
parser.add_argument('--epochs_net', type=int, default=200, help="Number of epochs to train net.")
parser.add_argument('--hidden1', type=int, default=800, help="Number of units in hidden layer 1. best 800 400")
parser.add_argument('--hidden2', type=int, default=400, help="Number of units in hidden layer 2.")
parser.add_argument('--weight_decay', type=float, default=0, help="Weight for L2 loss on embedding matrix.")
parser.add_argument('--dropout', type=float, default=0.5, help="Dropout rate (1 - keep probability).")
parser.add_argument('--threshold', type=float, default=0.02, help="threshold for two classes.")
parser.add_argument('--k_folds', type=int, default=10, help="kflod")
parser.add_argument('--model', type=str, default="gcn_vae", help="Model string.")
parser.add_argument('--result',type=str,default="../output/result.json")
parser.add_argument('--input',type=str,default="../input/input.csv")
parser.add_argument('--output1',type=str,default="../output/output1.csv")
args = parser.parse_args()
print(args)

save_path = os.path.join("ppv_10k")
    
def main():
    ########
    # 存入输入的药物名csv文件
    #headers = ['Drug_name']
    # rows = ['Sorbitol']
    # save_path1 = os.path.join("input")  # 用于路径拼接文件路径，可以传入多个路径
    # with open("../input/" + args.input + ".csv", 'w+', encoding='utf8', newline='') as f1:
    #     writer = csv.writer(f1)
    #     #writer.writerow(headers)
    #     writer.writerows([rows])
    #     f1.close()
    sp = ''
    with open(args.input , 'r') as f1:
        reader =csv.reader(f1)
        for i in reader:
            sp=i[0].strip()
            print(sp)

    # 读取excel文件并存为列表
    def read_excel():
        wb = xlrd.open_workbook('./data/MDAD/drugs.xlsx')  # 打开Excel文件
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

    search_name = sp.strip().lower()
    str_match = [
        s for s in a
        if any(str(cell).strip().lower() == search_name for cell in s)
    ]
    print(str_match)
    if not str_match:
        available = [
            str(row[1]).strip()
            for row in a
            if len(row) > 1 and str(row[1]).strip()
        ][:20]
        message = 'Drug name not found in MDAD dataset: {}. Example supported drugs: {}'.format(
            sp,
            ', '.join(available),
        )
        print(message, file=sys.stderr)
        raise ValueError(message)
    idx = int(str_match[0][0])
    print(idx)

    def read_excel1():
        wb = xlrd.open_workbook('./data/MDAD/microbes.xlsx')  # 打开Excel文件
        sheet = wb.sheet_by_name('Sheet1')  # 通过excel表格名称(rank)获取工作表
        dat = []
        for i in range(173):
            if i == 0:
                continue
            dat.append(sheet.cell_value(rowx=i, colx=1))
        return dat

    b = read_excel1()
    print(b)

    if os.path.exists("results/" + '/' + save_path + "_" + ".mat") == False:   ##
        print("Training", args.data_path)

        embeddings_list = []

        #for graph in args.graphs:
        graph = 'interaction'
        print("#############################")
        print("Training", graph)
        adj, features, labels, num_drug, num_microbe = load_data(graph, args)
        embeddings = train_gcn(features, adj, args, graph, num_drug, num_microbe)
        embeddings_list.append(embeddings)

        embeddings = np.hstack(embeddings_list)   #np.hstack将参数元组的元素数组按水平方向进行叠加
        io.savemat("results/"  + '/' + save_path + "_"  + ".mat", {'embeddings': embeddings, 'labels': labels})
    else:
        mat = io.loadmat("results/"  + '/' + save_path + "_"  + ".mat")
        embeddings = mat['embeddings']
        labels = mat['labels']

    k_folds = args.k_folds

    # split data into train and test
    num_test = int(np.floor(labels.shape[0] / k_folds))
    num_train = labels.shape[0] - num_test
    all_idx = list(range(labels.shape[0]))

    perf_list = []
    y_score_list = []
    print("###################################")
    #for k in range(k_folds):
    for k in range(1):
        print("------this is %dth cross validation------" % (k + 1))
        np.random.seed(k)
        np.random.shuffle(all_idx)

        train_idx = all_idx[:num_train]
        test_idx = all_idx[num_train:(num_train + num_test)]

        Y_train = labels[train_idx]

        Y_test = labels[test_idx]

        X_train = embeddings[train_idx]
        X_test = embeddings[test_idx]

        print('....train_nn....')
        y_score = train_nn(X_train, Y_train, X_test, Y_test)

        print("---------------------------------")
        print('....evalution....')

        y_pred = [int(item > args.threshold) for item in y_score.flatten()]

        for i in range(137):
            print(i + 1237, end=" ")
            for j in range(173):
                print(y_pred[i * 173 + j], end=" ")
            print()
        a = []
        for i in range(173):
            if y_pred[i + (idx - 1237) * 173] == 1:
                print(b[i])
                a.append(b[i])

        perf = evaluate_performance_two(Y_test.flatten(), y_pred, y_score.flatten().tolist())
        print(perf)
        perf_list.append(perf)

        y_score_list.append(y_score.tolist())

    print("###################################")
    perf_result = get_max_avg_results(perf_list)

    with open(args.result, "w") as f:
        json.dump(perf_result, f)

    
    with open(args.output1, "w") as f3:
        writer = csv.writer(f3)
        for i in range(len(a)):
            writer.writerow([a[i]])


if __name__ == '__main__':
      main()
