import numpy as np
import pandas as pd
import torch
from torch.utils import data
from tqdm import tqdm

torch.manual_seed(2)  # reproducible torch:2 np:3
np.random.seed(3)
from argparse import ArgumentParser
from pre_stream import BIN_Data_Encoder

use_cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if use_cuda else "cpu")

parser = ArgumentParser(description='MolTrans Training.')
parser.add_argument('-b', '--batch-size', default=8, type=int,metavar='N')
parser.add_argument('-j', '--workers', default=8, type=int, metavar='N')
parser.add_argument('-o', '--csv_save_model', default='out.csv', type=str, metavar='N')
parser.add_argument('-id','--input_drug',default='../input/drug.csv')
parser.add_argument('-ip','--input_protein',default='/nfs_storage/Website_Client/dti_input/protein.csv')
parser.add_argument('-m','--input_model',default='/nfs_storage/Website_Client/dti_input/model.pth')

def predict(data_generator, model,csv_save_model):
    y_pred = []
    y_drug = []
    y_protein = []
    model.eval()
    for i, (drug, protein, d, p, d_mask, p_mask) in enumerate(tqdm(data_generator)):
        score = model(d.long(), p.long(), d_mask.long(), p_mask.long())
        # score = model(d.long().cuda(), p.long().cuda(), d_mask.long().cuda(), p_mask.long().cuda())
        m = torch.nn.Sigmoid()
        logits = torch.squeeze(m(score))
        logits = logits.detach().cpu().numpy()
        y_pred = y_pred + logits.flatten().tolist()

        drug = list(drug)
        protein = list(protein)
        y_drug = y_drug + drug
        y_protein = y_protein + protein

        y_drug_df = pd.DataFrame({'SMILES': y_drug})
        y_protein_df = pd.DataFrame({'Protein': y_protein})
        y_pred_df = pd.DataFrame({'Pred': y_pred})

        output_df = pd.concat([y_drug_df, y_protein_df], axis=1)
        output_df = pd.concat([output_df, y_pred_df], axis=1)

        # 降序排列
        output_df.sort_values(by=['Pred'], ascending=False).to_csv(csv_save_model, index=False)

    return

def main():
    args = parser.parse_args()

    model = torch.load(args.input_model, map_location=torch.device('cpu'))
    # model = torch.load(args.input_model)

    # model = model.cuda()

    params = {'batch_size': args.batch_size,
              'shuffle': False,
              'num_workers': args.workers,
              'drop_last': True}

    df_drug = pd.read_csv(args.input_drug)
    df_protein = pd.read_csv(args.input_protein)

    #将药物进行复制
    df_drug_x, df_drug_y = df_protein.shape
    drug = df_drug.iloc[0]
    for i in range(df_drug_x - 1):
        df_drug.loc[df_drug.shape[0]] = drug

    df_data = pd.concat([df_drug, df_protein], axis=1)
    # df_data.to_csv('./input/data.csv', index=False)

    # df_data = pd.read_csv('./input/data.csv')
    predicting_set = BIN_Data_Encoder(df_data.index.values, df_data)
    predicting_generator = data.DataLoader(predicting_set, **params)

    print('--- Go for Predicting ---')
    predict(predicting_generator, model,args.csv_save_model)

main()
print("Done!")

