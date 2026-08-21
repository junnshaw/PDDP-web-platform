import numpy as np
import scipy.io as sio
import scipy.sparse as sp
import random
import tensorflow as tf           
from tqdm import tqdm

#数据预处理中的归一化函数
def normalize_features(feat):

    degree = np.asarray(feat.sum(1)).flatten()  #每个邻接矩阵行元素之和为 度

    # set zeros to inf to avoid dividing by zero  将0设置为inf以避免被零除
    degree[degree == 0.] = np.inf     #np.inf表示正无穷
    degree_inv = 1. / degree
    degree_inv_mat = sp.diags([degree_inv], [0])    #从对角线构建矩阵
    feat_norm = degree_inv_mat.dot(feat)

    return feat_norm

def sample_mask(idx, l):  #构建样本掩码，掩码是全0矩阵，除了idx部分是1    创建 mask 并返回mask矩阵
    """
    :param idx: 有标签样本的索引列表
    :param l: 所有样本数量
    :return: 布尔类型数组，其中有标签样本所对应的位置为True，无标签样本所对应的位置为False
    """
    # np.zeros()函数创建一个给定形状和类型的用0填充的数组

    mask = np.zeros(l)
    mask[idx] = 1
    return np.array(mask, dtype=np.bool)

def load_label():
    print('loading labels...')
    labels = np.loadtxt("../data/adj.txt")

    temp_label = np.zeros((1373, 173))
    for temp in labels:
        temp_label[int(temp[0]) - 1, int(temp[1]) - 1] = int(temp[2])
    labels = temp_label


def load_data(graph_type,args):

    print('loading adj...')
    P = {}
    P_v ={}

    if graph_type == "net2":
        P = sio.loadmat('./data/net2.mat')
        #print(P)
        P_v = P['net2']
        #print(P_v)
        interaction = preprocess_adj(P)
    elif graph_type == "interaction":
        P = sio.loadmat('./data/interaction.mat')
        P_v = P['interaction']

        P = np.vstack((np.hstack((np.zeros(shape=(1373,1373),dtype=int), P_v)),np.hstack((P_v.transpose(),np.zeros(shape=(173,173),dtype=int)))))
        #np.hstack将参数元组的元素数组按水平方向进行叠加,np.vstack按垂直方向（行顺序）堆叠数组构成一个新的数组
        #a=np.hstack((np.zeros(shape=(1373,1373),dtype=int), P_v))
        #b=np.hstack((P_v.transpose(),np.zeros(shape=(173,173),dtype=int)))

        interaction = preprocess_adj(P)   #   interaction = preprocess_adj(P)


    interaction = sp.csr_matrix(interaction)
    attributes_list = []
    print('loading attributes...')
    for attribute in args.attributes:
        if attribute =='features':
            F1 = np.loadtxt("./data/MDAD/drug_features.txt")      # 读取txt文件   Python默认的数字的数据类型为双精度浮点数
            F2 = np.loadtxt("./data/MDAD/microbe_features.txt")
            feature = np.vstack((np.hstack((F1, np.zeros(shape=(F1.shape[0], F2.shape[1]), dtype=int))),
                                  np.hstack((np.zeros(shape=(F2.shape[0], F1.shape[0]), dtype=int), F2))))
            attributes_list.append(feature)

        elif attribute =='similarity':
            F1 = np.loadtxt("./data/MDAD/drug_similarity.txt")
            F2 = np.loadtxt("./data/MDAD/microbe_similarity.txt")
            similarity = np.vstack((np.hstack((F1, np.zeros(shape=(F1.shape[0], F2.shape[1]), dtype=int))),
                                     np.hstack((np.zeros(shape=(F2.shape[0], F1.shape[0]), dtype=int), F2))))
            attributes_list.append(similarity)

    features = np.hstack(attributes_list)
    features = normalize_features(features)
    features = sp.csr_matrix(features)

    num_drug = F1.shape[0]
    num_microbe =F2.shape[0]

    print('loading labels...')
    labels = np.loadtxt("./data/MDAD/adj.txt")

    temp_label = np.zeros((num_drug, num_microbe))
    for temp in labels:    #遍历
        temp_label[int(temp[0])-1, int(temp[1])-1] = int(temp[2])
    labels = temp_label

    #print("labels",labels)  ##

    return interaction, features, labels, num_drug, num_microbe


