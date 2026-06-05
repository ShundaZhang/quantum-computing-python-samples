# 量子计算与后量子密码常用词汇表

这份词汇表收集本仓库文档中反复出现的缩略语和核心概念。读正文时遇到 `QPE`、`逆 QFT`、`KEM`、`ML-KEM` 这类词，可以先来这里建立直觉，再回到对应章节。

## 1. 量子计算基础

<a id="qubit"></a>
### Qubit：量子比特

量子比特是量子计算的信息单位。经典 bit 只能是 `0` 或 `1`，qubit 在测量前可以处于：

```text
α|0⟩ + β|1⟩
```

其中 `α` 和 `β` 是复数振幅，满足 `|α|^2 + |β|^2 = 1`。测量时看到 `0` 的概率是 `|α|^2`，看到 `1` 的概率是 `|β|^2`。

<a id="superposition"></a>
### Superposition：叠加态

叠加态表示一个量子态不是单纯的 `|0⟩` 或 `|1⟩`，而是多个基态的线性组合。Hadamard 门把 `|0⟩` 变成 `(|0⟩ + |1⟩)/√2`，这是最常见的入门例子。

<a id="amplitude"></a>
### Amplitude：振幅

振幅是量子态中每个基态前面的复数系数。振幅本身不能直接当概率，概率来自振幅模长的平方。很多量子算法的核心就是让正确答案的振幅变大，让错误答案的振幅互相抵消。

<a id="measurement"></a>
### Measurement：测量

测量会把量子态投影到某个经典结果。比如 `(|0⟩ + |1⟩)/√2` 被测量后，只会得到 `0` 或 `1`，不会得到“半个 0 半个 1”。

<a id="basis"></a>
### Basis：基

基是一组用来描述和测量量子态的坐标轴。计算基通常是 `|0⟩`、`|1⟩`；BB84 里还会用 `+` 直线基和 `x` 对角基。选错测量基会引入随机性。

<a id="bitstring"></a>
### Bitstring：比特串

多个 bit 写在一起就是 bitstring，例如 `011`、`10`。Qiskit 的测量结果通常以 bitstring 显示，但显示顺序和 qubit 编号可能让初学者困惑，所以本仓库提供了比特序说明和辅助函数。

<a id="statevector"></a>
### Statevector：状态向量

状态向量列出量子态在所有计算基上的振幅。2 个 qubit 的状态向量有 4 个分量，对应 `|00⟩`、`|01⟩`、`|10⟩`、`|11⟩`。

<a id="counts"></a>
### Counts：测量计数

`counts` 是多次运行电路后，每个测量 bitstring 出现的次数。例如 `{"00": 512, "11": 512}` 表示 1024 次采样中大约一半是 `00`，一半是 `11`。

<a id="shots"></a>
### Shots：采样次数

`shots` 是重复运行同一个量子电路的次数。真实量子设备和采样模拟器都需要多次运行来估计概率分布。

<a id="unitary"></a>
### Unitary：酉算子

酉算子是量子门和量子演化的数学形式。它保持向量长度，也就是保持总概率为 1。QPE、Shor、VQE 等算法都会反复谈到某个酉算子 `U`。

<a id="eigenstate"></a>
### Eigenstate / Eigenvalue：本征态 / 本征值

如果一个量子态 `|u⟩` 经过酉算子 `U` 后只多了一个相位：

```text
U|u⟩ = e^(2πiθ)|u⟩
```

那么 `|u⟩` 是 `U` 的本征态，`e^(2πiθ)` 是本征值。QPE 的目标就是估计这里的 `θ`。

<a id="phase"></a>
### Phase：相位

相位是复数振幅中的角度部分。单个全局相位通常测不出来，但不同基态之间的相对相位会影响干涉，Grover、QFT、QPE 都依赖这一点。

<a id="entanglement"></a>
### Entanglement：纠缠

