import numpy as np
import pandas as pd
from keras.preprocessing import sequence
import keras
from keras import backend as K
from keras.models import load_model
import argparse
import h5py
import csv
from rdkit import Chem
from rdkit.Chem import AllChem
seq_rdic = ['A', 'I', 'L', 'V', 'F', 'W', 'Y', 'N', 'C', 'Q', 'M', 'S', 'T', 'D', 'E', 'R', 'H', 'K', 'G', 'P', 'O',
            'U', 'X', 'B', 'Z']
seq_dic = {w: i + 1 for i, w in enumerate(seq_rdic)}

#摩根转换及相关csv生成
def smiles_to_morgan():
    # smiles_path = './input/morgan_test.csv'
    morgan_train = pd.read_csv('./input/morgan_test.csv')
    outfile = open('./input/morgan_test.csv', 'w')
    outfile.write('Compound_ID,SMILES,morgan_fp\n')
    for i in range(len(morgan_train)):
        temp = Chem.MolFromSmiles(morgan_train['SMILES'][i])
        fp = AllChem.GetMorganFingerprintAsBitVect(temp, radius=2, nBits=2048).ToBitString()
        fp = '\t'.join(str(i) for i in fp)
        outfile.write(morgan_train['Compound_ID'][i])
        outfile.write(',')
        outfile.write(morgan_train['SMILES'][i])
        outfile.write(',')
        outfile.write(fp)
        outfile.write('\n')
    # with open('predict_data/morgan_test.csv','r') as csvfile:
    #     reader = csv.reader(csvfile)
    #     Compound_ID = [row[0] for row in reader]
    #     usertxt=Compound_ID[1]
    #     print(usertxt)

#复制药物ID和Smiles串，数量等同于测试csv中蛋白质的数量
def copy_drug():
    df_drug=pd.read_csv('./input/morgan_test.csv',engine='python')
    df_protein=pd.read_csv('./input/protein_test.csv',engine='python')
    df_drug_x, df_drug_y = df_protein.shape
    drug = df_drug.iloc[0]
    for i in range(df_drug_x - 1):
        df_drug.loc[df_drug.shape[0]] = drug

    df_data = pd.concat([df_drug, df_protein], axis=1)
    df_data.to_csv('./input/data.csv', index=False)


    df_del=pd.read_csv('./input/data.csv',engine='python')
    # dfdel=df_del.drop(["Protein_ID","Sequence"],axis=1)
    dfdel=df_del.drop(["morgan_fp"],axis=1)
    dfdel.to_csv('./input/data.csv',index=False)

    df=pd.read_csv('./input/data.csv',engine='python')
    df.insert(3, 'Label', 0, allow_duplicates=False)
    df.to_csv('./input/data.csv',index=False)


    # print("del")

    print('copy finish')


def encodeSeq(seq, seq_dic):
    if pd.isnull(seq):
        return [0]
    else:
        return [seq_dic[aa] for aa in seq]


def encodeSeq(seq, seq_dic):
    if pd.isnull(seq):
        return [0]
    else:
        return [seq_dic[aa] for aa in seq]


def parse_data(dti_dir, drug_dir, protein_dir, with_label=True,
               prot_len=2500, prot_vec="Convolution",
               drug_vec="Convolution", drug_len=2048):
    print("Parsing {0} , {1}, {2} with length {3}, type {4}".format(
        *[dti_dir, drug_dir, protein_dir, prot_len, prot_vec]))

    protein_col = "Protein_ID"
    drug_col = "Compound_ID"
    col_names = [protein_col, drug_col]
    if with_label:
        label_col = "Label"
        col_names += [label_col] 
    print(dti_dir)
    dti_df = pd.read_csv(dti_dir[0])
    drug_df = pd.read_csv(drug_dir[0], index_col="Compound_ID")
    protein_df = pd.read_csv(protein_dir[0], index_col="Protein_ID")

    if prot_vec == "Convolution":
        protein_df["encoded_sequence"] = protein_df.Sequence.map(lambda a: encodeSeq(a, seq_dic))
    dti_df = pd.merge(dti_df, protein_df, left_on=protein_col, right_index=True)
    dti_df = pd.merge(dti_df, drug_df, left_on=drug_col, right_index=True)
    drug_feature = np.stack(dti_df[drug_vec].map(lambda fp: fp.split("\t")))
    if prot_vec == "Convolution":
        protein_feature = sequence.pad_sequences(dti_df["encoded_sequence"].values, prot_len)
    else:
        protein_feature = np.stack(dti_df[prot_vec].map(lambda fp: fp.split("\t")))
    if with_label:
        label = dti_df[label_col].values
        print("\tPositive data : %d" % (sum(dti_df[label_col])))
        print("\tNegative data : %d" % (dti_df.shape[0] - sum(dti_df[label_col])))
        return {"protein_feature": protein_feature, "drug_feature": drug_feature, "label": label,
                "Compound_ID": dti_df["Compound_ID"].tolist(), "Protein_ID": dti_df["Protein_ID"].tolist()}
    else:
        return {"protein_feature": protein_feature, "drug_feature": drug_feature,
                "Compound_ID": dti_df["Compound_ID"].tolist(), "Protein_ID": dti_df["Protein_ID"].tolist()}


