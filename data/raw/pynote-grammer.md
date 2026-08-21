# Python 语法备忘录（刷题向）

> 整理说明：按数据结构分类重排，原文内容未改写；错误处以 ⚠️【订正】标注（原文保留删除线），整理者补充均以 💡【补充】醒目标注。

---

## 1. dict 字典

```python
seen = {}  # 花括号创建字典dict
```
![alt text](attach/image.png)

> 💡【补充】空花括号 `{}` 创建的是 **dict**，不是 set；空集合必须写 `set()`。

- `for key, value in data.items():` 遍历键值对
- `merged = d1 | d2` 合并
  > 💡【补充】`|` 合并需 Python 3.9+；3.8 及以前用 `{**d1, **d2}`。
- ~~seen.values()返回所有的值，是个list~~
  > ⚠️【订正】`seen.values()` 返回的是 **dict_values 视图对象**，不是 list（视图会随原字典动态变化）。需要列表时写 `list(seen.values())`。`keys()` / `items()` 同理。
- 字典（哈希表）的**键必须是不可变（可哈希）类型**，list 不可以
  > 💡【补充】tuple 可以当键（只要其元素都可哈希）；list / dict / set 不可当键。
- 查的时候要用 `in` 或 `.get()`

### defaultdict

defaultdict可以处理缺失键，`from collections import defaultdict`

![alt text](attach/image-1.png)

```python
.append
```

> 💡【补充】`defaultdict(list)` 的值默认初始化为 `[]`，因此能直接 `.append` 而无需先判断键是否存在——这正是它"处理缺失键"的机制。

### typing

```python
from typing import List
```

`Optional[str]表示值可以为None`

> 💡【补充】`Optional[str]` 等价于 `Union[str, None]`——类型可以是 str 或 None，用于函数参数/返回值可空的场景（LeetCode 链表题 `Optional[ListNode]` 就是典型，见 160/234 题）。Python 3.10+ 可直接写 `str | None`。

---

## 2. set 集合

`set()` 是 Python 中另一个基于**哈希表**实现的核心数据结构。可以理解为"只有键（Key），没有值（Value）"的字典。

```python
s = {1, 2, 3}
s.add(4)            # {1, 2, 3, 4}
s.discard(10)       # 无报错，依然 {1,2,3,4}
s.remove(2)         # {1, 3, 4}
print(3 in s)       # True
```

