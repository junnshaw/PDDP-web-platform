import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from torch.autograd import Variable

import math, random, sys
from optparse import OptionParser
from collections import deque
import rdkit
import rdkit.Chem as Chem
from rdkit.Chem import Draw
import pandas as pd
from molvae import *
#from molvae.mol_tree import Vocab

lg = rdkit.RDLogger.logger() 
lg.setLevel(rdkit.RDLogger.CRITICAL)

parser = OptionParser()
parser.add_option("-n", "--nsample", dest="nsample",default=50)
parser.add_option("-v", "--vocab", dest="vocab_path",default='./data/vocab1.txt')
parser.add_option("-m", "--model", dest="model_path",default='./molvae/vaemodel/model.iter-2')
parser.add_option("-w", "--hidden", dest="hidden_size", default=450)
parser.add_option("-l", "--latent", dest="latent_size", default=56)
parser.add_option("-d", "--depth", dest="depth", default=3)
parser.add_option('--result',type=str,default='../output/result.txt')
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

f = open(opts.result, 'a')

for i in range(nsample):
    smiles = model.sample_prior(prob_decode=False)
    f.write('\n'+smiles)
    #print(model.sample_prior(prob_decode=False))
    #print(model.sample_prior(prob_decode=True))
