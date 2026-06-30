"""
位移插值 vs 线性插值 —— 最优传输定性理论的招牌动画。
镜像 slides_assets/ot/sec4-displacement.tex 的高斯例子：
  线性插值  (1-t)μ₀ + t·μ₁          → 中间出现双峰
  位移插值  μ_t = N(m_t, σ_t²)       → 单峰平移, m_t=(1-t)m₀+t·m₁, σ_t=(1-t)σ₀+t·σ₁

渲染（在 manimdemo conda 环境里）：
  conda run -n manimdemo manim -qh ot_displacement.py OTDisplacement      # mp4
  conda run -n manimdemo manim -qm --format=gif ot_displacement.py OTDisplacement
"""
from manim import *
import numpy as np

CJK    = "Source Han Serif SC"      # 已注册到 fontconfig
TEAL   = "#00796b"
ORANGE = "#e65100"
GREYL  = "#9aa0a6"


def gaussian(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))


# 端点：两个等宽高斯，仅平移
M0, S0, M1, S1 = -2.6, 0.6, 2.6, 0.6


def lin_pdf(x, t):
    return (1 - t) * gaussian(x, M0, S0) + t * gaussian(x, M1, S1)


def disp_params(t):
    return (1 - t) * M0 + t * M1, (1 - t) * S0 + t * S1


def disp_pdf(x, t):
    m, s = disp_params(t)
    return gaussian(x, m, s)


class OTDisplacement(Scene):
    def construct(self):
        t = ValueTracker(0.0)

        title = Text("位移插值 vs 线性插值", font=CJK, color=TEAL, weight=BOLD).scale(0.82)
        title.to_edge(UP, buff=0.35)
        sub = Text("最优传输：质量该如何随时间移动？", font=CJK, color=GREYL).scale(0.4)
        sub.next_to(title, DOWN, buff=0.12)
        self.play(Write(title), FadeIn(sub, shift=DOWN * 0.2))
        self.wait(0.3)

        # 两个堆叠坐标系
        def make_axes(shift):
            return Axes(
                x_range=[-5, 5, 1], y_range=[0, 0.75, 0.5],
                x_length=10.0, y_length=1.9, tips=False,
                axis_config={"color": GREYL, "stroke_width": 2,
                             "include_ticks": False},
            ).shift(shift)

        ax_lin = make_axes(UP * 1.15)
        ax_dis = make_axes(DOWN * 1.95)

        lbl_lin = Text("线性插值  (1−t)μ₀ + t·μ₁", font=CJK, color=ORANGE).scale(0.44)
        lbl_lin.next_to(ax_lin, UP, buff=0.06).align_to(ax_lin, LEFT)
        lbl_dis = Text("位移插值  μₜ = N(mₜ, σₜ²)", font=CJK, color=TEAL).scale(0.44)
        lbl_dis.next_to(ax_dis, UP, buff=0.06).align_to(ax_dis, LEFT)

        self.play(Create(ax_lin), Create(ax_dis), FadeIn(lbl_lin), FadeIn(lbl_dis))

        # 端点虚影（μ₀, μ₁）作参照
        ghosts = VGroup()
        for ax in (ax_lin, ax_dis):
            for (m, s, c) in [(M0, S0, ORANGE), (M1, S1, TEAL)]:
                g = ax.plot(lambda x, m=m, s=s: gaussian(x, m, s), x_range=[-5, 5],
                            color=c, stroke_opacity=0.22, stroke_width=3)
                ghosts.add(g)
        self.play(*[Create(g) for g in ghosts], run_time=0.8)

        # 动态曲线
        lin_curve = always_redraw(lambda: ax_lin.plot(
            lambda x: lin_pdf(x, t.get_value()), x_range=[-5, 5],
            color=ORANGE, stroke_width=5))
        lin_fill = always_redraw(lambda: ax_lin.get_area(
            ax_lin.plot(lambda x: lin_pdf(x, t.get_value()), x_range=[-5, 5]),
            x_range=[-5, 5], color=ORANGE, opacity=0.18))
        dis_curve = always_redraw(lambda: ax_dis.plot(
            lambda x: disp_pdf(x, t.get_value()), x_range=[-5, 5],
            color=TEAL, stroke_width=5))
        dis_fill = always_redraw(lambda: ax_dis.get_area(
            ax_dis.plot(lambda x: disp_pdf(x, t.get_value()), x_range=[-5, 5]),
            x_range=[-5, 5], color=TEAL, opacity=0.18))

        # 位移插值的"质心"标记（看它平移）
        dot = always_redraw(lambda: Dot(
            ax_dis.c2p(disp_params(t.get_value())[0],
                       disp_pdf(disp_params(t.get_value())[0], t.get_value())),
            color=TEAL, radius=0.06))

        # t 指示器
        t_label = always_redraw(lambda: Text(
            f"t = {t.get_value():.2f}", font=CJK, color=GREYL).scale(0.5).to_edge(DOWN, buff=0.25))

        self.add(lin_fill, lin_curve, dis_fill, dis_curve, dot, t_label)
        self.wait(0.4)

        # 主动画：t 0→1
        self.play(t.animate.set_value(1.0), run_time=5.0, rate_func=linear)
        self.wait(0.4)

        # 在 t=0.5 处回放并高亮"双峰"
        self.play(t.animate.set_value(0.5), run_time=1.6)
        bimodal = Text("← 中间出现双峰（不自然）", font=CJK, color=ORANGE).scale(0.42)
        bimodal.next_to(ax_lin, RIGHT, buff=-3.2).shift(UP * 0.1)
        single = Text("← 始终单峰，整体平移", font=CJK, color=TEAL).scale(0.42)
        single.next_to(ax_dis, RIGHT, buff=-3.2).shift(UP * 0.1)
        self.play(FadeIn(bimodal, shift=LEFT * 0.2))
        self.play(FadeIn(single, shift=LEFT * 0.2))
        self.wait(1.2)

        # 收尾要点
        take = Text("位移插值 = Wasserstein 测地线：沿最优路径平移，保持形状",
                    font=CJK, color=TEAL).scale(0.46)
        take.to_edge(DOWN, buff=0.55)
        self.play(FadeOut(t_label), FadeIn(take, shift=UP * 0.2))
        self.play(t.animate.set_value(1.0), run_time=2.0)
        self.wait(1.5)
