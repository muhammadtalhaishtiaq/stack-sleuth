#!/usr/bin/env python3
"""Render StackSleuth V3 demo video scenes with PIL, 1920x1080 @ 15fps."""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
BG   = (13, 17, 23)
PANEL= (22, 27, 34)
FG   = (230, 237, 243)
DIM  = (139, 148, 158)
BLUE = (88, 166, 255)
GREEN= (63, 185, 80)
RED  = (248, 81, 73)
AMBER= (210, 153, 34)

FD = "/usr/share/fonts/truetype/dejavu/"
def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)

F_TITLE = F("DejaVuSans-Bold.ttf", 120)
F_SUB   = F("DejaVuSans.ttf", 44)
F_BIG   = F("DejaVuSans-Bold.ttf", 64)
F_MED   = F("DejaVuSans-Bold.ttf", 40)
F_TXT   = F("DejaVuSans.ttf", 36)
F_SMALL = F("DejaVuSans.ttf", 30)
F_TINY  = F("DejaVuSans.ttf", 26)
F_MONO  = F("DejaVuSansMono.ttf", 34)
F_MONOB = F("DejaVuSansMono-Bold.ttf", 34)
F_MONOS = F("DejaVuSansMono.ttf", 28)

ROOT = os.path.expanduser("~/workspace/hackathons/stack-sleuth/work-backup/videos/v3")

def audio_dur(path):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","json",path], capture_output=True, text=True)
    return float(json.loads(out.stdout)["format"]["duration"])

def blank():
    return Image.new("RGB", (W, H), BG)

