"""Compute and save a csv file with the MolLogP feature."""
import csv
import os
import os.path as op
import sys
import pandas as pd
import numpy as np
import argparse
import math
import pickle
from rdkit.Chem import Crippen
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem import QED

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from rdkit import rdBase, Chem
from rdkit.Chem import Draw, Descriptors
from rdkit.Chem.Draw import rdMolDraw2D
from IPython.display import SVG
#get_sa_score start
_fscores = None


def readFragmentScores(name='fpscores'):
    import gzip
    global _fscores
    # generate the full path filename:
    if name == "fpscores":
        name = op.join(os.getcwd(), name)
        # name = op.join(op.dirname(__file__), name)
    data = pickle.load(gzip.open('%s.pkl.gz' % name))
    outDict = {}
    for i in data:
        for j in range(1, len(i)):
            outDict[i[j]] = float(i[0])
    _fscores = outDict


def numBridgeheadsAndSpiro(mol, ri=None):
    nSpiro = rdMolDescriptors.CalcNumSpiroAtoms(mol)
    nBridgehead = rdMolDescriptors.CalcNumBridgeheadAtoms(mol)
    return nBridgehead, nSpiro


def calculateScore(m):
    if _fscores is None:
        readFragmentScores()

    # fragment score
    fp = rdMolDescriptors.GetMorganFingerprint(m,
                                            2)  # <- 2 is the *radius* of the circular fingerprint
    fps = fp.GetNonzeroElements()
    score1 = 0.
    nf = 0
    for bitId, v in fps.items():
        nf += v
        sfp = bitId
        score1 += _fscores.get(sfp, -4) * v
    score1 /= nf

    # features score
    nAtoms = m.GetNumAtoms()
    nChiralCenters = len(Chem.FindMolChiralCenters(m, includeUnassigned=True))
    ri = m.GetRingInfo()
    nBridgeheads, nSpiro = numBridgeheadsAndSpiro(m, ri)
    nMacrocycles = 0
    for x in ri.AtomRings():
        if len(x) > 8:
            nMacrocycles += 1

    sizePenalty = nAtoms**1.005 - nAtoms
    stereoPenalty = math.log10(nChiralCenters + 1)
    spiroPenalty = math.log10(nSpiro + 1)
    bridgePenalty = math.log10(nBridgeheads + 1)
    macrocyclePenalty = 0.
    # ---------------------------------------
    # This differs from the paper, which defines:
    # macrocyclePenalty = math.log10(nMacrocycles+1)
    # This form generates better results when 2 or more macrocycles are present
    if nMacrocycles > 0:
        macrocyclePenalty = math.log10(2)

    score2 = 0. - sizePenalty - stereoPenalty - spiroPenalty - bridgePenalty - macrocyclePenalty

    # correction for the fingerprint density
    # not in the original publication, added in version 1.1
    # to make highly symmetrical molecules easier to synthetise
    score3 = 0.
    if nAtoms > len(fps):
        score3 = math.log(float(nAtoms) / len(fps)) * .5

    sascore = score1 + score2 + score3

    # need to transform "raw" value into scale between 1 and 10
    min = -4.0
    max = 2.5
    sascore = 11. - (sascore - min + 1) / (max - min) * 9.
    # smooth the 10-end
    if sascore > 8.:
        sascore = 8. + math.log(sascore + 1. - 9.)
    if sascore > 10.:
        sascore = 10.0
    elif sascore < 1.:
        sascore = 1.0

    return sascore


def my_score(mols:list):
    readFragmentScores("fpscores")
    print('smiles\tsa_score')
    for m in mols:
        s = calculateScore(m)
        smiles = Chem.MolToSmiles(m)
        print(smiles + "\t" + "\t%3f" % s)
        return s



#get_sa_score end




