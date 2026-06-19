# Deck 6 — 源图采用清单 (source-first)

把指定帧的自制 TikZ 换成源讲义原图（已抠白边，`slides_assets/fluid_deck06/`）。**只改下列帧；其它 TikZ 全保留。**
文件：`/data/weidong/auto-beamer/fluid-mech-06-head-loss-zh.tex`。相对路径 `slides_assets/fluid_deck06/<file>`。

特别重要：D2、D8 两帧目前用我自制的「示意」TikZ 近似画尼古拉兹/穆迪曲线 —— 必须换成**真实的原图**（这正是源图最准确的典型案例）。

## 替换 TikZ → 源图（该帧若有 tikzpicture 就整体替换该 tikzpicture 块，含外层 \begin{center}）
片段：`\begin{center}\includegraphics[width=<W>,height=0.62\textheight,keepaspectratio]{slides_assets/fluid_deck06/<file>}\\{\scriptsize 图：源讲义原图}\end{center}`
（双栏 \column 用 width=\linewidth；整宽用 width=0.72\textwidth；尼古拉兹/穆迪图建议整宽 width=0.8\textwidth 但 height 上限 0.66\textheight 防溢出；务必 keepaspectratio。）

| 帧标题（精确） | 源图 |
|---|---|
| `C6 圆管切应力分布：沿半径线性增加` | circ-shear.png |
| `C7 宽矩形明渠：从床面到水面线性减小` | channel-shear.png |
| `C9 积分求圆管层流速度剖面` | laminar-profile.png |
| `D2 尼古拉兹实验：把 $\lambda$ 的变化分成五区` | nikuradse.png |
| `D8 穆迪图与实用管道` | moody.png |
| `E2a 突然扩大：控制体与假设` | sudden-expansion.png |
| `E3 淹没出流与自由出流` | submerged-outflow.png |
| `E4 突然缩小：经验公式` | sudden-contraction.png |

## 硬约束
只改上面 8 帧；不动 preamble/正文/公式。2-pass 构建，Overfull hbox 无 >10pt、Overfull vbox 必须空（图溢出就调小 width/height）。
`xelatex -output-directory=build -interaction=nonstopmode fluid-mech-06-head-loss-zh.tex`（×2）。回报改了哪些帧 + 四项 grep。不要 commit/push。
