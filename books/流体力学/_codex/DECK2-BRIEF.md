# Deck 2 简报 — 流体运动学（第三章）

**先读** `books/流体力学/_codex/SHARED-DECK-SPEC.md`。本文件只给本 deck 范围、文件名、大纲。

- **输出文件**：`/data/weidong/auto-beamer/fluid-mech-02-kinematics-zh.tex`（仓库根目录）
- **源材料**：`books/流体力学/_txt/第三章讲义.txt`（+ PDF `books/流体力学/第三章讲义.pdf`，20 页）
- **标题**：「流体运动学」/ 副标题「流体力学（水力学）自学讲义 · 第 2 部分（第三章）」
- **页脚**：`\TLsetfoot{流体力学（水力学）\textperiodcentered{} 自学讲义 \textperiodcentered{} 第 2 部分：流体运动学}`
- 预期规模：55–80 帧。

## 大纲（按 SHARED-DECK-SPEC 第 3 节阶梯）

### A. 标题 + 如何使用本讲义

### B. `\TLsection{先建直觉 · 怎么"描述"流体在动（新手先读）}`（4–5 帧，零黑话）
1. 两种视角：跟着一个水分子走（拉格朗日 / 给每个质点编号追踪）vs 守在一个固定窗口看谁经过（欧拉 / 一帧帧拍流场照片）——用"给气球编号" vs "测站守株待兔"的比喻。
2. 为什么"在固定点测到的变化"≠"跟着质点感受到的变化"：传送带上温度计的例子 → 引出质点导数 = 当地 + 迁移。
3. 流体不仅会平移，还会转、会被拉长、会被剪歪 → 平动/旋转/线变形/角变形 一张图。
4. 流线 = 某一瞬间处处与速度相切的曲线（给流场拍一张"方向照片"）；迹线 = 一个质点的轨迹。恒定流时两者重合。
5. 阅读路径帧（★必读 vs 推导可跳；背景 = 高数（含多元微积分/散度旋度）+ 线代 + 大学物理）。

### C. `\TLsection{3.1 描述流体运动的两种方法}`
- 拉格朗日法：拉格朗日变数 $(a,b,c,t)$；$\vec r=\vec r(a,b,c,t)$，$\vec u=\mathrm{d}\vec r/\mathrm{d}t$，$\vec a=\mathrm{d}\vec u/\mathrm{d}t$。
- 欧拉法（流场法）：场函数 $\vec u(x,y,z,t)$、$p$、$\rho$；欧拉变数；几何点不携带物理量、质点才携带（讲透）。
- **质点（物质）导数** —— 本节核心，**完整推导**：用链式法则从 $\phi(x(t),y(t),z(t),t)$ 推
  $\dfrac{\mathrm{D}\phi}{\mathrm{D}t}=\dfrac{\partial\phi}{\partial t}+(\vec u\cdot\nabla)\phi$；逐项解释当地（时变）导数 vs 迁移（位变）导数（用"传送带/守株待兔"直觉）。哈密顿算子 $\nabla$。
- 加速度：$\vec a=\dfrac{\partial\vec u}{\partial t}+(\vec u\cdot\nabla)\vec u$，写出三个分量式；当地加速度 vs 迁移加速度。
- **算例**：源 #29（$u=yz+t$ 等，求某点加速度/当地/迁移加速度），分步代入。

### D. `\TLsection{3.2 流体微团运动分析}`
- 为什么质点不足以描述变形 → 需要流体微团 + 速度的空间变化率。速度梯度张量 $\nabla\vec u$（9 分量矩阵）；$\vec u-\vec u_0=\nabla\vec u\cdot\mathrm{d}\vec r$。
- 四种基本形式：平动；**旋转** $\omega_x=\tfrac12(\partial u_z/\partial y-\partial u_y/\partial z)$ 等，$\vec\omega=\tfrac12\nabla\times\vec u$；**线变形** $\varepsilon_{xx}=\partial u_x/\partial x$ 等；**角变形** $\varepsilon_{xy}=\tfrac12(\partial u_y/\partial x+\partial u_x/\partial y)$ 等。变形速率张量 $\boldsymbol\varepsilon$（对称，6 独立分量）。
- **亥姆霍兹速度分解定理** $\vec u=\vec u_0+\vec\omega\times\mathrm{d}\vec r+\boldsymbol\varepsilon\cdot\mathrm{d}\vec r$（平动 + 旋转 + 变形），给出由 $\nabla\vec u=\boldsymbol\varepsilon+\boldsymbol\Omega$ 对称/反对称分解的**推导**，配 TikZ（微团被平移/转动/拉伸/剪切四联图）。
- **速度散度** $\nabla\cdot\vec u=\varepsilon_{xx}+\varepsilon_{yy}+\varepsilon_{zz}$ = 相对体积膨胀率；不可压缩 ⇒ $\nabla\cdot\vec u=0$（**不可压缩连续性方程**，仅由连续介质假设得出；可压缩版第四章）。

