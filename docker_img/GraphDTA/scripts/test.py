import numpy as np
import pandas as pd
import sys, os
from random import shuffle
import torch
import torch.nn as nn
from models.gat import GATNet
from models.gat_gcn import GAT_GCN
from models.gcn import GCNNet
from models.ginconv import GINConvNet
from utils import *


def predicting(model, device, loader):
    model.eval()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    print('Make prediction for {} samples...'.format(len(loader.dataset)))
    with torch.no_grad():
        for data in loader:
            data = data.to(device)
            output = model(data)
            total_preds = torch.cat((total_preds, output.cpu()), 0)
            total_labels = torch.cat((total_labels, data.y.view(-1, 1).cpu()), 0)
    return total_labels.numpy().flatten(),total_preds.numpy().flatten()


if __name__ == "__main__":
    dataset = "davis"
    test_data = TestbedDataset(root='data', dataset=dataset + '_test')
    test_loader = DataLoader(test_data, batch_size=1, shuffle=False)
    cuda_name = "cuda:0"
    if len(sys.argv) > 3:
        cuda_name = "cuda:" + str(int(sys.argv[3]))
    print('cuda_name:', cuda_name)
    device = torch.device(cuda_name if torch.cuda.is_available() else "cpu")
    model = GAT_GCN().to(device)
    model.load_state_dict(torch.load("model_GAT_GCN_davis.model"))
    G,P = predicting(model, device, test_loader)
    print("打印参数G:",G)
    print("打印参数P:",P)
    ret = [rmse(G, P), mse(G, P), pearson(G, P), spearman(G, P), ci(G, P)]
    print(ret)
    with open(dataset+".txt",'a',encoding='utf-8') as f:
        f.write("参数G:"+str(G)+"\n")
        f.write("参数P:"+str(P)+"\n")
        f.write("rmse(G, P), mse(G, P), pearson(G, P), spearman(G, P), ci(G, P):"+str(ret)+"\n")