# 示例逐个讲解

本文对应 `examples/` 与 `src/quantum_samples/demos.py`。建议先运行：

```bash
quantum-samples --shots 1024 basics
```

然后对照下面说明阅读代码。

## 1. Hadamard 叠加

文件：`examples/01_superposition.py`

核心电路：

```python
circuit = QuantumCircuit(1, 1)
circuit.h(0)
circuit.measure(0, 0)
```

初始态是 `|0>`。施加 `H` 后变成：

```text
(|0> + |1>) / sqrt(2)
```

测量时，`0` 和 `1` 理论概率各 50%。模拟输出不会永远精确一半，因为 shots 是采样。1024 shots 时可能看到类似：

```text
0: 513, 1: 511
```

学习点：

- 振幅不是概率，振幅模平方才是概率。
- 单次测量只会得到一个经典 bit。
- 多次 shots 用于估计概率分布。

## 2. Bell 态纠缠

文件：`examples/02_bell_entanglement.py`

核心电路：

```python
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])
```

状态变化：

```text
|00>
-> H on q0
(|00> + |10>) / sqrt(2)
-> CX q0 -> q1
(|00> + |11>) / sqrt(2)
```

注意上面的表达和 Qiskit 显示 bit order 可能看起来不同，但物理含义是：两个 qubit 会同向相关。你应该主要看到：

```text
00, 11
```

而不是 `01` 或 `10`。

学习点：

- `CX` 可以把叠加态变成纠缠态。
- 纠缠态不能简单拆成两个独立 qubit。
- statevector 能显示振幅，counts 显示采样结果。

## 3. 超密编码

文件：`examples/03_superdense_coding.py`

超密编码回答的问题是：如果 Alice 和 Bob 已经共享一个 Bell pair，Alice 能否只发送一个 qubit，却传两个 classical bits？

流程：

1. Alice 和 Bob 共享 Bell pair。
2. Alice 根据两个 classical bits 对自己的 qubit 施加 `I/X/Z/XZ`。
3. Alice 把自己的 qubit 发给 Bob。
4. Bob 对两个 qubit 做 Bell basis 解码。
5. Bob 测量，得到两个 classical bits。

本仓库的编码约定：

```python
if message[0] == "1":
    circuit.x(0)
if message[1] == "1":
    circuit.z(0)
```

然后解码：

```python
circuit.cx(0, 1)
circuit.h(0)
circuit.measure([0, 1], [0, 1])
```

学习点：

- 共享纠缠可以增强通信协议。
- Alice 发送的是一个 qubit，但协议依赖预先共享的 Bell pair。
- 这不是超光速通信，因为 Bell pair 分发和 qubit 发送都受物理限制。

## 4. 量子隐形传态

文件：`examples/04_teleportation.py`

隐形传态回答的问题是：如果 Alice 有一个未知 qubit 态，能否用共享纠缠和 classical communication 把这个态转移给 Bob？

标准流程：

1. Alice 有待传输的 qubit `q0`。
2. Alice 和 Bob 共享 Bell pair：`q1` 在 Alice，`q2` 在 Bob。
3. Alice 对 `q0` 和 `q1` 做 Bell basis measurement。
4. Alice 把两个 classical bits 发给 Bob。
5. Bob 根据 bits 对 `q2` 做 `X/Z` 校正。

本仓库为了让 statevector 验证更简单，使用 coherent correction：用 `CX` 和 `CZ` 代替中途测量与 classical feed-forward。最终通过 reduced density matrix 检查 qubit 2：

```python
output_state = partial_trace(full_state, [0, 1])
fidelity = state_fidelity(input_state, output_state)
```

如果 fidelity 接近 1，说明 Bob 的 qubit 拿到了原状态。

学习点：

- 传输的是量子态，不是把物质本身传过去。
- 协议需要纠缠资源和 classical communication。
- fidelity 是比较两个量子态相似度的常用指标。

## 5. Deutsch-Jozsa

文件：`examples/05_deutsch_jozsa.py`

