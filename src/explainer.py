"""How hash-based signatures work: a short explainer in the style of the sig.golf records page.

Render:  .venv/bin/manim -qh explainer.py <Scene>   (or -a for all scenes)
"""
import os
import random
import re

import manimpango
from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
for f in ("Inter-Regular", "Inter-Italic", "Inter-Medium", "Inter-SemiBold"):
    manimpango.register_font(os.path.join(HERE, "fonts", f + ".ttf"))
FONT = "Inter"
MONO = "Menlo"

config.background_color = "#ffffff"

INK = "#1d1d1f"
MUTED = "#6e6e73"
SOFT = "#86868b"
LINE = "#d2d2d7"
FAINT = "#ececf0"
ACC = "#0a84ff"
ACC_BG = "#e6f2ff"
BAD = "#ff3b30"
SCENES = ["S1Goal", "S2Hash", "S3YesNo", "S4Stairs", "S5Once", "S6Tree", "S7Stack", "S8Score"]


def T(s, size=36, color=INK, weight=NORMAL, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def wrap(s, limit):
    plain = lambda x: re.sub(r"<[^>]+>", "", x)
    lines, cur = [], ""
    for w in s.split(" "):
        if cur and len(plain(cur + " " + w)) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    lines.append(cur)
    return "\n".join(lines)


def M(s, size=30, color=INK, limit=None):
    return MarkupText(wrap(s, limit) if limit else s, font=FONT, font_size=size, color=color, line_spacing=0.9)


def hexs(seed, n=1):
    r = random.Random(seed)
    return " ".join("".join(r.choice("0123456789abcdef") for _ in range(4)) for _ in range(n))


def dot(p, r=0.1, color=INK):
    return Dot(p, radius=r, color=color)


def ring(m, color=ACC, r=0.2, w=3.5):
    return Circle(radius=r, color=color, stroke_width=w).move_to(m)


def tick(color=ACC):
    return T("✓", 40, color)


def xmark(color=BAD):
    return T("✕", 34, color)


def tile(text, dark, w=1.2, h=0.62, size=24):
    """A secret (dark) or public (blue) value."""
    bg = RoundedRectangle(corner_radius=0.12, width=w, height=h, stroke_width=0,
                          fill_color=INK if dark else ACC_BG, fill_opacity=1)
    t = Text(text, font=MONO, font_size=size, color=WHITE if dark else ACC).move_to(bg)
    return VGroup(bg, t)


def hbox(size=0.7):
    bg = RoundedRectangle(corner_radius=0.1, width=size, height=size, stroke_width=0, fill_color=FAINT, fill_opacity=1)
    return VGroup(bg, T("H", 24, INK, weight=SEMIBOLD).move_to(bg))


class Cap(Scene):
    """Headline at top left, one caption at bottom left."""

    cap = None
    hd = None

    def head(self, s):
        new = T(s, 40, INK, weight=SEMIBOLD).to_corner(UL, buff=0.7)
        anims = [FadeIn(new, shift=DOWN * 0.1)]
        if self.hd is not None:
            anims.append(FadeOut(self.hd))
        self.play(*anims, run_time=0.7)
        self.hd = new

    def say(self, s, wait=2.0, run_time=0.6):
        new = M(s, 32, MUTED, limit=56).to_corner(DL, buff=0.7)
        if self.cap is None:
            self.play(FadeIn(new, shift=UP * 0.1), run_time=run_time)
        else:
            self.play(FadeOut(self.cap), FadeIn(new, shift=UP * 0.1), run_time=run_time)
        self.cap = new
        if wait:
            self.wait(wait)

    def clear_all(self, run_time=0.8):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self.cap = None
        self.hd = None


# ---------------------------------------------------------------- 1. what a signature does
class S1Goal(Cap):
    def construct(self):
        title = T("How hash-based signatures work", 56, weight=SEMIBOLD)
        sub = T("A signature anyone can check and no one can fake", 30, MUTED).next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=1.0)
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.wait(2.0)
        self.play(FadeOut(title), FadeOut(sub))

        self.head("What a signature does")
        card = RoundedRectangle(corner_radius=0.2, width=4.6, height=1.9, stroke_width=0, fill_color=FAINT, fill_opacity=1)
        card.move_to([-3.7, 0.4, 0])
        msg = T("“Send 5 coins to Bob”", 30).move_to(card).shift(UP * 0.35)
        sig = T("signed: Alice", 24, ACC, weight=MEDIUM).move_to(card).shift(DOWN * 0.4)
        self.play(FadeIn(card), FadeIn(msg))
        self.say("Alice sends a message, and attaches a signature to it.", wait=0)
        self.play(FadeIn(sig, shift=UP * 0.1))
        self.wait(1.4)
        rules = VGroup(T("Only Alice can make it", 30), T("Anyone can check it", 30), T("It only fits this message", 30))
        rules.arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([0.9, 0.4, 0], aligned_edge=LEFT)
        nums = VGroup(*[T(str(i + 1), 26, ACC, weight=SEMIBOLD).next_to(r, LEFT, buff=0.3) for i, r in enumerate(rules)])
        self.say("A signature has to do three things.", wait=0)
        for n, r in zip(nums, rules):
            self.play(FadeIn(n), FadeIn(r, shift=RIGHT * 0.1), run_time=0.6)
            self.wait(0.7)
        self.wait(1.0)
        self.say("Hash-based signatures do this using only one ingredient: a hash function.", wait=2.2)
        self.clear_all()


