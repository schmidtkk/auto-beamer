# Deck 5 简报 — 紊流概论与壁面速度分布（第五章 5.1–5.2）

**先读** `books/流体力学/_codex/SHARED-DECK-SPEC.md`。

- **输出文件**：`/data/weidong/auto-beamer/fluid-mech-05-turbulence-velocity-zh.tex`（仓库根目录）
- **源材料**：`books/流体力学/_txt/第五章讲义（5.1节）.txt` + `（5.2节）.txt`（+ PDF）
- **标题**：「紊流概论与壁面速度分布」/ 副标题「流体力学（水力学）自学讲义 · 第 5 部分（第五章 5.1–5.2）」
- **页脚**：`\TLsetfoot{流体力学（水力学）\textperiodcentered{} 自学讲义 \textperiodcentered{} 第 5 部分：紊流概论·壁面速度分布}`
- 预期规模：55–75 帧。**注意**：本章定性分析 + 半经验公式多（与前几章风格不同），更要用大白话讲清"每个经验公式在拟合什么、假设了什么"。

## 衔接（开头 1 帧"承前"，就地复述）
用到 Deck 3/4：N-S 方程、动量定理、应力张量、水头损失 $h_w$；Deck 1：运动粘度 $\nu$、牛顿内摩擦 $\tau=\mu\,\mathrm du/\mathrm dy$；Deck 2/4：断面平均流速 $v$、过水断面、均匀流。

## 大纲

### A. 标题 + 如何使用 + 承前

### B. `\TLsection{先建直觉 · 层流与紊流（新手先读）}`（4–5 帧）
1. 倒蜂蜜（规整=层流）vs 大河奔涌（混乱=紊流）；雷诺实验红墨水一图。
2. 雷诺数一句话：$\Rey=$ 惯性力/粘性力之比；大→乱（紊流），小→稳（层流）；口算一个 $\Rey$。
3. 紊流的"脉动"：固定点测到的量在剧烈抖动 → 只能谈时均值（时均 + 脉动 $u=\bar u+u'$）。
4. 壁面附近三层：贴壁薄层速度陡（粘性底层）、中间过渡、管心平缓（紊流核心区）——一张速度剖面图（层流抛物线 vs 紊流更"钝"）。
5. 阅读路径帧（★必读：$\Rey$ 定义与判据、时均分解、雷诺应力概念、$u^+=y^+$ 与对数律的结论；半经验推导可跳。背景 = 高数 + 大学物理）。

