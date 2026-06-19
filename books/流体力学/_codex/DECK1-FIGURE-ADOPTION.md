# Deck 1 — 源图采用清单 (source-first figure adoption)

把指定帧里我自制的 TikZ 示意图换成**源讲义原图**（已抠白边、放在 `slides_assets/fluid_deck01/`）。
源图是最准确的来源（policy: TikZ 是倒数第二选择）。**只改下面列出的帧；其它帧的 TikZ 全部保留。**

文件：`/data/weidong/auto-beamer/fluid-mech-01-properties-statics-zh.tex`（仓库根目录，xelatex 从根目录跑，相对路径 `slides_assets/fluid_deck01/xxx.png` 可用）。

## A. 替换 TikZ → 源图（这些帧目前有一张 tikzpicture，把那张 tikzpicture 整体换成 \includegraphics）
按帧标题定位；保留帧的其余文字/列结构，只替换 `\begin{tikzpicture}…\end{tikzpicture}` 那一块（含其外层若有的 `\begin{center}`）。换成：
```
\begin{center}\includegraphics[width=<W>,height=0.6\textheight,keepaspectratio]{slides_assets/fluid_deck01/<file>}\\{\scriptsize 图：源讲义原图}\end{center}
```
（在双栏 `\column` 里的，用 `width=\linewidth`；独占整宽的用 `width=0.7\textwidth`。务必 `keepaspectratio` 且 `height` 上限防溢出。）

| 帧标题（精确匹配） | 源图文件 |
|---|---|
| `粘滞性与无滑移：为什么壁面会拖住流体？` | newton-plate.png |
| `牛顿流体、非牛顿流体与理想流体` | fluid-types.png |
| `算例 C2：斜面木块的受力平衡` | ex-incline-block.png |
| `等加速直线运动：自由液面为什么倾斜？` | accel-cart.png |
| `旋转抛物面：中心下降与边壁上升` | rotation-parabola.png |
| `算例 S3（\#64）：求压力中心到转轴距离` | ex-gate-incline.png |
| `算例 S4（\#63）：半圆弧曲面的水平分力` | ex-curved-3arc.png |

## B. 给纯文字练习帧**添加**源图（这些练习帧没有图；把题目图加进去）
在该帧 `\TLinfoblock{题目}{…}` 之后、提示 `itemize` 之前（或用 `\begin{columns}` 左文右图），插入一张小图：
```
\begin{center}\includegraphics[width=0.46\textwidth,height=0.4\textheight,keepaspectratio]{slides_assets/fluid_deck01/<file>}\\{\scriptsize 图：源讲义原图}\end{center}
```

| 帧标题（精确匹配） | 源图文件 |
|---|---|
| `练习 F3（\#30）：圆管抛物线速度分布的切应力` | ex-pipe-parabola.png |
| `练习 F4（\#34）：圆锥旋转的黏性阻力矩` | ex-cone.png |
| `练习 F6（\#59）：轻油与重油的深度和测压管高度` | ex-oil-2layer.png |
| `练习 F8（\#69）：两侧水位同升时闸门合力增大` | ex-gate-2side.png |

## 硬约束
- **不要改动** 任何未列出的帧、preamble、正文文字、公式。只做上面两类图的替换/添加。
- 保持帧不溢出：2-pass 构建，`Overfull \hbox` 无 >10pt、`Overfull \vbox` 必须为空（图太大就调小 width/height）。
- 构建命令（从仓库根目录，跑两遍）：
  `xelatex -output-directory=build -interaction=nonstopmode fluid-mech-01-properties-statics-zh.tex`
- 回报：改了哪些帧、四项 grep 结果（^!/Undefined、Overfull hbox>10pt、Overfull vbox、Pages）。不要 commit/push。
