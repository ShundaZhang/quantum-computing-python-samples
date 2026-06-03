# Quantum Computing Python Samples

这是一个面向学习者的量子计算 Python 示例仓库。项目选择 **Qiskit** 作为主库：它是 IBM Quantum 维护的开源 Python SDK，官方文档覆盖电路、量子信息、模拟器、transpiler、primitives 等核心工作流；GitHub 上的 Qiskit 主题和生态资料也显示它仍是量子计算入门与研究中使用面很广的 Python 工具。

本仓库目标不是做一个抽象库，而是给读者一套可以直接运行、阅读和修改的样例：

- 常见基础例子：叠加、纠缠、超密编码、量子隐形传态、Deutsch-Jozsa、Grover、QPE、VQE。
- 一个较复杂的综合场景：把 QRNG、BB84 思想、超密编码、隐形传态、Grover、相位估计、VQE、QAOA、噪声模拟、transpilation 串在同一个故事里。
- 详细中文文档：从量子比特和门开始，逐步讲到 Qiskit 代码结构、比特序、模拟器、噪声和混合量子-经典优化。

参考入口：

- Qiskit 官方文档：https://quantum.cloud.ibm.com/docs/api/qiskit
- IBM Quantum 文档：https://docs.quantum.ibm.com
- Qiskit GitHub 主题页：https://github.com/topics/qiskit

## 项目结构

```text
.
├── examples/                         # 可单独运行的示例脚本
├── src/quantum_samples/
│   ├── common.py                      # AerSimulator、counts、比特序等工具函数
│   ├── demos.py                       # 常见量子计算例子
│   ├── advanced_workflow.py           # 综合串联场景
│   └── cli.py                         # 命令行入口
├── docs/
│   ├── quickstart_zh.md               # 量子计算快速入门
│   ├── quantum_computing_intro_course_zh.md
│   │                                  # 系统入门课程、习题与答案
│   ├── learning_guide_zh.md           # 量子计算与 Qiskit 学习指南
│   ├── example_walkthrough_zh.md      # 每个样例的讲解
│   └── advanced_workflow_zh.md        # 综合场景讲解
├── tests/                             # smoke tests
├── pyproject.toml
└── requirements.txt
```

## 快速开始

建议使用 Python 3.13 或 3.11。当前依赖已在 Python 3.13、Qiskit 2.4.1、qiskit-aer 0.17.2 下验证。Python 3.14 生态兼容性可能还不稳定，因此 `pyproject.toml` 限制为 `<3.14`。

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

运行测试：

```bash
pytest -q
```

运行所有基础示例：

```bash
quantum-samples --shots 1024 basics
```

运行综合场景，并写出 JSON 报告：

```bash
quantum-samples --shots 1024 advanced --output outputs/advanced_report.json
```

如果你不想安装为 editable package，也可以直接设置 `PYTHONPATH`：

```bash
PYTHONPATH=src python -m quantum_samples.cli --shots 1024 basics
PYTHONPATH=src python -m quantum_samples.cli --shots 1024 advanced --output outputs/advanced_report.json
```

## 基础示例

| 文件 | 主题 | 读者会学到什么 |
| --- | --- | --- |
| `examples/01_superposition.py` | Hadamard 叠加 | 一个量子位如何从确定态变成 50/50 测量分布 |
| `examples/02_bell_entanglement.py` | Bell 态纠缠 | 为什么两个量子位的测量结果会强相关 |
| `examples/03_superdense_coding.py` | 超密编码 | 如何用共享 Bell 对和一个 qubit 传两个 classical bits |
| `examples/04_teleportation.py` | 量子隐形传态 | 如何用 Bell 对和校正门传递未知量子态 |
| `examples/05_deutsch_jozsa.py` | Deutsch-Jozsa | 一次 oracle 查询区分 constant/balanced 函数 |
| `examples/06_grover_search.py` | Grover 搜索 | 如何放大一个被 oracle 标记的答案 |
| `examples/07_phase_estimation.py` | 量子相位估计 | 如何把酉算子的本征相位读成二进制 |
| `examples/08_vqe.py` | VQE | 混合量子-经典优化的基本形态 |
| `examples/09_advanced_workflow.py` | 综合场景 | 多个量子计算构件如何串成一个端到端流程 |

