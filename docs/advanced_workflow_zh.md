# 综合场景：Quantum-assisted Dispatch Lab

这个综合场景是一个教学型故事，不是生产级调度系统。它的目标是把尽可能多的常见量子计算构件放到同一条可运行流程里，让读者看到它们在工程代码里如何组织。

入口：

```bash
quantum-samples --shots 1024 advanced --output outputs/advanced_report.json
```

核心代码：

```text
src/quantum_samples/advanced_workflow.py
```

## 1. 场景设定

假设有一个调度系统，要从四条路线中选出一条：

| bitstring | 路线 | distance | congestion | battery_risk | priority |
| --- | --- | ---: | ---: | ---: | ---: |
| `00` | north ridge | 2 | 2 | 1 | 3 |
| `01` | east tunnel | 1 | 4 | 2 | 2 |
| `10` | south bridge | 3 | 1 | 1 | 5 |
| `11` | west harbor | 2 | 3 | 3 | 4 |

示例评分：

```text
score = priority * 3 - distance - congestion - battery_risk
```

最高分路线是 `10 / south bridge`。后续 Grover oracle 会标记这个 bitstring。

## 2. 流程总览

| 步骤 | 代码函数 | 量子计算概念 | 输出 |
| --- | --- | --- | --- |
| 1 | `quantum_random_bits` | QRNG、Hadamard、测量 | 随机 bit 串 |
| 2 | `bb84_sifted_key` | BB84 basis sifting | sifted key |
| 3 | `superdense_coding_demo` | Bell pair、超密编码 | 解码路线 bit |
| 4 | `teleport_route_state` | 隐形传态、fidelity | 传态保真度 |
| 5 | `choose_route_with_grover` | phase oracle、振幅放大 | 选中路线 |
| 6 | `phase_estimation_demo` | QPE、inverse QFT | phase bits |
| 7 | `vqe_demo` | ansatz、Hamiltonian、期望值 | 最低能量近似 |
| 8 | `qaoa_route_partition` | QAOA、MaxCut | 分区 bitstring |
| 9 | `noisy_bell_comparison` | noise model | 理想/噪声 counts |
| 10 | `transpilation_snapshot` | transpile、depth、ops | 编译前后指标 |

## 3. QRNG：用量子叠加生成随机位

`quantum_random_bits` 对每个 qubit 施加 Hadamard，然后测量：

```python
circuit.h(range(width))
circuit.measure(range(width), range(width))
```

因为模拟器默认 backend 宽度有限，函数分 chunk 生成随机位，而不是一次构造 64 qubits。这样更贴近实际工程：不要假设 backend 能接受任意宽电路。

在真实硬件上，QRNG 的随机性来自量子测量；在本地模拟器中，我们固定 seed 以便教学和测试复现。

## 4. BB84 思想：basis sifting

BB84 是量子密钥分发的经典协议。本项目没有模拟完整窃听检测和硬件通道，而是演示核心 basis sifting 思想：

1. Alice 选择随机 bit 和随机 basis。
2. Bob 选择随机 basis 测量。
3. Alice 和 Bob 公开比较 basis，不公开 bit。
4. basis 相同的位置保留下来，形成 sifted key。

代码中：

```python
if sender_bases[index] == receiver_bases[index]:
    measured = bit
    sifted.append(measured)
else:
    measured = fallback[index]
```

当 basis 不同时，测量结果在理想模型里是随机的，所以示例用 QRNG 的 fallback bits 表示。

## 5. 超密编码：发送路线 bit

Grover 选择路线后，路线 bitstring 需要作为控制消息传出。超密编码展示了共享 Bell pair 的通信能力：

```python
superdense_coding_demo(message=chosen_route.bitstring)
```

如果路线是 `10`，Bob 解码后应该得到 `10`。这个步骤的作用是把“纠缠资源如何服务通信协议”放进流程。

## 6. 隐形传态：传递路线风险 qubit

`teleport_route_state` 把路线风险编码成单 qubit 角度：

```python
theta = (route.battery_risk + route.congestion) / 8 * pi
phi = route.distance / 8 * pi
```

然后调用 `teleportation_circuit`，最后比较输入态和输出 qubit 的 fidelity：

```python
output_state = partial_trace(DensityMatrix.from_instruction(circuit), [0, 1])
state_fidelity(input_state, output_state)
```

输出接近 1，表示传态正确。