### C. `\TLsection{5.1 紊流概论}`
- **雷诺实验**：层流/过渡流(转捩)/紊流；上临界流速 $v_{cr}'$ / 下临界流速 $v_c$（配 TikZ 装置 + 三种红线形态）。
- **雷诺数**：$\boxed{\Rey=\dfrac{\rho vd}{\mu}=\dfrac{vd}{\nu}}$（无量纲）；上/下临界雷诺数；圆管下临界 $\Rey_c\approx2000$（判据 $\Rey<2000$ 层流）；广义 $\Rey=\rho UL/\mu$（参考流速/长度）；**水力半径** $R=A/\chi$（湿周 $\chi$），圆管 $R=d/4$，以 $R$ 为参考长度时临界 $\Rey\approx500$。
- **物理意义**：惯性力/粘性力之比；稳定 vs 不稳定因素制衡；紊流形成机理（流线扰动→压差→涡体→粘性能否抑制）配 TikZ。
- **时均化（雷诺分解）**：$\bar u_x=\dfrac1T\displaystyle\int_t^{t+T}u_x\rd t$；脉动 $u_x'=u_x-\bar u_x$，$\overline{u_x'}=0$，脉动强度 $\sqrt{\overline{u_x'^2}}$；时均流场、"恒定紊流/均匀紊流"是对时均而言；牛顿内摩擦定律不适用于紊流时均流场。
- **雷诺应力（附加应力）**：用动量交换**完整推导** $\tau_{yx}^{Re}=-\rho\,\overline{u_x'u_y'}$（讲清 $u_x',u_y'$ 异号 → 负号）；雷诺应力张量（对称，6 独立分量，含雷诺正应力 $-\rho\overline{u_i'^2}$、雷诺切应力）；雷诺时均方程（形式上比 N-S 多 9 项，结论即可，推导从略但说明来源）。
- **普朗特混合长理论**：类比分子自由程；$|u_x'|=c_1 l'|\mathrm du_x/\mathrm dy|$ 等 → $\boxed{\tau^{Re}=\rho l^2\big(\dfrac{\mathrm du}{\mathrm dy}\big)^2}$；卡门常数 $\kappa\approx0.4$，$l\approx\kappa y\sqrt{1-y/r_0}$；总切应力 $\tau=\mu\dfrac{\mathrm du}{\mathrm dy}+\rho l^2\big(\dfrac{\mathrm du}{\mathrm dy}\big)^2$；涡粘系数 $\eta=\rho l^2|\mathrm du/\mathrm dy|$，布辛涅斯克 $\tau=(\mu+\eta)\dfrac{\mathrm du}{\mathrm dy}$。

### D. `\TLsection{5.2 壁面附近的紊流速度分布}`
- 三分区（粘性底层/过渡层/紊流核心区）+ 紊流剖面比层流"钝"（TikZ）。
- **粘性底层**：贴壁 $\tau\approx\mu\,\mathrm du/\mathrm dy\approx\tau_w$ → 积分（$u|_{y=0}=0$）得 $u=\dfrac{\tau_w}{\mu}y$（线性）；**摩阻流速** $u_*=\sqrt{\tau_w/\rho}$（构造量，非实际流速）；无量纲化 $u^+=u/u_*$、$y^+=u_*y/\nu$ → **壁面律** $\boxed{u^+=y^+}$；$y^+$ 在 CFD 网格中的意义。
- **紊流核心区（对数律）**：$\tau\approx\rho l^2(\mathrm du/\mathrm dy)^2$，代入圆管 $\tau=\tau_w(1-y/r_0)$ 与 $l\approx\kappa y\sqrt{1-y/r_0}$ ⇒ $\dfrac{\mathrm du}{\mathrm dy}=\dfrac{u_*}{\kappa y}$，积分 ⇒ $u=\dfrac{u_*}{\kappa}\ln y+C_1$ → 无量纲 $\boxed{u^+=\dfrac1\kappa\ln y^++C}$；光滑管 $C=5.5$：$u^+=2.5\ln y^++5.5=5.75\lg y^++5.5$。
- **各层厚度**：粘性底层实际厚度 $\delta'=5\nu/u_*$（$y^+\le5$）；过渡层 $\delta'+\delta''=70\nu/u_*$（$y^+\le70$）；名义（理论）厚度 $\delta=11.6\nu/u_*$（$\approx2.32\delta'$，①③曲线交点）。配分区 TikZ（横轴对数）。
- **壁面粗糙度**：绝对粗糙度 $\Delta$、相对粗糙度 $\Delta/d$；水力光滑（$\Delta\le5\nu/u_*$）/水力过渡粗糙/水力粗糙（$\Delta>70\nu/u_*$）三区（与雷诺数有关，同一管可在不同 $\Rey$ 下不同）；粗糙管对数律 $u^+=5.75\lg(y/\Delta)+8.5$。
- **指数形式流速分布**：$\dfrac{u}{u_{\max}}=\big(\dfrac{y}{r_0}\big)^n$（拟合，$n<1$，$\Rey$ 越大 $n$ 越小越"钝"）；$n$、$u_{\max}/v$、$\alpha$、$\beta$ 随 $\Rey$ 的变化（表，呼应 Deck 4 修正系数）。

### E. 常见误区（`\TLwarnblock`）
牛顿内摩擦定律对紊流时均流场成立（错）；$\Rey$ 算出来就能确定层流/紊流（不严格，只是越大越易紊流，上临界波动大）；摩阻流速 $u_*$ 是某处实际流速（错，是构造量）；"恒定/均匀紊流"指瞬时场不变（错，指时均场）；粘性底层"过渡区"= 层流→紊流的过渡区（两个不同概念）。

### F. `\TLsection{练习}`（≥4 题 分级 + 提示 + 附录解答）
⭐ 给 $\rho,v,d,\nu$ 算 $\Rey$ 判层流/紊流；算圆管/明渠水力半径与对应判据；⭐⭐ 给 $\tau_w,\rho,\nu$ 求 $u_*$、粘性底层厚度 $\delta'$、名义厚度 $\delta$；由对数律求某 $y$ 处流速；⭐⭐⭐ 推导 $\tau^{Re}=-\rho\overline{u_x'u_y'}$（动量交换）/ 由混合长 + 切应力线性分布推对数律 / 判别水力光滑/粗糙并选公式。

### G. `\TLsection{延伸与文献注记}`（3–4 帧）
源讲义 5.1–5.2；人物（雷诺、普朗特、卡门、布辛涅斯克、尼古拉兹）；RANS/混合长/涡粘在 CFD（湍流模型 k-ε、$y^+$ 网格）一段科普；教材（闻德荪《水力学》、Pope《Turbulent Flows》、White、莫宁-亚格洛姆）。

### H. `\TLsection{术语速查}` 双语表（层流/laminar、紊流(湍流)/turbulent、雷诺数/Reynolds number、雷诺应力/Reynolds stress、脉动/fluctuation、混合长/mixing length、摩阻流速/friction velocity $u_*$、粘性底层/viscous sublayer、壁面律/law of the wall、对数律/log law、相对粗糙度/relative roughness …）+ `\appendix` 练习解答。

## 重申硬约束
科学性（$\Rey=\rho vd/\mu$、$R=A/\chi$、$\tau^{Re}=-\rho\overline{u_x'u_y'}$、混合长 $\tau^{Re}=\rho l^2(\mathrm du/\mathrm dy)^2$、$\kappa\approx0.4$、$u_*=\sqrt{\tau_w/\rho}$、$u^+=y^+$、$u^+=2.5\ln y^++5.5$、$\delta'=5\nu/u_*$、$\delta=11.6\nu/u_*$）务必正确；半经验公式要讲清"假设 + 拟合"性质（理解优先），雷诺应力符号推导无跳步；每个分区/装置配 TikZ；2-pass 构建 + QA + 回报。