# ---------------------------------------------------------------- 2. the hash function as a lock
class S2Hash(Cap):
    def construct(self):
        self.head("A one-way function")
        box = hbox(1.3).shift(UP * 0.4)
        box[1].scale(1.8)
        inp = T("“hello”", 34).next_to(box, LEFT, buff=1.4)
        a1 = Arrow(inp.get_right(), box.get_left(), buff=0.25, color=LINE, stroke_width=3)
        out = Text("2cf2 4dba 5fb0", font=MONO, font_size=30, color=INK).next_to(box, RIGHT, buff=1.4)
        a2 = Arrow(box.get_right(), out.get_left(), buff=0.25, color=LINE, stroke_width=3)
        self.play(FadeIn(box))
        self.say("A hash function scrambles any input into a short code.", wait=0)
        self.play(FadeIn(inp, shift=RIGHT * 0.2), GrowArrow(a1))
        self.play(GrowArrow(a2), AddTextLetterByLetter(out, time_per_char=0.03))
        self.wait(1.2)
        inp2 = T("“hellp”", 34).move_to(inp)
        out2 = Text("9e41 07ac d3b8", font=MONO, font_size=30, color=INK).move_to(out)
        self.say("Change one letter, and the code is completely different.", wait=0)
        self.play(Transform(inp, inp2), run_time=0.5)
        self.play(Transform(out, out2), run_time=0.7)
        self.wait(1.6)
        back = CurvedArrow(out.get_bottom() + DOWN * 0.25, inp.get_bottom() + DOWN * 0.25, angle=-PI / 4, color=BAD,
                           stroke_width=3)
        q = xmark().next_to(back, DOWN, buff=0.05)
        self.say("It only works one way. From the code, there’s no way back to the input.", wait=0)
        self.play(Create(back), run_time=1.0)
        self.play(FadeIn(q, scale=1.4))
        self.wait(2.0)
        self.play(FadeOut(VGroup(box, inp, a1, out, a2, back, q)))

        # the trick: publish H(secret), reveal the secret later
        self.head("The trick")
        s = tile("a91c", True, 1.5, 0.75, 28).move_to([-3.6, 0.4, 0])
        sl = T("secret", 24, SOFT).next_to(s, UP, buff=0.25)
        hb = hbox().move_to([-0.6, 0.4, 0])
        p = tile("7f03", False, 1.5, 0.75, 28).move_to([2.4, 0.4, 0])
        pl = T("public", 24, ACC).next_to(p, UP, buff=0.25)
        ar1 = Arrow(s.get_right(), hb.get_left(), buff=0.15, color=LINE, stroke_width=3)
        ar2 = Arrow(hb.get_right(), p.get_left(), buff=0.15, color=LINE, stroke_width=3)
        self.say("Pick a random secret. Hash it, and publish only the result.", wait=0)
        self.play(FadeIn(s), FadeIn(sl))
        self.play(GrowArrow(ar1), FadeIn(hb), GrowArrow(ar2), FadeIn(p), FadeIn(pl))
        self.wait(1.8)
        self.say("Later, reveal the secret. Anyone can hash it and see that it matches.", wait=0)
        copy = s.copy()
        self.play(copy.animate.move_to([-3.6, -1.3, 0]))
        hb2 = hbox().move_to([-0.6, -1.3, 0])
        r = tile("7f03", False, 1.5, 0.75, 28).move_to([2.4, -1.3, 0])
        self.play(GrowArrow(Arrow(copy.get_right(), hb2.get_left(), buff=0.15, color=LINE, stroke_width=3)),
                  FadeIn(hb2))
        self.play(GrowArrow(Arrow(hb2.get_right(), r.get_left(), buff=0.15, color=LINE, stroke_width=3)), FadeIn(r))
        eq = T("=", 40, ACC).move_to((p.get_center() + r.get_center()) / 2)
        ok = tick().next_to(r, RIGHT, buff=0.3)
        self.play(FadeIn(eq), FadeIn(ok, scale=1.4))
        self.wait(1.2)
        self.say("Since nobody can run the hash backwards, only the person who chose the secret could reveal it.",
                 wait=2.6)
        self.clear_all()