单独运行示例时，先安装项目：

```bash
pip install -e .
python examples/06_grover_search.py
```

## 综合场景：Quantum-assisted Dispatch Lab

综合场景是一个教学型调度实验。它假设有四条候选路线，需要在共享随机性、控制消息、状态传递、路线搜索、相位校准、能量估计、分区优化、噪声检查之间走一遍完整流程：

1. **QRNG**：用 Hadamard 量子随机数生成器提供随机位。
2. **BB84 思想**：用随机 basis 演示密钥筛选。
3. **超密编码**：把选中路线的两个 bit 编成一个 qubit 发送。
4. **量子隐形传态**：把用路线风险角度编码的 qubit 态传到另一个 qubit。
5. **Grover 搜索**：在四条路线中放大最高分路线。
6. **QPE**：估计一个玩具相位，用作“传感器校准”示意。
7. **VQE**：估计一个小 Hamiltonian 的最低能量，展示混合量子-经典循环。
8. **QAOA**：对四个路线监控节点做 MaxCut 分区示例。
9. **噪声模拟**：比较理想 Bell 对和带 depolarizing noise 的结果。
10. **Transpilation**：查看电路编译前后的深度和操作计数。

这个流程不是声称量子计算已经能在真实调度问题上胜过经典算法；它的用途是教学：在一个统一的故事里看到常见概念如何组合。

## 学习路线

建议按下面顺序阅读和运行：

1. 阅读 [docs/quickstart_zh.md](docs/quickstart_zh.md)，用 30 到 90 分钟建立第一层直觉。
2. 阅读 [docs/quantum_computing_intro_course_zh.md](docs/quantum_computing_intro_course_zh.md)，系统学习 9 章核心概念并完成习题。
3. 阅读 [docs/learning_guide_zh.md](docs/learning_guide_zh.md)，建立量子比特、电路、测量和 Qiskit 基础。
4. 运行 `quantum-samples --shots 1024 basics`，观察 counts 和 statevector。
5. 阅读 [docs/example_walkthrough_zh.md](docs/example_walkthrough_zh.md)，对照每个示例理解电路。
6. 运行 `quantum-samples --shots 1024 advanced --output outputs/advanced_report.json`。
7. 阅读 [docs/advanced_workflow_zh.md](docs/advanced_workflow_zh.md)，修改路线评分、oracle、噪声强度、QAOA 图结构。

## 常见问题

### 为什么模拟结果每次相同？

示例默认设置了 simulator seed，方便读者复现、测试和比较输出。真实硬件或者不固定 seed 的模拟器会产生不同采样结果。

### 为什么 bitstring 有时看起来反了？

Qiskit 的 counts 字符串按经典寄存器显示，最左边通常对应最高索引 classical bit。仓库中的 `bitstring_to_assignment` 和 `assignment_to_bitstring` 专门用于把显示顺序和 qubit-index 顺序互转。学习 Qiskit 时，比特序是非常值得早一点弄清楚的细节。

### 这个项目能跑真实量子硬件吗？

当前仓库以本地模拟为主，避免读者必须申请云端 token。若要接入真实硬件，可以在理解 `QuantumCircuit`、`transpile` 和 backend 概念后，继续学习 IBM Quantum Runtime。

## 验证记录

本地验证命令：

```bash
.venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python -m quantum_samples.cli --shots 128 basics
PYTHONPATH=src .venv/bin/python -m quantum_samples.cli --shots 128 advanced --output outputs/advanced_report.json
```

结果：测试全部通过，综合场景生成了 `outputs/advanced_report.json`。
