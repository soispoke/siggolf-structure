"""How hash-based signatures work: a short explainer in the style of the sig.golf records page.

Render:  .venv/bin/manim -qh explainer.py S1Hash   (one scene)  or  -a  (all scenes)
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
BAD = "#ff3b30"
SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"


def T(s, size=36, color=INK, weight=NORMAL, **kw):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, **kw)


def wrap(s, limit):
    words, lines, cur = s.split(" "), [], ""
    plain = lambda x: re.sub(r"<[^>]+>", "", x)
    for w in words:
        if cur and len(plain(cur + " " + w)) > limit:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w) if cur else w
    lines.append(cur)
    return "\n".join(lines)


def M(s, size=30, color=INK, limit=None):
    if limit:
        s = wrap(s, limit)
    return MarkupText(s, font=FONT, font_size=size, color=color, line_spacing=0.9)


def hexs(seed, n=3):
    r = random.Random(seed)
    return " ".join("".join(r.choice("0123456789abcdef") for _ in range(4)) for _ in range(n))


def Hpow(k):
    return "s" if k == 0 else ("H(s)" if k == 1 else f"H{SUP[k]}(s)")


def tick(color=ACC):
    return T("✓", 40, color)


def xmark(color=BAD):
    return T("✕", 34, color)


def dot(p, r=0.1, color=INK):
    return Dot(p, radius=r, color=color)


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

    def say(self, s, wait=1.6, run_time=0.7):
        new = M(s, 30, MUTED, limit=58).to_corner(DL, buff=0.7)
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


# ---------------------------------------------------------------- 1. the hash function
class S1Hash(Cap):
    def construct(self):
        title = T("How hash-based signatures work", 56, weight=SEMIBOLD)
        sub = T("What every sig.golf entry is made of", 30, MUTED).next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=1.0)
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.wait(1.6)
        self.play(FadeOut(title), FadeOut(sub))

        self.head("A hash function")
        box = RoundedRectangle(corner_radius=0.22, width=1.7, height=1.3, stroke_width=0, fill_color=FAINT, fill_opacity=1)
        box.shift(UP * 0.3)
        hl = T("H", 60, INK, weight=SEMIBOLD).move_to(box)
        inp = T("“pay alice 5”", 34).next_to(box, LEFT, buff=1.3)
        a1 = Arrow(inp.get_right(), box.get_left(), buff=0.25, color=LINE, stroke_width=3)
        out = Text(hexs(1), font=MONO, font_size=30, color=INK).next_to(box, RIGHT, buff=1.3)
        a2 = Arrow(box.get_right(), out.get_left(), buff=0.25, color=LINE, stroke_width=3)
        self.play(FadeIn(box), FadeIn(hl))
        self.say("A hash function turns any input into a short fingerprint.", wait=0)
        self.play(FadeIn(inp, shift=RIGHT * 0.2), GrowArrow(a1))
        self.play(GrowArrow(a2), AddTextLetterByLetter(out, time_per_char=0.03))
        self.wait(1.2)

        inp2 = T("“pay alice 6”", 34).move_to(inp)
        out2 = Text(hexs(2), font=MONO, font_size=30, color=ACC).move_to(out)
        self.say("Change one character and you get a completely different fingerprint.", wait=0)
        self.play(Transform(inp, inp2), run_time=0.5)
        self.play(Transform(out, out2), run_time=0.8)
        self.wait(1.4)

        fwd = T("fast", 24, SOFT).next_to(a2, UP, buff=0.12)
        back = CurvedArrow(out.get_bottom() + DOWN * 0.25, inp.get_bottom() + DOWN * 0.25, angle=-PI / 4, color=BAD,
                           stroke_width=3)
        q = T("no known way", 24, BAD).next_to(back, DOWN, buff=0.1)
        self.say("Computing it is fast. Going backwards is not: no one knows how to find an input for a given fingerprint.",
                 wait=0)
        self.play(FadeIn(fwd))
        self.play(Create(back), FadeIn(q), run_time=1.1)
        self.wait(2.2)
        self.say("Quantum computers don’t change that much.", wait=1.6)
        self.say("Every part of the signature is built from this one function.", wait=2.0)
        self.clear_all()


# ---------------------------------------------------------------- 2. one-time keys: hash chains
def chain_row(w=8, x0=-5.6, dx=1.6, y=0.4):
    dots = VGroup(*[dot([x0 + i * dx, y, 0], 0.11, INK) for i in range(w)])
    arrows = VGroup(*[Arrow(dots[i].get_center(), dots[i + 1].get_center(), buff=0.2, stroke_width=2.5,
                            max_tip_length_to_length_ratio=0.1, color=LINE) for i in range(w - 1)])
    hs = VGroup(*[T("H", 20, SOFT).next_to(a, UP, buff=0.04) for a in arrows])
    labs = VGroup(*[T(Hpow(i), 24, MUTED).next_to(dots[i], DOWN, buff=0.3) for i in range(w)])
    return dots, arrows, hs, labs


def chain_col(x, w=8, y0=-1.9, dy=0.48, r=0.075):
    dots = VGroup(*[dot([x, y0 + i * dy, 0], r, LINE) for i in range(w)])
    segs = VGroup(*[Line(dots[i].get_center(), dots[i + 1].get_center(), buff=r + 0.03, stroke_width=2, color=FAINT)
                    for i in range(w - 1)])
    return dots, segs


def ring(m, color=ACC, r=0.19, w=3.5):
    return Circle(radius=r, color=color, stroke_width=w).move_to(m)


XS = [-5.0, -3.5, -2.0, -0.5]


def make_cols(scene):
    cols = [chain_col(x) for x in XS]
    for d, s in cols:
        d[0].set_color(INK)
        d[-1].set_color(ACC).scale(1.35)
    return cols


class S2Chain(Cap):
    def construct(self):
        self.head("One-time keys")
        dots, arrows, hs, labs = chain_row()
        self.play(GrowFromCenter(dots[0]), FadeIn(labs[0]))
        self.say("Pick a random secret and hash it, over and over.", wait=0)
        for i in range(7):
            self.play(GrowArrow(arrows[i]), FadeIn(hs[i]), GrowFromCenter(dots[i + 1]), FadeIn(labs[i + 1]),
                      run_time=0.38)
        self.play(dots[7].animate.set_color(ACC).scale(1.5), labs[7].animate.set_color(ACC))
        pub = T("public", 24, ACC).next_to(dots[7], UP, buff=0.35)
        sec = T("secret", 24, INK).next_to(dots[0], UP, buff=0.35)
        self.play(FadeIn(pub), FadeIn(sec))
        self.say("The last value is made public. The first one stays secret.", wait=1.4)

        nums = VGroup(*[T(str(i), 24, SOFT).next_to(labs[i], DOWN, buff=0.3) for i in range(8)])
        self.play(LaggedStart(*[FadeIn(n) for n in nums], lag_ratio=0.05))
        self.say("Each position stands for a digit, from 0 to 7.", wait=1.0)
        r3 = ring(dots[3], r=0.3)
        self.say("To sign a 3, reveal the value at position 3.", wait=0)
        self.play(Create(r3), dots[3].animate.set_color(ACC), nums[3].animate.set_color(ACC))
        self.play(*[dots[i].animate.set_opacity(0.2) for i in range(3)],
                  *[labs[i].animate.set_opacity(0.2) for i in range(3)], FadeOut(sec))
        self.wait(0.8)

        self.say("Anyone can hash it four more times and check that it reaches the public value.", wait=0)
        runner = dot(dots[3].get_center(), 0.11, ACC)
        self.add(runner)
        for i in range(3, 7):
            self.play(runner.animate.move_to(dots[i + 1]), run_time=0.36)
        ok = tick().next_to(pub, RIGHT, buff=0.2)
        self.play(FadeIn(ok, scale=1.4))
        self.wait(1.0)
        self.play(FadeOut(runner), FadeOut(ok))

        self.say("The catch: anyone can also hash forward, and turn a signed 3 into a 5.", wait=0)
        evil = dot(dots[3].get_center(), 0.11, BAD)
        self.add(evil)
        self.play(evil.animate.move_to(dots[5]), run_time=0.9)
        self.play(nums[5].animate.set_color(BAD))
        self.wait(1.6)
        self.clear_all()

        # ---- many chains with a fixed digit sum (WOTS+C)
        self.head("Many chains, one fixed total")
        cols = make_cols(self)
        self.play(LaggedStart(*[AnimationGroup(Create(s), FadeIn(d)) for d, s in cols], lag_ratio=0.12), run_time=1.3)
        sides = VGroup(T("secret", 22, SOFT).next_to(cols[0][0][0], LEFT, buff=0.35),
                       T("public", 22, ACC).next_to(cols[0][0][-1], LEFT, buff=0.35))
        self.play(FadeIn(sides))
        self.say("Real keys use dozens of chains, one for each digit of the message’s fingerprint.", wait=1.2)

        target = 15
        tries = [[5, 2, 7, 4], [1, 3, 0, 6], [6, 7, 2, 5], [3, 6, 1, 5]]
        counters = [1, 2, 3, 4]
        rings = VGroup(*[ring(cols[i][0][tries[0][i]]) for i in range(4)])
        digs = VGroup(*[T(str(tries[0][i]), 30, ACC, weight=MEDIUM).next_to(cols[i][0][-1], UP, buff=0.3) for i in range(4)])

        def sum_line(ds, k):
            s = sum(ds)
            g = VGroup(T(f"counter {k}", 24, SOFT),
                       T(" + ".join(map(str, ds)) + f" = {s}", 32, ACC if s == target else INK, weight=MEDIUM),
                       T(f"must equal {target}", 24, SOFT))
            return g.arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([1.4, 0.1, 0], aligned_edge=LEFT)

        sl = sum_line(tries[0], counters[0])
        self.say("The signer tries counter values until the digits add up to a fixed total.", wait=0)
        self.play(FadeIn(digs), Create(rings), FadeIn(sl))
        self.wait(0.6)
        for k, ds in enumerate(tries[1:], start=1):
            new_r = VGroup(*[ring(cols[i][0][ds[i]]) for i in range(4)])
            new_d = VGroup(*[T(str(ds[i]), 30, ACC, weight=MEDIUM).move_to(digs[i]) for i in range(4)])
            self.play(Transform(rings, new_r), Transform(digs, new_d), Transform(sl, sum_line(ds, counters[k])),
                      run_time=0.6)
            self.wait(0.3)
        self.say("This is WOTS+C, the one-time signature sig.golf entries use.", wait=1.4)

        self.say("A forger can still raise a digit by hashing forward.", wait=0)
        up = Arrow(cols[1][0][6].get_center() + RIGHT * 0.3, cols[1][0][7].get_center() + RIGHT * 0.3, buff=0,
                   color=BAD, stroke_width=4, max_tip_length_to_length_ratio=0.35)
        self.play(GrowArrow(up), digs[1].animate.set_color(BAD))
        bad = T("3 + 7 + 1 + 5 = 16", 32, BAD, weight=MEDIUM).move_to(sl[1], aligned_edge=LEFT)
        self.play(Transform(sl[1], bad))
        self.wait(0.8)
        self.say("But the total has to stay at 15, so another digit must go down. That means running H backwards.",
                 wait=0)
        down = Arrow(cols[0][0][3].get_center() + RIGHT * 0.3, cols[0][0][2].get_center() + RIGHT * 0.3, buff=0,
                     color=BAD, stroke_width=4, max_tip_length_to_length_ratio=0.35)
        x = xmark().scale(0.8).next_to(down, RIGHT, buff=0.08)
        self.play(GrowArrow(down))
        self.play(FadeIn(x, scale=1.4))
        self.wait(2.2)
        self.play(FadeOut(VGroup(up, down, x, sl, rings, digs)))

        self.say("Finally, the public ends of all the chains are hashed into one public key.", wait=0)
        cx = sum(XS) / 4
        pk = dot([cx, 2.35, 0], 0.14, ACC)
        pkl = T("public key", 24, ACC).next_to(pk, RIGHT, buff=0.25)
        lines = VGroup(*[Line(d[-1].get_center(), pk.get_center(), buff=0.16, color=ACC, stroke_width=1.5)
                         for d, _ in cols])
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.1), GrowFromCenter(pk))
        self.play(FadeIn(pkl))
        self.wait(2.0)
        self.clear_all()


# ---------------------------------------------------------------- 3. why only once
class S3OneTime(Cap):
    def construct(self):
        self.head("Why a key signs only once")
        cols = make_cols(self)
        self.play(*[AnimationGroup(Create(s), FadeIn(d)) for d, s in cols])
        A, B = [3, 6, 1, 5], [5, 1, 6, 3]
        ra = VGroup(*[ring(cols[i][0][A[i]], INK) for i in range(4)])
        rb = VGroup(*[ring(cols[i][0][B[i]], SOFT) for i in range(4)])
        la = T("message 1", 24, INK).move_to([1.4, 1.2, 0], aligned_edge=LEFT)
        lb = T("message 2", 24, SOFT).next_to(la, DOWN, buff=0.25, aligned_edge=LEFT)
        self.say("Suppose the same key signs two messages.", wait=0)
        self.play(Create(ra), FadeIn(la))
        self.play(Create(rb), FadeIn(lb))
        self.wait(0.8)
        lo = [min(a, b) for a, b in zip(A, B)]
        self.say("In every chain, the forger now has the lower of the two values, and everything above it.", wait=0)
        spans = VGroup(*[Line(cols[i][0][lo[i]].get_center() + LEFT * 0.28, cols[i][0][-1].get_center() + LEFT * 0.28,
                              color=BAD, stroke_width=5) for i in range(4)])
        self.play(LaggedStart(*[Create(s) for s in spans], lag_ratio=0.12), run_time=1.2)
        self.wait(1.0)
        F = [3, 4, 2, 6]
        rf = VGroup(*[ring(cols[i][0][F[i]], BAD) for i in range(4)])
        lf = T("forged: 3 + 4 + 2 + 6 = 15", 24, BAD).next_to(lb, DOWN, buff=0.25, aligned_edge=LEFT)
        self.say("That’s enough to build a new message with the right total.", wait=0)
        self.play(Create(rf), FadeIn(lf))
        self.wait(2.0)
        self.say("So each key signs exactly one message, and we need a lot of keys.", wait=2.0)
        self.clear_all()


# ---------------------------------------------------------------- 4. Merkle tree
def tree_positions(h, width, top, dy):
    pos = {}
    for d in range(h + 1):
        for j in range(2 ** d):
            pos[(d, j)] = np.array([-width / 2 + (j + 0.5) * width / 2 ** d, top - d * dy, 0])
    return pos


class S4Merkle(Cap):
    def construct(self):
        self.head("A tree of keys")
        h = 3
        P = tree_positions(h, 10.5, 1.9, 1.2)
        leaves = VGroup(*[RoundedRectangle(corner_radius=0.1, width=0.95, height=0.5, stroke_width=0, fill_color=FAINT,
                                           fill_opacity=1).move_to(P[(h, j)]) for j in range(8)])
        ll = VGroup(*[T(f"key {j}", 18, MUTED).move_to(leaves[j]) for j in range(8)])
        self.say("Make many one-time keys. Here, eight.", wait=0)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(leaves[j]), FadeIn(ll[j])) for j in range(8)], lag_ratio=0.07))
        self.wait(0.4)
        nodes = {}
        self.say("Hash them in pairs, then hash the results, up to a single value.", wait=0)
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
            self.play(*anims, run_time=0.75)
        root = nodes[(0, 0)]
        self.play(root.animate.set_color(ACC).scale(1.5))
        rl = T("public key", 24, ACC).next_to(root, RIGHT, buff=0.3)
        self.play(FadeIn(rl))
        self.say("That top value is the public key: 32 bytes that stand for all eight keys.", wait=1.6)

        leaf = 5
        self.say("To sign, use one key. Say, key 5.", wait=0)
        self.play(leaves[leaf].animate.set_fill(ACC, opacity=1), ll[leaf].animate.set_color(WHITE))
        self.wait(0.6)
        sibs, j = [], leaf
        for d in range(h, 0, -1):
            sibs.append(leaves[j ^ 1] if d == h else nodes[(d, j ^ 1)])
            j >>= 1
        self.say("Send its signature, plus the three neighbours on the way up.", wait=0)
        marks = VGroup(*[SurroundingRectangle(m, color=ACC, buff=0.07, corner_radius=0.12, stroke_width=3)
                         if isinstance(m, RoundedRectangle) else ring(m, r=0.24) for m in sibs])
        self.play(LaggedStart(*[Create(r) for r in marks], lag_ratio=0.3), run_time=1.2)
        self.wait(0.8)

        self.say("The verifier rebuilds the path. If it reaches the public key, the signing key is genuine.", wait=0)
        j, cur = leaf, leaves[leaf].get_top()
        for d in range(h - 1, -1, -1):
            j >>= 1
            tgt = nodes[(d, j)]
            pulse = dot(cur, 0.09, ACC)
            self.add(pulse)
            self.play(pulse.animate.move_to(tgt), run_time=0.55)
            self.remove(pulse)
            if d:
                tgt.set_color(ACC)
            cur = tgt.get_center()
        ok = tick().next_to(rl, RIGHT, buff=0.2)
        self.play(FadeIn(ok, scale=1.4))
        self.wait(1.0)
        self.say("Faking a path would mean finding two inputs with the same hash.", wait=1.8)
        self.say("A tree of height <i>h</i> holds 2<sup>h</sup> keys, but each proof is only <i>h</i> hashes.", wait=2.2)
        self.clear_all()


# ---------------------------------------------------------------- 5. hypertree
class S5Hyper(Cap):
    def construct(self):
        self.head("Trees of trees")
        self.say("A real key has to cover billions of signatures. That’s far too many leaves to build up front.",
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
        self.say("So trees are stacked. A key at the bottom of each tree signs the top of the next one.", wait=0)
        tris = VGroup()
        for li in range(4):
            c = np.array([TX, ys[li], 0])
            top = c + UP * heights[li] / 2
            base_y = c[1] - heights[li] / 2
            tri = Polygon(top, [TX - widths[li] / 2, base_y, 0], [TX + widths[li] / 2, base_y, 0], stroke_width=0,
                          fill_color=FAINT, fill_opacity=1)
            tris.add(tri)
            conn = Line(prev, top, color=LINE, stroke_width=2) if li == 0 else \
                CurvedArrow(prev, top + UP * 0.04, angle=-0.5, color=LINE, stroke_width=2, tip_length=0.13)
            lab = M(f"<i>h</i> = {hs[li]}", 22, SOFT).next_to(tri, LEFT, buff=0.3)
            frac = rng.uniform(0.2, 0.8)
            leaf = np.array([TX - widths[li] / 2 + frac * widths[li], base_y, 0])
            path = Line(top, leaf, color=INK, stroke_width=2)
            ld = dot(leaf, 0.06, INK)
            chains = VGroup(*[Line(ORIGIN, UP * 0.4, stroke_width=2, color=LINE) for _ in range(14)]) \
                .arrange(RIGHT, buff=0.09).move_to([2.4, base_y + 0.2, 0])
            vals = VGroup(*[dot(ch.point_from_proportion(rng.random()), 0.04, ACC) for ch in chains])
            link = DashedLine(leaf, chains.get_left() + DOWN * 0.2, color=LINE, stroke_width=1.5, dash_length=0.06)
            wl = T("one-time key", 20, SOFT).next_to(chains, RIGHT, buff=0.25)
            self.play(Create(conn), FadeIn(tri), FadeIn(lab), run_time=0.55)
            self.play(Create(path), GrowFromCenter(ld), Create(link), FadeIn(chains), FadeIn(vals), FadeIn(wl),
                      run_time=0.55)
            prev = chains.get_bottom() + DOWN * 0.06
        self.wait(0.6)
        self.say("A signature follows one path down: a few small trees, never the whole structure.", wait=1.6)
        self.say("sig.golf entries today use four layers, with heights 12, 7, 6 and 6.", wait=2.2)
        self.clear_all()


# ---------------------------------------------------------------- 6. few-time signature at the bottom
class S6FewTime(Cap):
    def construct(self):
        self.head("The last step: a few-time key")
        self.say("The key at the very bottom signs the message itself. Its leaves are secrets.", wait=0)
        h = 4
        P = tree_positions(h, 11.0, 1.9, 0.85)
        edges = VGroup(*[Line(P[(d - 1, j >> 1)], P[(d, j)], stroke_width=1.5, color=LINE)
                         for d in range(1, h + 1) for j in range(2 ** d)])
        nodes = {k: dot(v, 0.05 if k[0] < h else 0.09, LINE if k[0] < h else INK) for k, v in P.items()}
        self.play(Create(edges), *[FadeIn(n) for n in nodes.values()], run_time=1.3)
        self.play(nodes[(0, 0)].animate.set_color(ACC).scale(2.2))
        self.wait(0.8)

        def pick(leaves, color, text, pos):
            return VGroup(*[ring(P[(h, l)], color, r=0.2) for l in leaves]), T(text, 22, color).move_to(pos)

        m1, l1 = pick([2, 9, 13], INK, "message 1", [-4.2, -2.15, 0])
        self.say("The message’s fingerprint picks a few leaves, and only those are revealed.", wait=0)
        self.play(Create(m1), FadeIn(l1))
        self.wait(1.2)
        m2, l2 = pick([5, 6, 11], SOFT, "message 2", [4.2, -2.15, 0])
        self.say("A second message reveals a few more.", wait=0)
        self.play(Create(m2), FadeIn(l2))
        self.wait(1.0)
        self.say("A forger needs a new message whose picks were all revealed already.", wait=0)
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
        self.say("With real sizes, like 16,384 leaves and 15 picks, that essentially never happens.", wait=2.0)
        self.say("The message also picks which bottom key to use, so each one is rarely used twice.", wait=2.2)
        self.clear_all()


# ---------------------------------------------------------------- 7. the whole thing, and the sig.golf score
class S7Whole(Cap):
    def construct(self):
        self.head("The whole signature")
        labels = ["public key", "tree", "one-time key", "tree", "one-time key", "tree", "one-time key", "tree",
                  "one-time key", "few-time key", "message"]
        cols = [ACC, INK, MUTED, INK, MUTED, INK, MUTED, INK, MUTED, INK, SOFT]
        stack = VGroup(*[T(s, 22, c) for s, c in zip(labels, cols)]).arrange(DOWN, buff=0.16)
        stack.move_to([-5.0, 0.0, 0])
        self.say("From the public key down to the message, every piece is made of hashes.", wait=0)
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.08) for s in stack], lag_ratio=0.07), run_time=1.5)
        self.wait(1.0)

        # contents of the current record's signature (564ba604)
        parts = [("few-time key", 1808, INK), ("one-time keys", 2928, ACC), ("tree paths", 494, SOFT),
                 ("other", 18, LINE)]
        total = sum(p[1] for p in parts)
        W, x0, y = 8.4, -2.4, 1.55
        bar, x = VGroup(), x0
        for name, b, c in parts:
            r = Rectangle(width=max(0.03, W * b / total), height=0.42, stroke_width=0, fill_color=c, fill_opacity=1)
            r.move_to([x + r.width / 2, y, 0])
            x += r.width
            bar.add(r)
        bl = T(f"{total:,} bytes", 30, INK, weight=SEMIBOLD).next_to(bar, UP, buff=0.3, aligned_edge=LEFT)
        leg = VGroup(*[VGroup(Square(0.16, stroke_width=0, fill_color=c, fill_opacity=1), T(f"{n}  {b:,}", 20, MUTED))
                       .arrange(RIGHT, buff=0.12) for n, b, c in parts[:3]]).arrange(RIGHT, buff=0.45)
        leg.next_to(bar, DOWN, buff=0.25, aligned_edge=LEFT)
        self.say("The signature is just the revealed values and the neighbour hashes. About 5 KB.", wait=0)
        self.play(FadeIn(bl), LaggedStart(*[GrowFromEdge(r, LEFT) for r in bar], lag_ratio=0.15), run_time=1.3)
        self.play(FadeIn(leg))
        self.wait(1.6)

        Sx = VGroup(T("Size", 22, SOFT), T("bytes sent", 28, INK)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        Cx = VGroup(T("Verify cost", 22, SOFT), T("work to check", 28, INK)).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        Xx = VGroup(T("Score", 22, SOFT), T("size × cost", 28, ACC, weight=MEDIUM)).arrange(DOWN, buff=0.1,
                                                                                              aligned_edge=LEFT)
        row = VGroup(Sx, Cx, Xx).arrange(RIGHT, buff=0.8, aligned_edge=UP).move_to([x0, -0.4, 0], aligned_edge=LEFT)
        self.say("sig.golf scores each design by its size times its verification cost.", wait=0)
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.08) for g in row], lag_ratio=0.3), run_time=1.3)
        self.wait(1.0)

        val = ValueTracker(70998144)
        num = always_redraw(lambda: T(f"{int(val.get_value()):,}", 44, INK, weight=SEMIBOLD)
                            .move_to([x0, -1.75, 0], aligned_edge=LEFT))
        note = T("Sep 30, first record", 22, SOFT).next_to(num, RIGHT, buff=0.4)
        self.add(num)
        self.play(FadeIn(note))
        self.say("Over 22 records, the score dropped by almost half.", wait=0)
        self.play(val.animate.set_value(36683520), FadeOut(note), run_time=3.0, rate_func=smooth)
        note2 = T("Oct 17, 22nd record", 22, ACC).next_to(num, RIGHT, buff=0.4)
        self.play(FadeIn(note2))
        self.wait(2.0)
        self.clear_all()

        fin = VGroup(T("As secure as the hash function.", 46, INK, weight=SEMIBOLD),
                     T("No number theory, so quantum computers don’t break it.", 30, MUTED)).arrange(DOWN, buff=0.35)
        self.play(FadeIn(fin[0], shift=UP * 0.12), run_time=1.0)
        self.play(FadeIn(fin[1], shift=UP * 0.1))
        self.wait(3.0)
        self.play(FadeOut(fin))