if __name__ == "__main__":

##morgan
    smiles_to_morgan()
    # print('finish1')
    copy_drug()
    # print('finish2')

    parser = argparse.ArgumentParser()
    # parser.add_argument("model")
    # test_params
    parser.add_argument("--test-name", default="Prediction", help="Name of test data sets", nargs="*")
    parser.add_argument("--test-dti-dir", default="./input/data.csv", help="Test dti [drug, target, [label]]", nargs="*")
    parser.add_argument("--test-drug-dir", default="./input/morgan_test.csv",
                        help="Test drug information [drug, SMILES,[feature_name, ..]]", nargs="*")
    parser.add_argument("--test-protein-dir", default="./input/protein_test.csv",
                        help="Test Protein information [protein, seq, [feature_name]]", nargs="*")
    parser.add_argument("--with-label", "-W", help="Existence of label information in test DTI", action="store_true",
                        default=True)
    parser.add_argument("--output", default="./output/output.csv", help="Prediction output", type=str)
    parser.add_argument("--prot-vec",
                        help="Type of protein feature, if Convolution, it will execute conlvolution on sequeunce",
                        type=str, default="Convolution")
    parser.add_argument("--prot-len", help="Protein vector length", default=2500, type=int)
    parser.add_argument("--drug-vec", help="Type of drug feature", type=str, default="morgan_fp")
    parser.add_argument("--drug-len", help="Drug vector length", default=2048, type=int)
    parser.add_argument("--model", default="./input/model.hdf5", help="Test dti [drug, target, [label]]", type=str)
    args = parser.parse_args()

    model = args.model

    test_name = args.test_name
    test_dti = args.test_dti_dir
    test_protein = args.test_protein_dir
    test_drug = args.test_drug_dir

    # test_sets = zip(test_names, tests, test_drugs, test_proteins)
    # for i in test_sets:
    #     print(i)
    with_label = args.with_label
    output_file = args.output

    f = h5py.File(model, 'r+')

    try:
        f.__delitem__("optimizer_weights")
    except:
        print("optimizer_weights are already deleted")

    f.close()

    type_params = {
        "prot_vec": args.prot_vec,
        "prot_len": args.prot_len,
        "drug_vec": args.drug_vec,
        "drug_len": args.drug_len,
    }

    # for test_name, test_dti, test_drug, test_protein in test_sets:
    #     test_dic = {test_name: parse_data(test_dti, test_drug, test_protein, with_label=with_label, **type_params)}
    # print("test_dic:")
    # print(test_dic)
    test_dic = {test_name: parse_data(test_dti, test_drug, test_protein, with_label=with_label, **type_params)}

    loaded_model = load_model(model)
    print("prediction")
    result_df = pd.DataFrame()
    result_columns = []
    for dataset in test_dic:
        temp_df = pd.DataFrame()
        prediction_dic = test_dic[dataset]
        N = int(prediction_dic["drug_feature"].shape[0] / 50)
        d_splitted = np.array_split(prediction_dic["drug_feature"], N)
        p_splitted = np.array_split(prediction_dic["protein_feature"], N)
        predicted = sum([np.squeeze(loaded_model.predict([d, p])).tolist() for d, p in zip(d_splitted, p_splitted)], [])
        temp_df[dataset, 'predicted'] = predicted
        temp_df[dataset, 'Compound_ID'] = prediction_dic["Compound_ID"]
        temp_df[dataset, 'Protein_ID'] = prediction_dic["Protein_ID"]
        if with_label:
            temp_df[dataset, 'label'] = np.squeeze(test_dic[dataset]['label'])
        result_df = pd.concat([result_df, temp_df], ignore_index=True, axis=1)
        result_columns.append((dataset, "predicted"))
        result_columns.append((dataset, "Compound_ID"))
        result_columns.append((dataset, "Protein_ID"))
        if with_label:
            result_columns.append((dataset, "label"))
    result_df.columns = pd.MultiIndex.from_tuples(result_columns)
    print("save to %s" % output_file)
    result_df.to_csv(output_file, index=False)
    # output_df.sort_values(by=['Pred'], ascending=False).to_csv(csv_save_model, index=False)
    result_sort=pd.read_csv(output_file,header=1)
    result_sort.sort_values(by=['predicted'], ascending=False).to_csv(output_file, index=False)
    '''
    predicted = loaded_model.predict([prediction_dic["drug_feature"],prediction_dic["protein_feature"]])
    dti_dic = prediction_dic['dti']
    dti_dic["predicted"] = predicted
    dti_dic.to_csv(output)
    '''
