import torch
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import add_self_loops, degree, softmax
from torch_geometric.nn import global_add_pool, global_mean_pool, global_max_pool, GlobalAttention, Set2Set
import torch.nn.functional as F
from torch_scatter import scatter_add
from torch_geometric.nn.inits import glorot, zeros
import copy
import random
import torch.nn as nn
from samples import sample_datasets, sample_test_datasets, sample_premeta_datasets
from loader import MoleculeDataset
from torch_geometric.data import DataLoader
import torch.optim as optim
from tqdm import tqdm
import numpy as np
from sklearn.metrics import roc_auc_score
from torch.nn.utils.convert_parameters import (vector_to_parameters,
                                               parameters_to_vector)

num_atom_type = 120 #including the extra mask tokens
num_chirality_tag = 3

num_bond_type = 6 #including aromatic and self-loop edge, and extra masked tokens
num_bond_direction = 3 

class GINConv(MessagePassing):
    """
    Extension of GIN aggregation to incorporate edge information by concatenation.

    Args:
        emb_dim (int): dimensionality of embeddings for nodes and edges.
        embed_input (bool): whether to embed input or not. 
        

    See https://arxiv.org/abs/1810.00826
    """
    def __init__(self, emb_dim, aggr = "add"):
        super(GINConv, self).__init__()
        #multi-layer perceptron
        self.mlp = torch.nn.Sequential(torch.nn.Linear(emb_dim, 2*emb_dim), torch.nn.ReLU(), torch.nn.Linear(2*emb_dim, emb_dim))
        self.edge_embedding1 = torch.nn.Embedding(num_bond_type, emb_dim)
        self.edge_embedding2 = torch.nn.Embedding(num_bond_direction, emb_dim)

        torch.nn.init.xavier_uniform_(self.edge_embedding1.weight.data)
        torch.nn.init.xavier_uniform_(self.edge_embedding2.weight.data)
        self.aggr = aggr

    def forward(self, x, edge_index, edge_attr):
        #add self loops in the edge space
        edge_index = add_self_loops(edge_index, num_nodes = x.size(0))[0]

        #add features corresponding to self-loop edges.
        self_loop_attr = torch.zeros(x.size(0), 2)
        self_loop_attr[:,0] = 4 #bond type for self-loop edge
        self_loop_attr = self_loop_attr.to(edge_attr.device).to(edge_attr.dtype)
        edge_attr = torch.cat((edge_attr, self_loop_attr), dim = 0)

        edge_embeddings = self.edge_embedding1(edge_attr[:,0]) + self.edge_embedding2(edge_attr[:,1])

        return self.propagate(edge_index, x=x, edge_attr=edge_embeddings)

    def message(self, x_j, edge_attr):
        return x_j + edge_attr

    def update(self, aggr_out):
        return self.mlp(aggr_out)


class GCNConv(MessagePassing):

    def __init__(self, emb_dim, aggr = "add"):
        super(GCNConv, self).__init__()

        self.emb_dim = emb_dim
        self.linear = torch.nn.Linear(emb_dim, emb_dim)
        self.edge_embedding1 = torch.nn.Embedding(num_bond_type, emb_dim)
        self.edge_embedding2 = torch.nn.Embedding(num_bond_direction, emb_dim)

        torch.nn.init.xavier_uniform_(self.edge_embedding1.weight.data)
        torch.nn.init.xavier_uniform_(self.edge_embedding2.weight.data)

        self.aggr = aggr

    def norm(self, edge_index, num_nodes, dtype):
        ### assuming that self-loops have been already added in edge_index
        edge_weight = torch.ones((edge_index.size(1), ), dtype=dtype,
                                     device=edge_index.device)
        row, col = edge_index
        deg = scatter_add(edge_weight, row, dim=0, dim_size=num_nodes)
        deg_inv_sqrt = deg.pow(-0.5)
        deg_inv_sqrt[deg_inv_sqrt == float('inf')] = 0

        return deg_inv_sqrt[row] * edge_weight * deg_inv_sqrt[col]


    def forward(self, x, edge_index, edge_attr):
        #add self loops in the edge space
        edge_index = add_self_loops(edge_index, num_nodes = x.size(0))[0]

        #add features corresponding to self-loop edges.
        self_loop_attr = torch.zeros(x.size(0), 2)
        self_loop_attr[:,0] = 4 #bond type for self-loop edge
        self_loop_attr = self_loop_attr.to(edge_attr.device).to(edge_attr.dtype)
        edge_attr = torch.cat((edge_attr, self_loop_attr), dim = 0)

        edge_embeddings = self.edge_embedding1(edge_attr[:,0]) + self.edge_embedding2(edge_attr[:,1])

        norm = self.norm(edge_index, x.size(0), x.dtype)

        x = self.linear(x)

        return self.propagate(edge_index, x=x, edge_attr=edge_embeddings, norm = norm)

    def message(self, x_j, edge_attr, norm):
        return norm.view(-1, 1) * (x_j + edge_attr)