def center_text(d, y, s, font, fill, x=W//2):
    d.text((x, y), s, font=font, fill=fill, anchor="mm")

def label_pill(d, text, color=BLUE):
    f = F_TINY
    bb = d.textbbox((0,0), text, font=f)
    tw = bb[2]-bb[0]+44
    x0, y0 = 40, H-78
    d.rounded_rectangle([x0, y0, x0+tw, y0+46], radius=23, fill=(30,36,45), outline=color, width=3)
    d.text((x0+22, y0+23), text, font=f, fill=color, anchor="lm")

def arrow(d, x0, y0, x1, y1, color=DIM, width=4):
    d.line([x0,y0,x1,y1], fill=color, width=width)
    ang = math.atan2(y1-y0, x1-x0)
    s = 16
    pts = [(x1,y1),
           (x1-s*math.cos(ang-0.45), y1-s*math.sin(ang-0.45)),
           (x1-s*math.cos(ang+0.45), y1-s*math.sin(ang+0.45))]
    d.polygon(pts, fill=color)

def fade(a, b, t):
    """a,b are 0..1 blend weights applied to fill alpha; returns 0..1"""
    return max(0.0, min(1.0, t))

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1-(1-t)**3

# ---------------- Scene 1: failing test terminal ----------------
def scene1(D):
    cmd = "python3 -m pytest tests/ -v"
    out_lines = [
        ("tests/test_pricing.py::test_bulk_discount_at_ten FAILED", RED),
        ("tests/test_pricing.py::test_bulk_discount_above_ten PASSED", GREEN),
        ("tests/test_pricing.py::test_save10_rate FAILED", RED),
        ("tests/test_pricing.py::test_subtotal PASSED", GREEN),
        ("", FG),
        ("2 failed, 8 passed in 0.07s", RED),
    ]
    type_end = 3.2
    def frame(t):
        img = blank(); d = ImageDraw.Draw(img)
        # terminal window
        x0,y0,x1,y1 = 260,180,1660,900
        d.rounded_rectangle([x0,y0,x1,y1], radius=18, fill=(10,12,16), outline=(48,54,63), width=2)
        d.rounded_rectangle([x0,y0,x1,y0+64], radius=18, fill=(30,36,45))
        d.rectangle([x0,y0+40,x1,y0+64], fill=(30,36,45))
        d.text((x0+28, y0+32), "terminal - demo repo", font=F_SMALL, fill=DIM, anchor="lm")
        for i,c in enumerate([(248,81,73),(210,153,34),(63,185,80)]):
            d.ellipse([x1-40-i*36, y0+20, x1-20-i*36, y0+40], fill=c)
        px, py = x0+40, y0+130
        d.text((px,py), "$ ", font=F_MONO, fill=BLUE, anchor="lm")
        n = int(max(0, min(len(cmd), (t-0.5)/(type_end-0.5)*len(cmd)))) if t>0.5 else 0
        d.text((px+52,py), cmd[:n], font=F_MONO, fill=FG, anchor="lm")
        if n == len(cmd) and (t*2 % 1) < 0.5:
            cx = px+52 + d.textlength(cmd[:n], font=F_MONO)
            d.rectangle([cx, py-18, cx+16, py+18], fill=FG)
        ly = py + 64
        # output appears line by line after typing
        start = type_end + 0.5
        for i,(ln,color) in enumerate(out_lines):
            lt = start + i*0.45
            if t >= lt and ln:
                d.text((px, ly), ln, font=F_MONOS, fill=color, anchor="lm")
                ly += 52
        # pulse on the FAILED lines near the end
        if t > start + 3.0:
            pulse = 0.5 + 0.5*math.sin(t*4)
            d.rounded_rectangle([px-14, py+50, x1-60, py+50+2*52+20], radius=10,
                                outline=(248,81,73,int(120+100*pulse)), width=3)
        label_pill(d, "Use-case walkthrough")
        return img
    return frame

# ---------------- Scene 2: title ----------------
def scene2(D):
    title = "StackSleuth"
    sub = "A debugging loop built on IBM Bob"
    chips = ["Reproduce","Bisect","Explain","Propose","Approve","Verify"]
    def frame(t):
        img = blank(); d = ImageDraw.Draw(img)
        n = int(max(0, min(len(title), t/2.4*len(title)))) if t>0.2 else 0
        center_text(d, 400, title[:n], F_TITLE, FG)
        if t > 2.6:
            a = ease((t-2.6)/0.8)
            # fake alpha via color blend
            c = tuple(int(BG[i]+(DIM[i]-BG[i])*a) for i in range(3))
            center_text(d, 520, sub, F_SUB, c)
        # chips
        chip_w, gap = 250, 24
        total = len(chips)*chip_w + (len(chips)-1)*gap
        x = (W-total)/2
        for i,ch in enumerate(chips):
            ct = 3.6 + i*0.55
            a = ease((t-ct)/0.5)
            y = 700
            if a > 0:
                alpha_c = tuple(int(BG[j]+(PANEL[j]-BG[j])*a) for j in range(3))
                d.rounded_rectangle([x, y-44, x+chip_w, y+44], radius=22, fill=alpha_c,
                                    outline=tuple(int(BG[j]+(BLUE[j]-BG[j])*a) for j in range(3)), width=2)
                d.text((x+chip_w/2, y), ch, font=F_MED,
                       fill=tuple(int(BG[j]+(FG[j]-BG[j])*a) for j in range(3)), anchor="mm")
            x += chip_w + gap
        label_pill(d, "How StackSleuth works")
        return img
    return frame

# ---------------- Scene 3: loop flowchart ----------------
NODES = ["Reproduce","Bisect","Explain","Propose","Human Approval","Verify"]
def scene3(D):
    cx, cy, rx, ry = 960, 560, 620, 300
    pos = []
    for i in range(6):
        ang = -math.pi/2 + i*(2*math.pi/6)
        pos.append((cx+rx*math.cos(ang), cy+ry*math.sin(ang)))
    slot = (D-1.2)/6
    def frame(t):
        img = blank(); d = ImageDraw.Draw(img)
        center_text(d, 120, "The StackSleuth loop", F_BIG, FG)
        # arrows
        for i in range(6):
            x0,y0 = pos[i]; x1,y1 = pos[(i+1)%6]
            mx,my = (x0+x1)/2,(y0+y1)/2
            dx,dy = x1-x0,y1-y0
            L = math.hypot(dx,dy)
            sx,sy = x0+dx/L*120, y0+dy/L*72
            ex,ey = x1-dx/L*120, y1-dy/L*72
            arrow(d, sx,sy,ex,ey, DIM, 4)
        # traveling token between current and next node
        cur = min(5, int(t/slot))
        ft = (t - cur*slot)/slot
        x0,y0 = pos[cur]; x1,y1 = pos[(cur+1)%6]
        dx,dy = x1-x0,y1-y0; L = math.hypot(dx,dy)
        tx,ty = x0+dx*ease(ft), y0+dy*ease(ft)
        d.ellipse([tx-14,ty-14,tx+14,ty+14], fill=BLUE)
        for i,(px,py) in enumerate(pos):
            active = (i == cur)
            gate = (NODES[i] == "Human Approval")
            w,h = (300,140) if gate else (280,110)
            fill = (36,44,56) if active else PANEL
            border = AMBER if gate else (BLUE if active else (60,68,80))
            bw = 5 if (active or gate) else 2
            d.rounded_rectangle([px-w/2,py-h/2,px+w/2,py+h/2], radius=20, fill=fill,
                                outline=border, width=bw)
            if gate:
                gf = F("DejaVuSans-Bold.ttf", 34)
                d.text((px,py-30), "Human", font=gf, fill=FG if active else DIM, anchor="mm")
                d.text((px,py+6), "Approval", font=gf, fill=FG if active else DIM, anchor="mm")
                gy = py+42
                d.rectangle([px-26,gy-13,px-18,gy+13], fill=AMBER)
                d.rectangle([px-8,gy-13,px,gy+13], fill=AMBER)
                d.rectangle([px+10,gy-13,px+18,gy+13], fill=AMBER)
            else:
                d.text((px,py-8), NODES[i], font=F_MED,
                       fill=FG if active else DIM, anchor="mm")
            if active:
                pulse = 0.5+0.5*math.sin(t*5)
                d.rounded_rectangle([px-w/2-8,py-h/2-8,px+w/2+8,py+h/2+8], radius=26,
                                    outline=(88,166,255,int(80+120*pulse)), width=3)
        # caption for current node
        caps = {
            "Reproduce":"run the suite, capture the failing test",
            "Bisect":"search commit history for the culprit",
            "Explain":"describe what changed and why it broke",
            "Propose":"draft a minimal patch",
            "Human Approval":"nothing applies without a human OK",
            "Verify":"re-run tests, close the loop",
        }
        center_text(d, 940, caps[NODES[cur]], F_SMALL, DIM)
        label_pill(d, "How StackSleuth works")
        return img
    return frame

# ---------------- Scene 4: code bug animation ----------------
def scene4(D):
    def code_card(d, x0, y0, w, h, title, lines, t, reveal_t):
        d.rounded_rectangle([x0,y0,x0+w,y0+h], radius=18, fill=PANEL, outline=(48,54,63), width=2)
        d.text((x0+30, y0+44), title, font=F_MED, fill=FG, anchor="lm")
        d.line([x0+30, y0+78, x0+w-30, y0+78], fill=(48,54,63), width=2)
        y = y0+140
        for kind, txt in lines:
            d.text((x0+50, y), txt, font=F_MONO, fill=FG, anchor="lm")
            y += 56
        return y
    def frame(t):
        img = blank(); d = ImageDraw.Draw(img)
        center_text(d, 100, "Two small bugs, caught by tests", F_BIG, FG)
        # Card 1: off-by-one (operator line drawn in parts for clean morph)
        x0,y0,w,h = 110,200,830,560
        morph = ease((t - 0.35*D)/1.2)
        d.rounded_rectangle([x0,y0,x0+w,y0+h], radius=18, fill=PANEL, outline=(48,54,63), width=2)
        d.text((x0+30, y0+44), "pricing.py : bulk discount", font=F_MED, fill=FG, anchor="lm")
        d.line([x0+30, y0+78, x0+w-30, y0+78], fill=(48,54,63), width=2)
        y = y0+140
        for txt in ["def bulk_price(qty, price):"]:
            d.text((x0+50, y), txt, font=F_MONO, fill=FG, anchor="lm")
            y += 56
        # operator line
        op = ">=" if morph > 0.5 else ">"
        opc = GREEN if morph > 0.5 else RED
        d.text((x0+50, y), "    if qty ", font=F_MONO, fill=FG, anchor="lm")
        ox = x0+50 + d.textlength("    if qty ", font=F_MONO)
        pulse = 0.5+0.5*math.sin(t*4)
        bw = d.textlength(op, font=F_MONOB)+28
        d.rounded_rectangle([ox-14, y-30, ox-14+bw, y+30], radius=10,
                            outline=(opc[0],opc[1],opc[2],int(120+110*pulse)), width=4)
        d.text((ox, y), op, font=F_MONOB, fill=opc, anchor="lm")
        d.text((ox + d.textlength(op, font=F_MONOB), y), " 10:", font=F_MONO, fill=FG, anchor="lm")
        y += 56
        for txt in ["        return price * 0.9", "    return price"]:
            d.text((x0+50, y), txt, font=F_MONO, fill=FG, anchor="lm")
            y += 56
        if morph > 0:
            c = tuple(int(DIM[i]+(GREEN[i]-DIM[i])*morph) for i in range(3))
            d.text((x0+50, y0+140+4*56+20), "buying exactly 10 now qualifies",
                   font=F_SMALL, fill=c, anchor="lm")
        # Card 2: SAVE10
        x0 = 980
        a2 = ease((t - 0.5*D)/0.8)
        if a2 > 0:
            yo = y0 + int((1-a2)*60)
            alpha = lambda c: tuple(int(BG[i]+(c[i]-BG[i])*a2) for i in range(3))
            d.rounded_rectangle([x0,yo,x0+w,yo+h], radius=18, fill=alpha(PANEL),
                                outline=alpha((48,54,63)), width=2)
            d.text((x0+30, yo+44), "coupons.py : SAVE10 rate", font=F_MED, fill=alpha(FG), anchor="lm")
            morph2 = ease((t - 0.72*D)/1.0)
            rate = "0.10" if morph2>0.5 else "0.05"
            rc = GREEN if morph2>0.5 else RED
            d.text((x0+50, yo+140), '"SAVE10": ', font=F_MONO, fill=alpha(FG), anchor="lm")
            rx = x0+50 + d.textlength('"SAVE10": ', font=F_MONO)
            d.rounded_rectangle([rx-10, yo+140-28, rx+d.textlength(rate, font=F_MONOB)+10, yo+140+28],
                                radius=10, outline=(rc[0],rc[1],rc[2],int(120+110*pulse)), width=4)
            d.text((rx, yo+140), rate, font=F_MONOB, fill=(rc[0],rc[1],rc[2]) if a2>=1 else alpha(rc), anchor="lm")
            if morph2 > 0:
                c = tuple(int(DIM[i]+(GREEN[i]-DIM[i])*morph2) for i in range(3))
                d.text((x0+50, yo+140+56+20), "coupon rate fixed: 5 percent becomes 10 percent",
                       font=F_SMALL, fill=c, anchor="lm")
        label_pill(d, "Use-case walkthrough")
        return img
    return frame

# ---------------- Scene 5: git bisect timeline ----------------
def scene5(D):
    N = 16
    xs = [240 + i*(1680-240)/(N-1) for i in range(N)]
    y = 560
    def frame(t):
        img = blank(); d = ImageDraw.Draw(img)
        center_text(d, 110, "Bisecting the commit history", F_BIG, FG)
        center_text(d, 180, "test the middle, mark good or bad, halve the search",
                    F_SMALL, DIM)
        # phases
        # iter marks: (time, tested_idx, mark) and range after each
        iters = [
            (0.16*D, 7, "bad",  (0, 7)),
            (0.40*D, 3, "good", (4, 7)),
            (0.62*D, 5, "bad",  (4, 5)),
        ]
        # current range
        lo, hi = 0, N-1
        tested = {}
        for it, idx, mark, rng in iters:
            if t >= it:
                tested[idx] = mark
                lo, hi = rng
        culprit_t = 0.84*D
        culprit = t >= culprit_t
        # range bracket
        bx0, bx1 = xs[lo]-44, xs[hi]+44
        d.rounded_rectangle([bx0, y-110, bx1, y+110], radius=24,
                            outline=BLUE, width=4)
        d.text(((bx0+bx1)/2, y-140), "search range", font=F_TINY, fill=BLUE, anchor="mm")
        for i,x in enumerate(xs):
            in_range = lo <= i <= hi
            c = (60,68,80) if not in_range else DIM
            r = 24 if in_range else 18
            d.ellipse([x-r, y-r, x+r, y+r], fill=(30,36,45), outline=c, width=3)
            if i in tested:
                m = tested[i]
                mc = GREEN if m=="good" else RED
                d.ellipse([x-r, y-r, x+r, y+r], fill=mc)
                d.text((x, y-58), "good" if m=="good" else "bad", font=F_TINY, fill=mc, anchor="mm")
            if i in [it[1] for it in iters if t>=it[0] and t<it[0]+0.06*D]:
                # tester marker pulse right after test
                pass
        # tester marker on most recent tested
        recent = None
        for it, idx, mark, rng in iters:
            if t >= it: recent = idx
        if recent is not None and not culprit:
            x = xs[recent]
            d.polygon([(x, y+70),(x-20, y+110),(x+20, y+110)], fill=BLUE)
            d.text((x, y+140), "test", font=F_TINY, fill=BLUE, anchor="mm")
        if culprit:
            x = xs[4]
            pulse = 0.5+0.5*math.sin(t*5)
            d.ellipse([x-40, y-40, x+40, y+40], outline=(248,81,73,int(120+110*pulse)), width=5)
            d.ellipse([x-24, y-24, x+24, y+24], fill=RED)
            center_text(d, 880, "culprit found", F_MED, RED)
            center_text(d, 940, "one commit introduced the bug", F_SMALL, DIM)
        # progress dots of narration beats
        label_pill(d, "Use-case walkthrough")
        return img
    return frame

# ---------------- Scene 6: real evidence ----------------
def scene6(D):
    shots = [
        ("cropped-01-ide-project-open.png", "project opened in IBM Bob IDE 2.2.0"),
        ("cropped-02-ide-tests-passing.png", "10 passed in 0.07s in the integrated terminal"),
        ("cropped-03-ide-pricing-code.png", "pricing.py reviewed in the editor"),
    ]
    imgs = []
    for fn, cap in shots:
        im = Image.open(os.path.join(ROOT, "../../images/ide-sessions", fn)).convert("RGB")
        im.thumbnail((1680, 860), Image.LANCZOS)
        imgs.append((im, cap))
    seg = 0.26*D
    def frame(t):
        img = blank(); d = ImageDraw.Draw(img)
        if t < 3*seg:
            idx = min(2, int(t/seg))
            im, cap = imgs[idx]
            nxt = None
            # crossfade at segment boundaries
            ft = (t - idx*seg)
            base = img.copy(); bd = ImageDraw.Draw(base)
            bx = (W-im.width)//2; by = 120
            base.paste(im, (bx, by))
            bd.rounded_rectangle([bx-4,by-4,bx+im.width+4,by+im.height+4], radius=14,
                                 outline=(48,54,63), width=3)
            center_text(bd, by+im.height+56, cap, F_SMALL, FG)
            # Real run pill top-right
            pill = "Real run"
            bb = bd.textbbox((0,0), pill, font=F_TINY)
            tw = bb[2]-bb[0]+44
            bd.rounded_rectangle([W-60-tw, 40, W-60, 86], radius=23, fill=(30,36,45),
                                 outline=GREEN, width=3)
            bd.text((W-60-tw+22, 63), pill, font=F_TINY, fill=GREEN, anchor="lm")
            img = base
            # blend into next near boundary
            if idx < 2 and ft > seg-0.5:
                im2, cap2 = imgs[idx+1]
                ov = Image.new("RGB",(W,H),BG); od = ImageDraw.Draw(ov)
                bx2=(W-im2.width)//2
                ov.paste(im2,(bx2,by))
                center_text(od, by+im2.height+56, cap2, F_SMALL, FG)
                img = Image.blend(base, ov, ease((ft-(seg-0.5))/0.5))
        else:
            # end card: API analysis summary
            a = ease((t-3*seg)/0.8)
            c = lambda col: tuple(int(BG[i]+(col[i]-BG[i])*a) for i in range(3))
            center_text(d, 220, "Bob API analysis", F_BIG, c(FG))
            bullets = ["off-by-one spotted", "culprit commit explained",
                       "patch drafted", "edge cases flagged"]
            y = 380
            for i,b in enumerate(bullets):
                bt = ease((t-3*seg-0.8-i*0.5)/0.5)
                if bt>0:
                    bc = lambda col: tuple(int(BG[j]+(col[j]-BG[j])*bt) for j in range(3))
                    d.ellipse([554, y-20, 596, y+20], fill=bc(GREEN))
                    d.text((575, y), "ok", font=F_TINY, fill=bc(BG), anchor="mm")
                    d.text((620, y), b, font=F_MED, fill=bc(FG), anchor="lm")
                y += 92
            center_text(d, 900, "IDE used for editing and tests; analysis via Bob API",
                        F_SMALL, c(DIM))
            # Real run pill
            pill="Real run"
            bb=d.textbbox((0,0),pill,font=F_TINY); tw=bb[2]-bb[0]+44
            d.rounded_rectangle([W-60-tw,40,W-60,86], radius=23, fill=c((30,36,45)),
                                outline=c(GREEN), width=3)
            d.text((W-60-tw+22,63), pill, font=F_TINY, fill=c(GREEN), anchor="lm")
        return img
    return frame

# ---------------- Scene 7: approval gate ----------------
def scene7(D):
    def stamp(d, cx, cy, t, appear_t, scale=1.0):
        a = ease((t-appear_t)/0.6)
        if a <= 0: return
        s = int(460*scale*(0.6+0.4*a))
        layer = Image.new("RGBA", (s, int(s*0.42)), (0,0,0,0))
        ld = ImageDraw.Draw(layer)
        ld.rounded_rectangle([6,6,s-6,s*0.42-6], radius=24,
                             outline=(63,185,80,int(255*a)), width=10)
        lf = F("DejaVuSans-Bold.ttf", int(64*scale*(0.6+0.4*a)))
        ld.text((s/2, s*0.42/2), "APPROVED", font=lf,
                fill=(63,185,80,int(255*a)), anchor="mm")
        rot = layer.rotate(12, expand=True, resample=Image.BICUBIC)
        img_rgba = Image.new("RGBA",(W,H),(0,0,0,0))
        img_rgba.alpha_composite(rot, (int(cx-rot.width/2), int(cy-rot.height/2)))
        return img_rgba
    def frame(t):
        img = blank(); d = ImageDraw.Draw(img)
        center_text(d, 110, "The human stays in charge", F_BIG, FG)
        center_text(d, 175, "both fixes were reviewed and explicitly approved",
                    F_SMALL, DIM)
        cards = [
            ("pricing.py", [("- if qty > 10:", RED), ("+ if qty >= 10:", GREEN)]),
            ("coupons.py", [('- "SAVE10": 0.05', RED), ('+ "SAVE10": 0.10', GREEN)]),
        ]
        overlays = []
        for i,(title, lines) in enumerate(cards):
            x0 = 110 + i*880; y0=260; w=800; h=420
            at = ease((t-0.2-i*0.25)/0.6)
            if at<=0: continue
            yo = y0+int((1-at)*50)
            cc = lambda col: tuple(int(BG[j]+(col[j]-BG[j])*at) for j in range(3))
            d.rounded_rectangle([x0,yo,x0+w,yo+h], radius=18, fill=cc(PANEL),
                                outline=cc((48,54,63)), width=2)
            d.text((x0+36, yo+52), title, font=F_MED, fill=cc(FG), anchor="lm")
            d.line([x0+36, yo+92, x0+w-36, yo+92], fill=cc((48,54,63)), width=2)
            y = yo+160
            for ln, col in lines:
                d.text((x0+50, y), ln, font=F_MONO, fill=cc(col), anchor="lm")
                y += 70
            st = stamp(d, x0+w/2, yo+h-70, t, 0.35*D + i*0.3*D, scale=0.62)
            if st: overlays.append(st)
        for ov in overlays:
            img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        d = ImageDraw.Draw(img)
        label_pill(d, "How StackSleuth works")
        return img
    return frame

# ---------------- Scene 8: closing ----------------
def scene8(D):
    steps = ["Reproduce","Bisect","Explain","Propose","Approve","Verify"]
    def frame(t):
        img = blank(); d = ImageDraw.Draw(img)
        center_text(d, 330, "StackSleuth", F_TITLE, FG)
        a = ease((t-1.2)/0.8)
        c = lambda col: tuple(int(BG[i]+(col[i]-BG[i])*a) for i in range(3))
        center_text(d, 470, " : ".join(steps), F_SMALL, c(BLUE))
        b = ease((t-2.2)/0.8)
        cc = lambda col: tuple(int(BG[i]+(col[i]-BG[i])*b) for i in range(3))
        d.rounded_rectangle([560, 600, 1360, 690], radius=18, fill=cc(PANEL), outline=cc((48,54,63)), width=2)
        center_text(d, 645, "github.com/Muhammadtalhaishtiaq/stack-sleuth", F_MONOS, cc(FG))
        g = ease((t-3.0)/0.8)
        cg = lambda col: tuple(int(BG[i]+(col[i]-BG[i])*g) for i in range(3))
        center_text(d, 800, "Built for the IBM Bob 2.0 Hackathon", F_MED, cg(DIM))
        label_pill(d, "How StackSleuth works")
        return img
    return frame

SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]

def render_scene(i, D):
    fn = SCENES[i](D)
    n = int(D*FPS)
    out = os.path.join(ROOT, "scenes", "s%d.mp4" % (i+1))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = ["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s","%dx%d"%(W,H),
           "-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","medium",
           "-crf","20","-pix_fmt","yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for k in range(n):
        fr = fn(k/FPS)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    return out, D

def main():
    audio = [os.path.join(ROOT,"audio","s%d.mp3"%(i+1)) for i in range(8)]
    durs = []
    for i,a in enumerate(audio):
        da = audio_dur(a)
        D = da + 0.8
        durs.append(D)
        print("scene %d: audio %.2f -> video %.2f" % (i+1, da, D), flush=True)
        render_scene(i, D)
    print("TOTAL video: %.2f" % sum(durs), flush=True)
    with open(os.path.join(ROOT,"durs.json"),"w") as f:
        json.dump(durs, f)

if __name__ == "__main__":
    main()
