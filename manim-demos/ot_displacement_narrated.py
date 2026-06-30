"""
位移插值 vs 线性插值 —— 带中文旁白的教学短视频版。
旁白经由本地 OpenAI 兼容 TTS 服务器（/data/weidong/TTS, localhost:8880）合成，
manim-voiceover 自动让每段动画时长对齐旁白音频时长。

先启动 TTS 服务器（F5-TTS / zh_female），再：
  conda run -n manimdemo manim -qh --media_dir media ot_displacement_narrated.py OTDisplacementNarrated
"""
from manim import *
from manim_voiceover import VoiceoverScene

from local_tts import LocalOpenAITTS
from ot_displacement import (
    gaussian, lin_pdf, disp_pdf, disp_params,
    M0, S0, M1, S1, CJK, TEAL, ORANGE, GREYL,
)


class OTDisplacementNarrated(VoiceoverScene):
    def construct(self):
        self.set_speech_service(LocalOpenAITTS(model="f5tts", voice="zh_female"))
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

        # Beat 1 — 引入问题
        with self.voiceover(text="在最优传输里，我们常问：两个概率分布之间，如何构造一条合理的演化路径？") as tr:
            self.play(Write(title), FadeIn(sub, shift=DOWN * 0.2), run_time=min(tr.duration, 3))
            self.play(Create(ax_lin), Create(ax_dis), FadeIn(lbl_lin), FadeIn(lbl_dis), run_time=2)

        # Beat 2 — 线性插值的想法
        with self.voiceover(text="最直接的想法是线性插值——把起点和终点两个分布，按时间比例加权平均。") as tr:
            self.play(*[Create(g) for g in ghosts], run_time=min(tr.duration, 2))
            self.add(lin_fill, lin_curve, dis_fill, dis_curve, t_label)

        # Beat 3 — 线性插值的缺陷：双峰
        with self.voiceover(text="但请看上面一行：线性插值在中间会分裂成两个峰。质量仿佛凭空消失又出现，而不是真正地移动。") as tr:
            self.play(t.animate.set_value(0.5), run_time=max(tr.duration * 0.55, 3), rate_func=smooth)
            bimodal = Text("← 中间出现双峰（不自然）", font=CJK, color=ORANGE).scale(0.42).move_to(ax_lin.c2p(3.6, 0.62))
            self.play(FadeIn(bimodal, shift=LEFT * 0.2))

        # Beat 4 — 位移插值：单峰平移
        with self.voiceover(text="下面一行是位移插值：每一份质量沿着最优路径匀速平移。中间分布始终保持单峰，只是整体移动并形变。") as tr:
            single = Text("← 始终单峰，整体平移", font=CJK, color=TEAL).scale(0.42).move_to(ax_dis.c2p(3.6, 0.62))
            self.play(FadeIn(single, shift=LEFT * 0.2), run_time=1.5)
            self.play(t.animate.set_value(1.0), run_time=max(tr.duration - 1.5, 3), rate_func=smooth)

        # Beat 5 — 要点
        take = Text("位移插值 = Wasserstein 测地线：沿最优路径平移，保持形状", font=CJK, color=TEAL).scale(0.46).to_edge(DOWN, buff=0.55)
        with self.voiceover(text="这正是 Wasserstein 空间中的测地线——最优传输给出的，最自然的分布演化方式。") as tr:
            self.play(FadeOut(t_label), FadeIn(take, shift=UP * 0.2), run_time=2)
            self.wait(max(tr.duration - 2, 0.5))