# ---------------------------------------------------------------- 3. the simplest signature: yes or no
class S3YesNo(Cap):
    def construct(self):
        self.head("The simplest signature")
        ys = [0.9, -0.5]
        names = ["yes", "no"]
        secs = [tile(h, True) for h in ("a91c", "3e57")]
        pubs = [tile(h, False) for h in ("7f03", "c2d8")]
        rows = VGroup()
        for i in range(2):
            lab = T(names[i], 30, INK, weight=MEDIUM).move_to([-5.6, ys[i], 0])
            secs[i].move_to([-3.9, ys[i], 0])
            hb = hbox(0.55).move_to([-2.2, ys[i], 0])
            pubs[i].move_to([-0.5, ys[i], 0])
            a1 = Arrow(secs[i].get_right(), hb.get_left(), buff=0.1, color=LINE, stroke_width=2.5,
                       max_tip_length_to_length_ratio=0.3)
            a2 = Arrow(hb.get_right(), pubs[i].get_left(), buff=0.1, color=LINE, stroke_width=2.5,
                       max_tip_length_to_length_ratio=0.3)
            rows.add(VGroup(lab, secs[i], a1, hb, a2, pubs[i]))
        hs = T("secrets", 22, SOFT).next_to(secs[0], UP, buff=0.35)
        hp = T("public key", 22, ACC).next_to(pubs[0], UP, buff=0.35)
        self.say("Say Alice only ever needs to sign “yes” or “no”. She makes two secrets, one for each answer.",
                 wait=0)
        self.play(*[FadeIn(r[0]) for r in rows], *[FadeIn(r[1]) for r in rows], FadeIn(hs))
        self.wait(1.4)
        self.say("She hashes both and publishes the two results. That’s her public key.", wait=0)
        self.play(*[AnimationGroup(GrowArrow(r[2]), FadeIn(r[3]), GrowArrow(r[4]), FadeIn(r[5])) for r in rows],
                  FadeIn(hp))
        self.wait(1.8)

        # sign "yes"
        sep = Line([1.2, 2.2, 0], [1.2, -1.6, 0], color=FAINT, stroke_width=2)
        mt = T("message", 22, SOFT).move_to([3.9, 1.9, 0])
        m = T("yes", 34, INK, weight=MEDIUM).next_to(mt, DOWN, buff=0.2)
        st = T("signature", 22, SOFT).next_to(m, DOWN, buff=0.45)
        self.play(Create(sep), FadeIn(mt), FadeIn(m))
        self.say("To sign “yes”, she reveals the “yes” secret. Nothing else.", wait=0)
        sg = secs[0].copy()
        self.play(FadeIn(st), sg.animate.next_to(st, DOWN, buff=0.2), run_time=1.0)
        self.wait(1.2)
        self.say("Anyone can hash it and check it against the public key.", wait=0)
        hb = hbox(0.55).next_to(sg, DOWN, buff=0.5)
        res = tile("7f03", False).next_to(hb, DOWN, buff=0.4)
        va1 = Arrow(sg.get_bottom(), hb.get_top(), buff=0.08, color=LINE, stroke_width=2.5,
                    max_tip_length_to_length_ratio=0.3)
        va2 = Arrow(hb.get_bottom(), res.get_top(), buff=0.08, color=LINE, stroke_width=2.5,
                    max_tip_length_to_length_ratio=0.3)
        self.play(GrowArrow(va1), FadeIn(hb))
        self.play(GrowArrow(va2), FadeIn(res))
        self.play(Indicate(pubs[0], color=ACC, scale_factor=1.1), Indicate(res, color=ACC, scale_factor=1.1))
        ok = tick().next_to(res, RIGHT, buff=0.3)
        self.play(FadeIn(ok, scale=1.4))
        self.wait(1.4)
        self.play(FadeOut(VGroup(mt, m, st, sg, hb, res, va1, va2, ok)))

        # forger wants "no"
        mt2 = T("message", 22, SOFT).move_to([3.9, 1.9, 0])
        m2 = T("no", 34, BAD, weight=MEDIUM).next_to(mt2, DOWN, buff=0.2)
        st2 = T("signature", 22, SOFT).next_to(m2, DOWN, buff=0.45)
        qm = T("?", 40, BAD, weight=SEMIBOLD).next_to(st2, DOWN, buff=0.3)
        self.say("A forger who wants to sign “no” needs the “no” secret. They only have its hash.", wait=0)
        self.play(FadeIn(mt2), FadeIn(m2), FadeIn(st2), FadeIn(qm))
        back = CurvedArrow(pubs[1].get_bottom() + DOWN * 0.1, secs[1].get_bottom() + DOWN * 0.1, angle=-PI / 3,
                           color=BAD, stroke_width=3)
        x = xmark().next_to(back, DOWN, buff=0.05)
        self.play(Create(back))
        self.play(FadeIn(x, scale=1.4))
        self.wait(1.6)
        self.say("That’s a complete signature. It can only say yes or no, but every idea that follows builds on it.",
                 wait=2.6)
        self.clear_all()


