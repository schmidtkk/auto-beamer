"""
位移插值 vs 线性插值 —— 旁白版（离线音频，CosyVoice3 女声）。
每个 beat 的时长对齐 voiceover_audio/durations.json，渲染静音视频后用 ffmpeg
把 sample_all.wav（含 0.4s 间隔）混入，得到口型/节奏对齐的教学短视频。

  conda run -n manimdemo manim -qh --media_dir media ot_displacement_voiced.py OTDisplacementVoiced
  ffmpeg -y -i <silent.mp4> -i voiceover_audio/sample_all.wav -c:v copy -c:a aac -shortest out/ot_displacement_cosyvoice.mp4
"""
import json
from pathlib import Path
from manim import *

from ot_displacement import (
    gaussian, lin_pdf, disp_pdf, disp_params,
    M0, S0, M1, S1, CJK, TEAL, ORANGE, GREYL,
)

_DUR = json.load(open(Path(__file__).parent / "voiceover_audio" / "durations.json"))
DURS = _DUR["durations"]
GAP = 0.4


class OTDisplacementVoiced(Scene):
    def construct(self):
        d = DURS
        t = ValueTracker(0.0)

        title = Text("位移插值 vs 线性插值", font=CJK, color=TEAL, weight=BOLD).scale(0.82).to_edge(UP, buff=0.35)
        sub = Text("最优传输：质量该如何随时间移动？", font=CJK, color=GREYL).scale(0.4).next_to(title, DOWN, buff=0.12)

        def make_axes(shift):
            return Axes(x_range=[-5, 5, 1], y_range=[0, 0.75, 0.5], x_length=10.0, y_length=1.9,
                        tips=False, axis_config={"color": GREYL, "stroke_width": 2, "include_ticks": False}).shift(shift)

        ax_lin = make_axes(UP * 1.15)
        ax_dis = make_axes(DOWN * 1.95)
        lbl_lin = Text("线性插值  (1−t)μ₀ + t·μ₁", font=CJK, color=ORANGE).scale(0.44).next_to(ax_lin, UP, buff=0.06).align_to(ax_lin, LEFT)
        lbl_dis = Text("位移插值  μₜ = N(mₜ, σₜ²)", font=CJK, color=TEAL).scale(0.44).next_to(ax_dis, UP, buff=0.06).align_to(ax_dis, LEFT)

        ghosts = VGroup()
        for ax in (ax_lin, ax_dis):
            for (m, s, c) in [(M0, S0, ORANGE), (M1, S1, TEAL)]:
                ghosts.add(ax.plot(lambda x, m=m, s=s: gaussian(x, m, s), x_range=[-5, 5], color=c, stroke_opacity=0.22, stroke_width=3))

        lin_curve = always_redraw(lambda: ax_lin.plot(lambda x: lin_pdf(x, t.get_value()), x_range=[-5, 5], color=ORANGE, stroke_width=5))
        lin_fill = always_redraw(lambda: ax_lin.get_area(ax_lin.plot(lambda x: lin_pdf(x, t.get_value()), x_range=[-5, 5]), x_range=[-5, 5], color=ORANGE, opacity=0.18))
        dis_curve = always_redraw(lambda: ax_dis.plot(lambda x: disp_pdf(x, t.get_value()), x_range=[-5, 5], color=TEAL, stroke_width=5))
        dis_fill = always_redraw(lambda: ax_dis.get_area(ax_dis.plot(lambda x: disp_pdf(x, t.get_value()), x_range=[-5, 5]), x_range=[-5, 5], color=TEAL, opacity=0.18))
        t_label = always_redraw(lambda: Text(f"t = {t.get_value():.2f}", font=CJK, color=GREYL).scale(0.5).to_edge(DOWN, buff=0.25))

        def pad(dur, used):
            self.wait(max(dur - used, 0.05))
            self.wait(GAP)

        # Beat 0
        self.play(Write(title), FadeIn(sub, shift=DOWN * 0.2), run_time=2.2)
        self.play(Create(ax_lin), Create(ax_dis), FadeIn(lbl_lin), FadeIn(lbl_dis), run_time=2.5)
        pad(d[0], 4.7)

        # Beat 1
        self.play(*[Create(g) for g in ghosts], run_time=2.0)
        self.add(lin_fill, lin_curve, dis_fill, dis_curve, t_label)
        pad(d[1], 2.0)

        # Beat 2 — 双峰
        self.play(t.animate.set_value(0.5), run_time=4.5, rate_func=smooth)
        bimodal = Text("← 中间出现双峰（不自然）", font=CJK, color=ORANGE).scale(0.42).move_to(ax_lin.c2p(3.6, 0.62))
        self.play(FadeIn(bimodal, shift=LEFT * 0.2), run_time=1.0)
        pad(d[2], 5.5)

        # Beat 3 — 单峰平移
        single = Text("← 始终单峰，整体平移", font=CJK, color=TEAL).scale(0.42).move_to(ax_dis.c2p(3.6, 0.62))
        self.play(FadeIn(single, shift=LEFT * 0.2), run_time=1.2)
        self.play(t.animate.set_value(1.0), run_time=5.0, rate_func=smooth)
        pad(d[3], 6.2)

        # Beat 4 — 要点
        take = Text("位移插值 = Wasserstein 测地线：沿最优路径平移，保持形状", font=CJK, color=TEAL).scale(0.46).to_edge(DOWN, buff=0.55)
        self.play(FadeOut(t_label), FadeIn(take, shift=UP * 0.2), run_time=2.0)
        pad(d[4], 2.0)
