import DNNXGB
import numpy as np
import pandas as pd

from keras.models import Model

from sklearn.preprocessing import RobustScaler
import argparse
import AAC
import CTriad
import ld
from xgboost import XGBClassifier
parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, default='/input/dnnxgb.csv')
parser.add_argument('--output', type=str, default='/output/output.csv')
args = parser.parse_args()

df_pos = pd.read_csv(r'Dataset/Human_Bacillus_Anthracis/HBA_P.csv',header=None)
df_neg = pd.read_csv(r'Dataset/Human_Bacillus_Anthracis/HBA_N.csv',header=None)
# df_pos = pd.read_csv(r'/home/aita/HL/Dataset/Human/H_P.csv',header=None)
# df_neg = pd.read_csv(r'/home/aita/HL/Dataset/Human/H_N.csv',header=None)
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
# scaler = StandardScaler().fit(X)
scaler = RobustScaler().fit(X)
X = scaler.transform(X)

X1_train = X[:,0:993]
X2_train = X[:,993:]
model=DNNXGB.define_model()
model.fit([X1_train, X2_train], y, epochs=10, batch_size=64, verbose=0)
# # model.save('/home/aita/HL/model.h5')
# # def read_protein(path):
# #     with open(path) as f:
# #         seq = f.read()
# #     return seq
# # p1 = read_protein('../Dataset/input1.csv')
# # p2 = read_protein('../Dataset/input2.csv')
intput_p = pd.read_csv(args.input,header=None)#p1=pd.read_csv(args.input1)

protein = intput_p.iloc[:,:].values

p1 = protein[0][0]
p2 = protein[0][1]
# # p1 = 'MFDHDVEYLITALSSETRIQYDQRLLDEIAANVVYYVPRVKSPDTLYRLVGALFRSQFIVQLPPLRLLHIVKDVFLWKLEVSEPTLPISKFYLVWNAVFESHRATWNLSQLMVLDGVLVTYPSFKQLNNAYFIDESSNKTALYYRNWKLQLFSPIWAQLWNTAIVRANLSIQHCLLIALALLFNQSNRSALLHGVDVSWNLVTEKLLDLLEEYVHGIVQPMEIFSTDSVLSTNLNHLASCLTSSITRSNEATLVNSVRKLERICRYLSDTVASLKEQQLDFKFQNVFILIILALKELSAMNMTILPNHKDTFYSMICLSLFHVHVLTQKIGTVGFPSYDYVYDNLVTYFIVMDDLSKITTVLELMKRNNTKQDPNKLVFYINFLNKITNYYGCRIRLPFITEFIEPLLHFDVFFSGKTGNTLDIEIKESIHTLTITVLSIDSSYSSQVAQWQVSRILVYLKMSMDQFIAGKLSANQILLIFGHLSTQLPSLHNYNKHLLRDSLHETYIRIVNVKNPEKKNVLIECLIVQIAFINNPHHLIGWLNICLQLINTHNKKLLQQLWEMVSSLESSLAIDWWYTTVLSSQSSKL'
# # p2 = 'MEGVYFNIDNGFIEGVVRGYRNGLLSNNQYINLTQCDTLEDLKLQLSSTDYGNFLSSVSSESLTTSLIQEYASSKLYHEFNYIRDQSSGSTRKFMDYITYGYMIDNVALMITGTIHDRDKGEILQRCHPLGWFDTLPTLSVATDLESLYETVLVDTPLAPYFKNCFDTAEELDDMNIEIIRNKLYKAYLEDFYNFVTEEIPEPAKECMQTLLGFEADRRSINIALNSLQSSDIDPDLKSDLLPNIGKLYPLATFHLAQAQDFEGVRAALANVYEYRGFLETGNLEDHFYQLEMELCRDAFTQQFAISTVWAWMKSKEQEVRNITWIAECIAQNQRERINNYISVY'
AAC1 = []
CT1 = []
LD1 = []
AAC2 = []
CT2 = []
LD2 = []
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
AAC1 = pd.DataFrame(AAC1)
CT1 = pd.DataFrame(CT1)
LD1 = pd.DataFrame(LD1)
AAC2 = pd.DataFrame(AAC2)
CT2 = pd.DataFrame(CT2)
LD2 = pd.DataFrame(LD2)
protein1 = pd.concat([AAC1,CT1,LD1],axis=1)
# print(protein1)
protein2 = pd.concat([AAC2,CT2,LD2],axis=1)

intermediate_layer_model = Model(inputs=model.input,outputs=model.get_layer('merged_protein1_2').output)
intermediate_output_p1 = intermediate_layer_model.predict([X1_train,X2_train])
p_merge = pd.DataFrame(intermediate_output_p1)
X_train_feat=pd.concat((p_merge,pd.DataFrame(pd.DataFrame(Trainlabels))),axis=1,ignore_index=True)
# X_train_feat.to_csv('X_train.csv',header=False, index=False)
# Train=pd.read_csv("X_train.csv",header=None)
Train = X_train_feat
Train=Train.sample(frac=1)
X=Train.iloc[:,0:128].values
y=Train.iloc[:,128:].values

extracted_df=X_train_feat
scaler=RobustScaler()
X=scaler.fit_transform(X)
model = XGBClassifier(n_estimators=100)
model.fit(X,y)
intermediate_output_p1 = intermediate_layer_model.predict([protein1,protein2])
p_merge = pd.DataFrame(intermediate_output_p1)
p_merge=scaler.fit_transform(p_merge)
y_score = model.predict_proba(p_merge)

result = y_score[0][1]
score = []
score = np.append(score,result)
score = pd.DataFrame(score)
output = pd.concat((intput_p,score),axis=1)
output.to_csv(args.output,header=False, index=False)
