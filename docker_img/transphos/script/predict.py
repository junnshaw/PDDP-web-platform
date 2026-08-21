import functools
import itertools
import os,sys
import random
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import csv
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.layers import Dense, Activation, Flatten, Dropout, Reshape
from tensorflow.keras.layers import Conv1D,Conv2D, MaxPooling2D
from tensorflow.keras.models import Sequential,Model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import optimizers
from tensorflow.keras.optimizers import Adam,SGD
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.regularizers import l2
pwd = os.path.dirname(os.path.abspath(__file__)) 
import copy
import time
model_S_weight = pwd+'/PELM_S.h5'
model_T_weight = pwd+'/PELM_T.h5'
model_Y_weight = pwd+'/PELM_Y.h5'
def predict(train_file_name,sites,outfile='./output/results.txt'):
    
    win1 = 51
    win2 = 33
    
    from dataprocess_predict import getMatrixInput
    [X_test1,y_test,ids,position] = getMatrixInput(train_file_name, sites, win1)
    [X_test2,_,_,_] = getMatrixInput(train_file_name, sites, win2)
    

    from transnet import transphos
    model = transphos(X_test1, X_test2, y_test)
    #根据sites不同来加载模型
    if sites=='S':
        model.load_weights(model_S_weight)
    elif sites=='T':
        model.load_weights(model_T_weight)
    else:
        model.load_weights(model_Y_weight)  
    predictions_t = model.predict([X_test1, X_test2])
    results_ST = np.column_stack((ids,position,predictions_t[:, 1]))
    result = pd.DataFrame(results_ST)
    outputfile = outfile
    result.to_csv(outfile, index=False, header=None, sep='\t',
                  quoting=csv.QUOTE_NONNUMERIC)



if __name__ == '__main__':
    print(time.ctime())
    data_csv = sys.argv[1]#输入csv
    site = sys.argv[2]#'Y'
    outfile = sys.argv[3]#输出txt
    predict(data_csv,site,outfile)
    print(time.ctime())