def get_logp():
    logp_list = []
    # for molecule in full_molecule_list:
    # path = 'chemp/ChempropUncertaintyQuantification/data/drug.csv'
    with open(input_file) as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        # lines = []
        for line in reader:
            smiles=line[0]
            print(smiles)
            #logp
            logp_list.append(Crippen.MolLogP(Chem.MolFromSmiles(line[0])))
            return logp_list[0]
            # with open('logp_testdrug.csv', 'w+') as logp_csv:
            #     csv_writer = csv.writer(logp_csv, delimiter=',')
            #     csv_writer.writerow(['smiles', 'logp'])
            #     csv_writer.writerow([smiles,str(logp_list[0])])
            #     print("*******")
def get_sa():
    df = pd.read_csv(input_file)
    df.head()
    PandasTools.AddMoleculeColumnToFrame(frame=df, smilesCol='smiles')
    df.head()
def get_tpsa():
    suppl = Chem.SDMolSupplier('mol_tpsa.sdf')
    mols = [x for x in suppl if x is not None]
    declist = Descriptors.descList
    calc = {}
    for (i,j) in declist:
        calc[i] = j
    tpsa = [calc['TPSA'](i) for i in mols]
def get_mw():
    with open(input_file) as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        # lines = []
        for line in reader:
            smiles=line[0]
            print(smiles)
            # print('****')
            mw=Descriptors.MolWt(Chem.MolFromSmiles(smiles))
            # print('++++')
            print(mw)
            return mw


def test():
    rdkit.Chem.Descriptors.NumRadicalElectrons(smiles) 
    #分子所具有的自由基电子数   
    rdkit.Chem.Descriptors.NumValenceElectrons(smiles)
    #分子的价电子数
def get_ve():
    with open(input_file) as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        # lines = []
        for line in reader:
            smiles=line[0]
            print(smiles)
            # print('****')
            ve=Descriptors.NumValenceElectrons(Chem.MolFromSmiles(smiles))
            # print('++++')
            # print(ve)
            return ve
def get_qed():
    with open(input_file) as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        # 分子量（MW）
        # logP（ALOGP）
        # 氢键供体的数量（HBDs）
        # 氢键受体的数量（HBAs）
        # 极表面积（PSA）
        # 可旋转键数目（ROTBs）
        # 芳环数目（AROMs）
        # 警报结构数目（ALERTS）
        for line in reader:
            smiles=line[0]
            print(smiles)
            print('****')
            qed=QED.properties(Chem.MolFromSmiles(smiles))
            print(qed[0])
            print(qed[1])
            print(qed)
            print('++++')
            return qed
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_csv',help="Output directory",default='result.csv')
    parser.add_argument('-i', '--input_file',help="Input file",default='./input/drug.csv')
    options = parser.parse_args()
    input_file = options.input_file
    output_csv = options.output_csv

    ve = get_ve()
    with open(input_file) as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        # lines = []
        for line in reader:
            smiles=line[0]
            #TPSA已有
            # TPSA=rdMolDescriptors.CalcTPSA(Chem.MolFromSmiles(smiles))
            # print('0000')
            # print(TPSA)
            qed=QED.properties(Chem.MolFromSmiles(smiles))
            MW=qed[0]
            ALOGP=qed[1]
            HBA=qed[2]
            HBD=qed[3]
            PSA=qed[4]
            ROTB=qed[5]
            AROM=qed[6]
            ALERTS=qed[7]
            #sa
            m = Chem.MolFromSmiles(smiles)
            x = [m]
            sa_score=my_score(x)
            # print(sa_score)

            with open(output_csv, 'w+') as drugp_csv:
                csv_writer = csv.writer(drugp_csv, delimiter=',')
                csv_writer.writerow(['SMILES','SA_SCORE','MW','ALOGP','HBA','HBD','PSA','ROTB','AROM','ALERTS','VE'])
                csv_writer.writerow([smiles,str(sa_score),str(MW),str(ALOGP),str(HBA),str(HBD),str(PSA),
                                    str(ROTB),str(AROM),str(ALERTS),str(ve)])
                print("finish")


