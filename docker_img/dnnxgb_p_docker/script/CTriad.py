#!/usr/bin/env python
#_*_coding:utf-8_*_
import pandas as pd
import re

def CalculateKSCTriad(sequence, gap, features, AADict):
	res = []
	for g in range(gap+1):
		myDict = {}
		for f in features:
			myDict[f] = 0

		for i in range(len(sequence)):
			if i+gap+1 < len(sequence) and i+2*gap+2<len(sequence):
				fea = AADict[sequence[i]] + '.' + AADict[sequence[i+gap+1]]+'.'+AADict[sequence[i+2*gap+2]]
				myDict[fea] = myDict[fea] + 1

		maxValue, minValue = max(myDict.values()), min(myDict.values())
		for f in features:
			res.append((myDict[f] - minValue) / maxValue)

	return res

def CTriad(sequence, gap = 0, **kw):
	AAGroup = {
		'g1': 'AGV',
		'g2': 'ILFP',
		'g3': 'YMTS',
		'g4': 'HNQW',
		'g5': 'RK',
		'g6': 'DE',
		'g7': 'C'
	}

	myGroups = sorted(AAGroup.keys())

	AADict = {}
	for g in myGroups:
		for aa in AAGroup[g]:
			AADict[aa] = g

	features = [f1 + '.'+ f2 + '.' + f3 for f1 in myGroups for f2 in myGroups for f3 in myGroups]

	encodings = []
	header = ['#']
	for f in features:
		header.append(f)
	encodings.append(header)



	code = []
	if len(sequence) < 3:
			print('Error: for "CTriad" encoding, the input fasta sequences should be greater than 3. \n\n')
			return 0
	code = code + CalculateKSCTriad(sequence, 0, features, AADict)


	return code

if __name__ == '__main__':
	print("1")
	df_neg = pd.read_csv(r'E:\ieDownload\DNN-XGB-for-PPI-Prediction-main\Dataset\Helicobacter pylori\HP_N_protein_A.csv',header=None)
	# df_neg = pd.read_csv('/home/aita/HL/Dataset/Helicobacter_pylori/N_protein_A.csv',header=None)
	# print(df_neg.iloc[0:1, ])
	neg = df_neg.iloc[:,:].values
	print(neg)
	print(type(neg))
	CT=[]

	for index in range(len(df_neg)):
		df = CTriad(neg[index][0])
		CT.append(df)
	print(CT)
