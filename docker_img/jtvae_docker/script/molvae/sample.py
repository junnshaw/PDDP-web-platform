import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from torch.autograd import Variable

import math, random, sys
from optparse import OptionParser
from collections import deque
import rdkit
from rdkit.Chem.Descriptors import MolWt,MolLogP,HeavyAtomCount
import rdkit.Chem as Chem
from rdkit.Chem import Draw
from rdkit.Chem import Descriptors
from rdkit.Chem import MolFromSmiles, MolToSmiles
from rdkit.Chem import rdmolops
import sascorer

import numpy as np  
import pandas as pd
from jtnn import *
import csv

lg = rdkit.RDLogger.logger() 
lg.setLevel(rdkit.RDLogger.CRITICAL)

parser = OptionParser()
parser.add_option("-n", "--nsample", dest="nsample",default=500)
parser.add_option("-v", "--vocab", dest="vocab_path",default='./data/vocab1.txt')
parser.add_option("-m", "--model", dest="model_path",default='./molvae/vaemodel/model.iter-2')
parser.add_option("-w", "--hidden", dest="hidden_size", default=450)
parser.add_option("-l", "--latent", dest="latent_size", default=56)
parser.add_option("-d", "--depth", dest="depth", default=3)
parser.add_option('--result',type=str,default='../output/result.csv')
parser.add_option('--input',type=str,default='../input/jtvae_input.csv')
opts,args = parser.parse_args()
   
vocab = [x.strip("\r\n ") for x in open(opts.vocab_path)] 
vocab = Vocab(vocab)

hidden_size = int(opts.hidden_size)
latent_size = int(opts.latent_size)
depth = int(opts.depth)
nsample = int(opts.nsample)

model = JTNNVAE(vocab, hidden_size, latent_size, depth)
load_dict = torch.load(opts.model_path,map_location='cpu')
missing = {k: v for k, v in model.state_dict().items() if k not in load_dict}
load_dict.update(missing) 
model.load_state_dict(load_dict)
#model = model.cuda()

torch.manual_seed(0)

f = open(opts.result, 'w',newline="")
f_in = open(opts.input, 'r')

input_csv = csv.reader(f_in)
f_csv = csv.writer(f)
input_list = []
for row in input_csv:
    input_list = row 
    break

nsample = int(input_list[0])
weight = float(input_list[1])
lgp = float(input_list[2])

print(nsample)
print(weight)
print('%%%%%%%%%%%%%%%%%%%%%%')

#f_csv.writerow(['smiles','logp','sa'])
smilelist = []

lz = 0
for i in range(nsample*10):
    smiles = model.sample_prior(prob_decode=False)

    sr_t = MolToSmiles(MolFromSmiles(smiles), isomericSmiles=True)
    lp_t = Descriptors.MolLogP(MolFromSmiles(sr_t))
    sa_t = sascorer.calculateScore(MolFromSmiles(sr_t))
    mol = Chem.MolFromSmiles(smiles)
    wt = MolWt(mol)

    if lp_t > 1.0 and lp_t < lgp:
        if sa_t < 3.0 and wt < weight:
            smilelist.append(smiles)
            lz = lz + 1
    if lz == nsample:
        break
    

#for i in range(nsample):
    
#   smiles = model.sample_prior(prob_decode=False)
#   smilelist.append(smiles)

    #f_csv = csv.DictWriter(f, headers)
    #f_csv.writeheader()# 写入标题
smiles_rdkit = []
for i in range(len(smilelist)):
    smiles_rdkit.append(MolToSmiles(MolFromSmiles(smilelist[ i ]), isomericSmiles=True))

logP_values = []
for i in range(len(smilelist)):
    logP_values.append(Descriptors.MolLogP(MolFromSmiles(smiles_rdkit[ i ])))
    #print(logP_values[i])
    #print('\n')

SA_scores = []
for i in range(len(smilelist)):
    SA_scores.append(-sascorer.calculateScore(MolFromSmiles(smiles_rdkit[ i ])))

for i in range(len(smilelist)):
    mol = Chem.MolFromSmiles(smilelist[i])
    wt = MolWt(mol)
    f_csv.writerow([smilelist[i],logP_values[i],-SA_scores[i],wt])
nei_mols = [Chem.MolFromSmiles(s) for s in smilelist]
img = Draw.MolsToGridImage(nei_mols, molsPerRow=10, subImgSize=(200,200), useSVG=True)
filename = '../output/test2.svg'
with open(filename, 'w') as f2:
    f2.write(img)
    
f.close()
f2.close()
    #f.write('\n'+smiles)
    #print(model.sample_prior(prob_decode=False))
    #print(model.sample_prior(prob_decode=True))
