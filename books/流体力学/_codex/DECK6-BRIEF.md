# Deck 6 简报 — 沿程与局部水头损失（第五章 5.3–5.5）

**先读** `books/流体力学/_codex/SHARED-DECK-SPEC.md`。

- **输出文件**：`/data/weidong/auto-beamer/fluid-mech-06-head-loss-zh.tex`（仓库根目录）
- **源材料**：`books/流体力学/_txt/第五章讲义（5.3节）.txt` + `（5.4节）.txt` + `（5.5节）.txt`（+ PDF）
- **标题**：「沿程与局部水头损失」/ 副标题「流体力学（水力学）自学讲义 · 第 6 部分（第五章 5.3–5.5）」
- **页脚**：`\TLsetfoot{流体力学（水力学）\textperiodcentered{} 自学讲义 \textperiodcentered{} 第 6 部分：沿程与局部水头损失}`
- 预期规模：55–75 帧。

## 衔接（开头 1 帧"承前"，就地复述）
用到 Deck 4：能量方程、水头损失 $h_w=\sum h_f+\sum h_j$、水力坡度 $J=h_f/l$、动能/动量修正系数；Deck 5：摩阻流速 $u_*$、粘性底层厚度、相对粗糙度 $\Delta/d$、紊流光滑/粗糙区、$\lambda$ 与 $\Rey$；Deck 1/5：牛顿内摩擦、水力半径 $R=A/\chi$。

## 大纲

### A. 标题 + 如何使用 + 承前

### B. `\TLsection{先建直觉 · 水头损失怎么算（新手先读）}`（4–5 帧）
1. 两类损失：沿程（沿管壁一路磨，正比于管长，$h_f$）vs 局部（拐弯/变径/阀门处剧变，$h_j$）——一张管路示意图标注两类损失位置。
2. 达西—威斯巴赫一句话：$h_f=\lambda\dfrac{l}{d}\dfrac{v^2}{2g}$，只要知道无量纲系数 $\lambda$ 就能算沿程损失；$\lambda$ 由 $\Rey$ 和 $\Delta/d$ 决定（穆迪图查）。
3. 切应力为什么沿半径线性分布：一段均匀流受力平衡（驱动力 = 壁面阻力）→ $\tau_w=\rho gRJ$ 的直觉。
4. 五个区一句话：层流（$\lambda=64/\Rey$）→ 过渡 → 紊流光滑 → 紊流过渡 → 紊流粗糙（阻力平方区，$\lambda$ 只看粗糙度）；一张尼古拉兹/穆迪图示意。
5. 阅读路径帧（★必读：$\tau_w=\rho gRJ$、达西公式、五区与各自 $\lambda$ 公式、局部损失 $h_j=\zeta v^2/2g$；切应力/流速分布积分推导可跳。背景 = 高数 + 大学物理）。