> 💡【补充】`remove(x)` 与 `discard(x)` 的区别：元素不存在时，`remove` 抛 `KeyError`，`discard` 静默通过。不确定元素是否存在时用 `discard`。

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(a | b)   # {1, 2, 3, 4, 5, 6}
print(a & b)   # {3, 4}
print(a - b)   # {1, 2}
print(a ^ b)   # {1, 2, 5, 6} （互斥的元素）
```

---

## 3. list 列表

| 方法                  | 用法示例                                       | 说明                                     | 时间复杂度             |
| ------------------- | ------------------------------------------ | -------------------------------------- | ----------------- |
| **`append(x)`**     | `lst.append(4)`                            | 末尾追加**单个元素**（可以是任意类型）                  | O(1)              |
| **`extend(iter)`**  | `lst.extend([4,5])` 或 `lst += [4,5]`       | 将可迭代对象的**每个元素**逐个追加到末尾（平铺）             | O(k)              |
| **`insert(i, x)`**  | `lst.insert(0, 'start')`                   | 在指定索引 `i` 处插入元素（后续元素后移）                | O(n)              |
| **`remove(x)`**     | `lst.remove(3)`                            | 移除**第一个**匹配值 `x` 的元素（无则报 `ValueError`） | O(n)              |
| **`pop(i)`**        | `lst.pop()`（默认末尾）  <br>`lst.pop(0)`（弹出第一个） | 删除并返回指定索引的元素                           | O(1) 末尾 / O(n) 中间 |
| **`clear()`**       | `lst.clear()`                              | 清空列表中所有元素                              | O(n)              |
| **`sort()`**        | `lst.sort()`  <br>`lst.sort(reverse=True)` | 原地升序/降序排序（可传 `key=str.lower`）          | O(n log n)        |
| **`reverse()`**     | `lst.reverse()`                            | 原地反转列表顺序                               | O(n)              |
| **`list.copy()`**   | `new = lst.copy()`                         | 返回原列表的**浅拷贝**（等价于 `lst[:]`）            | 新列表               |
| **切片 `[:]`**        | `sub = lst[1:3]`                           | 截取子列表（左闭右开）                            | 新列表               |
| **`list.index(x)`** | `idx = lst.index(3)`                       | 返回第一个匹配项的索引（无则报错，可指定 start/end）        | 整数                |
| **`list.count(x)`** | `cnt = lst.count(3)`                       | 统计元素 `x` 出现的次数                         | 整数                |
| **成员运算**            | `if 3 in lst:`                             | 判断元素是否存在（底层遍历）                         | 布尔值               |
| **`len(lst)`**      | `n = len(lst)`                             | 获取列表长度                                 | 整数                |
| **`sorted(lst)`**   | `new = sorted(lst)`                        | **内置函数**，返回排序后的新列表（原列表不变）              | 新列表               |
| **`reversed(lst)`** | `for i in reversed(lst):`                  | **内置函数**，返回反向迭代器（不生成新列表）               | 迭代器               |

---

## 4. tuple 元组

~~tuple 元组不可哈希 不可排序~~

> ⚠️【订正】tuple 是**不可变**的，但只要其元素都可哈希，**tuple 就是可哈希的**——能当字典的键，这正是它和 list 的核心区别（经典面试题）。tuple 也可以被 `sorted()` 排序（返回新 list）。原表述把"不可变"与"不可哈希/不可排序"混淆了。

---

## 5. 通用内置函数与技巧

### enumerate

```python
for i, num in enumerate(nums):
```
`enumerate(nums)` 枚举，返回的是包含索引和元素的元组

> 💡【补充】`enumerate(nums, start=1)` 可以让索引从 1 开始，刷题偶尔用到。

### sorted

`sorted(iterable, *, key=None, reverse=False)` 用于对**任何可迭代对象**（如列表、元组、字典、字符串等）进行排序，并**返回一个新的排序后的列表**

> key（指定排序依据）—— **最核心、最常用**
> 接收一个**函数**，该函数会被应用到可迭代对象的**每一个元素**上，排序时依据函数的**返回值**进行比较

> 💡【补充】常见组合：`sorted(d.items(), key=lambda x: -x[1])` 按值降序排字典；多关键字用元组：`key=lambda x: (x[0], -x[1])`。

### reversed

`reversed() 返回的不是一个列表，而是一个“反向迭代器（iterator）”`

```python
lst = [1, 2]
print(list(reversed(lst)))   # [2, 1]
```

> 💡【补充】与 `sorted` 类似是**内置函数、返回新迭代器、原对象不变**；迭代器只能遍历一次，需要列表就 `list(...)` 包一层。对应列表方法 `lst.reverse()` 是**原地反转**（见 §3 表格）。

### join

```python
''.join(...)
```

### math.prod

`math.prod()` 累乘，默认起始值（start）是 1，对空表使用返回1

> 💡【补充】Python 3.8+ 才有；238题"除自身以外数组的乘积"的前后缀积、`numpy`不便用时它是首选。对应累加是内置 `sum()`。

### range

`range(start, stop[, step])`
> `range(10)` # 从 0 开始到 9 → [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

### 负数索引

Python 中负数索引从末尾往前数：-1 是最后一个元素，-2 是倒数第二个

### ord

ord函数的主要功能是将单个字符转换为其对应的Unicode

> 💡【补充】逆函数是 `chr()`（码点→字符）。刷题高频用法：`ord(c) - ord('a')` 把字母映射到 0-25（438题字母异位词的计数数组下标就是这么来的）。

### 切片赋值插入

```python
my_list = [1, 2, 3]
# 在索引 1 的位置插入新元素（不替换任何旧元素）
my_list[1:1] = ['a', 'b']
print(my_list)  # 输出：[1, 'a', 'b', 2, 3]
```

> 💡【补充】切片赋值是通用替换操作：`lst[1:3] = []` 删除一段、`lst[1:2] = ['x','y']` 一换多。比 `insert()` 灵活但可读性差，刷题酌情用。

---

## 6. collections 模块

### deque 双端队列

```python
from collections import deque