class GATConv(MessagePassing):
    def __init__(self, emb_dim, heads=2, negative_slope=0.2, aggr = "add"):
        super(GATConv, self).__init__()

        self.aggr = aggr

        self.emb_dim = emb_dim
        self.heads = heads
        self.negative_slope = negative_slope

        self.weight_linear = torch.nn.Linear(emb_dim, heads * emb_dim)
        self.att = torch.nn.Parameter(torch.Tensor(1, heads, 2 * emb_dim))

        self.bias = torch.nn.Parameter(torch.Tensor(emb_dim))

        self.edge_embedding1 = torch.nn.Embedding(num_bond_type, heads * emb_dim)
        self.edge_embedding2 = torch.nn.Embedding(num_bond_direction, heads * emb_dim)

        torch.nn.init.xavier_uniform_(self.edge_embedding1.weight.data)
        torch.nn.init.xavier_uniform_(self.edge_embedding2.weight.data)

        self.reset_parameters()

    def reset_parameters(self):
        glorot(self.att)
        zeros(self.bias)

    def forward(self, x, edge_index, edge_attr):

        #add self loops in the edge space
        edge_index = add_self_loops(edge_index, num_nodes = x.size(0))[0]

        #add features corresponding to self-loop edges.
        self_loop_attr = torch.zeros(x.size(0), 2)
        self_loop_attr[:,0] = 4 #bond type for self-loop edge
        self_loop_attr = self_loop_attr.to(edge_attr.device).to(edge_attr.dtype)
        edge_attr = torch.cat((edge_attr, self_loop_attr), dim = 0)

        edge_embeddings = self.edge_embedding1(edge_attr[:,0]) + self.edge_embedding2(edge_attr[:,1])

        x = self.weight_linear(x).view(-1, self.heads, self.emb_dim)
        return self.propagate(edge_index, x=x, edge_attr=edge_embeddings)

    def message(self, edge_index, x_i, x_j, edge_attr):
        edge_attr = edge_attr.view(-1, self.heads, self.emb_dim)
        x_j += edge_attr

        alpha = (torch.cat([x_i, x_j], dim=-1) * self.att).sum(dim=-1)

        alpha = F.leaky_relu(alpha, self.negative_slope)
        alpha = softmax(alpha, edge_index[0])

        return x_j * alpha.view(-1, self.heads, 1)

    def update(self, aggr_out):
        aggr_out = aggr_out.mean(dim=1)
        aggr_out = aggr_out + self.bias

        return aggr_out


class GraphSAGEConv(MessagePassing):
    def __init__(self, emb_dim, aggr = "mean"):
        super(GraphSAGEConv, self).__init__()

        self.emb_dim = emb_dim
        self.linear = torch.nn.Linear(emb_dim, emb_dim)
        self.edge_embedding1 = torch.nn.Embedding(num_bond_type, emb_dim)
        self.edge_embedding2 = torch.nn.Embedding(num_bond_direction, emb_dim)

        torch.nn.init.xavier_uniform_(self.edge_embedding1.weight.data)
        torch.nn.init.xavier_uniform_(self.edge_embedding2.weight.data)

        self.aggr = aggr

    def forward(self, x, edge_index, edge_attr):
        #add self loops in the edge space
        edge_index = add_self_loops(edge_index, num_nodes = x.size(0))[0]

        #add features corresponding to self-loop edges.
        self_loop_attr = torch.zeros(x.size(0), 2)
        self_loop_attr[:,0] = 4 #bond type for self-loop edge
        self_loop_attr = self_loop_attr.to(edge_attr.device).to(edge_attr.dtype)
        edge_attr = torch.cat((edge_attr, self_loop_attr), dim = 0)

        edge_embeddings = self.edge_embedding1(edge_attr[:,0]) + self.edge_embedding2(edge_attr[:,1])

        x = self.linear(x)

        return self.propagate(edge_index, x=x, edge_attr=edge_embeddings)

    def message(self, x_j, edge_attr):
        return x_j + edge_attr

    def update(self, aggr_out):
        return F.normalize(aggr_out, p = 2, dim = -1)



