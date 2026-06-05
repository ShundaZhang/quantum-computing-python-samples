# 量子计算快速入门

这是一份“先跑起来，再慢慢理解”的快速入门文档。读完后，你应该能做到三件事：

- 看懂最小量子电路：qubit、gate、measurement、shots。
- 知道叠加、纠缠、干涉、oracle 为什么是量子算法的关键词。
- 用本仓库运行 Qiskit 示例，并知道下一步该改哪里。

如果你只想快速建立直觉，先按“30 分钟路线”读；如果想能自己改代码，按“90 分钟路线”读。

## 30 分钟路线

1. 读完本文第 1 到第 6 节。
2. 安装依赖并运行基础示例：

   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   quantum-samples --shots 1024 basics
   ```

3. 重点观察三个输出：

   - `Hadamard superposition`：结果接近 0/1 各一半。
   - `Bell-state entanglement`：只出现 `00` 和 `11`。
   - `Grover search`：几乎总能找到目标 bitstring。

## 90 分钟路线

1. 跑完 30 分钟路线。
2. 单独运行每个 example：

   ```bash
   python examples/01_superposition.py
   python examples/02_bell_entanglement.py
   python examples/06_grover_search.py
   python examples/07_phase_estimation.py
   python examples/08_vqe.py
   ```

3. 阅读：

   - `docs/example_walkthrough_zh.md`
   - `docs/advanced_workflow_zh.md`

4. 修改三个参数：

   - 把 Grover target 从 `"10"` 改成 `"11"`。
   - 把 QPE phase 从 `3 / 8` 改成 `5 / 8`。
   - 把 `shots` 从 `128` 改成 `4096`，观察统计波动变小。

## 1. 量子计算到底在算什么

经典计算处理 bit。bit 是 `0` 或 `1`。

量子计算处理 qubit。一个 qubit 可以写成：

```text
|psi> = alpha |0> + beta |1>
```

这里的 `alpha` 和 `beta` 是振幅。它们不是直接测出来的概率，但概率来自振幅：

```text
P(0) = |alpha|^2
P(1) = |beta|^2
```

所以量子计算的核心不是“一个 qubit 同时等于 0 和 1，所以暴力并行”。更准确的说法是：

```text
量子程序操纵振幅，让正确答案的振幅变大，让错误答案的振幅互相抵消。
```

这就是为什么“干涉”很重要。

## 2. 最小 Qiskit 电路

下面是一个最小量子随机数生成器：

```python
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

circuit = QuantumCircuit(1, 1)
circuit.h(0)
circuit.measure(0, 0)

backend = AerSimulator(seed_simulator=42)
compiled = transpile(circuit, backend)
counts = backend.run(compiled, shots=1024).result().get_counts()

