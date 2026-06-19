# 流体力学 自学讲义系列 — 共享规范 (Codex 必读)

你（Codex）是这套讲义的实现者。本文件是 **6 个 deck 共用的硬规范**；每个 deck 另有
一份"逐 deck 简报"给出具体范围、文件名与大纲。**先完整读本文件，再读 deck 简报。**

模式 = **passive-study（自学/导师式讲义）**。读者是跨学科自学者：会高等数学、线性代数、
基础大学物理，但 **没有** 流体力学背景、不熟测度论/高级分析。这份讲义 *就是* 老师，没有人
在旁边补充——所有空白都必须由文字本身填上。

---

## 0. 输出位置与构建 / QA（每个 deck 都要做）

- deck 的 `.tex` 文件放在 **仓库根目录** `/data/weidong/auto-beamer/`（与 `template-lib/`
  目录平级）。`\usepackage[teal]{template-lib/template-lib}` 是相对路径，放错目录会报
  "File template-lib/template-lib.sty not found"。
- 构建（从仓库根目录，**必须跑两遍**——第二遍才会读 `.aux`、metropolis 进度条第一遍会
  产生假的 Overfull）：
  ```bash
  cd /data/weidong/auto-beamer
  xelatex -output-directory=build -interaction=nonstopmode <deck>.tex
  xelatex -output-directory=build -interaction=nonstopmode <deck>.tex
  ```
- **QA 门槛（全部必须通过，在简报里回报结果）：**
  1. 第二遍日志无致命错误：`grep -nE "^! |Undefined control sequence|Runaway|Missing \\\$" build/<deck>.log` → 空。
  2. 无 `Overfull \hbox` 超过 10pt：`grep -oE "Overfull \\\\hbox \(([0-9.]+)pt" build/<deck>.log` → 理想为空；任何 >10pt 必须修掉（先删 `\vspace`/缩 `max height`，仍溢出就 **拆帧**）。
  3. 无 `Overfull \vbox`（帧内容溢出）：`grep -n "Overfull \\\\vbox" build/<deck>.log` → 空。
  4. 回报最终 **帧数**（`pdfinfo build/<deck>.pdf | grep Pages`）。
  5. 如运行环境支持读图：`pdftoppm -png -r 130 build/<deck>.pdf /tmp/<deck>` 抽查几页有无溢出/重叠。
- **不要** merge/push 到任何远端。只在工作区改文件。

---

## 1. 预置（preamble）—— 每个 deck 用这个骨架

```latex
\documentclass[aspectratio=169,10pt]{beamer}
\usepackage[teal]{template-lib/template-lib}
\uselayout{text}\uselayout{eq}\uselayout{twocol}\uselayout{1img}\uselayout{table}
\usetikzlibrary{arrows.meta,calc,positioning,patterns,decorations.pathmorphing,decorations.markings}

% ── 记号缩写（按 deck 需要增删；流体力学常用）─────────────────────
\newcommand{\rd}{\,\mathrm{d}}                 % 微分 d（直立体）
\newcommand{\dd}[2]{\frac{\mathrm{d}#1}{\mathrm{d}#2}}      % 全导数
\newcommand{\pd}[2]{\frac{\partial #1}{\partial #2}}        % 偏导
\newcommand{\DDt}[1]{\frac{\mathrm{D}#1}{\mathrm{D}t}}      % 质点(物质)导数
\newcommand{\grad}{\nabla}
\newcommand{\divg}{\nabla\!\cdot}
\newcommand{\vc}[1]{\boldsymbol{#1}}           % 矢量加粗
\newcommand{\Real}{\mathbb{R}}
\newcommand{\Rey}{\mathit{Re}}                 % 雷诺数
\newcommand{\proofskipnote}{\footnote{\scriptsize 非数学背景读者：本帧为\emph{推导细节}，第一遍可先跳过，记住本帧\emph{要点}即可。}}

\TLsetfoot{流体力学（水力学）\textperiodcentered{} 自学讲义 \textperiodcentered{} 第 N 部分：<标题>}
\begin{document}
... 正文 ...
\end{document}
```

主题固定 **teal**（用户偏好）。正文 **简体中文**。所有图用 **TikZ teal 配色** 重绘
（`TLprimary`/`TLaccent`/`TLprimaryTint`/`TLinkSoft`），**不要** 从源 PDF 抠扫描位图。

---

## 2. passive-study 的 P0 红线（违反任意一条 = 不合格，必须返工）

1. **推导无跳步**：每一步都给出依据；**禁止** "易证 / 可验证 / 显然 / 同理可得（却不写）/
   由…即得（却跳过中间）"。一行只做一个逻辑动作。长推导 **拆成多帧**（页数免费）。
2. **科学性**：每一条显示公式的符号、不等号方向、下标、量纲都必须正确。这些是 **标准流体力学
   公式**（牛顿内摩擦、静水压强、欧拉/N-S、伯努利、雷诺数、达西-威斯巴赫…），务必准确无误。
3. **理解优先（understanding-first）**：每个定义/定理/推导 **先用大白话说"它回答什么问题、
   为什么需要它"，再上形式化**。禁止"目的不明"的公式堆砌。