class GNN(torch.nn.Module):
    """
    

    Args:
        num_layer (int): the number of GNN layers
        emb_dim (int): dimensionality of embeddings
        JK (str): last, concat, max or sum.
        max_pool_layer (int): the layer from which we use max pool rather than add pool for neighbor aggregation
        drop_ratio (float): dropout rate
        gnn_type: gin, gcn, graphsage, gat

    Output:
        node representations

    """
    def __init__(self, num_layer, emb_dim, JK = "last", drop_ratio = 0, gnn_type = "gin"):
        super(GNN, self).__init__()
        self.num_layer = num_layer
        self.drop_ratio = drop_ratio
        self.JK = JK

        if self.num_layer < 2:
            raise ValueError("Number of GNN layers must be greater than 1.")

        self.x_embedding1 = torch.nn.Embedding(num_atom_type, emb_dim)
        self.x_embedding2 = torch.nn.Embedding(num_chirality_tag, emb_dim)

        torch.nn.init.xavier_uniform_(self.x_embedding1.weight.data)
        torch.nn.init.xavier_uniform_(self.x_embedding2.weight.data)

        ###List of MLPs
        self.gnns = torch.nn.ModuleList()
        for layer in range(num_layer):
            if gnn_type == "gin":
                self.gnns.append(GINConv(emb_dim, aggr = "add"))
            elif gnn_type == "gcn":
                self.gnns.append(GCNConv(emb_dim))
            elif gnn_type == "gat":
                self.gnns.append(GATConv(emb_dim))
            elif gnn_type == "graphsage":
                self.gnns.append(GraphSAGEConv(emb_dim))

        ###List of batchnorms
        self.batch_norms = torch.nn.ModuleList()
        for layer in range(num_layer):
            self.batch_norms.append(torch.nn.BatchNorm1d(emb_dim))

    #def forward(self, x, edge_index, edge_attr):
    def forward(self, *argv):
        if len(argv) == 3:
            x, edge_index, edge_attr = argv[0], argv[1], argv[2]
        elif len(argv) == 1:
            data = argv[0]
            x, edge_index, edge_attr = data.x, data.edge_index, data.edge_attr
        else:
            raise ValueError("unmatched number of arguments.")

        x = self.x_embedding1(x[:,0]) + self.x_embedding2(x[:,1])

        h_list = [x]
        for layer in range(self.num_layer):

            h = self.gnns[layer](h_list[layer], edge_index, edge_attr)
            h = self.batch_norms[layer](h)
            #h = F.dropout(F.relu(h), self.drop_ratio, training = self.training)
            if layer == self.num_layer - 1:
                #remove relu for the last layer
                h = F.dropout(h, self.drop_ratio, training = self.training)
            else:
                h = F.dropout(F.relu(h), self.drop_ratio, training = self.training)
            h_list.append(h)

        ### Different implementations of Jk-concat
        if self.JK == "concat":
            node_representation = torch.cat(h_list, dim = 1)
        elif self.JK == "last":
            node_representation = h_list[-1]
        elif self.JK == "max":
            h_list = [h.unsqueeze_(0) for h in h_list]
            node_representation = torch.max(torch.cat(h_list, dim = 0), dim = 0)[0]
        elif self.JK == "sum":
            h_list = [h.unsqueeze_(0) for h in h_list]
            node_representation = torch.sum(torch.cat(h_list, dim = 0), dim = 0)[0]

        return node_representation


