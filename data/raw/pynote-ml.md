# ML 八股笔记 v1（2026-07-31 开写）

> 来源：李宏毅ML（2021版 B站全集，BV1Wv411h7kN）选讲：反向传播、机器学习任务攻略、过拟合相关 + AI 八股补充
> 整理说明：原文未改写，仅分类重排；AI 补充均以 💡【补充】标注；公式/截图统一处理方式见「0. 笔记书写说明」

---

## 0. 笔记书写说明（公式表达规则）

💡【补充】公式用 Markdown 纯文本/代码块写，不必截图：如 `f(x) = 1 / (1 + e^(-x))`、`sum[l..r] = prefix[r] - prefix[l-1]`。上标用 `^`，下标用 `_`。截图（如 image-2.png）统一存 `attach/` 目录。

---

## 1. 机器学习三步骤

未知数func——定义loss——opt优化

> 三个步骤：① 定义未知函数（找 func）② 定义损失函数（loss）③ 优化器优化（opt）

---

## 2. 反向传播 Backpropagation

- BP 是**梯度下降在神经网络上的算法**：nn 有很多参数，先选一个初始参数，计算每一个对 loss 的偏微分
- gradient vector 很大
- 核心：**chain rule 链式法则**（多元微分）
- loss 是误差之和；layer 层

![alt text](attach/image-2.png)

- z 对 w 偏微分就是前 input，**forward pass**
- 反向 nn 计算，**backward pass**

---

## 3. 训练问题排查：机器学习任务攻略

**流程**：未知数func——定义loss——opt优化（见 §1）。训练不顺时按以下顺序排查：

**① 检查 training data**（数据本身是否标错/有噪声）

**② training data 上的 loss 过大** → 两类原因，先分辨是哪类：
- **model bias**：模型过简单，连训练集都拟合不了 → 重新设计 model、增加参数
- **optimization 优化差**：模型够强但找不到最小 loss → 判断技巧：跑简单的、容易优化的 model 对比（如加参数后 loss 反而上升 = 优化问题，不是 bias）

> 比较不同的模型判断问题所在，不一定是 overfitting

**③ testing data 上的 loss 大才是 overfitting**（训练集上 loss 小不算）

---

## 4. 过拟合与欠拟合

### 4.1 现象与判断

overfitting：找到的func很差，只适用于traing data

> ⚠️【订正】原文 "traing" 为 "training" 笔误，下同。

💡【补充】**判断标准：只看 testing/validation 上的表现**——训练集 loss 低、测试集 loss 高（差距大）→ 过拟合；训练集 loss 小本身不算。

### 4.2 解决手段全家桶（含原文 + 整理表格）

原文：解决：增加训练资料/data augmentation 创造资料，数据增强/减少弹性，限制条件，减少或共用参数/早停/少特征/dropout。但是限制太多就bias了

💡【补充】整理为表格（与上方原文一一对应）：

| 手段 | 原理 | 注意 |
|---|---|---|
| 增加数据/数据增强 | 最有效；让模型见更多分布 | 翻转/裁剪/加噪（图像），同义替换（文本） |
| L1 正则 | 损失 + λ‖w‖₁，倾向让权重变 0，产生稀疏解、特征选择 | 适合特征多且相关 |
| L2 正则 | 损失 + λ‖w‖₂²，权重大小被惩罚（权重衰减 weight decay） | 最常见，SGD 里叫 weight_decay |
| Dropout | 训练时随机丢弃神经元，强迫网络学冗余特征（集成效果） | 测试时关闭（nn.Module.eval()） |
| Early Stopping | 验证集 loss 不再下降就停 | 需另留验证集 |
| 减少模型弹性 | 少特征、少参数、共用参数（CNN 共享卷积核）、简化结构 | **限制过头会欠拟合（bias 增大）**，对应原文"限制太多就bias了" |

### 4.3 欠拟合 vs 过拟合

💡【补充】训练集 loss 都大 = 欠拟合（模型太简单/opt 不好）；训练小测试大 = 过拟合。

### 4.4 模型选择：validation set 与交叉验证

- mse最低的模型最好，但可能所有模型都很差，可能只是public testing set分数高
- traing set 分一部分作validation（确认） set
- n-fold cross validation：n等分后每一部分分别作validation set后取mse平均值
- 用了validation set还会overfitting：validation set本质其实是用validation set在一个缩小的model上训练(func为之前traing训练的几个func)，抽到了不好的traing set

