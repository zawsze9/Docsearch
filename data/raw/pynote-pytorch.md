# PyTorch 笔记（Blitz 教程前三部分：张量 → autograd → 神经网络）

> 来源：PyTorch 官方 60 分钟 Blitz 教程（中文站 docs.pytorch.ac.cn），2026-07-31 理论日Ⅰ完成
> 整理说明：原文未改写，分类重排；💡 = AI 补充，⚠️ = 订正

---

## 0. 三个检查点（任务要求）

**① 张量与 numpy 互转后共享内存的表现**
一个修改，另一个随之变化
💡【补充】仅限 CPU 张量：`torch.from_numpy(n)` 与 `t.numpy()` 都是共享底层内存，改一方另一方必变；张量移到 GPU 后不再共享。用 `copy()`/`clone()` 可切断共享。

**② 梯度存在哪、为什么要 zero_grad**
.grad属性里；防止反向传播时梯度累积

**③ 五步曲默写**
~~正向传播——计算损失函数——优化器/梯度清零——反向传播~~
⚠️【订正】漏了 step 且顺序错（zero_grad 必须在 backward 之前）。正确五步曲：
1. **forward**：input 过网络得到 prediction
2. **loss**：prediction 与 label 算损失
3. **zero_grad**：optimizer.zero_grad() 清空参数 .grad（backward 是累加语义，不清会跨 batch 累积）
4. **backward**：loss.backward()，autograd 沿计算图反传，梯度存入每个参数的 .grad
5. **step**：optimizer.step() 按 lr × 梯度更新权重（权重 -= lr × 梯度）

---

## 1. PyTorch 是什么

PyTorch 是一个基于 Python 的科学计算包，主要有两个用途：
- 替代 NumPy，以利用 GPU 和其他加速器的强大功能
- 一个自动微分库，可用于实现神经网络

---

## 2. 张量 Tensor

### 2.1 张量是什么

与数组和矩阵非常相似，编码模型的输入和输出，以及模型的参数

### 2.2 创建张量

**直接从数据创建**（数据类型会自动推断）：
```python
data = [[1, 2], [3, 4]]
x_data = torch.tensor(data)
```

**从 NumPy 数组创建**：
```python
x_np = torch.from_numpy(np_array)
```

**从另一个张量创建**：
```python
x_ones = torch.ones_like(x_data)                    # retains the properties of x_data
x_rand = torch.rand_like(x_data, dtype=torch.float) # overrides the datatype of x_data
```

**使用随机值或常数值**（shape 是一个元组，代表张量的维度）：
```python
shape = (2, 3,)
rand_tensor = torch.rand(shape)  # 用 0 到 1 之间的均匀分布随机数填充
ones_tensor = torch.ones(shape)  # 用1填充
zeros_tensor = torch.zeros(shape) # 用0填充
```

### 2.3 张量属性

```python
.shape   # 维度
.dtype   # 数据类型
.device  # 所在设备
```

### 2.4 张量运算

**移动到设备**：
```python
device = torch.accelerator.current_accelerator().type if torch.accelerator.is_available() else 'cpu'
tensor = tensor.to(device)
```

**索引和切片**（类似 NumPy）：
```python
tensor[:,1] = 0  # 第二列=0，左侧表示所有行
```

**连接张量**：
```python
t1 = torch.cat([tensor, tensor, tensor], dim=1)  # dim是维度索引，从0开始；[批次, 通道数, 高, 宽]
```

**逐元素乘 vs 矩阵乘（重点区分）**：
```python
tensor.mul(tensor)        # 对应位置相乘（逐元素乘，Hadamard积），形状不变
tensor.matmul(tensor.T)   # 矩阵乘法（行列点积），形状会改变，且数学意义完全不同
```

**原地操作**：后缀为 `_` 的操作是原地操作。例如：`x.copy_(y)`，`x.t_()` 会直接改变 x 的值

### 2.5 与 NumPy 互转：共享内存

CPU 上的张量和 NumPy 数组可以共享底层内存位置，改变其中一个也会改变另一个。
```python
t = torch.ones(5)
n = t.numpy()      # 张量的变化会反映在 NumPy 数组中

n = np.ones(5)
t = torch.from_numpy(n)
```
💡【补充】与检查点①对应：共享仅限 CPU、双向生效；GPU 张量需先 `cpu()` 再转，`copy()`/`clone()` 可切断共享。

---

## 3. 自动微分 torch.autograd

### 3.1 自动微分引擎与训练两步

torch.autograd 是 PyTorch 的自动微分引擎。

神经网络（NN）是作用于输入数据的一系列嵌套函数集合。这些函数由参数（包含权重和偏置）定义，在 PyTorch 中这些参数存储在张量（tensors）中。

神经网络的训练分为两步：
- **前向传播（Forward Propagation）**：神经网络对正确的输出做出最佳猜测。它将输入数据传入每一层函数以得出此猜测。
- **反向传播（Backward Propagation）**：神经网络根据其猜测的误差比例调整参数。它通过从输出端向后遍历，收集误差相对于函数参数的导数（梯度），并使用梯度下降优化参数。

### 3.2 计算图（DAG）

从概念上讲，autograd 在一个有向无环图（DAG）中记录了数据（张量）及所有已执行的操作（以及由此产生的新张量），该图由 Function 对象组成。在这个 DAG 中，叶子节点是输入张量，根节点是输出张量。通过从根节点回溯到叶子节点，你可以利用链式法则自动计算梯度。