print(counts)
```

你可能看到：

```text
{'0': 505, '1': 519}
```

逐行理解：

- `QuantumCircuit(1, 1)`：1 个 qubit，1 个 classical bit。
- `h(0)`：对第 0 个 qubit 施加 Hadamard 门，让它进入 50/50 叠加。
- `measure(0, 0)`：把 qubit 0 测量到 classical bit 0。
- `shots=1024`：重复执行 1024 次，统计结果。

## 3. 三个最重要的直觉

### 叠加

叠加不是“模糊的经典状态”，而是振幅的线性组合。

```text
H |0> = (|0> + |1>) / sqrt(2)
```

单次测量只会得到一个 classical 结果。你看不到“半个 0 半个 1”，只能通过很多次 shots 估计概率。

### 纠缠

Bell 态是最常见的纠缠态：

```text
(|00> + |11>) / sqrt(2)
```

测量后，你会看到 `00` 或 `11`，几乎不会看到 `01` 或 `10`。这说明两个 qubit 的结果不是独立的。

Qiskit 代码：

```python
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])
```

### 干涉

量子算法的关键是让振幅相加或相消。

Grover 搜索就是典型例子：

1. 所有候选答案先进入均匀叠加。
2. oracle 给目标答案加一个负相位。
3. diffuser 通过反射放大目标答案。
4. 测量时目标答案概率变大。

## 4. 常见量子门速查

| 门 | 你可以先这样理解 |
| --- | --- |
| `X` | 类似经典 NOT，`0` 和 `1` 互换 |
| `Z` | 相位翻转，对 `|1>` 加负号 |
| `H` | 在确定态和均匀叠加之间转换 |
| `RX/RY/RZ` | 绕 Bloch 球三个轴旋转 |
| `CX` | 如果控制位是 1，就翻转目标位 |
| `CZ` | 如果控制位是 1，就给目标位加相位 |
| `MCX` | 多控制 X，常用于构造 oracle |
| `RZZ` | 两 qubit 的 ZZ 相互作用，QAOA 常用 |

一开始不需要背矩阵。先记住每个门在示例中的作用，再回头补线性代数。

## 5. counts、statevector、density matrix

Qiskit 里你会经常看到三种结果。

### counts

`counts` 是实际测量或模拟采样后的统计：

```text
{'00': 506, '11': 518}
```

它最接近真实硬件输出。

### statevector

`Statevector` 是完整振幅：

```text
|psi> = 0.707 |00> + 0.707 |11>
```

它适合学习和小规模调试，但真实硬件不会直接给你 statevector。

### density matrix

`DensityMatrix` 可以描述混合态，也能提取子系统状态。比如隐形传态示例里，我们用它检查 Bob 的 qubit 是否真的拿到了 Alice 的输入态。

## 6. 最容易踩的坑：Qiskit bit order

如果你看到：

```text
{'10': 1024}
```

不要立刻以为 qubit 0 是 1、qubit 1 是 0。Qiskit 的 counts 字符串显示的是 classical bits 的顺序，左边通常是最高索引 classical bit。

本仓库提供了两个工具函数：

```python
bitstring_to_assignment("10")
assignment_to_bitstring([0, 1])
```

当你把 bitstring 当作图节点、路线编号、优化变量时，一定要明确这个转换。

## 7. 五个入门算法怎么串起来理解

### Deutsch-Jozsa

目标：判断 oracle 是 constant 还是 balanced。

你应该记住：

```text
它展示的是量子查询复杂度优势。
```

它不是现实里最常用的商业算法，但很适合理解 phase kickback。

### Grover

目标：在无结构候选中找一个被 oracle 标记的答案。

你应该记住：

```text
它通过 oracle 标记 + 振幅放大，把目标答案的测量概率变大。
```

完整推导和图解见 [grover_algorithm_zh.md](grover_algorithm_zh.md)。

### [QPE](glossary_zh.md#qpe)

目标：估计酉算子的本征相位。

你应该记住：

```text
[QPE](glossary_zh.md#qpe) 把相位信息变成可读的二进制 bits。
```

它是 Shor 算法等更复杂算法的重要子程序。

### [VQE](glossary_zh.md#vqe)

目标：估计 [Hamiltonian](glossary_zh.md#hamiltonian) 的低能量态。

你应该记住：

```text
[VQE](glossary_zh.md#vqe) = 参数化量子电路 + 经典优化器。
```

它是 NISQ 时代很常见的混合量子-经典算法范式。

### [QAOA](glossary_zh.md#qaoa)

目标：求组合优化问题的近似解，例如 MaxCut。

你应该记住：

```text
[QAOA](glossary_zh.md#qaoa) = [cost layer](glossary_zh.md#cost-layer) + [mixer layer](glossary_zh.md#mixer-layer) + 参数搜索。
```

本仓库在综合场景中用 QAOA 做四节点 MaxCut 教学示例。

## 8. 建议你先运行这些命令

基础示例：

```bash
quantum-samples --shots 1024 basics
```

综合场景：

```bash
quantum-samples --shots 1024 advanced --output outputs/advanced_report.json
```

只看 Grover：

```bash
python examples/06_grover_search.py
```

只看 QPE：

```bash
python examples/07_phase_estimation.py
```

只看 VQE：

```bash
python examples/08_vqe.py
```

## 9. 三个小练习

### 练习 1：改变 shots

运行：

```bash
quantum-samples --shots 64 basics
quantum-samples --shots 4096 basics
```

观察 Hadamard 示例中 `0` 和 `1` 的比例。shots 越大，比例通常越接近 50/50。

### 练习 2：改变 Grover 目标

打开 `src/quantum_samples/demos.py`，找到：

```python
def grover_demo(target: str = "10", shots: int = 1024) -> dict[str, object]:
```

把运行时 target 改成 `"11"`，然后检查输出是否找到 `"11"`。

### 练习 3：改变相位估计

运行：

```python
from quantum_samples.demos import phase_estimation_demo

print(phase_estimation_demo(phase=5 / 8))
```

`5 / 8` 的三位二进制是 `101`，所以你应该看到 measured bits 接近 `101`。

## 10. 你现在应该掌握的词汇

| 词 | 快速解释 |
| --- | --- |
| qubit | 量子比特，状态是振幅向量 |
| gate | 量子门，对状态做酉变换 |
| circuit | 量子电路，由门和测量组成 |
| measurement | 测量，把量子态变成 classical 结果 |
| shots | 重复运行次数 |
| amplitude | 振幅，模平方给概率 |
| superposition | 叠加，多个基态的线性组合 |
| entanglement | 纠缠，不能拆成独立子系统的状态 |
| interference | 干涉，振幅相加或相消 |
| oracle | 把问题编码进量子电路的黑盒 |
| transpile | 把抽象电路编译到目标 backend |
| noise model | 模拟硬件误差的模型 |

## 11. 下一步读什么

建议顺序：

1. `docs/example_walkthrough_zh.md`：逐个理解本仓库的基础示例。
2. `docs/learning_guide_zh.md`：系统补全量子计算和 Qiskit 概念。
3. `docs/advanced_workflow_zh.md`：看一个复杂场景如何把算法串起来。
4. Qiskit 官方文档：学习真实 backend、primitives、Runtime、transpiler 和噪声。

最有效的学习方式是：每次只改一个参数，然后观察输出为什么变了。量子计算一开始容易显得抽象，但只要把“振幅如何被门改变，测量如何变成 counts”这条线抓住，就不会迷路。
