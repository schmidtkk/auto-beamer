# Deck 4 — 源图采用清单 (source-first)

把指定帧的自制 TikZ 换成源讲义原图（已抠白边，`slides_assets/fluid_deck04/`）。**只改下列帧；其它 TikZ 全保留。**
文件：`/data/weidong/auto-beamer/fluid-mech-04-steady-1d-flow-zh.tex`。相对路径 `slides_assets/fluid_deck04/<file>` 可用。

## A. 替换 TikZ → 源图（若该帧有 tikzpicture 就整体替换；若无图则插入）
片段：
```
\begin{center}\includegraphics[width=<W>,height=0.6\textheight,keepaspectratio]{slides_assets/fluid_deck04/<file>}\\{\scriptsize 图：源讲义原图}\end{center}
```
双栏内用 `width=\linewidth`；整宽用 `width=0.72\textwidth`。务必 keepaspectratio + height 上限防溢出。

| 帧标题（精确） | 源图 |
|---|---|
| `分岔管：流量按支路相加` | branch-Y.png |
| `算例 D-2：分叉管镇墩的控制体` | ex-anchor-branch.png |
| `应用 E-2：文丘里管测流量` | venturi.png |
| `水头线：把伯努利方程画出来` | head-lines.png |
| `算例 F-2：水泵安装高度上限` | pump.png |

## B. 给纯文字练习帧添加源图（在 `\TLinfoblock{题目}{…}` 之后插入）
```
\begin{center}\includegraphics[width=0.5\textwidth,height=0.42\textheight,keepaspectratio]{slides_assets/fluid_deck04/<file>}\\{\scriptsize 图：源讲义原图}\end{center}
```
| 帧标题（精确） | 源图 |
|---|---|
| `练习 H2（习题 \#32）$\star\star$：阀门开闭求流量` | ex-valve.png |
| `练习 H3（习题 \#41）$\star\star$：变径管压差计` | ex-umanometer.png |
| `练习 H4（习题 \#43）$\star\star\star$：虹吸管真空校核` | ex-siphon.png |
| `练习 H5（习题 \#44）$\star\star\star$：倒虹吸管流量` | ex-inv-siphon.png |

## 硬约束
不改动未列出的帧/preamble/正文/公式。2-pass 构建，Overfull hbox 无 >10pt、Overfull vbox 必须空（图溢出就调小 width/height，不缩正文）。
构建：`xelatex -output-directory=build -interaction=nonstopmode fluid-mech-04-steady-1d-flow-zh.tex`（×2）。回报改了哪些帧 + 四项 grep。不要 commit/push。