💡【补充】MSE（Mean Squared Error 均方误差）是什么：回归任务最常用的损失，`MSE = (1/n) Σ(y_pred - y_true)²`，即预测值与真实值差的平方的平均。李宏毅课里用 MSE 衡量模型在测试集上的好坏，MSE 越小越好。

### 4.5 分布不匹配 mismatch

mismatch：训练资料和测试资料分布不一样，增加训练资料一般没用

### 4.6 CNN 的弹性较小

CNN的弹性较小（共享卷积核 → 参数少 → 弹性小 → 相对不易过拟合）

---

## 5. 为什么用深度学习（hidden layer）

- hidden layer：常数项+阶梯func（sigmod）/relu，加layer效果变好，所以用DeepLearning
- dl需要的参数更少

---

## 6. 激活函数

作用：给神经网络引入非线性。没有激活函数，多层线性变换叠加还是线性（等价于一层），网络再深也没意义。激活函数让网络能拟合任意复杂函数。（分段线性属于非线性）

常用激活函数：
1. Sigmoid（sigmoid 型）
   f(x) = 1 / (1 + e^(-x))        输出范围: (0, 1)
   输出可解释为概率，适合二分类输出层
   缺点：饱和区梯度几乎为 0（梯度消失）；输出非零中心，训练慢
2. Tanh（双曲正切）
   f(x) = (e^x - e^(-x)) / (e^x + e^(-x))   输出范围: (-1, 1)
   零中心，比 Sigmoid 训练快
   缺点：饱和区仍会梯度消失
3. ReLU（最常用）
   f(x) = max(0, x)
   计算极快，正区间梯度恒为 1，有效缓解梯度消失
   缺点：负数全部输出 0，神经元可能"死掉"（失活后梯度为 0 无法恢复）
4. Leaky ReLU / PReLU
   f(x) = x (x>0)  或  0.01x (x≤0)
   负数有微小梯度，解决 ReLU 神经元死亡问题
5. ELU / SELU
   f(x) = x (x>0)  或  α(e^x - 1) (x≤0)
   负数端平滑，对噪声更鲁棒
6. GELU（Transformer 标配）
   f(x) = x · Φ(x)
   GPT、BERT、ViT 全用它，平滑且接近 ReLU 的稀疏性
7. Softmax（输出层专用）
   把多个输出归一化成概率分布，多分类必备（和 CrossEntropyLoss 配套）

选型建议：

| 场景 | 推荐 |
|---|---|
| 隐藏层默认 | ReLU（绝大多数情况） |
| Transformer | GELU |
| 二分类输出 | Sigmoid |
| 多分类输出 | Softmax |
| 输出有界(-1,1) | Tanh |
| ReLU 死神经元严重 | Leaky ReLU / ELU |

```python
import torch.nn as nn
nn.ReLU()          # 默认选择
nn.GELU()          # Transformer
nn.Sigmoid()       # 二分类输出
nn.Softmax(dim=1)  # 多分类输出
```

---

## 7. 分类评估指标：Precision / Recall / F1 / Accuracy

💡【补充】以二分类为例，4 个基本量：TP（预测正、实际正）、FP（预测正、实际负）、FN（预测负、实际正）、TN（预测负、实际负）。

| 指标 | 公式 | 含义 |
|---|---|---|
| Precision 精确率 | TP / (TP + FP) | 预测为正的里面有多少是对的（宁缺毋滥） |
| Recall 召回率 | TP / (TP + FN) | 真正的正样本里找回了多少（宁滥毋缺） |
| F1 | 2·P·R / (P + R) | P 和 R 的调和平均，两者平衡时最大 |
| Accuracy | (TP + TN) / 全部 | 整体正确率，**类别不平衡时失真** |

场景：搜广推里推荐列表看 Precision（推的准不准），安全/风控看 Recall（漏网的多不多）；两者矛盾时用 F1。

---

## 8. AUC 与 ROC

💡【补充】**含义**：随机取一个正样本和一个负样本，模型给正样本打分高于负样本的概率。**AUC = 0.5 是随机，1.0 是完美，>0.5 有意义**（低于 0.5 反着用）。

- 与阈值无关：Precision/Recall 依赖你选的判定阈值，AUC 不依赖，直接反映模型排序能力
- 画法：ROC 曲线（横轴 FPR = FP/(FP+TN)，纵轴 TPR = TP/(TP+FN)），曲线下面积即 AUC
- 类别不平衡下比 Accuracy 可靠
- 面试常问：AUC 为 0.7 怎么解释 → "正样本得分高于负样本的概率是 70%"