## 7. Grover：选择最高分路线

路线数量为 4，所以用 2 qubits 表示候选空间。phase oracle 标记最高分路线：

```text
target = "10"
```

Grover 的直觉：

1. 用 Hadamard 准备所有候选的均匀叠加。
2. oracle 给目标态加负号。
3. diffuser 围绕平均值反射，放大目标振幅。
4. 测量得到目标。

四个候选时，一次 Grover iteration 就能把目标概率推到 1，因此测试中 `found == "10"`。

## 8. QPE：传感器相位校准

流程中加入 QPE 作为“传感器相位校准”的示意。我们构造一个已知 phase：

```text
theta = 3/8
```

三位二进制刚好是：

```text
011
```

QPE 输出：

```text
measured_bits = "011"
estimated_phase = 0.375
```

这个步骤展示了 QFT 类子程序如何把相位信息变成 classical bits。

## 9. VQE：能量代理估计

调度系统里可以想象有一个“能耗/风险 Hamiltonian”。示例使用一个两 qubit toy Hamiltonian：

```python
("II", 0.20)
("ZI", -0.75)
("IZ", -0.45)
("ZZ", 0.35)
("XX", 0.55)
```

VQE 做的是：

1. 用参数化 ansatz 制备状态。
2. 计算 Hamiltonian 期望值。
3. 经典网格搜索参数。
4. 找到最低能量近似。

真实 VQE 通常需要更好的 ansatz、优化器、shot-based expectation、误差缓解和问题映射。这里保留最小可懂版本。

## 10. QAOA：路线监控分区

QAOA 部分把四个路线监控节点构造成 MaxCut 图：

```python
edges = [(0, 1), (1, 2), (2, 3), (0, 3), (1, 3)]
```

一层 QAOA：

```python
for left, right in edges:
    circuit.rzz(2 * gamma, left, right)
for qubit in range(nodes):
    circuit.rx(2 * beta, qubit)
```

然后在 `gamma` 和 `beta` 网格上搜索期望 cut value。最后采样得到一个分区 bitstring，例如：

```text
1010
```

这表示哪些节点在一侧，哪些在另一侧。因为 Qiskit counts 字符串和 qubit index 顺序不同，代码会用 `bitstring_to_assignment` 转换。

## 11. 噪声比较

`noisy_bell_comparison` 创建一个简化 depolarizing noise model：

```python
noise_model.add_all_qubit_quantum_error(depolarizing_error(0.01, 1), ["h", "x", "z", "rx", "ry"])
noise_model.add_all_qubit_quantum_error(depolarizing_error(0.04, 2), ["cx", "cz", "rzz"])
```

理想 Bell 态只应看到：

```text
00, 11
```

加入噪声后可能看到：

```text
01, 10
```

这提醒读者：量子算法和硬件执行之间还有编译、校准、噪声、误差缓解等工程层。

## 12. Transpilation

最后，`transpilation_snapshot` 比较电路编译前后的：

- depth；
- operation counts。

模拟器上的变化可能很小，但真实设备上 transpiler 会考虑 basis gates、coupling map、优化级别和布局。写量子程序时，抽象电路只是第一步，能否在目标 backend 上高质量执行是另一件事。

## 13. 如何修改这个场景

你可以做以下练习：

1. 改 `ROUTES` 的评分，让 Grover target 变成其他 bitstring。
2. 把路线数量扩展到 8 条，修改 Grover oracle 为 3 qubits。
3. 改 QPE 的 phase，例如 `5/8`，观察 measured bits。
4. 提高 noise rate，观察 Bell counts 中错误项如何增加。
5. 给 QAOA 增加更多 edges，观察 best partition 变化。
6. 把 VQE 的 grid search 换成 scipy optimizer。
7. 把报告 JSON 转成 Markdown 或图表。

## 14. 重要限制

这个综合流程是教学用的“概念串联”，不是量子优势证明。特别是：

- QRNG 在本地模拟器中是伪随机且固定 seed 的。
- BB84 没有模拟真实信道、窃听者和误码率估计。
- Grover 的问题规模很小，经典 brute force 更简单。
- VQE 和 QAOA 都是玩具问题。
- 噪声模型是简化 depolarizing noise，不代表真实设备完整噪声。

这些限制是有意保留的：初学者先看清楚结构，再逐步把每个模块替换成更真实的版本。