问题：给定一个函数 `f: {0,1}^n -> {0,1}`，承诺它要么 constant，要么 balanced。我们要判断它是哪种。

经典确定性算法最坏需要多次查询。Deutsch-Jozsa 在理想 oracle 下只需要一次量子查询。

电路结构：

1. 输入寄存器置于均匀叠加。
2. 输出 qubit 准备成 `|->`。
3. 调用 oracle。
4. 对输入寄存器再施加 Hadamard。
5. 测量输入寄存器。

结果：

- 全 0：constant。
- 非全 0：balanced。

学习点：

- 量子算法常通过相位回 kickback 获得全局信息。
- 这个例子强调 query complexity，而不是实际工程加速。

## 6. Grover 搜索

文件：`examples/06_grover_search.py`

Grover 用于无结构搜索。给定 `N` 个候选和一个 oracle，它能以约 `O(sqrt(N))` 次 oracle 查询找到目标。四个候选时，只需一次迭代就能把目标振幅放大到 1。

如果想看振幅放大、oracle、diffuser 和迭代次数的完整推导，读 [grover_algorithm_zh.md](grover_algorithm_zh.md)。

本仓库示例：

```python
target = "10"
oracle = phase_oracle(target)
circuit.h(range(len(target)))
circuit.compose(grover_operator(oracle), inplace=True)
```

`phase_oracle` 负责给目标态加负号，`grover_operator` 负责 diffuser 和整体放大。

学习点：

- oracle 只标记答案，不直接把答案告诉你。
- 负相位通过干涉变成可测概率。
- 迭代次数过多会“转过头”，概率反而下降。

## 7. 量子相位估计 [QPE](glossary_zh.md#qpe)

文件：`examples/07_phase_estimation.py`

[QPE](glossary_zh.md#qpe) 估计酉算子的本征相位。示例中选择：

```text
theta = 3/8 = 0.011 in binary
```

因此 3 个 evaluation qubits 可以精确测到 `011`。

核心步骤：

1. evaluation qubits 做 Hadamard。
2. 对 target qubit 施加受控的 `U^(2^k)`。
3. 对 evaluation register 做 [inverse QFT](glossary_zh.md#inverse-qft)。
4. 测量得到 phase bits。

学习点：

- [QPE](glossary_zh.md#qpe) 是很多重要算法的核心子程序。
- [QFT](glossary_zh.md#qft) 把相位信息转换到计算基。
- evaluation qubits 越多，估计精度越高。

## 8. [VQE](glossary_zh.md#vqe)

文件：`examples/08_vqe.py`

[VQE](glossary_zh.md#vqe) 是混合量子-经典算法：

```text
parameters -> quantum ansatz -> expectation value -> classical optimizer -> new parameters
```

本仓库使用一个小 [Hamiltonian](glossary_zh.md#hamiltonian)：

```python
SparsePauliOp.from_list([
    ("II", 0.20),
    ("ZI", -0.75),
    ("IZ", -0.45),
    ("ZZ", 0.35),
    ("XX", 0.55),
])
```

[ansatz](glossary_zh.md#ansatz) 是两个 `RY` 旋转加一个 `CX`。为了降低依赖和方便读者理解，优化器使用网格搜索。

学习点：

- [Hamiltonian](glossary_zh.md#hamiltonian) 期望值可以看作能量。
- [ansatz](glossary_zh.md#ansatz) 表达能力影响最优结果。
- 真实 VQE 中，测量 shot noise 和硬件误差很关键。

## 9. 综合工作流

文件：`examples/09_advanced_workflow.py`

这个脚本调用 `run_advanced_workflow()`，返回一个嵌套报告。它把多个主题串到一起：

- QRNG
- BB84 basis sifting
- Superdense coding
- Teleportation
- Grover search
- [QPE](glossary_zh.md#qpe)
- [VQE](glossary_zh.md#vqe)
- [QAOA](glossary_zh.md#qaoa)
- Noise model
- Transpilation

详细解释见 [advanced_workflow_zh.md](advanced_workflow_zh.md)。