# ---------------------------------------------------------------- 4. numbers: staircases you can only climb
def stair(x, n=8, y0=-2.0, dy=0.55, r=0.1):
    dots = VGroup(*[dot([x, y0 + i * dy, 0], r, LINE) for i in range(n)])
    segs = VGroup(*[Line(dots[i].get_center(), dots[i + 1].get_center(), buff=r + 0.03, stroke_width=2.5, color=LINE)
                    for i in range(n - 1)])
    dots[0].set_color(INK)
    dots[-1].set_color(ACC).scale(1.3)
    return dots, segs


class S4Stairs(Cap):
    def construct(self):
        self.head("Signing a number")
        dots, segs = stair(-3.0, y0=-1.8, dy=0.56, r=0.11)
        nums = VGroup(*[T(str(i), 24, SOFT).next_to(dots[i], LEFT, buff=0.45) for i in range(8)])
        hs = VGroup(*[T("H", 18, SOFT).next_to(segs[i], RIGHT, buff=0.15) for i in range(7)])
        sec = T("secret", 24, INK).next_to(dots[0], RIGHT, buff=0.45)
        pub = T("public", 24, ACC).next_to(dots[-1], RIGHT, buff=0.45)
        self.say("To sign a number, hash a secret over and over. Each step up is one more hash.", wait=0)
        self.play(GrowFromCenter(dots[0]), FadeIn(sec))
        for i in range(7):
            self.play(Create(segs[i]), FadeIn(hs[i]), GrowFromCenter(dots[i + 1]), run_time=0.32)
        self.play(FadeIn(pub))
        self.wait(1.0)
        self.say("Publish the top. Number the steps from 0 at the bottom to 7 at the top.", wait=0)
        self.play(LaggedStart(*[FadeIn(n) for n in nums], lag_ratio=0.06))
        self.wait(1.4)

        r3 = ring(dots[3], r=0.26)
        sl = T("signature for 3", 24, ACC).next_to(dots[3], RIGHT, buff=0.5)
        self.say("To sign a 3, reveal the value on step 3.", wait=0)
        self.play(FadeOut(hs), Create(r3), dots[3].animate.set_color(ACC), FadeIn(sl))
        self.wait(1.2)
        self.say("A checker climbs the remaining 4 steps by hashing. If they land on the public top, it’s valid.",
                 wait=0)
        run = dot(dots[3].get_center(), 0.12, ACC)
        self.add(run)
        for i in range(3, 7):
            self.play(run.animate.move_to(dots[i + 1]), run_time=0.35)
        ok = tick().next_to(pub, RIGHT, buff=0.25)
        self.play(FadeIn(ok, scale=1.4))
        self.wait(1.2)
        self.play(FadeOut(run), FadeOut(ok))

        self.say("The problem: anyone can climb up. A forger can turn your 3 into a 5.", wait=0)
        evil = dot(dots[3].get_center(), 0.12, BAD)
        self.add(evil)
        self.play(evil.animate.move_to(dots[5]), run_time=0.8)
        f5 = T("fake 5", 24, BAD).next_to(dots[5], RIGHT, buff=0.5)
        self.play(FadeIn(f5), nums[5].animate.set_color(BAD))
        self.wait(1.4)
        self.say("But nobody can climb down. That would mean undoing a hash.", wait=0)
        down = Arrow(dots[3].get_center() + LEFT * 0.0 + RIGHT * 0.3, dots[1].get_center() + RIGHT * 0.3, buff=0.1,
                     color=BAD, stroke_width=4, max_tip_length_to_length_ratio=0.2)
        self.play(FadeOut(evil), GrowArrow(down))
        x = xmark().next_to(down, RIGHT, buff=0.1)
        self.play(FadeIn(x, scale=1.4))
        self.wait(1.6)
        self.say("So the fix is to make sure that raising one number forces another one down.", wait=1.8)
        self.clear_all()

        # several staircases, fixed total
        self.head("Several staircases, one fixed total")
        XS = [-5.2, -3.8, -2.4, -1.0]
        cols = [stair(x, dy=0.52, r=0.085) for x in XS]
        self.play(LaggedStart(*[AnimationGroup(Create(s), FadeIn(d)) for d, s in cols], lag_ratio=0.12), run_time=1.2)
        self.say("Sign with several staircases at once, and require the numbers to always add up to 15.", wait=1.6)
        target = 15
        tries = [[5, 2, 7, 4], [1, 3, 0, 6], [6, 7, 2, 5], [3, 6, 1, 5]]
        rings = VGroup(*[ring(cols[i][0][tries[0][i]], r=0.19) for i in range(4)])
        digs = VGroup(*[T(str(tries[0][i]), 32, ACC, weight=MEDIUM).next_to(cols[i][0][-1], UP, buff=0.3)
                        for i in range(4)])

        def panel(ds, k):
            s = sum(ds)
            g = VGroup(T(f"message + counter {k}", 24, SOFT),
                       T(" + ".join(map(str, ds)) + f" = {s}", 34, ACC if s == target else INK, weight=MEDIUM))
            return g.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([0.6, 0.2, 0], aligned_edge=LEFT)

        pl = panel(tries[0], 1)
        self.say("The numbers come from hashing the message. The signer adds a counter and retries until the total is 15.",
                 wait=0)
        self.play(FadeIn(digs), Create(rings), FadeIn(pl))
        self.wait(0.8)
        for k, ds in enumerate(tries[1:], start=2):
            self.play(Transform(rings, VGroup(*[ring(cols[i][0][ds[i]], r=0.19) for i in range(4)])),
                      Transform(digs, VGroup(*[T(str(ds[i]), 32, ACC, weight=MEDIUM).move_to(digs[i]) for i in range(4)])),
                      Transform(pl, panel(ds, k)), run_time=0.6)
            self.wait(0.4)
        okp = tick().next_to(pl[1], RIGHT, buff=0.3)
        self.play(FadeIn(okp, scale=1.4))
        self.wait(1.4)
        self.play(FadeOut(okp))

        self.say("Now a forger raises one number by climbing up…", wait=0)
        up = Arrow(cols[1][0][6].get_center() + RIGHT * 0.32, cols[1][0][7].get_center() + RIGHT * 0.32, buff=0,
                   color=BAD, stroke_width=4, max_tip_length_to_length_ratio=0.35)
        self.play(GrowArrow(up), digs[1].animate.set_color(BAD))
        bad = T("3 + 7 + 1 + 5 = 16", 34, BAD, weight=MEDIUM).move_to(pl[1], aligned_edge=LEFT)
        self.play(Transform(pl[1], bad))
        self.wait(1.0)
        self.say("…and the total breaks. To fix it, another number has to go down. That’s impossible.", wait=0)
        down = Arrow(cols[0][0][3].get_center() + RIGHT * 0.32, cols[0][0][2].get_center() + RIGHT * 0.32, buff=0,
                     color=BAD, stroke_width=4, max_tip_length_to_length_ratio=0.35)
        x = xmark().scale(0.8).next_to(down, RIGHT, buff=0.06)
        self.play(GrowArrow(down))
        self.play(FadeIn(x, scale=1.4))
        self.wait(2.0)
        self.play(FadeOut(VGroup(up, down, x, pl, rings, digs)))
        self.say("This is WOTS+C, the one-time signature inside every sig.golf entry. Real ones use dozens of staircases.",
                 wait=0)
        cx = sum(XS) / 4
        pk = dot([cx, 2.35, 0], 0.13, ACC)
        pkl = T("one public key", 24, ACC).next_to(pk, RIGHT, buff=0.25)
        lines = VGroup(*[Line(d[-1].get_center(), pk.get_center(), buff=0.15, color=ACC, stroke_width=1.5)
                         for d, _ in cols])
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.1), GrowFromCenter(pk), FadeIn(pkl))
        self.wait(2.4)
        self.clear_all()