纠缠表示多个 qubit 的状态不能拆成各自独立的状态。例如 Bell 态 `(|00⟩ + |11⟩)/√2` 中，一测到第一个 qubit 是 `0`，第二个也会是 `0`；一测到第一个是 `1`，第二个也会是 `1`。

<a id="bell-state"></a>
### Bell State：Bell 态

Bell 态是最常见的两 qubit 纠缠态。典型形式是：

```text
(|00⟩ + |11⟩) / √2
```

它是超密编码、量子隐形传态和纠缠演示的基本资源。

<a id="epr"></a>
### EPR：Einstein-Podolsky-Rosen 佯谬

EPR 佯谬讨论量子纠缠是否意味着量子力学不完备，或者是否需要放弃某些经典直觉，例如局域性或预先确定的实在性。

<a id="bell-inequality"></a>
### Bell Inequality：贝尔不等式

贝尔不等式是一类局域隐变量理论必须满足的相关性限制。纠缠态在合适测量设置下可以违反这些限制，说明量子关联不能由朴素局域隐藏答案表解释。

<a id="chsh"></a>
### CHSH 不等式

CHSH 是最常用的贝尔不等式形式之一。局域隐变量模型要求 `|S| <= 2`，量子力学允许最高达到 `2√2`。

<a id="local-hidden-variables"></a>
### Local Hidden Variables：局域隐变量

局域隐变量模型认为测量结果由预先存在但不可见的变量决定，而且远处测量设置不能瞬间影响本地结果。贝尔实验排除了大类这样的模型。

<a id="no-signaling"></a>
### No-Signaling：无信号定理

无信号定理说明纠缠虽然能产生强远距离关联，但 Alice 不能通过选择测量方式来控制 Bob 的本地统计。因此纠缠不能传递可控超光速信息。

<a id="measurement-problem"></a>
### Measurement Problem：测量问题

测量问题追问：如果量子态按薛定谔方程连续演化并可叠加，为什么测量时我们只看到一个确定结果？薛定谔的猫就是这个问题的经典思想实验。

<a id="schrodingers-cat"></a>
### Schrödinger's Cat：薛定谔的猫

薛定谔的猫把微观叠加放大到宏观场景，逼问“猫活 + 猫死”的叠加为什么在日常世界中不可见。它主要用于讨论测量、退相干和量子解释。

<a id="decoherence"></a>
### Decoherence：退相干

退相干是量子系统和环境发生不可控相互作用后，叠加和纠缠逐渐丢失的过程。它是当前真实量子硬件的核心限制之一。

## 2. 量子门、电路和模拟

<a id="h-gate"></a>
### H / Hadamard Gate：Hadamard 门

Hadamard 门常用于制造叠加。它把 `|0⟩` 变成 `(|0⟩ + |1⟩)/√2`，把 `|1⟩` 变成 `(|0⟩ - |1⟩)/√2`。

<a id="x-gate"></a>
### X Gate：X 门

X 门类似经典 NOT，把 `|0⟩` 翻转为 `|1⟩`，把 `|1⟩` 翻转为 `|0⟩`。

<a id="z-gate"></a>
### Z Gate：Z 门

Z 门不改变 `|0⟩` 和 `|1⟩` 的测量值，但会给 `|1⟩` 加一个负号。它常用于相位标记。

<a id="cx-gate"></a>
### CX / CNOT Gate：受控非门

CX 有一个控制 qubit 和一个目标 qubit。控制 qubit 为 `1` 时，目标 qubit 执行 X；控制 qubit 为 `0` 时，目标不变。Bell 态常用 `H + CX` 制备。

<a id="pauli"></a>
### Pauli Operators：Pauli 算符

Pauli `X`、`Y`、`Z` 是描述单 qubit 操作和测量的基本算符。VQE 中常把 Hamiltonian 分解成 Pauli 项。

<a id="rzz"></a>
### RZZ Gate：ZZ 旋转门

