import tensorflow as tf
import numpy as np

def weight_variable_glorot(input_dim, output_dim, name=""):
    """Create a weight variable with Glorot & Bengio (AISTATS 2010)
    initialization.
    Glorot 均匀分布初始化器，也称为 Xavier 均匀分布初始化器。它从 [-limit，limit] 中的均匀分布中抽取样本，
    其中 limit 是 sqrt(6 / (fan_in + fan_out))， fan_in 是权值张量中的输入单位的数量， fan_out 是权值张量中的输出单位的数量。
    """
    init_range = np.sqrt(6.0 / (input_dim + output_dim))
    initial = tf.random_uniform([input_dim, output_dim], minval=-init_range,
                                maxval=init_range, dtype=tf.float64)
    return tf.Variable(initial, name=name)
