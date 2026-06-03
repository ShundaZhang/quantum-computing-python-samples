# 量子计算与 Qiskit 学习指南

这份文档面向已经会一点 Python、但刚开始学习量子计算的读者。它不会假设你已经懂量子力学，但会保留必要的数学表达，因为量子计算的核心正是“状态向量如何被线性变换改变，以及测量如何把概率分布变成样本”。

## 1. 为什么选择 Qiskit

Python 量子计算生态里常见选择包括 Qiskit、Cirq、PennyLane、QuTiP、tket 等。它们各有重点：

- Qiskit：通用量子电路、模拟、transpiler、IBM Quantum 生态、教学资料丰富。
- Cirq：Google 量子生态，适合研究硬件拓扑和电路。
- PennyLane：量子机器学习和可微分编程体验很好。
- QuTiP：偏量子物理系统和开放量子系统模拟。
- tket/pytket：偏编译优化和多后端工作流。

本仓库选择 Qiskit，是因为它对初学者和工程读者都友好：你可以从 `QuantumCircuit` 起步，逐步接触 statevector、density matrix、simulator、noise model、transpile、优化算法和真实后端。

## 2. 量子比特是什么

经典 bit 只有两个值：`0` 或 `1`。量子 bit，也就是 qubit，可以处于两个基态的线性组合：

```text
|psi> = alpha |0> + beta |1>
```

其中 `alpha` 和 `beta` 是复数振幅，并且满足：

```text
|alpha|^2 + |beta|^2 = 1
```

测量时，你不会直接看到 `alpha` 或 `beta`。你会以 `|alpha|^2` 的概率看到 `0`，以 `|beta|^2` 的概率看到 `1`。

Hadamard 门 `H` 是最常见的入门门：

```text
H |0> = (|0> + |1>) / sqrt(2)
```

因此对 `|0>` 施加 `H` 后测量，理论上 0 和 1 各有 50% 概率。

## 3. 多量子位与张量积

两个 qubit 的基态有四个：

```text
|00>, |01>, |10>, |11>
```

如果第一个 qubit 处于 `a|0> + b|1>`，第二个 qubit 处于 `c|0> + d|1>`，整体状态是张量积：

```text
(a|0> + b|1>) ⊗ (c|0> + d|1>)
```

展开后会得到四个基态的振幅。随着 qubit 数量增加，状态空间大小按 `2^n` 增长，这也是为什么经典模拟量子电路会很快变贵。

## 4. 纠缠

纠缠是量子计算最重要的概念之一。Bell 态：

```text
(|00> + |11>) / sqrt(2)
```

不能拆成两个独立单 qubit 状态的张量积。测量第一个 qubit 得到 0 时，第二个也会是 0；测量第一个得到 1 时，第二个也会是 1。注意，这不是“提前藏好的经典随机数”那么简单；在更严格的实验中，Bell 不等式能区分量子纠缠和经典局域隐变量模型。

