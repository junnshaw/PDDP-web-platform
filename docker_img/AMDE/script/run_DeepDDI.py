import argparse
import os
import shutil
import logging
import time
import csv
import pandas as pd
import numpy as np
import DeepDDI
import preprocessing
import result_processing

def find_ID():
    with open ("/input/input_structures.txt", 'r') as file1:
    # data = file1.readline()
        for line in file1:

            sptlist = line.strip().split(' ')
            drug1 = sptlist[0].strip()
            smiles1 = sptlist[1].strip()

        with open("/input/final_input.txt","w") as f:
            with open("/resource/druglist.csv", 'r') as file:
                reader = csv.reader(file)
                rows = [row for row in reader]
                # print len(rows)
                for i in range(len(rows)):
                    # print line
                    temp=rows[i]
                    db_id=temp[0]
                    db_smiles=temp[1]
                    f.write(drug1)
                    f.write('\t')
                    f.write(smiles1)
                    f.write('\t')
                    f.write(db_id)
                    f.write('\t')
                    f.write(db_smiles)
                    f.write('\n')
                    # print('finish')

if __name__ == '__main__':
    find_ID()
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_csv',help="Output directory",default='/output/result.csv')
    # parser.add_argument('-o', '--output_dir',help="Output directory",default='/output')
    # output list
    # parser.add_argument('-o1', '--output_tanimoto',help="Output directory")
    # parser.add_argument('-o2', '--output_ddi',help="Output directory")
    # parser.add_argument('-o3', '--output_ddi_f',help="Output directory")
    # parser.add_argument('-o4', '--output_annotated',help="Output directory")
    # parser.add_argument('-o5', '--output_similarity',help="Output directory")
    # parser.add_argument('-o6', '--output_pca',help="Output directory")
    # parser.add_argument('-o7', '--output_result',help="Output directory")
    # output list
    parser.add_argument('-i', '--input_file',help="Input file",default='/input/final_input.txt')
    parser.add_argument('-p', '--PCA_profile_file', help="PCA profile file")
    
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    
    options = parser.parse_args()
    input_file = options.input_file
    output_csv = options.output_csv
    PCA_profile_file = options.PCA_profile_file
    ##
    # output_tanimoto = options.output_tanimoto
    # output_ddi = options.output_ddi
    # output_ddi_f = options.output_ddi_f
    # output_annotated = options.output_annotated
    # output_similarity = options.output_similarity
    # output_pca = options.output_pca
    # output_result = options.output_result
    ##



    drug_dir = './data/DrugBank5.0_Approved_drugs/'
    pca_model = './data/PCA_tanimoto_model_50.pkl'
    trained_weight_model = './data/deepddi_model.h5'
    
    multiclass_trained_model = './data/Multiclass_weight.ckpt'
    binaryclass_trained_model = './data/Binary_weight.ckpt'
    DDI_sentence_information_file = './data/Interaction_information.csv'
    
    known_DDI_file = './data/DrugBank_known_ddi.txt'
    drug_information_file = './data/Approved_drug_Information.txt'
    # print output_dir
    # if not os.path.isdir(output_dir):
    #     os.mkdir(output_dir)

    ddi_input_file = './tanimoto_PCA50_DDI_Input.csv'
    output_file = './DDI_result.txt'
    ddi_output_file = './Final_DDI_result.txt'
    annotation_output_file = './Final_annotated_DDI_result.txt'
    known_drug_similarity_file = './data/drug_similarity.csv'
    if PCA_profile_file == None:
        similarity_profile = './similarity_profile.csv'
        pca_similarity_profile = './PCA_transformed_similarity_profile.csv'
        pca_profile_file = './PCA_transformed_similarity_profile.csv'
        print 'calculate structure similarity profile'
        # print pca_model
        preprocessing.calculate_structure_similarity(drug_dir, input_file, similarity_profile)
        preprocessing.calculate_pca(similarity_profile, pca_similarity_profile, pca_model)

        print 'combine structural similarity profile'
        preprocessing.generate_input_profile(input_file, pca_similarity_profile, ddi_input_file)
    else:
        pca_similarity_profile = PCA_profile_file
        print 'generate input profile'
        preprocessing.generate_input_profile(input_file, pca_similarity_profile, ddi_input_file)
    
    threshold = 0.47
    DeepDDI.predict_DDI('', output_file, ddi_input_file, trained_weight_model, threshold)    
    result_processing.summarize_prediction_outcome(output_file, ddi_output_file, DDI_sentence_information_file)
    result_processing.annotate_similar_drugs(ddi_output_file, drug_information_file, similarity_profile, known_DDI_file, annotation_output_file, DDI_sentence_information_file, 0.75)
    
    logging.info(time.strftime("Elapsed time %H:%M:%S", time.gmtime(time.time() - start)))
    #sort result to csv
    # reader = open('./output_dir/DDI_result.txt')
    # list_data = reader.readlines()
    # # columns = list_data[0].split(',')


    # list = []
    # for i in list_data [1:]:
    #     list.append(i.split())
    # print(list)


    with open(output_csv, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, dialect='excel')
        fieldnames = ['Drug_pair','Predicted_class', 'Score']
        spamwriter.writerow(fieldnames)
        with open('./DDI_result.txt', 'rb') as filein:
            for line in filein:
                line_list = line.strip('\n').split('\t')
                spamwriter.writerow(line_list)
    # with open("./output_dir/test.csv","wb") as csvfile:
    #     writer = csv.writer(csvfile)
        
    #     writer.writerows(list)
    result_sort=pd.read_csv(output_csv,engine='python',header=1)
    result_sort.sort_values(by=['Score'], ascending=False).to_csv(output_csv, index=False)