### E. `\TLsection{3.3 描述流体运动的若干基本概念}`（每个概念：大白话 + 图/式）
恒定流/非恒定流（$\partial\phi/\partial t=0$）；迹线 vs 流线（各自微分方程；同时刻流线不相交不折，例外：驻点/相切/奇点）配 TikZ；一/二/三元流动；流管、元流、总流、过水断面、流量 $Q$、断面平均流速 $v=Q/A$；均匀流/非均匀流（三条性质：流线平行直线、迁移加速度为零、过水断面动水压强按静压分布即测压管水头为常数）；渐变流/急变流；系统 vs 控制体（拉格朗日 vs 欧拉的积分对象）；有旋/无旋流动（判别条件 $\nabla\times\vec u=0$）→ **速度势函数** $\vec u=\nabla\varphi$（无旋 ⇔ 有势，互为充要）。

### F. `\TLsection{3.4 不可压缩流体平面势流}`
- **流函数 $\psi$**：平面流线微分方程 $-u_y\,\mathrm{d}x+u_x\,\mathrm{d}y=0$；不可压缩 ⇒ 该式为某 $\psi$ 全微分（存在充要条件 = 二维连续性 $\partial u_x/\partial x+\partial u_y/\partial y=0$，自动满足）；$u_x=\partial\psi/\partial y,\;u_y=-\partial\psi/\partial x$；性质：两流线 $\psi$ 之差 = 单宽流量；流函数只在平面流动中定义。
- **平面速度势 $\varphi$**：$u_x=\partial\varphi/\partial x,\;u_y=\partial\varphi/\partial y$；等势线 $\varphi=C$；存在充要条件 = 无旋。
- **流函数与势函数关系**：柯西-黎曼 $\partial\varphi/\partial x=\partial\psi/\partial y,\;\partial\varphi/\partial y=-\partial\psi/\partial x$；**证明流线与等势线正交**；流网。
- **拉普拉斯方程与叠加性**：既不可压又无旋 ⇒ $\nabla^2\varphi=0,\;\nabla^2\psi=0$（给出由四式合并的推导）；线性 ⇒ 速度场/$\varphi$/$\psi$ 可叠加（**但压强场不可简单叠加**，留待第四章）。
- **三种基本平面势流**（给出 $u_x,u_y,\varphi,\psi$ 并配 TikZ 流线图）：① 均匀等速流 $\varphi=u_0(x\cos\alpha+y\sin\alpha)$、$\psi=u_0(y\cos\alpha-x\sin\alpha)$；② 点源($q>0$)/点汇($q<0$) $\varphi=\tfrac{q}{2\pi}\ln r$、$\psi=\tfrac{q}{2\pi}\theta$；③ 点涡（环量 $\Gamma$）$\varphi=\tfrac{\Gamma}{2\pi}\theta$、$\psi=-\tfrac{\Gamma}{2\pi}\ln r$。

### G. 常见误区（`\TLwarnblock`，取自判断题）
无旋 ≠ "看起来不转"（绕圈可无旋、直线可有旋，见点涡与剪切流）；均匀流 ≠ 速度处处相等（只是沿流向不变）；势流叠加：速度/势/流函数可加但**压强不可加**；点源/点汇/点涡速度都 $\propto 1/r$。

### H. `\TLsection{练习}`（≥5 题 分级，提示 + 附录解答）
⭐ #28（$u_x=kx,u_y=-ky$ 求流线）、#32（$u_x=x+t,u_y=-y+t$ 求流线并画）；⭐⭐ #29（验证连续性 + 求加速度分解）、#34（判定流函数/势函数是否存在并求之）、#21（$\psi=a(x^2-y^2)$ 求速度）；⭐⭐⭐ #30（证明某速度场不可能存在）、#31（综合：判定恒定平面势流 + 变形速率 + 迹线/等势线正交 + 单宽流量）、#35（证明点涡除中心外处处无旋）。

### I. `\TLsection{延伸与文献注记}`（3–4 帧）
源讲义第三章；经典教材（闻德荪/吴持恭《水力学》，Batchelor、White）；人物（拉格朗日、欧拉、亥姆霍兹、柯西、黎曼、拉普拉斯）；应用（势流叠加→绕流/机翼升力定性、源汇法、CFD 中的欧拉描述）。

### J. `\TLsection{术语速查}` 双语表 + `\appendix` 练习解答。

## 重申硬约束
公式科学性（质点导数链式推导、$\vec\omega=\tfrac12\nabla\times\vec u$、应变率张量对称式、柯西-黎曼号、点源/汇/涡的 $\varphi/\psi$ 符号）务必正确；推导无跳步、理解优先；每个抽象对象配 TikZ；2-pass 构建并通过 QA，回报帧数与覆盖。
