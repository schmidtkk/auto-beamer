# Deck 3 简报 — 流体动力学微分方程（第四章 4.1–4.3）

**先读** `books/流体力学/_codex/SHARED-DECK-SPEC.md`。

- **输出文件**：`/data/weidong/auto-beamer/fluid-mech-03-dynamics-diff-eqs-zh.tex`（仓库根目录）
- **源材料**：`books/流体力学/_txt/第四章讲义.txt` 的 **4.1–4.3 节**（行 1–746；4.4 节属于 Deck 4，本 deck 不做）（+ PDF `books/流体力学/第四章讲义.pdf`）
- **标题**：「流体动力学微分方程」/ 副标题「流体力学（水力学）自学讲义 · 第 3 部分（第四章 4.1–4.3）」
- **页脚**：`\TLsetfoot{流体力学（水力学）\textperiodcentered{} 自学讲义 \textperiodcentered{} 第 3 部分：连续性方程·欧拉方程·N-S 方程}`
- 预期规模：50–70 帧。

## 衔接（开头放一帧"承前"）
本 deck 用到 Deck 2（质量力 $\vec f$、压强、应力 $\sigma/\tau$）与 Deck 2/3（控制体、系统、质点导数 $\mathrm D/\mathrm Dt$、应变率张量 $\boldsymbol\varepsilon$、散度）。**就地复述**这些结论（1 帧 prerequisites），不要让读者翻回去。

## 大纲

### A. 标题 + 如何使用 + 承前（前置知识 1 帧）

### B. `\TLsection{先建直觉 · 动力学要解什么（新手先读）}`（4–5 帧，零黑话）
1. 本章目标：求 4 个未知场 $u_x,u_y,u_z,p$ → 需要 4 个方程 = 1 个连续性 + 3 个动量；这是"流体的牛顿第二定律 + 质量守恒"。
2. 控制体 vs 系统 一图（欧拉盒子 vs 跟随的一团流体）+ 雷诺输运的直觉（盒内变化 = 当地积累 + 净流出）。
3. 理想流体 vs 粘性流体：表面力只有压强 vs 还有粘性切应力/附加正应力。
4. N-S 方程一句话：$\underbrace{\vec f-\tfrac1\rho\nabla p}_{\text{力}}+\underbrace{\nu\nabla^2\vec u}_{\text{粘性扩散}}=\underbrace{\tfrac{\mathrm D\vec u}{\mathrm Dt}}_{\text{加速度}}$，并说明 200 年未完全攻克。
5. 阅读路径帧（★必读：四个方程的最终形式 + 物理意义；推导可跳：高斯定理那几步。背景 = 多元微积分（散度/高斯定理）+ 线代 + 大学物理）。

### C. `\TLsection{4.1 连续性方程（质量守恒）}`
- 积分形式（欧拉观点）：$\dfrac{\partial}{\partial t}\displaystyle\int_V\rho\rd V=-\oint_A\rho\vec u\cdot\rd\vec A$，逐项物理意义。
- 拉格朗日观点：系统 $\dfrac{\mathrm d}{\mathrm dt}\int_V\rho\rd V=0$ + 雷诺输运 $\dfrac{\mathrm d}{\mathrm dt}\int\rho\rd V=\dfrac{\partial}{\partial t}\int\rho\rd V+\oint\rho\vec u\cdot\rd\vec A$ → 合并得积分形式。
- **微分形式（完整推导）**：时间偏导移入积分；**高斯定理** $\oint\rho\vec u\cdot\rd\vec A=\int\nabla\cdot(\rho\vec u)\rd V$；任意控制体 ⇒ 被积函数为零 ⇒
  $\boxed{\dfrac{\partial\rho}{\partial t}+\nabla\cdot(\rho\vec u)=0}$；展开分量式。
- 简化：恒定 $\nabla\cdot(\rho\vec u)=0$；不可压缩 $\nabla\cdot\vec u=0$（与第三章呼应，强调"无条件成立，仅需连续介质假设"）。

### D. `\TLsection{4.2 理想流体的动量方程（欧拉方程）}`
- 积分形式：动量定理 $\dfrac{\mathrm d}{\mathrm dt}\int_V\rho\vec u\rd V=\vec F_{合}$ + 雷诺输运 → $\dfrac{\partial}{\partial t}\int_V\rho\vec u\rd V+\oint(\rho\vec u\cdot\rd\vec A)\vec u=\vec F_{合}$；合力 $\vec F_{合}=\vec F_{质}+\vec F_{表}$，$\vec F_{质}=\int\rho\vec f\rd V$，理想流体 $\vec F_{表}=-\oint p\rd\vec A$。
- **微分形式（完整推导）**：时间偏导移入；$-\oint p\rd\vec A=-\int\nabla p\rd V$；分量投影；对流项用高斯定理 $\oint\rho u_x\vec u\cdot\rd\vec A=\int\nabla\cdot(\rho u_x\vec u)\rd V$；去积分 ⇒ $\rho f_x-\partial p/\partial x=\partial(\rho u_x)/\partial t+\nabla\cdot(\rho u_x\vec u)$；与连续性联立化简（这一步可写"利用连续性方程化简"并给出关键中间步，不要直接跳）⇒
  **欧拉方程** $\boxed{\vec f-\tfrac1\rho\nabla p=\dfrac{\mathrm D\vec u}{\mathrm Dt}=\dfrac{\partial\vec u}{\partial t}+(\vec u\cdot\nabla)\vec u}$，写出三分量式。物理意义 = 牛顿第二定律（单位质量）。