4. **不先于定义使用概念**：任何术语第一次出现就给"一句话直觉"桥接（中文白话 + 英文术语）。
5. **就地回忆（in-place recall）**：读者工作记忆≈2–3 帧；凡引用 2–3 帧以前的结果/记号，
   **就地复述**，不要只甩一个编号。需要被回忆的公式给一个 **deck 内可见编号**。
6. **无外语句子泄漏**：正文是中文；不要把英文整句/简报原文粘进去。英文 **术语** 和 `$...$` 允许。
7. **多帧证明/推导**：每帧开头一行"进度/地图"（我们在哪、上一帧得到了什么、本帧要拿到什么）。

> 北极星是 **让自学者真的看懂**。无跳步是必要但不充分——一个无跳步却"目的不明"的推导仍然判不合格。

---

## 3. 内容阶梯（每个 deck 的骨架，按此顺序）

1. `\TLtitlecenter{...}` 标题页。
2. **"如何使用本讲义"** 帧：含一行"非数学/非流体背景？→ 先读下一节'先建直觉'，第一遍可跳过带
   \proofskipnote 的推导帧，记住要点即可"。
3. **`\TLsection{先建直觉 · ...（新手先读）}`** on-ramp：**3–5 帧、零黑话**，每帧配一张
   极简 TikZ 图或一个可口算的数字，内容 **贴合本 deck 主题**（不要照搬别的 deck）。最后一帧是
   **阅读路径帧**：★必读 vs 推导可跳；声明假定背景 = 高数+线代+大学物理。
4. **核心内容**：严格按源讲义的小节顺序展开。每个概念遵循
   **动机(大白话) → 形式定义/定理 → 带具体数字的算例 → 性质/物理意义/常见误区**。
   - 定理与证明 **不同帧**；长证明用 **连续多帧**，每步可见。
   - 每个抽象对象配一张 2D 直觉图（TikZ）。
5. **算例**：每个主要概念 2–3 个，**具体数字、分步、可复算**。
6. **常见误区**：用 `\TLwarnblock` 点出初学者易错点。
7. **`\TLsection{练习}`**：≥3 题，难度分级 ⭐/⭐⭐/⭐⭐⭐，每题给 2–3 条 **由弱到强的提示**；
   完整解答放附录。
8. **`\TLsection{延伸与文献注记}`**：3–5 帧——对应源讲义章节、经典教材（如《流体力学》《水力学》、
   White / 莫宁-亚格洛姆 等）、工程应用、相关人物史（雷诺、达西、曼宁、普朗特等，按 deck 主题）。
   外部链接/教材只是 **深化**，本讲义不依赖它们也能完全看懂。
9. **`\TLsection{术语速查}`** 术语表：双语表 `中文 | English | 记号 | 一句话含义`。
10. `\appendix`：练习完整解答（每题分步），可 `\hyperlink` 回到题面。

---

## 4. 密度与排版（passive-study）

- 每帧上限：显示公式 ≤3、bullet ≤10、新记号 ≤8、彩色块 ≤3（`\TLtakeaway` 计入彩色块上限）。
- 每帧 ≥1 个实质元素（公式/图/表/定理/证明步/算例）。纯文字帧 ≤20%。
- 溢出一律 **拆帧** 解决，**绝不** 用 `\resizebox`/`\tiny` 把正文压到 `\scriptsize` 以下。
- 表格：`booktabs`（`\toprule/\midrule/\bottomrule`，无竖线），居中（`\begin{center}`），
  标题与 `\toprule` 间留 `\vspace{4pt}`；数字右对齐、文字左对齐。

## 5. template-lib 关键 API 与坑

- 块：`\TLinfoblock{标题}{正文}`、`\TLalertblock[标题]{正文}`、`\TLresultblock{标题}{正文}`、
  `\TLwarnblock{标题}{正文}`、`\TLtakeaway{正文}`。
- 行内：`\TLterm{术语}`、`\TLpos{}`、`\TLneg{}`、`\TLhl{}`、`\TLmuted{}`。
- 结构：`\TLsection{标题}`、`\TLtitlecenter{标题}{副标题}{作者}{日期}`。
- 图文：`\TLoneimgleft{图}{文}`、`\TLoneimgright{文}{图}`（**右图版文在前**，顺序相反会报
  "Missing \endcsname"）。
- **坑**：① `\textcolor{}{...}` 内不能出现 `\par`/空行（会报 "Paragraph ended before \@textcolor"）；
  ② `$...$——`（math 紧跟中文破折号）不可断行→Overfull，用 `，` 代替；
  ③ TikZ 节点样式以裸色名结尾且前面有 `fill=white` 时标签会变黑块，显式写 `text=...`；
  ④ `\TLthead` 用 `l` 列，表头里别放裸 ✓/✗。

## 6. 与源材料的关系

- 源讲义文本在 `books/流体力学/_txt/*.txt`（用 pdftotext 抽的，**公式排版被打乱**——分式拆成
  多行、unicode 数学符号）。**按标准流体力学形式重建每条公式**，必要时用
  `pdftoppm -png -r 150 books/流体力学/<对应PDF> /tmp/src` 渲染源页核对。
- **讲义内容必须比源更详细**（导师式补足背景），不得更简。源里"从略/简述"的推导，这里要 **写全**。
- 参考已有同风格 deck：`numopt-ch12-constrained-zh.tex`（preamble/无障碍/TikZ teal）、
  `ot-qualitative-zh.tex`（passive-study 结构）。
