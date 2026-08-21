import pandas as pd
import numpy as np
import sys, os
import json, pickle
from collections import OrderedDict
from rdkit import Chem
from rdkit.Chem import MolFromSmiles
import networkx as nx
from utils import *
from random import shuffle
import torch
import torch.nn as nn
#from models.gat import GATNet
from gat_gcn import GAT_GCN
#from models.gcn import GCNNet
#from models.ginconv import GINConvNet
import json
import argparse


config=argparse.ArgumentParser()
config.add_argument('--drug_input_file',default='./input/test_ligands.txt',type=str,help="药物输入文件位置")
config.add_argument('--protein_input_file',default='./input/proteins.txt',type=str,help="蛋白质输入文件，默认使用全部蛋白质序列")
config.add_argument('--output_file',default='./',type=str,help="输出文件存放位置")
config.add_argument('--gpu_number',default=0,type=int,help="使用GPU数目，默认为一")
config.add_argument('--input_model',default='./input/model_GAT_GCN_davis.model',type=str,help="指定模型位置")

args=config.parse_args()


def atom_features(atom):
    return np.array(one_of_k_encoding_unk(atom.GetSymbol(),
                                          ['C', 'N', 'O', 'S', 'F', 'Si', 'P', 'Cl', 'Br', 'Mg', 'Na', 'Ca', 'Fe', 'As',
                                           'Al', 'I', 'B', 'V', 'K', 'Tl', 'Yb', 'Sb', 'Sn', 'Ag', 'Pd', 'Co', 'Se',
                                           'Ti', 'Zn', 'H', 'Li', 'Ge', 'Cu', 'Au', 'Ni', 'Cd', 'In', 'Mn', 'Zr', 'Cr',
                                           'Pt', 'Hg', 'Pb', 'Unknown']) +
                    one_of_k_encoding(atom.GetDegree(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    one_of_k_encoding_unk(atom.GetTotalNumHs(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    one_of_k_encoding_unk(atom.GetImplicitValence(), [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) +
                    [atom.GetIsAromatic()])


def one_of_k_encoding(x, allowable_set):
    if x not in allowable_set:
        raise Exception("input {0} not in allowable set{1}:".format(x, allowable_set))
    return list(map(lambda s: x == s, allowable_set))


def one_of_k_encoding_unk(x, allowable_set):
    """Maps inputs not in the allowable set to the last element."""
    if x not in allowable_set:
        x = allowable_set[-1]
    return list(map(lambda s: x == s, allowable_set))


def smile_to_graph(smile):
    mol = Chem.MolFromSmiles(smile)

    c_size = mol.GetNumAtoms()

    features = []
    for atom in mol.GetAtoms():
        feature = atom_features(atom)
        features.append(feature / sum(feature))

    edges = []
    for bond in mol.GetBonds():
        edges.append([bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()])
    g = nx.Graph(edges).to_directed()
    edge_index = []
    for e1, e2 in g.edges:
        edge_index.append([e1, e2])

    return c_size, features, edge_index


def seq_cat(prot):
    x = np.zeros(max_seq_len)
    for i, ch in enumerate(prot[:max_seq_len]):
        x[i] = seq_dict[ch]
    return x


seq_voc = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
seq_dict = {v: (i + 1) for i, v in enumerate(seq_voc)}
seq_dict_len = len(seq_dict)
max_seq_len = 1000


def predicting(model, device, loader):
    model.eval()
    total_preds = torch.Tensor()
    total_labels = torch.Tensor()
    print('Make prediction for {} samples...'.format(len(loader.dataset)))
    with torch.no_grad():
        for data in loader:
            data = data.to(device)
            output = model(data)
            # print(output)

            total_preds = torch.cat((total_preds, output.cpu()), 0)
            # total_labels = torch.cat((total_labels, data.y.view(-1, 1).cpu()), 0)
    return total_preds.numpy()


def create_data():
    fpath = ''
    print(args.drug_input_file)
    print(os.getcwd())
    print(os.path.abspath('../test_ligands.txt'))
    print()

    ligands = json.load(open(args.drug_input_file), object_pairs_hook=OrderedDict)
    proteins = json.load(open(args.protein_input_file), object_pairs_hook=OrderedDict)
    drugs = []
    prots = []
    # eval 中没作用，占位
    Y = []
    # print(ligands.keys()[0])
    drug = Chem.MolToSmiles(Chem.MolFromSmiles(ligands[list(ligands.keys())[0]]), isomericSmiles=True)

    for t in proteins.keys():
        prots.append(proteins[t])
    for i in range(len(prots)):
        drugs.append(drug)
    for i in range(len(prots)):
        Y.append(1)
    print('finished')

    smile_graph = {}
    for smile in drugs:
        g = smile_to_graph(smile)
        smile_graph[smile] = g
    os.system('rm -rf data/processed/')
    # test_drugs, test_prots=drugs,prots
    XT = [seq_cat(t) for t in prots]
    test_drugs, test_prots, test_Y = np.asarray(drugs), np.asarray(XT), np.asarray(Y)

    test_data = TestbedDataset(root='data', xd=test_drugs, xt=test_prots, y=test_Y,
                               smile_graph=smile_graph)
    print('finished')
    return test_data, prots


if __name__ == "__main__":
    test_data, prots = create_data()
    test_loader = DataLoader(test_data, batch_size=64, shuffle=False)
    cuda_name = "cuda:0"
    if args.gpu_number > 3:
        cuda_name = "cuda:" + str(int(args.gup_number))
    print('cuda_name:', cuda_name)
    device = torch.device(cuda_name if torch.cuda.is_available() else "cpu")
    model =GAT_GCN().to(device)
    model.load_state_dict(torch.load("/input/model_GAT_GCN_davis.model"))
    P = predicting(model, device, test_loader)
    print(P.shape)
    prots = np.array(prots)
    result = np.concatenate((prots[:, np.newaxis], P), axis=1)
    print(result.shape)

    df = pd.DataFrame(result, columns=['protein', 'affinity'])
    if not os.path.exists(args.output_file):
        os.mkdir(args.output_file)
    df.to_csv(args.output_file+"/out.csv")