class GNN_graphpred(torch.nn.Module):
    """
    Extension of GIN to incorporate edge information by concatenation.

    Args:
        num_layer (int): the number of GNN layers
        emb_dim (int): dimensionality of embeddings
        num_tasks (int): number of tasks in multi-task learning scenario
        drop_ratio (float): dropout rate
        JK (str): last, concat, max or sum.
        graph_pooling (str): sum, mean, max, attention, set2set
        gnn_type: gin, gcn, graphsage, gat
        
    See https://arxiv.org/abs/1810.00826
    JK-net: https://arxiv.org/abs/1806.03536
    """
    def __init__(self, num_layer, emb_dim, num_tasks, JK = "last", drop_ratio = 0, graph_pooling = "mean", gnn_type = "gin"):
        super(GNN_graphpred, self).__init__()
        self.num_layer = num_layer
        self.drop_ratio = drop_ratio
        self.JK = JK
        self.emb_dim = emb_dim
        self.num_tasks = num_tasks
        self.num_workers = 2

        if self.num_layer < 2:
            raise ValueError("Number of GNN layers must be greater than 1.")

        self.gnn = GNN(num_layer, emb_dim, JK, drop_ratio, gnn_type = gnn_type)

        #Different kind of graph pooling
        if graph_pooling == "sum":
            self.pool = global_add_pool
        elif graph_pooling == "mean":
            self.pool = global_mean_pool
        elif graph_pooling == "max":
            self.pool = global_max_pool
        elif graph_pooling == "attention":
            if self.JK == "concat":
                self.pool = GlobalAttention(gate_nn = torch.nn.Linear((self.num_layer + 1) * emb_dim, 1))
            else:
                self.pool = GlobalAttention(gate_nn = torch.nn.Linear(emb_dim, 1))
        elif graph_pooling[:-1] == "set2set":
            set2set_iter = int(graph_pooling[-1])
            if self.JK == "concat":
                self.pool = Set2Set((self.num_layer + 1) * emb_dim, set2set_iter)
            else:
                self.pool = Set2Set(emb_dim, set2set_iter)
        else:
            raise ValueError("Invalid graph pooling type.")

        #For graph-level binary classification
        if graph_pooling[:-1] == "set2set":
            self.mult = 2
        else:
            self.mult = 1
        
        if self.JK == "concat":
            self.graph_pred_linear = torch.nn.Linear(self.mult * (self.num_layer + 1) * self.emb_dim, self.num_tasks)
        else:
            self.graph_pred_linear = torch.nn.Linear(self.mult * self.emb_dim, self.num_tasks)

    def from_pretrained(self, model_file):
        # self.gnn = GNN(self.num_layer, self.emb_dim, JK = self.JK, drop_ratio = self.drop_ratio)
        self.gnn.load_state_dict(torch.load(model_file, map_location='cuda:0'),False)

    def forward(self, *argv):
        if len(argv) == 4:
            x, edge_index, edge_attr, batch = argv[0], argv[1], argv[2], argv[3]
        elif len(argv) == 1:
            data = argv[0]
            x, edge_index, edge_attr, batch = data.x, data.edge_index, data.edge_attr, data.batch
        else:
            raise ValueError("unmatched number of arguments.")

        node_representation = self.gnn(x, edge_index, edge_attr)

        return self.graph_pred_linear(self.pool(node_representation, batch)), node_representation

class attention(nn.Module):
    def __init__(self, dim):
        super(attention, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(dim, 100),
            nn.ReLU(),
            nn.Linear(100, 1)
        )
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        # # convert tensor (128, 1, 28, 28) --> (128, 1*28*28)
        # x = x.view(x.size(0), -1)
        x = self.layers(x)
        x = self.softmax(torch.transpose(x, 1, 0))
        return x