### C. `\TLsection{5.3 恒定均匀流的切应力分布与沿程损失系数}`
- **壁面平均切应力（完整推导）**：均匀流两断面间能量方程 ⇒ $h_f=(z_1+p_1/\rho g)-(z_2+p_2/\rho g)$；动量方程左端为 0 ⇒ 重力分量 + 压差力 − 壁面阻力 = 0：$G\sin\alpha+(p_1-p_2)A-T=0$（$G=\rho gAl$，$\sin\alpha=(z_1-z_2)/l$，$T=\tau_w l\chi$）⇒ $\boxed{\tau_w=\rho gRJ}$（$R=A/\chi$，$J=h_f/l$）。物理意义 + 适用任意断面形状。
- **内部流层切应力**：取半径 $r$ 圆柱面，同法 ⇒ $\tau=\rho gR'J=\tau_w\dfrac{R'}{R}$。
- **圆管**：$R'=r/2$ ⇒ $\boxed{\tau=\tfrac12\rho grJ=\tau_w\dfrac{r}{r_0}}$（线性，壁面最大 $\tau_w=\tfrac12\rho gr_0J$）；层流/紊流均适用（紊流时 $\tau=\tau_{粘}+\tau^{Re}$，和仍线性）配 TikZ。
- **宽矩形明渠**（$B\gg h$）：$R'\approx H-y$ ⇒ $\tau=\rho g(H-y)J=\tau_w(1-y/H)$，$\tau_w=\rho gHJ$ 配 TikZ。
- **圆管层流流速分布与沿程损失（完整推导）**：牛顿内摩擦 $\tau=-\mu\,\mathrm du/\mathrm dr$（注意 $\mathrm dy=-\mathrm dr$）联立 $\tau=\tfrac12\rho grJ$ 积分（$u|_{r=r_0}=0$）⇒ $u=\dfrac{\rho gJ}{4\mu}(r_0^2-r^2)$（旋转抛物面）；$u_{\max}=\dfrac{\rho gJr_0^2}{4\mu}=\dfrac{\rho gJd^2}{16\mu}$；$v=\tfrac12u_{\max}=\dfrac{\rho gJd^2}{32\mu}$ ⇒ $J=\dfrac{32\mu v}{\rho gd^2}$，$h_f=\dfrac{32\mu vl}{\rho gd^2}$；代入 $\Rey=\rho vd/\mu$ ⇒ $\boxed{h_f=\dfrac{64}{\Rey}\dfrac{l}{d}\dfrac{v^2}{2g}}$。
- **达西—威斯巴赫公式**：$\boxed{h_f=\lambda\dfrac{l}{d}\dfrac{v^2}{2g}=\lambda\dfrac{l}{4R}\dfrac{v^2}{2g}}$（推广到任意断面）；层流 $\lambda=64/\Rey$；紊流 $\lambda$ 需实验/查表；强调"$h_f\propto v^2$"仅当 $\lambda$ 为常数才成立（$h_f=kv^n$，层流 $n=1$，紊流 $n=1.75$–$2$）。
- （可放附录或正文末）宽矩形明渠层流：$u=\dfrac{\rho gJ}{\mu}(Hy-\tfrac{y^2}{2})$，$v=\tfrac23u_{\max}$，$\lambda=24/\Rey$。

### D. `\TLsection{5.4 沿程损失系数的变化规律}`
- **$u_*$ 与 $\lambda$ 关系**：$u_*=\sqrt{\tau_w/\rho}=\sqrt{gRJ}$；由达西 $J=\lambda\dfrac{1}{4R}\dfrac{v^2}{2g}$ ⇒ $\boxed{u_*=v\sqrt{\lambda/8}}$；代入 Deck 5 厚度式 ⇒ $\delta'=14.1\dfrac{d}{\Rey\sqrt\lambda}$、$\delta=32.8\dfrac{d}{\Rey\sqrt\lambda}$（$\Rey$ 越大底层越薄）。
- **尼古拉兹实验**（人工沙粒粗糙管，$\lambda=f(\Rey,\Delta/d)$）**五区**（配尼古拉兹 $\lg(100\lambda)$–$\lg\Rey$ 示意 TikZ）：
  ① 层流区 $\Rey<2000$：$\lambda=64/\Rey$（只与 $\Rey$ 有关）。
  ② 层流→紊流过渡区 $2000<\Rey<4000$：无可用公式。
  ③ 紊流光滑区：布拉休斯 $\lambda=\dfrac{0.3164}{\Rey^{1/4}}$（$4000<\Rey<10^5$）⇒ $h_f\propto v^{1.75}$；光滑管尼古拉兹 $\dfrac1{\sqrt\lambda}=2\lg(\Rey\sqrt\lambda)-0.8$（只与 $\Rey$ 有关）。
  ④ 紊流过渡粗糙区：柯列布鲁克—怀特 $\dfrac1{\sqrt\lambda}=-2\lg\!\Big(\dfrac{\Delta}{3.71d}+\dfrac{2.51}{\Rey\sqrt\lambda}\Big)$（与 $\Rey$、$\Delta/d$ 都有关）。
  ⑤ 紊流粗糙区（阻力平方区）：粗糙管尼古拉兹 $\lambda=\dfrac1{\big(2\lg\frac{3.71d}{\Delta}\big)^2}$（只与 $\Delta/d$ 有关，$h_f\propto v^2$）。
- **实用管道**：穆迪图（与尼古拉兹类似，查图得 $\lambda$）；非圆管用 $4R$ 代 $d$。
- **谢才公式与曼宁公式**：$v=C\sqrt{RJ}$，$h_f=\dfrac{v^2l}{C^2R}$；与达西关系 $C=\sqrt{8g/\lambda}$，$\lambda=8g/C^2$（两公式等价，谢才适用阻力平方区）；曼宁 $C=\dfrac{R^{1/6}}{n}$（糙率 $n$，$R$ 须取 m，量纲不和谐说明）；巴甫洛夫斯基（提一句，适用范围 $0.1\le R\le3.0$ m）。

