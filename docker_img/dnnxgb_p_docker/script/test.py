import numpy as np

import DNNXGB
import pandas as pd
from keras.models import Model
from sklearn.preprocessing import RobustScaler
import AAC
import CTriad
import ld

from xgboost import XGBClassifier

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, default='/input/dnnxgb_p.csv')
parser.add_argument('--output', type=str, default='/output/output_p.csv')
args = parser.parse_args()

df_pos = pd.read_csv(r'Dataset//Human/H_P.csv',header=None)
df_neg = pd.read_csv(r'Dataset//Human/H_N.csv',header=None)
df_neg['Status'] = 0
df_pos['Status'] = 1
df_neg=df_neg.sample(n=len(df_pos))
df = pd.concat([df_pos,df_neg])
df = df.reset_index()
df=df.sample(frac=1)
df = df.iloc[:,1:]
X = df.iloc[:,0:1986].values
y = df.iloc[:, 1986:].values
Trainlabels=y
scaler = RobustScaler().fit(X)
X = scaler.transform(X)
X1_train = X[:,0:993]
X2_train = X[:,993:]
model=DNNXGB.define_model()
model.fit([X1_train, X2_train], y, epochs=10, batch_size=64, verbose=0)
intermediate_layer_model = Model(inputs=model.input, outputs=model.get_layer('merged_protein1_2').output)
intermediate_output_p1 = intermediate_layer_model.predict([X1_train, X2_train])
p_merge = pd.DataFrame(intermediate_output_p1)
X_train_feat = pd.concat((p_merge, pd.DataFrame(pd.DataFrame(Trainlabels))), axis=1, ignore_index=True)
Train = X_train_feat
Train = Train.sample(frac=1)
X = Train.iloc[:, 0:128].values
y = Train.iloc[:, 128:].values
extracted_df = X_train_feat
scaler = RobustScaler()
X = scaler.fit_transform(X)
model = XGBClassifier(n_estimators=50)
model.fit(X, y)

p1 = pd.read_csv(args.input,header=None)
protein1 = p1.iloc[:,:].values
p1 = protein1[0][0]

AAC1 = []
CT1 = []
LD1 = []
acc1 = AAC.AAC(p1)
AAC1.append(acc1)
ct1 = CTriad.CTriad(p1)
CT1.append(ct1)
PS1 = p1
CS1 = ld.classification_sequence_of(PS1)
LD_INFO1 = ld.ld_info_of(CS1)
LD_CODE1 = ld.ld_code_of_0(CS1)
LD_CODE1 = ld.ld_code_of(PS1)
LD1.append(LD_CODE1)
AAC1 = pd.DataFrame(AAC1)
CT1 = pd.DataFrame(CT1)
LD1 = pd.DataFrame(LD1)
protein1 = pd.concat([AAC1,CT1,LD1],axis=1)
protein1 = protein1.iloc[:,:].values
df_pos1 = pd.read_csv('Dataset/Human/H_P_A.csv',header=None)
df_pos2 = pd.read_csv('Dataset/Human/H_P_B.csv',header=None)
df_neg1 = pd.read_csv('Dataset/Human/H_N_A.csv',header=None)
df_neg2 = pd.read_csv('Dataset/Human/H_N_B.csv',header=None)
df = pd.concat([df_pos1,df_pos2,df_neg1,df_neg2])
df = df.reset_index()
df = df.drop('index', axis=1)
df = df.iloc[:,:].values
# print(type(df))
# print(len(df))
pro1 = []
# for i in range(len(df)):
for i in range(0,100):
    pro1.append(protein1[0])
pro1 = pd.DataFrame(pro1)
pt1 = pro1.iloc[:,:].values
p1_list = []
# for j in range(len(df)):
for i in range(0,100):
    p1_list=np.append(p1_list,p1)
p1_list =pd.DataFrame(p1_list)
# print(p1_list)
p2_list = []
# for j in range(len(df)):
for i in range(0,100):
    p2_list=np.append(p2_list,df[i])
p2_list =pd.DataFrame(p2_list)
protein = pd.concat((p1_list,p2_list),axis=1)
# print(protein)
# df = df.iloc[:,:].values
list2 = []
# for index in range(len(df)):
for index in range(0,100):
    p2= df[index][0]
    AAC2 = []
    CT2 = []
    LD2 = []

    acc2 = AAC.AAC(p2)
    AAC2.append(acc2)
    ct2 = CTriad.CTriad(p2)
    CT2.append(ct2)
    PS2 = p2
    CS2 = ld.classification_sequence_of(PS2)
    LD_INFO2 = ld.ld_info_of(CS2)
    LD_CODE2 = ld.ld_code_of_0(CS2)
    LD_CODE2 = ld.ld_code_of(PS2)
    LD2.append(LD_CODE2)
    AAC2 = pd.DataFrame(AAC2)
    CT2 = pd.DataFrame(CT2)
    LD2 = pd.DataFrame(LD2)
    protein2 = pd.concat([AAC2,CT2,LD2],axis=1)
    protein2 = protein2.iloc[:, :].values
    list2.append(protein2[0])
pro2 = pd.DataFrame(list2)
pt2 = pro2.iloc[:,:].values
intermediate_output_p1 = intermediate_layer_model.predict([pt1,pt2])
p_merge = pd.DataFrame(intermediate_output_p1)
p_merge=scaler.fit_transform(p_merge)
y_score = model.predict_proba(p_merge)
# print(type(y_score[0][0]))
# print(type(y_score))
score = y_score[:,1]
score = pd.DataFrame(score)
result = pd.concat((protein,score),axis=1)
result.to_csv(args.output,header=False, index=False)