# ---------------------------------------------------------------- 5. one key, one message
class S5Once(Cap):
    def construct(self):
        self.head("One key, one message")
        XS = [-5.2, -3.8, -2.4, -1.0]
        cols = [stair(x, dy=0.52, r=0.085) for x in XS]
        self.play(*[AnimationGroup(Create(s), FadeIn(d)) for d, s in cols])
        A, B = [3, 6, 1, 5], [5, 1, 6, 3]
        ra = VGroup(*[ring(cols[i][0][A[i]], INK, r=0.19) for i in range(4)])
        rb = VGroup(*[ring(cols[i][0][B[i]], SOFT, r=0.19) for i in range(4)])
        la = T("first signature", 24, INK).move_to([0.6, 1.2, 0], aligned_edge=LEFT)
        lb = T("second signature", 24, SOFT).next_to(la, DOWN, buff=0.25, aligned_edge=LEFT)
        self.say("What if Alice uses the same key twice?", wait=0)
        self.play(Create(ra), FadeIn(la))
        self.play(Create(rb), FadeIn(lb))
        self.wait(1.2)
        lo = [min(a, b) for a, b in zip(A, B)]
        self.say("On every staircase, a forger can now start from the lower of the two steps and climb.", wait=0)
        spans = VGroup(*[Line(cols[i][0][lo[i]].get_center() + LEFT * 0.3, cols[i][0][-1].get_center() + LEFT * 0.3,
                              color=BAD, stroke_width=5) for i in range(4)])
        self.play(LaggedStart(*[Create(s) for s in spans], lag_ratio=0.12), run_time=1.2)
        self.wait(1.2)
        F = [3, 4, 2, 6]
        rf = VGroup(*[ring(cols[i][0][F[i]], BAD, r=0.19) for i in range(4)])
        lf = T("forged: 3 + 4 + 2 + 6 = 15", 24, BAD).next_to(lb, DOWN, buff=0.25, aligned_edge=LEFT)
        self.say("That leaves enough room to hit 15 with numbers Alice never signed.", wait=0)
        self.play(Create(rf), FadeIn(lf))
        self.wait(2.0)
        self.say("So each key must sign exactly one message. Alice will need a lot of keys.", wait=2.2)
        self.clear_all()


