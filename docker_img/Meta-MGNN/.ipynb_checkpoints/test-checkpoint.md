算子功能：根据微生物丰度预测代谢物丰度。

BiomeNED:一个稀疏的神经编码器-解码器模型，并用非负权重约束提高该网络的可解释性。该神经网络在微生物组 - 代谢组预测方面优于线性模型。

输出结果是vis文件。

# 容器内测试

以交互模式启动容器

```shell
创建镜像：aita@gpu1:~/yq/BiomeNED$ docker build -t bio:test .
挂载：aita@gpu1:~/yq/BiomeNED-test$ docker run -it -v /home/aita/yq/BiomeNED-test/input/:/input/ -v /home/aita/yq/BiomeNED-test/output/:/output/ -v /home/aita/zhongg/BiomeNED-test/conf/:/conf/  -v /home/aita/zhonggang/BiomeNED-test/ext/:/ext/ bio:test /bin/bash
```

测试程序是否可以运行

```
root@50327f4ec0bf:/run_script#python /run_script/main_cv_1dir.py --data_root /input/data/ --model BiomeAE --fea1 bac_group_fea --fea2 met_group_fea  --dataset_name ibd --data_type lr --cross_val_folds 5 --topk 10  --sparse None  --seed  0 --epochs 100 --batch_size 20 --learning_rate 0.1 --activation tanh_None --dropout 0 --batch_norm 1  --latent_size  20 --print_every 10 --fig_root /output/vis --gpu_num 0 --visualize subplot


```

## 容器内通过Wrapper进行测试

```shell
root@3b00bb797c02:/run_script# python wrapper.py
['python', '/run_script/main_cv_1dir.py', '--data_root', '/input/data/', '--model', 'BiomeAE', '--fea1', 'bac_group_fea', '--fea2', 'met_group_fea', '--dataset_name', 'ibd', '--data_type', 'clr', '--cross_val_folds', '5', '--topk', '10', '--sparse', 'None', '--seed', '0', '--epochs', '100', '--batch_size', '20', '--learning_rate', '0.1', '--activation', 'tanh_None', '--dropout', '0', '--batch_norm', '1', '--latent_size', '20', '--print_every', '10', '--fig_root', '/output/vis', '--gpu_num', '0', '--visualize', 'subplot']

aita@gpu1:~/yq/BiomeNED-test/output$ ls
vis
```

## 容器外进行测试

```shell
docker run --rm -v  /home/aita/yq/BiomeNED-test/input/:/input/ -v /home/aita/yq/BiomeNED-test/output/:/output/ -v /home/aita/yq/BiomeNED-test/conf/:/conf/  -v /home/aita/yq/BiomeNED-test/ext/:/ext/

```