# 创建一个 deque
d = deque()                            # deque([])
d = deque([1, 2, 3, 4])                # deque([1, 2, 3, 4])
d = deque("hello")                     # deque(['h', 'e', 'l', 'l', 'o'])
d = deque(maxlen=3)                    # deque([], maxlen=3)
```

| 方法 | 描述 | 时间复杂度 |
|---|---|---|
| `append(x)` | 在右端添加一个元素 x | O(1) |
| `appendleft(x)` | 在左端添加一个元素 x | O(1) |
| `extend(iterable)` | 在右端一次性添加多个元素 | O(k) |
| `extendleft(iterable)` | 在左端一次性添加多个元素。注意：添加后的顺序会反转 | O(k) |
| `pop()` | 移除并返回右端的一个元素 | O(1) |
| `popleft()` | 移除并返回左端的一个元素 | O(1) |
| `remove(value)` | 移除第一个值为 value 的元素 | O(n) |
| `clear()` | 移除所有元素 | O(n) |
| `rotate(n=1)` | 将队列中的所有元素向右或向左移动 n 步。n>0 右移，n<0 左移 | — |
| `count(value)` | 统计值为 value 的元素个数 | — |
| `index(value)` | 返回第一个值为 value 的元素的索引 | — |
| `reverse()` | 原地反转 deque 中的元素顺序 | — |

> 💡【补充】deque 的两大刷题场景：①**单调队列**（239滑动窗口最大值的核心数据结构——队首存当前窗口最大值下标，新元素从队尾挤掉所有比它小的）；②**BFS 层序遍历**（`popleft()` O(1)，用 list 当队列则 `pop(0)` 是 O(n)）。`maxlen` 参数适合做"定长滑动窗口"，满了自动从另一端挤出。

### Counter

```python
dic = Counter(list1)
```
返回的是dict，键值对为元素及其频率

> 💡【补充】严格说 `Counter` 是 **dict 的子类**（需 `from collections import Counter`），但比 dict 多三个关键特性：
> 1. 访问不存在的键返回 **0** 而不是 KeyError（和 defaultdict(int) 行为一致，76/438题字符计数常因此省掉判空）
> 2. `c.most_common(k)` 直接取频率前 k 名
> 3. 支持 `+` / `-` 运算（合并/扣减计数）

### any / all

`any()` 函数用于判断给定的可迭代参数 iterable 是否全部为 False，则返回 False，如果有一个为 True，则返回 True。

含有空list的list不是空

> 💡【补充】搭档函数 `all()`：全部为 True 才返回 True（空可迭代对象时 `any([])` 为 False、`all([])` 为 True）。
> "含有空list的list不是空"的精确语义，刷题二维数组判空高频坑：
> - `bool([[]])` → **True**（外层list长度为1）
> - `any([[]])` → **False**（内层空list是falsy值）
> - 判断"二维数组是否有效"常用 `if matrix and matrix[0]:`

### // 除法向下取整

`// 除法向下取整`

> 💡【补充】`//` 是**地板除**（向下取整）：`7 // 2 = 3`，但 `-7 // 2 = -4`（向负无穷取整，不是向零截断）。与 C/Java 的整数除法（向零截断，`-7/2 = -3`）不同——面试常考。

### for _ in range(k)（占位变量）

`for _ in range(k): 就是循环 k 次的意思。`

这里的关键在于那个下划线 `_`。在 Python 中，它是一个合法的变量名，但被社区约定俗成地用作"一次性（Throwaway）"变量，用来占位表示"这个值我暂时用不到，随便循环几次就行"。

> 💡【补充】刷题高频场景：链表题"快指针先走 k 步"（`for _ in range(k): fast = fast.next`，见链表专题笔记）、K 个一组反转的探测/组内反转循环。同理 `_` 也可用于解包时丢弃值：`a, _ = divmod(x, y)`。