- 小结：连续性 + 欧拉 = 4 个方程对 4 个未知量（不可压），加初/边界条件原则可解。

### E. `\TLsection{4.3 粘性流体的动量方程（N-S 方程）}`
- 为什么需要：理想流体忽略粘性，误差大 → 加回粘性切应力/正应力。修改的欧拉方程（含应力散度项）。
- **应力张量** $\boldsymbol\sigma=\begin{psmallmatrix}-p_{xx}&\tau_{xy}&\tau_{xz}\\\tau_{yx}&-p_{yy}&\tau_{yz}\\\tau_{zx}&\tau_{zy}&-p_{zz}\end{psmallmatrix}$；**切应力互等** $\tau_{ij}=\tau_{ji}$（对称张量）。
- **牛顿流体本构关系**：从一维 $\tau=\mu\,\mathrm du/\mathrm dy$ 推广，补全剪切变形率两部分 ⇒ $\tau_{xy}=\tau_{yx}=2\mu\varepsilon_{xy}=\mu(\partial u_y/\partial x+\partial u_x/\partial y)$（及轮换两式）；正应力 $p_{xx}=p-2\mu\,\partial u_x/\partial x$（及轮换）；张量式 $\boxed{\boldsymbol\sigma=-p\boldsymbol I+2\mu\boldsymbol\varepsilon}$。
- **动水压强** $p=\tfrac13(p_{xx}+p_{yy}+p_{zz})$，说明为张量第一不变量、各向同性（与静水压强对比）。
- **N-S 方程**：本构代入动量方程（"整理过程从略"——但 deck 里要给出关键中间步：粘性项汇成 $\nu\nabla^2\vec u$）⇒
  $\boxed{\vec f-\tfrac1\rho\nabla p+\nu\nabla^2\vec u=\dfrac{\partial\vec u}{\partial t}+(\vec u\cdot\nabla)\vec u}$，写出三分量式；$\nabla^2=\Delta$ 拉普拉斯算子。性质：非线性、一般无解析解、需数值求解；理想流体方程是其 $\nu\to0$ 的特例。

### F. 常见误区（`\TLwarnblock`）
欧拉方程"仅适用于不可压缩"（错，本身不限可压；判断题 #2）；N-S"仅适用于层流"（错，层流紊流都满足，#18）；动水压强 = 某方向正应力（错，是三正应力均值）；连续性方程需要恒定/不可压前提（错，无条件成立）。

### G. `\TLsection{练习}`（≥4 题 分级 + 提示 + 附录解答）
⭐ 由速度场验证不可压缩连续性（仿 #19 的场）；⭐⭐ #19（给 $u_x=x+y,u_y=2x+3y,u_z=0$，求 $M(1,2,3)$ 处切应力与法向应力，用本构关系）；⭐⭐ 由欧拉方程求某重力场下压强分布；⭐⭐⭐ 证明应力张量对角和（动水压强×3）为旋转不变量 / 由 N-S 在简单边界（如平板间 Couette/Poiseuille）求解析解。

### H. `\TLsection{延伸与文献注记}`（3–4 帧）
源讲义 4.1–4.3；人物（欧拉、纳维、斯托克斯、雷诺输运定理）；斯托克斯三假设（科普一段）；N-S 存在性与光滑性（千禧难题）一句话；教材（吴望一《流体力学》、White、Batchelor、闻德荪）。

### I. `\TLsection{术语速查}` 双语表 + `\appendix` 练习解答。

## 重申硬约束
科学性：连续性 $\partial\rho/\partial t+\nabla\cdot(\rho\vec u)=0$、欧拉 $\vec f-\tfrac1\rho\nabla p=\mathrm D\vec u/\mathrm Dt$、本构 $\boldsymbol\sigma=-p\boldsymbol I+2\mu\boldsymbol\varepsilon$、N-S $\vec f-\tfrac1\rho\nabla p+\nu\nabla^2\vec u=\mathrm D\vec u/\mathrm Dt$ 符号务必正确；高斯定理那几步要写全（理解优先 + 无跳步）；矢量加粗用 `\vc{}`；preamble 需补 `\newenvironment{psmallmatrix}` 或用 `bmatrix`。2-pass 构建 + QA + 回报。