**前向传播时 autograd 同时做两件事**：
- 运行请求的操作以计算结果张量
- 在 DAG 中维护该操作的梯度函数

**调用 `.backward()` 时 autograd 会**：
- 根据每个 .grad_fn 计算梯度
- 将它们累加到对应张量的 .grad 属性中
- 利用链式法则，一直传播到叶子张量

💡【补充】在神经网络中，不计算梯度的参数通常被称为**冻结参数**。

### 3.3 完整示例：训练流程五步曲对应

```python
import torch
from torchvision.models import resnet18, ResNet18_Weights

model = resnet18(weights=ResNet18_Weights.DEFAULT)
data = torch.rand(1, 3, 64, 64)
labels = torch.rand(1, 1000)

prediction = model(data)                      # ① forward pass
loss = (prediction - labels).sum()            # ② loss
loss.backward()                               # ③④ backward（backward 前调 optimizer.zero_grad()）
optim = torch.optim.SGD(model.parameters(), lr=1e-2, momentum=0.9)  # 优化器
# ⑤ optim.step() 更新权重
```

将输入数据传入模型，使其通过每一层以进行预测。这就是前向传播（对应五步曲①）。

使用模型的预测值和对应的标签来计算误差（loss）（对应五步曲②）。下一步是将该误差通过网络进行反向传播。当我们对误差张量调用 .backward() 时，反向传播正式启动。此时 Autograd 会计算每个模型参数的梯度，并将其存储在参数的 .grad 属性中（对应五步曲③④）。

接下来，我们加载一个优化器，本例中使用学习率为 0.01 且动量（momentum）为 0.9 的 SGD。

最后，我们调用 .step() 来启动梯度下降。优化器会根据存储在 .grad 中的梯度来调整每个参数（对应五步曲⑤）。

---

## 4. torchvision（CV 工具箱，独立章节）

💡【补充】torchvision 是 PyTorch 生态中专门用于计算机视觉（CV）的官方工具箱。它不是 PyTorch 本身，而是必须单独安装的扩展包（pip install torchvision）。**不属于 Blitz 前三部分，是数据准备工具**：

- `torchvision.datasets`：`datasets.MNIST(root='./data', train=True, download=True)` 下载并加载主流 CV 数据集
- `torchvision.transforms`：把图片（PIL/NumPy）变成需要的 Tensor，并做归一化、裁剪、翻转等增强

```python
transforms.Compose([
    transforms.Resize(256),          # 缩放到 256x256
    transforms.CenterCrop(224),      # 中心裁剪到 224x224
    transforms.ToTensor(),           # 关键！把 PIL/NumPy 转为 [0,1] 的 Tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406],  # 标准化（ImageNet 标准值）
                         std=[0.229, 0.224, 0.225])
])
```

- `torchvision.models`：提供大量预训练权重的现成网络
- 底层图像操作：torchvision.io 和 torchvision.ops

---

## 5. 神经网络 torch.nn

### 5.1 nn 包概述

神经网络可以使用 torch.nn 包来构建，nn 依赖于 autograd 来定义模型并对其求导。nn.Module 包含各个层，以及一个返回 output 的 forward(input) 方法。

只需要定义 forward 函数，而 backward 函数（计算梯度的地方）会自动通过 autograd 为你定义。

模型的可学习参数由 `net.parameters()` 返回。

### 5.2 核心对象四件套

| 对象 | 作用 |
|---|---|
| `torch.Tensor` | 支持自动求导操作（如 backward()）的多维数组。同时保存有关该张量的梯度 |
| `nn.Module` | 神经网络模块。封装参数的便捷方式，并提供将参数移动到 GPU、导出、加载等的辅助方法 |
| `nn.Parameter` | 一种张量，当它被分配为 Module 的属性时，会被自动注册为参数 |
| `autograd.Function` | 实现自动求导操作的前向和反向定义。每个 Tensor 操作至少创建一个 Function 节点，该节点连接到创建 Tensor 的函数，并对其历史记录进行编码 |

### 5.3 常用层

```python
class torch.nn.Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros', device=None, dtype=None)
```
在由多个输入平面组成的输入信号上应用二维卷积

```python
class torch.nn.Linear(in_features, out_features, bias=True, device=None, dtype=None)
```
对输入数据应用仿射线性变换：y = xAᵀ + b

（随手记）convolutions 卷积 采样 卷积 采样 全连接 高斯连接
💡【补充】这是经典卷积网络结构：卷积层-池化（采样）-卷积-池化-全连接（如 LeNet 类），卷积+池化提取特征、全连接做分类。

### 5.4 典型训练过程（与五步曲对照）

神经网络的典型训练过程如下：
1. 定义具有可学习参数（或权重）的神经网络（五步曲之外的准备）
2. 在输入数据集上进行迭代（batch 循环，每轮跑一遍五步曲）
3. 通过网络处理输入（= 五步曲①forward）
4. 计算损失（输出距离目标有多远）（= 五步曲②loss）
5. 将梯度反向传播回网络的参数中（= 五步曲③④backward）
6. 更新网络的权重，通常使用简单的更新规则：权重 = 权重 - 学习率 * 梯度（= 五步曲⑤step）

💡【补充】这段与检查点③五步曲是同一件事的两种说法，合并理解即可。

---

## 6. 损失函数与权重更新

nn 包下有几种不同的损失函数。一种简单的损失是：nn.MSELoss，它计算输出和目标之间的均方误差。

更新权重：实践中使用的最简单的更新规则是随机梯度下降 (SGD)