# ---------------------------------------------------------------- 6. a tree of keys
def tree_positions(h, width, top, dy):
    return {(d, j): np.array([-width / 2 + (j + 0.5) * width / 2 ** d, top - d * dy, 0])
            for d in range(h + 1) for j in range(2 ** d)}


class S6Tree(Cap):
    def construct(self):
        self.head("Many keys, one public key")
        h = 3
        P = tree_positions(h, 10.5, 1.9, 1.2)
        leaves = VGroup(*[RoundedRectangle(corner_radius=0.1, width=0.95, height=0.5, stroke_width=0, fill_color=FAINT,
                                           fill_opacity=1).move_to(P[(h, j)]) for j in range(8)])
        ll = VGroup(*[T(f"key {j}", 18, MUTED).move_to(leaves[j]) for j in range(8)])
        self.say("Make many one-time keys. Here, eight. Publishing all of them would be too big.", wait=0)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(leaves[j]), FadeIn(ll[j])) for j in range(8)], lag_ratio=0.07))
        self.wait(1.4)
        nodes = {}
        self.say("Instead, hash them two by two, then hash the results, until one value is left.", wait=0)
        for d in range(h - 1, -1, -1):
            anims = []
            for j in range(2 ** d):
                n = dot(P[(d, j)], 0.1, INK)
                nodes[(d, j)] = n
                for c in (2 * j, 2 * j + 1):
                    src = leaves[c].get_top() if d == h - 1 else nodes[(d + 1, c)].get_center()
                    anims.append(Create(Line(src, n.get_center(), buff=0.12 if d < h - 1 else 0.02, stroke_width=2,
                                             color=LINE)))
                anims.append(GrowFromCenter(n))
            self.play(*anims, run_time=0.8)
        root = nodes[(0, 0)]
        self.play(root.animate.set_color(ACC).scale(1.5))
        rl = T("public key", 24, ACC).next_to(root, RIGHT, buff=0.3)
        self.play(FadeIn(rl))
        self.say("That single value is the public key. Change any key below, and it changes too.", wait=2.0)

        leaf = 5
        self.say("To sign, Alice uses one key, say key 5.", wait=0)
        self.play(leaves[leaf].animate.set_fill(ACC, opacity=1), ll[leaf].animate.set_color(WHITE))
        self.wait(1.0)
        sibs, j = [], leaf
        for d in range(h, 0, -1):
            sibs.append(leaves[j ^ 1] if d == h else nodes[(d, j ^ 1)])
            j >>= 1
        self.say("She sends its signature, plus the three values next to its path to the top.", wait=0)
        marks = VGroup(*[SurroundingRectangle(m, color=ACC, buff=0.07, corner_radius=0.12, stroke_width=3)
                         if isinstance(m, RoundedRectangle) else ring(m, r=0.24) for m in sibs])
        self.play(LaggedStart(*[Create(r) for r in marks], lag_ratio=0.35), run_time=1.3)
        self.wait(1.2)
        self.say("With those, a checker recomputes the path. Reaching the public key proves key 5 belongs to Alice.",
                 wait=0)
        j, cur = leaf, leaves[leaf].get_top()
        for d in range(h - 1, -1, -1):
            j >>= 1
            tgt = nodes[(d, j)]
            pulse = dot(cur, 0.09, ACC)
            self.add(pulse)
            self.play(pulse.animate.move_to(tgt), run_time=0.6)
            self.remove(pulse)
            if d:
                tgt.set_color(ACC)
            cur = tgt.get_center()
        ok = tick().next_to(rl, RIGHT, buff=0.2)
        self.play(FadeIn(ok, scale=1.4))
        self.wait(1.4)
        self.say("Doubling the keys adds just one more value to send. A million keys need only 20.", wait=2.4)
        self.clear_all()