def load_dataset(dataset):

    print('loading adj...')
    P = {}
    P_v ={}

    print('loading attributes...')

    F1 = np.loadtxt("./data/"+dataset+"/drug_similarity.txt")
    F2 = np.loadtxt("./data/"+dataset+"/virus_similarity.txt")
    similarity = np.vstack((np.hstack((F1, np.zeros(shape=(F1.shape[0], F2.shape[1]), dtype=int))),
                             np.hstack((np.zeros(shape=(F2.shape[0], F1.shape[0]), dtype=int), F2))))

    similarity = sp.csr_matrix(similarity)

    num_drug = F1.shape[0]
    num_microbe =F2.shape[0]

    print('loading labels...')
    labels = np.loadtxt("./data/"+dataset+"/adj.txt")

    P_v = labels
    P = np.vstack((np.hstack((np.zeros(shape=(num_drug, num_drug), dtype=int), P_v)),
                   np.hstack((P_v.transpose(), np.zeros(shape=(num_microbe, num_microbe), dtype=int)))))
    interaction = preprocess_adj(P)
    interaction = sp.csr_matrix(interaction)

    return interaction, similarity, labels, num_drug, num_microbe

def generate_mask(labels,N):  
    num = 0
    A = sp.csr_matrix((labels[:,2],(labels[:,0]-1, labels[:,1]-1)),shape=(1373,173)).toarray()
    mask = np.zeros(A.shape)
    label_neg=np.zeros((1*N,2)) 
    while(num<1*N):
        a = random.randint(0,1372)
        b = random.randint(0,172)
        if A[a,b] != 1 and mask[a,b] != 1:
            mask[a,b] = 1
            label_neg[num,0]=a
            label_neg[num,1]=b
            num += 1
    mask = np.reshape(mask,[-1,1])  
    return mask,label_neg

def test_negative_sample(labels,N,negative_mask):  
    num = 0
    A = sp.csr_matrix((labels[:,2],(labels[:,0]-1, labels[:,1]-1)),shape=(1373,173)).toarray()  
    mask = np.zeros(A.shape)
    test_neg=np.zeros((1*N,2))  
    while(num<1*N):
        a = random.randint(0,1372)
        b = random.randint(0,172)
        if A[a,b] != 1 and mask[a,b] != 1:
            mask[a,b] = 1
            test_neg[num,0]=a
            test_neg[num,1]=b
            num += 1
    return test_neg

def div_list(ls,n):
    ls_len=len(ls)  
    j = ls_len//n
    ls_return = []  
    for i in range(0,(n-1)*j,j):  
        ls_return.append(ls[i:i+j])  
    ls_return.append(ls[(n-1)*j:])  
    return ls_return

def glorot(shape, name=None):
    init_range = np.sqrt(6.0/(shape[0] +shape[1]))     #Glorot 均匀分布初始化器
    initial = tf.random.uniform(shape, minval=-init_range, maxval=init_range, dtype=tf.float32)
    return tf.Variable(initial, name=name)

def normalize_adj(adj):
    adj = sp.coo_matrix(adj)  # 转换为稀疏矩阵存储   （1373*173）
    rowsum = np.array(adj.sum(1))            #（1373*1）
    d_inv_sqrt = np.power(rowsum, -0.5).flatten()    #（1373,）
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.
    d_mat_inv_sqrt = sp.diags(d_inv_sqrt)            #(1373*1373)
    adj = adj.dot(d_mat_inv_sqrt).transpose().dot(d_mat_inv_sqrt)
    return adj.toarray()

def preprocess_adj(adj):
    #adj_normalized = normalize_adj(adj)+np.eye(adj.shape[0])
    #a=np.eye(adj.shape[0],adj.shape[1])    # 1373*173，对角线为1
    #b=sp.eye(adj.shape[0])  # 1373*1373      adj：1373*173     adj:dict
    #c=sp.eye(adj.shape[0],adj.shape[1])
    #d=np.eye(adj['interaction'].shape[0])     #1373*1373   p_v:1373*173
    #e=eval(np.eye(adj['interaction'].shape[0]))
    m=adj.shape[0]
    n=np.eye(adj.shape[0])
    adj_normalized = adj+np.eye(adj.shape[0])
    #adj_normalized = adj +np.eye(adj.shape[0],adj.shape[1])##

    #adj_normalized = normalize_adj(adj + np.eye(adj.shape[0]))
    #adj_normalized = normalize_adj(adj + sp.eye(adj.shape[0]))  #邻接矩阵+单位矩阵,前者是方阵
    return adj_normalized

#numpy.eye(N,M=None, k=0, dtype=<type ‘float’>)  第一个参数：输出方阵（行数=列数）的规模，即行数或列数    第三个参数：默认情况下输出的是对角线全“1”，其余全“0”的方阵，如果k为正整数，则在右上方第k条对角线全“1”其余全“0”，k为负整数则在左下方第k条对角线全“1”其余全“0”。
#scipy.sparse.eye(m, n=None, k=0, dtype=<class 'float'>, format=None)
#对角线上的稀疏矩阵,返回稀疏(M X N)矩阵，其中第k条对角线全为1，其他所有内容均为0。
#参数 m(集成)：行数。n(整型，可选):列数。默认值：m 。k(整型，可选):对角线放置一个。默认值：0(主对角线)。dtype(数据类型，可选):矩阵的数据类型。format(字符串，可选):结果的稀疏格式，例如，FORMAT=“CSR”等。