`RZZ` 表示两个 qubit 之间的 `ZZ` 相互作用旋转。在 QAOA 里，它常用来编码 MaxCut 这类图优化问题的边权。

<a id="transpilation"></a>
### Transpilation：转译 / 编译

Transpilation 是把抽象量子电路转换成某个 backend 能执行的门集合和连接结构。真实硬件通常只支持有限的门和 qubit 连接。

<a id="aer"></a>
### AerSimulator：Qiskit Aer 模拟器

AerSimulator 是 Qiskit Aer 提供的本地模拟器，可以模拟理想电路、采样结果、噪声模型等。本仓库大量示例使用它保证读者本地可运行。

## 3. 常见量子算法

<a id="oracle"></a>
### Oracle：预言机

Oracle 是把问题规则编码进量子电路的模块。Grover 的 oracle 会给目标态加负相位，后续 diffuser 再把这个相位差转成目标概率的提升。

<a id="diffuser"></a>
### Diffuser：扩散算子

Diffuser 是 Grover 算法中“围绕平均振幅反射”的步骤。它和 oracle 配合，反复放大目标态振幅。

<a id="grover"></a>
### Grover Search：Grover 搜索

Grover 算法用于无结构搜索。经典搜索 `N` 个候选平均需要 `O(N)` 次检查，Grover 约需要 `O(√N)` 次 oracle 查询。

<a id="qft"></a>
### QFT：Quantum Fourier Transform，量子傅里叶变换

QFT 是傅里叶变换的量子版本。它把周期性和相位结构转换成计算基上的尖峰分布。Shor 算法和 QPE 都依赖 QFT 或逆 QFT。

<a id="inverse-qft"></a>
### 逆 QFT / inverse QFT / IQFT

逆 QFT 是 QFT 的反向操作。在 QPE 中，受控 `U` 操作把相位写进 evaluation register，逆 QFT 再把这些相位信息转换成可测的 bitstring。

<a id="qpe"></a>
### QPE：Quantum Phase Estimation，量子相位估计

QPE 用来估计酉算子本征值里的相位 `θ`：

```text
U|u⟩ = e^(2πiθ)|u⟩
```

它是 Shor 算法的重要子程序，也常用于解释特征值、相位和 QFT 的关系。

<a id="shor"></a>
### Shor Algorithm：Shor 算法

Shor 算法能在理想容错量子计算机上高效解决整数分解和离散对数问题，因此威胁 RSA、DH、ECC 等传统公钥密码。它的量子核心是周期寻找/相位估计。

<a id="vqe"></a>
### VQE：Variational Quantum Eigensolver，变分量子本征求解器

VQE 是混合量子-经典算法。量子电路制备带参数的状态，测量 Hamiltonian 期望值；经典优化器调整参数，让能量尽量低。它常用于量子化学和小规模 Hamiltonian 教学。

<a id="ansatz"></a>
### Ansatz：试探电路 / 参数化假设

Ansatz 是 VQE、QAOA 中预先选定的一类参数化量子电路。它决定了算法能探索哪些量子态。

<a id="hamiltonian"></a>
### Hamiltonian：哈密顿量

Hamiltonian 描述系统能量。VQE 的目标通常是找到 Hamiltonian 的低能量态，也就是让测得的期望能量尽量小。

<a id="qaoa"></a>
### QAOA：Quantum Approximate Optimization Algorithm，量子近似优化算法

QAOA 是用于组合优化的混合量子-经典算法。它交替使用 cost layer 和 mixer layer，再用经典优化器寻找参数。

<a id="cost-layer"></a>
### Cost Layer：代价层

QAOA 中的 cost layer 把目标函数编码成相位。候选解的分数不同，相位演化也不同。

<a id="mixer-layer"></a>
### Mixer Layer：混合层

QAOA 中的 mixer layer 让状态在候选解之间流动，避免电路只停留在初始叠加或单个候选上。

## 4. 量子通信与密钥分发