# ---------------------------------------------------------------- 7. trees of trees, and the last layer
class S7Stack(Cap):
    def construct(self):
        self.head("Trees of trees")
        self.say("Real signers need room for billions of signatures. One giant tree would take forever to build.",
                 wait=1.8)
        hs = [12, 7, 6, 6]
        ys = [1.8, 0.7, -0.35, -1.35]
        widths = [2.6, 1.8, 1.6, 1.6]
        heights = [0.95, 0.78, 0.7, 0.7]
        rng = random.Random(4)
        TX = -1.6
        pk = dot([TX, 2.7, 0], 0.12, ACC)
        pkl = T("public key", 22, ACC).next_to(pk, RIGHT, buff=0.25)
        self.play(GrowFromCenter(pk), FadeIn(pkl))
        prev = pk.get_center()
        self.say("So trees are stacked. A one-time key at the bottom of each tree signs the top of the next tree.",
                 wait=0)
        for li in range(4):
            c = np.array([TX, ys[li], 0])
            top = c + UP * heights[li] / 2
            base_y = c[1] - heights[li] / 2
            tri = Polygon(top, [TX - widths[li] / 2, base_y, 0], [TX + widths[li] / 2, base_y, 0], stroke_width=0,
                          fill_color=FAINT, fill_opacity=1)
            conn = Line(prev, top, color=LINE, stroke_width=2) if li == 0 else \
                CurvedArrow(prev, top + UP * 0.04, angle=-0.5, color=LINE, stroke_width=2, tip_length=0.13)
            frac = rng.uniform(0.2, 0.8)
            leaf = np.array([TX - widths[li] / 2 + frac * widths[li], base_y, 0])
            path = Line(top, leaf, color=INK, stroke_width=2)
            ld = dot(leaf, 0.06, INK)
            chains = VGroup(*[Line(ORIGIN, UP * 0.4, stroke_width=2, color=LINE) for _ in range(14)]) \
                .arrange(RIGHT, buff=0.09).move_to([2.4, base_y + 0.2, 0])
            vals = VGroup(*[dot(ch.point_from_proportion(rng.random()), 0.04, ACC) for ch in chains])
            link = DashedLine(leaf, chains.get_left() + DOWN * 0.2, color=LINE, stroke_width=1.5, dash_length=0.06)
            wl = T("one-time key", 20, SOFT).next_to(chains, RIGHT, buff=0.25)
            self.play(Create(conn), FadeIn(tri), run_time=0.5)
            self.play(Create(path), GrowFromCenter(ld), Create(link), FadeIn(chains), FadeIn(vals), FadeIn(wl),
                      run_time=0.5)
            prev = chains.get_bottom() + DOWN * 0.06
        self.wait(0.8)
        self.say("A signature only follows one path down: a few small trees, never the whole thing.", wait=2.0)
        self.say("sig.golf entries today stack four trees, of heights 12, 7, 6 and 6.", wait=2.0)
        self.clear_all()

        # the last layer
        self.head("The last layer")
        h = 4
        P = tree_positions(h, 11.0, 2.1, 0.8)
        edges = VGroup(*[Line(P[(d - 1, j >> 1)], P[(d, j)], stroke_width=1.5, color=LINE)
                         for d in range(1, h + 1) for j in range(2 ** d)])
        nodes = {k: dot(v, 0.05 if k[0] < h else 0.09, LINE if k[0] < h else INK) for k, v in P.items()}
        self.say("At the very bottom sits a key that can safely sign a few times. Its 16 leaves are secrets.", wait=0)
        self.play(Create(edges), *[FadeIn(n) for n in nodes.values()], run_time=1.2)
        self.play(nodes[(0, 0)].animate.set_color(ACC).scale(2.2))
        self.wait(1.0)

        def pick(lv, color, text, pos):
            return VGroup(*[ring(P[(h, l)], color, r=0.2) for l in lv]), T(text, 22, color).move_to(pos)

        m1, l1 = pick([2, 9, 13], INK, "message 1", [-4.2, -1.65, 0])
        self.say("Each message picks just 3 of them to reveal.", wait=0)
        self.play(Create(m1), FadeIn(l1))
        self.wait(1.0)
        m2, l2 = pick([5, 6, 11], SOFT, "message 2", [4.2, -1.65, 0])
        self.play(Create(m2), FadeIn(l2))
        self.wait(0.8)
        self.say("To forge, you’d need a message whose 3 picks were all revealed already.", wait=0)
        rings = None
        for tl in [[2, 7, 13], [9, 5, 0], [6, 11, 14]]:
            r = VGroup(*[ring(P[(h, l)], BAD, r=0.28, w=2.5) for l in tl])
            if rings is None:
                rings = r
                self.play(FadeIn(r), run_time=0.45)
            else:
                self.play(Transform(rings, r), run_time=0.45)
            self.wait(0.3)
        x = xmark().next_to(nodes[(0, 0)], RIGHT, buff=0.35)
        self.play(FadeIn(x, scale=1.4))
        self.say("With thousands of leaves instead of 16, that essentially never happens.", wait=2.2)
        self.clear_all()