在 Qiskit 中，Bell 态通常这样做：

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
```

`H` 让 qubit 0 进入叠加，`CX` 把 qubit 0 的信息纠缠到 qubit 1。

## 5. 量子门与电路模型

量子门本质上是对状态向量的酉矩阵变换。常见门包括：

| 门 | 作用 |
| --- | --- |
| `X` | 类似经典 NOT，交换 `|0>` 和 `|1>` |
| `Z` | 对 `|1>` 加一个负号，相位翻转 |
| `H` | 在计算基和叠加基之间转换 |
| `RX/RY/RZ` | 绕 Bloch 球的 x/y/z 轴旋转 |
| `CX` | controlled-X，控制位为 1 时翻转目标位 |
| `CZ` | controlled-Z，控制位为 1 时给目标相位 |
| `RZZ` | 两 qubit 的 ZZ 相互作用，QAOA 中常见 |
| `MCX` | 多控制 X，构造 oracle 时常见 |

Qiskit 的核心对象是 `QuantumCircuit`。你向 circuit 添加门，最后测量到 classical bits。

## 6. 测量与 shots

量子测量会把量子态投影到经典结果。模拟器或真实硬件通常会重复运行同一电路多次，这个次数叫 `shots`。例如：

```python
counts = {"0": 498, "1": 526}
```

这表示 1024 次实验中，测得 0 有 498 次，测得 1 有 526 次。shots 越多，统计分布越接近理论概率，但运行成本也越高。

## 7. Qiskit 中的几个核心 API

### QuantumCircuit

描述量子电路的对象。它记录 qubit、classical bit、门、测量和控制流。

### Statevector

精确状态向量模拟，适合小规模电路和教学。它不采样，直接给出振幅。

### DensityMatrix

密度矩阵可以描述混合态，也常用于计算某个子系统的 reduced state。隐形传态示例中，我们用它检查 qubit 2 是否真的拿到了输入态。

### AerSimulator

`qiskit-aer` 提供的高性能本地模拟器。它支持 shots、噪声模型和多种模拟方法。

### transpile

把抽象电路编译成目标 backend 支持的门集和拓扑。即便只用模拟器，理解 transpile 也很重要，因为真实硬件不能随便执行任意门和任意连接。

## 8. Qiskit 的比特序

初学者最容易卡住的点之一是 bit order。

在代码中，qubit 往往按索引 `0, 1, 2...` 表示；但 counts 字符串显示时，左边通常是最高索引 classical bit。例如：

```text
counts = {"10": 1024}
```

这通常表示 classical bit 1 是 `1`，classical bit 0 是 `0`。如果你把 bitstring 当作节点 assignment，需要明确转换。本仓库在 `src/quantum_samples/common.py` 中提供了：

- `bitstring_to_assignment`
- `assignment_to_bitstring`

综合场景中的 QAOA 和路线 bitstring 都使用这两个函数避免混乱。

## 9. Oracle 是什么

很多量子算法把问题装进一个 oracle。你可以把 oracle 想成一个黑盒函数，它在量子叠加上同时作用。

Grover 搜索通常需要一个 phase oracle：

```text
|x> -> -|x>  if x is the target
|x> ->  |x>  otherwise
```

这个负号本身测不出来，但它会在后续的 diffuser 中变成可测的振幅放大。

## 10. QFT 与相位估计

量子傅里叶变换 QFT 是很多算法的核心，比如 Shor 算法和量子相位估计。它把周期性和相位信息转换成计算基上的分布。

量子相位估计 QPE 的目标是：给定一个酉算子 `U` 和它的本征态 `|u>`，如果：

```text
U |u> = exp(2πiθ) |u>
```

QPE 可以估计 `θ`。本仓库用一个单 qubit phase gate 构造最小示例，选择 `θ = 3/8`，因此 3 个 evaluation qubits 可以精确读出 `011`。

## 11. VQE：混合量子-经典算法

Variational Quantum Eigensolver 的模式是：

1. 选择一个带参数的量子电路，也叫 ansatz。
2. 在量子电路上制备状态。
3. 测量 Hamiltonian 的期望值，也就是能量。
4. 用经典优化器更新参数。
5. 重复直到能量尽量低。

真实 VQE 会涉及 Pauli decomposition、shot noise、optimizer、硬件误差缓解等细节。本仓库为了让代码透明，使用小 Hamiltonian 和网格搜索，不引入额外优化器。

## 12. QAOA：优化问题示例

Quantum Approximate Optimization Algorithm 常用于组合优化示例。它交替使用：

- cost unitary：把目标函数编码进相位；
- mixer unitary：让状态在候选解之间流动；
- classical optimizer：寻找好的参数。

本仓库的综合场景用一层 QAOA 解一个四节点 MaxCut 玩具问题。它不是大规模优化器，只是展示“问题图 -> 参数化电路 -> 期望值 -> 采样解”的完整形状。

## 13. 噪声模型

真实量子设备有噪声，包括退相干、门误差、读出误差等。`qiskit-aer` 的 `NoiseModel` 可以在本地模拟中加入简化噪声。

综合场景中，我们比较理想 Bell 态和带 depolarizing noise 的 Bell 态：

- 理想情况主要出现 `00` 和 `11`；
- 噪声情况下可能出现少量 `01` 和 `10`。

这能帮助读者理解：真实量子计算不是只写对电路就结束，还必须考虑硬件误差和编译。

## 14. 如何继续扩展这个仓库

你可以尝试：

1. 把 Grover 的候选空间从 2 qubits 扩展到 3 或 4 qubits。
2. 给 Deutsch-Jozsa 写更多 balanced oracle。
3. 把 VQE 的网格搜索换成 `scipy.optimize.minimize`。
4. 给 QAOA 增加层数 `p`。
5. 加入 measurement error mitigation 的演示。
6. 接入 IBM Quantum Runtime，把某些小电路提交到真实后端。
7. 为每个示例生成 circuit diagram 图片，放到文档里。

最好的学习方式是先改小参数：shots、seed、oracle target、phase、noise rate。每改一次，观察 counts 怎么变。