class Interact_attention(nn.Module):
    def __init__(self, dim, num_tasks):
        super(Interact_attention, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(num_tasks * dim, dim),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.layers(x)
        return x

class Meta_model(nn.Module):
    def __init__(self, args):
        super(Meta_model,self).__init__()

        self.dataset = args.dataset
        self.num_tasks = args.num_tasks
        self.num_train_tasks = args.num_train_tasks
        self.num_test_tasks = args.num_test_tasks
        self.n_way = args.n_way
        self.m_support = args.m_support
        self.k_query = args.k_query
        self.gnn_type = args.gnn_type

        self.emb_dim = args.emb_dim

        self.device = args.device

        self.add_similarity = args.add_similarity
        self.add_selfsupervise = args.add_selfsupervise
        self.add_masking = args.add_masking
        self.add_weight = args.add_weight
        self.interact = args.interact

        self.batch_size = args.batch_size

        self.meta_lr = args.meta_lr
        self.update_lr = args.update_lr
        self.update_step = args.update_step
        self.update_step_test = args.update_step_test

        self.criterion = nn.BCEWithLogitsLoss()
        
        self.graph_model = GNN_graphpred(args.num_layer, args.emb_dim, 1, JK = args.JK, drop_ratio = args.dropout_ratio, graph_pooling = args.graph_pooling, gnn_type = args.gnn_type)
        if not args.input_model_file == "":
            self.graph_model.from_pretrained(args.input_model_file)

        if self.add_selfsupervise:
            self.self_criterion = nn.BCEWithLogitsLoss()

        if self.add_masking:
            self.masking_criterion = nn.CrossEntropyLoss()
            self.masking_linear = nn.Linear(self.emb_dim, 119)

        if self.add_similarity:
            self.Attention = attention(self.emb_dim)

        if self.interact:
            self.softmax = nn.Softmax(dim=0)
            self.Interact_attention = Interact_attention(self.emb_dim, self.num_train_tasks)
            
        model_param_group = []
        model_param_group.append({"params": self.graph_model.gnn.parameters()})
        if args.graph_pooling == "attention":
            model_param_group.append({"params": self.graph_model.pool.parameters(), "lr":args.lr*args.lr_scale})
        model_param_group.append({"params": self.graph_model.graph_pred_linear.parameters(), "lr":args.lr*args.lr_scale})

        if self.add_masking:
            model_param_group.append({"params": self.masking_linear.parameters()})

        if self.add_similarity:
            model_param_group.append({"params": self.Attention.parameters()})
            
        if self.interact:
            model_param_group.append({"params": self.Interact_attention.parameters()})
        
        self.optimizer = optim.Adam(model_param_group, lr=args.meta_lr, weight_decay=args.decay)

        # for name, para in self.named_parameters():
        #     if para.requires_grad:
        #         print(name, para.data.shape)
        # raise TypeError

    def update_params(self, loss, update_lr):
        grads = torch.autograd.grad(loss, self.graph_model.parameters())
        return parameters_to_vector(grads), parameters_to_vector(self.graph_model.parameters()) - parameters_to_vector(grads) * update_lr

    def build_negative_edges(self, batch):
        font_list = batch.edge_index[0, ::2].tolist()
        back_list = batch.edge_index[1, ::2].tolist()
        
        all_edge = {}
        for count, front_e in enumerate(font_list):
            if front_e not in all_edge:
                all_edge[front_e] = [back_list[count]]
            else:
                all_edge[front_e].append(back_list[count])
        
        negative_edges = []
        for num in range(batch.x.size()[0]):
            if num in all_edge:
                for num_back in range(num, batch.x.size()[0]):
                    if num_back not in all_edge[num] and num != num_back:
                        negative_edges.append((num, num_back))
            else:
                for num_back in range(num, batch.x.size()[0]):
                    if num != num_back:
                        negative_edges.append((num, num_back))

        negative_edge_index = torch.tensor(np.array(random.sample(negative_edges, len(font_list))).T, dtype=torch.long)

        return negative_edge_index

    def forward(self, epoch):
        support_loaders = []
        query_loaders = []

        device = torch.device("cuda:" + str(self.device)) if torch.cuda.is_available() else torch.device("cpu")
        self.graph_model.train()

        # tasks_list = random.sample(range(0,self.num_train_tasks), self.batch_size)

        for task in range(self.num_train_tasks):
        # for task in tasks_list:
            dataset = MoleculeDataset("Original_datasets/" + self.dataset + "/new/" + str(task+1), dataset = self.dataset)
            support_dataset, query_dataset = sample_datasets(dataset, self.dataset, task, self.n_way, self.m_support, self.k_query)
            support_loader = DataLoader(support_dataset, batch_size=self.batch_size, shuffle=False, num_workers = 1)
            query_loader = DataLoader(query_dataset, batch_size=self.batch_size, shuffle=False, num_workers = 1)
            support_loaders.append(support_loader)
            query_loaders.append(query_loader)

        for k in range(0, self.update_step):
            # print(self.fi)
            old_params = parameters_to_vector(self.graph_model.parameters())

            losses_q = torch.tensor([0.0]).to(device)

            # support_params = []
            # support_grads = torch.Tensor(self.num_train_tasks, parameters_to_vector(self.graph_model.parameters()).size()[0]).to(device)

            for task in range(self.num_train_tasks):

                losses_s = torch.tensor([0.0]).to(device)
                if self.add_similarity or self.interact:
                    one_task_emb = torch.zeros(300).to(device)

                for step, batch in enumerate(tqdm(support_loaders[task], desc="Iteration")):
                    batch = batch.to(device)

                    pred, node_emb = self.graph_model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
                    y = batch.y.view(pred.shape).to(torch.float64)
                                
                    loss = torch.sum(self.criterion(pred.double(), y)) /pred.size()[0]

                    if self.add_selfsupervise:
                        positive_score = torch.sum(node_emb[batch.edge_index[0, ::2]] * node_emb[batch.edge_index[1, ::2]], dim = 1)

                        negative_edge_index = self.build_negative_edges(batch)
                        negative_score = torch.sum(node_emb[negative_edge_index[0]] * node_emb[negative_edge_index[1]], dim = 1)

                        self_loss = torch.sum(self.self_criterion(positive_score, torch.ones_like(positive_score)) + self.self_criterion(negative_score, torch.zeros_like(negative_score)))/negative_edge_index[0].size()[0]

                        loss += (self.add_weight * self_loss)

                    if self.add_masking:
                        mask_num = random.sample(range(0,node_emb.size()[0]), self.batch_size)
                        pred_emb = self.masking_linear(node_emb[mask_num])
                        loss += (self.add_weight * self.masking_criterion(pred_emb.double(), batch.x[mask_num,0]))

                    if self.add_similarity or self.interact:
                        one_task_emb = torch.div((one_task_emb + torch.mean(node_emb,0)), 2.0)

                    losses_s += loss

                if self.add_similarity or self.interact:
                    if task == 0:
                        tasks_emb = []
                    tasks_emb.append(one_task_emb)
                
                new_grad, new_params = self.update_params(losses_s, update_lr = self.update_lr)

                vector_to_parameters(new_params, self.graph_model.parameters())

                this_loss_q = torch.tensor([0.0]).to(device)
                for step, batch in enumerate(tqdm(query_loaders[task], desc="Iteration")):
                    batch = batch.to(device)

                    pred, node_emb = self.graph_model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
                    y = batch.y.view(pred.shape).to(torch.float64)

                    loss_q = torch.sum(self.criterion(pred.double(), y))/pred.size()[0]

                    if self.add_selfsupervise:
                        positive_score = torch.sum(node_emb[batch.edge_index[0, ::2]] * node_emb[batch.edge_index[1, ::2]], dim = 1)

                        negative_edge_index = self.build_negative_edges(batch)
                        negative_score = torch.sum(node_emb[negative_edge_index[0]] * node_emb[negative_edge_index[1]], dim = 1)

                        self_loss = torch.sum(self.self_criterion(positive_score, torch.ones_like(positive_score)) + self.self_criterion(negative_score, torch.zeros_like(negative_score)))/negative_edge_index[0].size()[0]

                        loss_q += (self.add_weight * self_loss)

                    if self.add_masking:
                        mask_num = random.sample(range(0,node_emb.size()[0]), self.batch_size)
                        pred_emb = self.masking_linear(node_emb[mask_num])
                        loss += (self.add_weight * self.masking_criterion(pred_emb.double(), batch.x[mask_num,0]))

                    this_loss_q += loss_q

                if task == 0:
                    losses_q = this_loss_q
                else:
                    losses_q = torch.cat((losses_q, this_loss_q), 0)

                vector_to_parameters(old_params, self.graph_model.parameters())

            if self.add_similarity:
                for t_index, one_task_e in enumerate(tasks_emb):
                    if t_index == 0:
                        tasks_emb_new = one_task_e
                    else:
                        tasks_emb_new = torch.cat((tasks_emb_new, one_task_e), 0)
                
                tasks_emb_new = torch.reshape(tasks_emb_new, (self.num_train_tasks, self.emb_dim))
                tasks_emb_new = tasks_emb_new.detach()

                tasks_weight = self.Attention(tasks_emb_new)
                losses_q = torch.sum(tasks_weight * losses_q)

            elif self.interact:
                for t_index, one_task_e in enumerate(tasks_emb):
                    if t_index == 0:
                        tasks_emb_new = one_task_e
                    else:
                        tasks_emb_new = torch.cat((tasks_emb_new, one_task_e), 0)

                tasks_emb_new = tasks_emb_new.detach()
                represent_emb = self.Interact_attention(tasks_emb_new)
                represent_emb = F.normalize(represent_emb, p=2, dim=0)

                tasks_emb_new = torch.reshape(tasks_emb_new, (self.num_train_tasks, self.emb_dim))
                tasks_emb_new = F.normalize(tasks_emb_new, p=2, dim=1)

                tasks_weight = torch.mm(tasks_emb_new, torch.reshape(represent_emb, (self.emb_dim, 1)))
                print(tasks_weight)
                print(self.softmax(tasks_weight))
                print(losses_q)

                # tasks_emb_new = tasks_emb_new * torch.reshape(represent_emb_m, (self.batch_size, self.emb_dim))
                
                losses_q = torch.sum(losses_q * torch.transpose(self.softmax(tasks_weight), 1, 0))
                print(losses_q)

            else:
                losses_q = torch.sum(losses_q)
            
            loss_q = losses_q / self.num_train_tasks       
            self.optimizer.zero_grad()
            loss_q.backward()
            self.optimizer.step()
        
        return []

    def test(self, support_grads):
        accs = []
        old_params = parameters_to_vector(self.graph_model.parameters())
        for task in range(self.num_test_tasks):
            print(self.num_tasks-task)
            dataset = MoleculeDataset("/input/" + self.dataset + "/new/" + str(self.num_tasks-task), dataset = self.dataset)
            support_dataset, query_dataset = sample_test_datasets(dataset, self.dataset, self.num_tasks-task-1, self.n_way, self.m_support, self.k_query)
            support_loader = DataLoader(support_dataset, batch_size=self.batch_size, shuffle=False, num_workers = 1)
            query_loader = DataLoader(query_dataset, batch_size=self.batch_size, shuffle=False, num_workers = 1)

            device = torch.device("cuda:" + str(self.device)) if torch.cuda.is_available() else torch.device("cpu")

            self.graph_model.eval()

            for k in range(0, self.update_step_test):
                loss = torch.tensor([0.0]).to(device)
                for step, batch in enumerate(tqdm(support_loader, desc="Iteration")):
                    batch = batch.to(device)

                    pred, node_emb = self.graph_model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
                    y = batch.y.view(pred.shape).to(torch.float64)

                    loss += torch.sum(self.criterion(pred.double(), y))/pred.size()[0]

                    if self.add_selfsupervise:
                        positive_score = torch.sum(node_emb[batch.edge_index[0, ::2]] * node_emb[batch.edge_index[1, ::2]], dim = 1)

                        negative_edge_index = self.build_negative_edges(batch)
                        negative_score = torch.sum(node_emb[negative_edge_index[0]] * node_emb[negative_edge_index[1]], dim = 1)

                        self_loss = torch.sum(self.self_criterion(positive_score, torch.ones_like(positive_score)) + self.self_criterion(negative_score, torch.zeros_like(negative_score)))/negative_edge_index[0].size()[0]

                        loss += (self.add_weight *self_loss)

                    if self.add_masking:
                        mask_num = random.sample(range(0,node_emb.size()[0]), self.batch_size)
                        pred_emb = self.masking_linear(node_emb[mask_num])
                        loss += (self.add_weight * self.masking_criterion(pred_emb.double(), batch.x[mask_num,0]))

                    print(loss)

                new_grad, new_params = self.update_params(loss, update_lr = self.update_lr)

                # if self.add_similarity:
                #     new_params = self.update_similarity_params(new_grad, support_grads)

                vector_to_parameters(new_params, self.graph_model.parameters())
                

            y_true = []
            y_scores = []
            for step, batch in enumerate(tqdm(query_loader, desc="Iteration")):
                batch = batch.to(device)

                pred, node_emb = self.graph_model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
                # print(pred)
                pred = F.sigmoid(pred)
                pred = torch.where(pred>0.5, torch.ones_like(pred), pred)
                pred = torch.where(pred<=0.5, torch.zeros_like(pred), pred)
                y_scores.append(pred)
                y_true.append(batch.y.view(pred.shape))
                

            y_true = torch.cat(y_true, dim = 0).cpu().detach().numpy()
            y_scores = torch.cat(y_scores, dim = 0).cpu().detach().numpy()
           
            roc_list = []
            roc_list.append(roc_auc_score(y_true, y_scores))
            acc = sum(roc_list)/len(roc_list)
            accs.append(acc)

            vector_to_parameters(old_params, self.graph_model.parameters())

        return accs

    
import argparse
parser = argparse.ArgumentParser(description='PyTorch implementation of pre-training of graph neural networks')
parser.add_argument('--device', type=int, default=0,
                    help='which gpu to use if any (default: 0)')
parser.add_argument('--batch_size', type=int, default=32,
                    help='input batch size for training (default: 32)') 
parser.add_argument('--epochs', type=int, default=1,
                    help='number of epochs to train (default: 100)')
parser.add_argument('--lr', type=float, default=0.001,
                    help='learning rate (default: 0.001)')
parser.add_argument('--lr_scale', type=float, default=1,
                    help='relative learning rate for the feature extraction layer (default: 1)')
parser.add_argument('--decay', type=float, default=0,
                    help='weight decay (default: 0)')
parser.add_argument('--num_layer', type=int, default=5,
                    help='number of GNN message passing layers (default: 5).')
parser.add_argument('--emb_dim', type=int, default=300,
                    help='embedding dimensions (default: 300)')
parser.add_argument('--dropout_ratio', type=float, default=0.5,
                    help='dropout ratio (default: 0.5)')
parser.add_argument('--graph_pooling', type=str, default="mean",
                    help='graph level pooling (sum, mean, max, set2set, attention)')
parser.add_argument('--JK', type=str, default="last",
                    help='how the node features across layers are combined. last, sum, max or concat')
parser.add_argument('--gnn_type', type=str, default="graphsage")
parser.add_argument('--dataset', type=str, default = 'sider', help='root directory of dataset. For now, only classification.')
parser.add_argument('--input_model_file', type=str, default = '/storage/zcg/wll/mm_docker/mounting/input/supervised_contextpred.pth', help='filename to read the model (if there is any)')
parser.add_argument('--filename', type=str, default = '/storage/zcg/wll/mm_docker/mounting/output/result.txt', help='output filename')
parser.add_argument('--seed', type=int, default=42, help = "Seed for splitting the dataset.")
parser.add_argument('--runseed', type=int, default=0, help = "Seed for minibatch selection, random initialization.")
parser.add_argument('--split', type = str, default="scaffold", help = "random or scaffold or random_scaffold")
parser.add_argument('--eval_train', type=int, default = 0, help='evaluating training or not')
parser.add_argument('--num_workers', type=int, default = 4, help='number of workers for dataset loading')

parser.add_argument('--num_tasks', type=int, default=12, help = "# of tasks")
parser.add_argument('--num_train_tasks', type=int, default=9, help = "# of training tasks")
parser.add_argument('--num_test_tasks', type=int, default=3, help = "# of testing tasks")
parser.add_argument('--n_way', type=int, default=2, help = "n_way of dataset")
parser.add_argument('--m_support', type=int, default=5, help = "size of the support dataset")
parser.add_argument('--k_query', type = int, default=128, help = "size of querry datasets")
parser.add_argument('--meta_lr', type=float, default=0.001) 
parser.add_argument('--update_lr', type=float, default=0.4) #0.4
parser.add_argument('--update_step', type=int, default=5) #5
parser.add_argument('--update_step_test', type=int, default=10) #10
parser.add_argument('--add_similarity', type=bool, default=True)
parser.add_argument('--add_selfsupervise', type=bool, default=True)
parser.add_argument('--interact', type=bool, default=False)
parser.add_argument('--add_weight', type=float, default=0.1)
parser.add_argument('--add_masking', type=bool, default=True)

args = parser.parse_args()


torch.manual_seed(args.runseed)
np.random.seed(args.runseed)
device = torch.device("cuda:" + str(args.device)) if torch.cuda.is_available() else torch.device("cpu")
#    device = torch.device("cpu")
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(args.runseed)

if args.dataset == "tox21":
    args.num_tasks = 12
    args.num_train_tasks = 9
    args.num_test_tasks = 3

elif args.dataset == "sider":
    args.num_tasks = 27
    args.num_train_tasks = 21
    args.num_test_tasks = 6
else:
    raise ValueError("Invalid dataset name.")

model = Meta_model(args).to(device)
# model.to(device)

print(args.dataset)

support_grads = []
accs = model.test(support_grads)
fw = open(args.filename ,"a")
for i in accs:
    fw.write(str(i) + "\t")
fw.close()