<a id="qrng"></a>
### QRNG：Quantum Random Number Generator，量子随机数发生器

QRNG 利用量子测量的内在随机性产生随机数。入门示例常用 Hadamard 后测量来演示。

<a id="bb84"></a>
### BB84

BB84 是 Bennett 和 Brassard 在 1984 年提出的量子密钥分发协议。它用不兼容测量基和公开抽样比对来检测窃听。

<a id="qkd"></a>
### QKD：Quantum Key Distribution，量子密钥分发

QKD 的目标是在通信双方之间建立共享密钥，并利用量子测量扰动检测窃听。BB84 是最经典的 QKD 协议之一。

<a id="basis-sifting"></a>
### Basis Sifting：基筛选

BB84 中 Alice 和 Bob 公开比较使用了哪个测量基，但不公开比特值。双方只保留基一致的位置，这一步叫 basis sifting。

<a id="alice-bob-eve"></a>
### Alice / Bob / Eve

密码学和量子通信里常用 Alice 表示发送方，Bob 表示接收方，Eve 表示窃听者。

## 5. 后量子密码和安全迁移

<a id="pqc"></a>
### PQC：Post-Quantum Cryptography，后量子密码

PQC 指在经典计算机上运行、但希望抵抗已知量子攻击的密码算法。它不是“用量子计算机加密”，而是为量子攻击时代准备新的经典密码算法。

<a id="crqc"></a>
### CRQC：Cryptanalytically Relevant Quantum Computer

CRQC 指足以对现实密码系统构成分析威胁的量子计算机。讨论 RSA/ECC 迁移时，真正关心的是何时会出现 CRQC，而不只是能运行小演示电路的量子设备。

<a id="hndl"></a>
### HNDL：Harvest Now, Decrypt Later，先收集后解密

攻击者现在保存加密流量，等未来有足够强的量子计算机后再解密历史数据。长期保密数据最需要优先考虑这个风险。

<a id="kem"></a>
### KEM：Key Encapsulation Mechanism，密钥封装机制

KEM 用于在公开信道上建立共享秘密。发送方用接收方公钥生成一个 ciphertext 和共享秘密；接收方用私钥解封装得到同一个共享秘密。ML-KEM 和 HQC 都是 KEM。

<a id="aead"></a>
### AEAD：Authenticated Encryption with Associated Data

AEAD 同时提供机密性和完整性保护。常见例子是 AES-GCM 和 ChaCha20-Poly1305。PQC KEM 通常只建立密钥，真正的数据加密仍交给 AEAD。

<a id="kdf"></a>
### KDF：Key Derivation Function，密钥派生函数

KDF 把一个共享秘密派生成协议需要的多个密钥，例如握手密钥、流量加密密钥、MAC 密钥等。Hybrid 密钥交换常写成 `KDF(classical_secret || pqc_secret)`。

<a id="pki"></a>
### PKI：Public Key Infrastructure，公钥基础设施

PKI 是证书、CA、信任链、吊销和验证规则的整体体系。PQC 迁移不只是换算法，还会影响证书大小、签名算法、HSM、浏览器和中间件。

<a id="tls"></a>
### TLS：Transport Layer Security

TLS 是 HTTPS 等协议使用的安全传输层。PQC 迁移中，TLS 密钥交换常先采用 hybrid ECDHE + ML-KEM。

<a id="rsa"></a>
### RSA

RSA 是基于大整数分解困难性的传统公钥算法。Shor 算法能高效分解整数，因此 RSA 在 CRQC 时代需要替换。

<a id="ecc"></a>
### ECC / ECDH / ECDSA / EdDSA

ECC 是椭圆曲线密码体系。ECDH 用于密钥交换，ECDSA/EdDSA 用于签名。它们依赖椭圆曲线离散对数困难性，也会被 Shor 算法威胁。

<a id="aes"></a>
### AES