### E. `\TLsection{5.5 局部水头损失}`
- 通用公式 $\boxed{h_j=\zeta\dfrac{v^2}{2g}}$（$\zeta$ 局部损失系数，无量纲，查表；注意取损失前/后哪个 $v$）。
- **突然扩大（完整推导/给假设）**：$h_j=\dfrac{(v_1-v_2)^2}{2g}$（假设：忽略壁面阻力、断面压强按静压分布、$\alpha=\beta=1$）；$\zeta_1=\big(1-\dfrac{A_1}{A_2}\big)^2$（对 $v_1$）、$\zeta_2=\big(\dfrac{A_2}{A_1}-1\big)^2$（对 $v_2$）配 TikZ。
- **淹没出流**（$A_2\gg A_1$，$v_2=0$）：$\zeta=1$，$h_j=v^2/2g$（动能全耗）；自由出流出口局部损失可忽略。
- **突然缩小**：$h_j=\zeta\dfrac{v_2^2}{2g}$，$\zeta=0.5\big(1-\dfrac{A_2}{A_1}\big)$ 配 TikZ。

### F. 常见误区（`\TLwarnblock`）
"$h_f$ 一定正比于 $v^2$"（仅阻力平方区/$\lambda$ 常数时；层流 $\propto v$）；层流区 $\Rey$ 增大 $\lambda$ 反减小（$\lambda=64/\Rey$，但 $h_f$ 仍随 $v$ 增）；谢才/曼宁糙率 $n$ 有量纲问题（$R$ 必须用 m）；局部损失系数 $\zeta$ 对应的 $v$ 取错断面；紊流"过渡区"（粗糙度）≠ 层流→紊流过渡区。

### G. `\TLsection{练习}`（≥5 题 分级 + 提示 + 附录解答）
⭐ 圆管层流由 $\Rey$ 求 $\lambda$ 与 $h_f$；给 $\zeta,v$ 求局部损失；⭐⭐ 紊流光滑区用布拉休斯求 $\lambda,h_f$；用 $\tau_w=\rho gRJ$ 求壁面切应力；突然扩大求 $h_j$ 与 $\zeta$；⭐⭐⭐ 判别五区并选公式综合算 $h_f$（含 $\Delta/d$）；谢才—曼宁求明渠流速/流量；用柯列布鲁克—怀特迭代求 $\lambda$。

### H. `\TLsection{延伸与文献注记}`（3–4 帧）
源讲义 5.3–5.5；人物（达西、威斯巴赫、布拉休斯、尼古拉兹、柯列布鲁克、怀特、穆迪、谢才、曼宁）；穆迪图工程用法 + 现代隐式 Colebrook 求解/显式近似（Swamee-Jain 一句话）；教材（闻德荪《水力学》、吴持恭、White、Munson）。

### I. `\TLsection{术语速查}` 双语表（沿程水头损失/major (frictional) head loss $h_f$、局部水头损失/minor (local) head loss $h_j$、沿程损失系数/Darcy friction factor $\lambda$、达西—威斯巴赫/Darcy–Weisbach、水力坡度/hydraulic gradient $J$、阻力平方区/fully rough regime、谢才系数/Chézy coefficient $C$、糙率/Manning roughness $n$、局部损失系数/loss coefficient $\zeta$ …）+ `\appendix` 练习解答（分步）。

## 重申硬约束
科学性（$\tau_w=\rho gRJ$、圆管 $\tau=\tfrac12\rho grJ$、层流 $u=\frac{\rho gJ}{4\mu}(r_0^2-r^2)$、$v=u_{\max}/2$、$h_f=\frac{64}{\Rey}\frac{l}{d}\frac{v^2}{2g}$、达西 $h_f=\lambda\frac{l}{d}\frac{v^2}{2g}$、布拉休斯 $\lambda=0.3164/\Rey^{1/4}$、柯列布鲁克—怀特、粗糙管尼古拉兹、谢才 $v=C\sqrt{RJ}$、$C=\sqrt{8g/\lambda}$、曼宁 $C=R^{1/6}/n$、突然扩大 $h_j=(v_1-v_2)^2/2g$、突然缩小 $\zeta=0.5(1-A_2/A_1)$）务必正确——这些经验系数/指数极易记错，逐条核对；切应力与流速分布的积分推导无跳步；五区判别讲清"$\lambda$ 依赖谁"；2-pass 构建 + QA + 回报。
