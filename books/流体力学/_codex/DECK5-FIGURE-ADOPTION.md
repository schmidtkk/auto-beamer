# Deck 5 — 源图采用清单 (source-first)

把指定帧的自制 TikZ 换成源讲义原图（已抠白边，`slides_assets/fluid_deck05/`）。**只改下列帧；其它 TikZ 全保留。**
文件：`/data/weidong/auto-beamer/fluid-mech-05-turbulence-velocity-zh.tex`。相对路径 `slides_assets/fluid_deck05/<file>`。

## 替换 TikZ → 源图（该帧若有 tikzpicture 就整体替换该 tikzpicture 块，含外层 \begin{center}）
片段：`\begin{center}\includegraphics[width=<W>,height=0.6\textheight,keepaspectratio]{slides_assets/fluid_deck05/<file>}\\{\scriptsize 图：源讲义原图}\end{center}`
（双栏 \column 用 width=\linewidth；整宽用 width=0.72\textwidth；务必 keepaspectratio + height 上限防溢出。）

| 帧标题（精确） | 源图 |
|---|---|
| `C1 雷诺实验：用一条红线看见流态` | reynolds-apparatus.png |
| `C5a 时均化：把瞬时速度拆成两部分` | fluctuation.png |
| `C6 雷诺应力 Part 1：动量交换图像` | reynolds-stress.png |
| `D1 三分区：近壁陡、管心钝` | three-zones.png |
| `D7c 分区图：线性律、过渡层与对数律` | loglaw-zones.png |
| `D8a 壁面粗糙度：三区分类取决于 $u_*$` | roughness.png |

## 硬约束
只改上面 6 帧；不动 preamble/正文/公式。2-pass 构建，Overfull hbox 无 >10pt、Overfull vbox 必须空（图溢出就调小）。
`xelatex -output-directory=build -interaction=nonstopmode fluid-mech-05-turbulence-velocity-zh.tex`（×2）。回报改了哪些帧 + 四项 grep。不要 commit/push。