# ---------------------------------------------------------------- 8. what sig.golf measures
class S8Score(Cap):
    def construct(self):
        self.head("What sig.golf measures")
        self.say("A signature is just revealed steps and path values. Its size and the work to check it both count.",
                 wait=1.6)

        def block(x, n, steps, dy):
            g = VGroup()
            for i in range(n):
                dts = VGroup(*[dot([x + i * 0.3, -1.4 + k * dy, 0], 0.045, LINE) for k in range(steps)])
                dts[-1].set_color(ACC)
                d = random.Random(n * 100 + i).randrange(steps - 1)
                dts[d].set_color(INK).scale(1.5)
                g.add(dts)
            return g

        short = block(-6.0, 16, 4, 0.3)
        tall = block(1.2, 8, 16, 0.2)
        ls = VGroup(T("Short staircases", 28, INK, weight=MEDIUM), T("16 values to send", 24, MUTED),
                    T("about 24 hashes to check", 24, MUTED)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        ls.next_to(short, DOWN, buff=0.4, aligned_edge=LEFT)
        lt = VGroup(T("Tall staircases", 28, INK, weight=MEDIUM), T("8 values to send", 24, MUTED),
                    T("about 60 hashes to check", 24, MUTED)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        lt.next_to(tall, DOWN, buff=0.4, aligned_edge=LEFT)
        VGroup(short, tall, ls, lt).shift(UP * 1.25)
        self.say("Take the staircases. Short ones carry less each, so you need more of them.", wait=0)
        self.play(LaggedStart(*[FadeIn(c) for c in short], lag_ratio=0.04), FadeIn(ls[0]))
        self.play(FadeIn(ls[1]), FadeIn(ls[2]))
        self.wait(1.4)
        self.say("Tall ones carry more, so fewer go in the signature, but checking means a longer climb.", wait=0)
        self.play(LaggedStart(*[FadeIn(c) for c in tall], lag_ratio=0.06), FadeIn(lt[0]))
        self.play(FadeIn(lt[1]), FadeIn(lt[2]))
        self.wait(2.2)
        self.say("Every part of the design has trade-offs like this: smaller signature, or less work to check.",
                 wait=2.2)
        self.play(FadeOut(VGroup(short, tall, ls, lt)))

        f = VGroup(T("score", 40, INK, weight=SEMIBOLD), T("=", 40, SOFT), T("size", 40, INK),
                   T("×", 40, SOFT), T("verify cost", 40, INK)).arrange(RIGHT, buff=0.3).move_to([0, 1.0, 0])
        f[0].set_color(ACC)
        self.say("sig.golf multiplies the two. Lower is better.", wait=0)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in f], lag_ratio=0.15), run_time=1.2)
        self.wait(1.4)
        val = ValueTracker(70998144)
        num = always_redraw(lambda: T(f"{int(val.get_value()):,}", 60, INK, weight=SEMIBOLD).move_to([0, -0.5, 0]))
        note = T("first record, Sep 30", 24, SOFT).next_to(num, DOWN, buff=0.3)
        self.add(num)
        self.play(FadeIn(note))
        self.wait(1.0)
        self.say("Over 23 records, people reshaped these trees and staircases and nearly halved the score.", wait=0)
        self.play(val.animate.set_value(36604800), FadeOut(note), run_time=3.2, rate_func=smooth)
        note2 = T("record 23, Oct 18", 24, ACC).next_to(num, DOWN, buff=0.3)
        self.play(FadeIn(note2))
        self.wait(2.4)
        self.clear_all()

        fin = VGroup(T("As secure as the hash function.", 46, INK, weight=SEMIBOLD),
                     T("No number theory, so quantum computers don’t break it.", 30, MUTED)).arrange(DOWN, buff=0.35)
        self.play(FadeIn(fin[0], shift=UP * 0.12), run_time=1.0)
        self.play(FadeIn(fin[1], shift=UP * 0.1))
        self.wait(3.2)
        self.play(FadeOut(fin))
