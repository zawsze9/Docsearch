# 廖雪峰Python教程笔记 —— 高级特性

> 整理说明：格式规范化重排，原文内容未改写；整理者补充均以 💡【补充】醒目标注。

---

## 1. 切片

list或tuple都可切片

> 💡【补充】str 同样可切片（`'abc'[::-1]` 是经典反转写法）；切片对 tuple 返回 tuple、对 list 返回 list、对 str 返回 str——返回类型跟随原类型。

## 2. 迭代

`collections.abc` 模块的 `Iterable` 类型判断：`isinstance('abc', Iterable)` # str是否可迭代

> 💡【补充】dict 默认迭代的是 **key**；迭代键值对用 `d.items()`，迭代值用 `d.values()`。

## 3. 列表生成式

```python
[x * x for x in range(1, 11) if x % 2 == 0]
```

- 可以多层循环
- for前面的 `if ... else` 是表达式，而 for后面的 `if` 是过滤条件，不能带 else

> 💡【补充】把 `[]` 换成 `()` 就是**生成器表达式**（见下节），不立即生成完整列表，省内存——刷题写 `sum(x*x for x in nums)` 比 `sum([x*x for x in nums])` 更优。

## 4. 生成器 generator

### 定义方法

**方法1：把list生成式的 `[]` 换成 `()`**

**方法2：generator函数（使用 `yield`）**

```python
def fib(max):
    n, a, b = 0, 0, 1
    while n < max:
        yield b
        a, b = b, a + b
        n = n + 1
    return 'done'
```

generator函数，在每次调用 `next()` 的时候执行，遇到 `yield` 语句返回，再次执行时从上次返回的 `yield` 语句处继续执行。

> 💡【补充】generator 函数跑完后会抛 `StopIteration`，`return 'done'` 的返回值存放在 `StopIteration.value` 里（用 for 循环遍历时拿不到它，for 会自动忽略）。这是廖教程原章节末尾的要点，建议补进笔记。

## 5. 迭代器 Iterator

可以被 `next()` 函数调用并不断返回下一个值的对象称为迭代器：`Iterator`

```python
isinstance([], Iterator)  # False
```

> 💡【补充】三者的关系（面试高频）：
> - **Iterable**（可迭代对象）：list / tuple / dict / str / generator 都是
> - **Iterator**（迭代器）：只有 generator 等"懒计算"对象是；list 等容器**不是**
> - 用 `iter([])` 可以把 Iterable 变成 Iterator；`for` 循环底层就是先调 `iter()` 再反复调 `next()`


---

# 函数式编程（7.28）

## 6. 高阶函数

变量可以指向函数：
```python
f = abs
f(-10)  # 10
```
函数名也是变量。

一个函数可以接收另一个函数作为参数，这种函数就称之为高阶函数。

- **map()**：接收两个参数，一个是函数，一个是Iterable，map将传入的函数依次作用到序列的每个元素，并把结果作为新的Iterator返回。
  ```python
  list(map(str, [1, 2, 3, 4, 5, 6, 7, 8, 9]))
  ```
- **reduce()**：把一个函数作用在一个序列[x1, x2, x3, ...]上，这个函数必须接收两个参数，reduce把结果继续和序列的下一个元素做累积计算，其效果就是：
  `reduce(f, [x1, x2, x3, x4]) = f(f(f(x1, x2), x3), x4)`
- **filter()**：把传入的函数依次作用于每个元素，然后根据返回值是True还是False决定保留还是丢弃该元素
- **sorted()**：也是一个高阶函数，它还可以接收一个key函数来实现自定义的排序
  ```python
  sorted(['bob', 'about', 'Zoo', 'Credit'], key=str.lower, reverse=True)
  ```

> 💡【补充】Python3 中 map/filter 返回的是**惰性 Iterator**，要用 `list()` 才能看到结果（和Py2返回list不同，面试可能问）；reduce 不在内置命名空间，需 `from functools import reduce`。

## 7. 返回函数与闭包

可以把函数作为结果值返回，再次调用时才返回结果。

**闭包**是一个函数，它可以访问并记住自己定义时的作用域（即使该作用域已经执行完毕）。
本质：函数内部嵌套的函数，能够"捕获"外部函数的变量，并长期保留这些变量的引用。

返回闭包时牢记一点：返回函数不要引用任何循环变量，或者后续会发生变化的变量。

使用闭包，就是内层函数引用了外层函数的局部变量，如果对外层变量赋值，会报错。使用闭包时，对外层变量赋值前，需要先使用 `nonlocal` 声明该变量不是当前函数的局部变量。

```python
def outer():
    x = 0
    def inner():
        nonlocal x
        x += 1
        return x
    return inner
```

> 💡【补充】循环变量陷阱的经典例子（廖教程原例，务必亲手跑一遍）：
> ```python
> def count():
>     fs = []
>     for i in range(1, 4):
>         def f():
>             return i * i
>         fs.append(f)
>     return fs
>
> f1, f2, f3 = count()
> f1(), f2(), f3()   # 9, 9, 9 —— 不是 1, 4, 9！三个闭包共享同一个 i（调用时 i 已是 3）
> ```
> 修复方法：用默认参数把当前值绑定进去 `def f(i=i): return i * i`。

## 8. 匿名函数 lambda

关键字 `lambda` 表示匿名函数，冒号前面的表示函数参数，返回值就是该表达式的结果。

> 💡【补充】lambda 只能写**单个表达式**（不能写语句/赋值）；刷题最高频场景是配合 key：`sorted(d.items(), key=lambda x: -x[1])`、`max(lst, key=lambda x: x[1])`。

## 9. 装饰器 Decorator

函数对象有一个 `__name__` 属性，可以拿到函数的名字。

在代码运行期间动态增加功能的方式，称之为"装饰器"（Decorator）。在 Python 中，`@` 是装饰器的标志，用于修饰函数或类。

如果decorator本身需要传入参数，那就需要编写一个返回decorator的高阶函数。

~~@functools.wraps(func)在装饰器内部修改_name_属性~~

> ⚠️【订正】属性名是 `__name__`（双下划线）。且 `functools.wraps` 的作用不是"修改"而是**保留**：装饰器本质是把原函数替换成了 wrapper，导致 `func.__name__` 变成 `'wrapper'`、`__doc__` 丢失；`@functools.wraps(func)` 把原函数的元信息复制到 wrapper 上，避免这个问题。

> 💡【补充】两个必懂点：
> 1. **@语法等价与执行时机**：`@log` + `def now(): ...` 等价于 `now = log(now)`——**装饰在函数定义时立即发生**（import 模块时就执行），不是调用时。
> 2. **带参数的装饰器是三层嵌套**：`@log('execute')` 的结构是 `def log(text)` → `def decorator(func)` → `def wrapper(*args, **kw)`。
>
> 标准模板（今天的 @timer 作业就按这个写）：
> ```python
> import functools
>
> def log(func):
>     @functools.wraps(func)
>     def wrapper(*args, **kw):
>         # 前置逻辑
>         result = func(*args, **kw)
>         # 后置逻辑
>         return result
>     return wrapper
> ```

## 10. 偏函数 functools.partial

`functools.partial` 的作用就是，把一个函数的某些参数给固定住（也就是设置默认值），返回一个新的函数，调用这个新函数会更简单。

```python
int2 = functools.partial(int, base=2)
```