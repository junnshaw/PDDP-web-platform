import numpy as np
import scipy.sparse as sp

#函数的作用就是 返回一个稀疏矩阵的非0值坐标、非0值和整个矩阵的shape
def sparse_to_tuple(sparse_mx):
    if not sp.isspmatrix_coo(sparse_mx):    # 判断是否为coo_matrix类型
        sparse_mx = sparse_mx.tocoo()        # 返回稀疏矩阵的coo_matrix形式
        #这个coo_matrix类型 其实就是稀疏矩阵的坐标形式：（所有非0元素 （row，col））根据row和col对应的索引对应非0元素在矩阵中的位置，其他位置自动补0
    coords = np.vstack((sparse_mx.row, sparse_mx.col)).transpose() # vstack 按垂直方向排列 再转置 则每一行的两个元素组成的元组就是非0元素的坐标
    values = sparse_mx.data
    shape = sparse_mx.shape
    return coords, values, shape

#在模型构建之前将节点特征向量处理完成
#对称归一化邻接矩阵
def preprocess_graph(adj):
    #print(adj) ##
    adj = sp.coo_matrix(adj) ##    1373*173               转化为稀疏矩阵存储   在矩阵中，若数值为0的元素数目远远多于非0元素的数目，并且非0元素分布没有规律时，则称该矩阵为稀疏矩阵
    #print(adj) ##
    #a=sp.eye(adj.shape[0]) ##    1373*1373的对角线稀疏矩阵
    adj_ = adj + sp.eye(adj.shape[0])
    #adj_ = adj + sp.eye(adj.shape[0],adj.shape[1])    #   1373*173

    #print(adj_) ##
    rowsum = np.array(adj_.sum(1))    #      1373*1              每个邻接矩阵行元素之和为 度
    degree_mat_inv_sqrt = sp.diags(np.power(rowsum, -0.5).flatten())  #    1373*1373              度的(-1/2)次方、将度向量转换为对角矩阵（度矩阵）
    adj_normalized = adj_.dot(degree_mat_inv_sqrt).transpose().dot(degree_mat_inv_sqrt).tocoo()  #矩阵乘法，转置后相乘
    #adj_normalized = adj_.transpose().dot(degree_mat_inv_sqrt).dot(degree_mat_inv_sqrt).tocoo()  ##
    return sparse_to_tuple(adj_normalized)


def construct_feed_dict(adj_normalized, adj, features, placeholders):
    # construct feed dictionary
    feed_dict = dict()
    feed_dict.update({placeholders['features']: features})  #更新字典
    feed_dict.update({placeholders['adj']: adj_normalized})
    feed_dict.update({placeholders['adj_orig']: adj})
    return feed_dict