AES 是主流对称加密算法。量子计算对 AES 的主要影响来自 Grover 搜索的平方加速；高价值长期安全场景通常偏向 AES-256。

<a id="hmac"></a>
### HMAC

HMAC 是基于哈希函数的消息认证码。它用于验证消息完整性和认证来源，在后量子时代总体仍然稳健，关键是使用足够强的哈希和密钥长度。

<a id="sha"></a>
### SHA-2 / SHA-3

SHA-2 和 SHA-3 是主流哈希函数家族。后量子时代一般继续可用；长期高保证场景可选择 SHA-384、SHA-512 或 SHAKE256。

<a id="ml-kem"></a>
### ML-KEM：Module-Lattice-Based Key-Encapsulation Mechanism

ML-KEM 是 NIST FIPS 203 标准化的 KEM，源自 CRYSTALS-Kyber。它基于 Module-LWE 格问题，用于替代 RSA/ECDH 类密钥建立。

<a id="ml-dsa"></a>
### ML-DSA：Module-Lattice-Based Digital Signature Algorithm

ML-DSA 是 NIST FIPS 204 标准化的数字签名算法，源自 CRYSTALS-Dilithium。它是替代 RSA/ECDSA/EdDSA 签名的主力 PQC 方案之一。

<a id="slh-dsa"></a>
### SLH-DSA：Stateless Hash-Based Digital Signature Algorithm

SLH-DSA 是 NIST FIPS 205 标准化的无状态哈希签名算法，源自 SPHINCS+。它主要依赖哈希函数，签名较大，但安全假设保守。

<a id="hqc"></a>
### HQC：Hamming Quasi-Cyclic

HQC 是 NIST 选择的额外 KEM 备份算法，基于纠错码问题。它的价值在于提供不同于格密码的数学基础。

<a id="fn-dsa"></a>
### FN-DSA / Falcon

FN-DSA 是 Falcon 的标准化名称，基于 NTRU 格。它追求较小签名和快速验证，但实现复杂度比 ML-DSA 更高。

<a id="lwe"></a>
### LWE / Module-LWE

Learning With Errors 是“带噪声学习”问题。直觉上，公开很多带小噪声的线性方程后，恢复秘密很难。Module-LWE 是更结构化、更高效的版本，是 ML-KEM 的重要安全基础。

<a id="sis"></a>
### SIS / Module-SIS

Short Integer Solution 是寻找短整数解的问题。Module-SIS 是结构化版本，和 ML-DSA 的不可伪造性直觉有关。

<a id="ntru"></a>
### NTRU

NTRU 是一类基于多项式环和格结构的密码构造。Falcon/FN-DSA 使用 NTRU 格相关结构。

<a id="ntt"></a>
### NTT：Number Theoretic Transform

NTT 是数论变换，可看成在有限域中的 FFT。格密码实现中常用它加速多项式乘法。

<a id="wots"></a>
### WOTS+：Winternitz One-Time Signature Plus

WOTS+ 是哈希签名的基本积木，一把一次性签名密钥只能安全地签很少次数。SLH-DSA 用 Merkle/hypertree 结构组织大量 WOTS+。

<a id="fors"></a>
### FORS：Forest of Random Subsets

FORS 是 SPHINCS+/SLH-DSA 中用于签消息摘要的哈希签名组件。它和 WOTS+、Merkle 认证路径共同组成完整签名。

<a id="cnsa"></a>
### CNSA：Commercial National Security Algorithm Suite

CNSA 是 NSA 面向美国国家安全系统发布的商用国家安全算法套件。CNSA 2.0 给出了高安全场景的后量子迁移方向。

<a id="enisa"></a>
### ENISA

ENISA 是欧盟网络安全局。它发布过后量子密码集成、迁移和风险管理相关材料。

<a id="etsi"></a>
### ETSI

ETSI 是欧洲电信标准化协会。它长期维护 Quantum-Safe Cryptography、hybrid key establishment 等相关标准和技术规范。
