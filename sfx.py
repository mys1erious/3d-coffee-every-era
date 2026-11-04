"""Sound bed for the ?play timeline, synthesised with the standard library only.

  python3 sfx.py out.wav      (mono 48 kHz; the narrator lines are mixed on top with ffmpeg, see README)
Timeline matches index.html: era i starts at i*2.6 - 0.55 s, the bump at +0.08, the impact at +0.72; era 8 is zero-g.
"""
import array, math, random, sys, wave

SR, DUR = 48000, 23.15
N = int(SR * DUR)
buf = array.array('d', bytes(8 * N))
R = random.Random(7)
ERA_START = [i * 2.6 - 0.55 for i in range(8)]
MATS = ['stone', 'clay', 'pewter', 'china', 'mug', 'mug', 'paper', 'zerog']


def put(t0, gen, n, gain=1.0):
    i0 = int(t0 * SR)
    for k in range(n):
        j = i0 + k
        if 0 <= j < N:
            buf[j] += gain * gen(k / SR)


def lp_noise(n, cut, rnd=R):  # one-pole lowpassed white noise
    a = math.exp(-2 * math.pi * cut / SR); y = 0.0; out = []
    for _ in range(n):
        y = a * y + (1 - a) * (rnd.random() * 2 - 1); out.append(y)
    return out


def hp(xs, cut):
    a = math.exp(-2 * math.pi * cut / SR); y = 0.0; px = 0.0; out = []
    for x in xs:
        y = a * (y + x - px); px = x; out.append(y)
    return out


def modes(t0, freqs, decays, gain, n_sec=1.5):
    n = int(n_sec * SR); ph = [R.random() * 6.28 for _ in freqs]
    put(t0, lambda t: sum(math.sin(2 * math.pi * f * t + p) * math.exp(-d * t) / (1 + i * .4) for i, (f, d, p) in enumerate(zip(freqs, decays, ph))), n, gain)


def noise_burst(t0, dur, cut, decay, gain, attack=0.004, hpcut=0):
    n = int(dur * SR); x = lp_noise(n, cut)
    if hpcut: x = hp(x, hpcut)
    put(t0, lambda t: x[min(int(t * SR), n - 1)] * min(1, t / attack) * math.exp(-decay * t), n, gain)


def thump(t0, f0, gain, decay=22):
    put(t0, lambda t: math.sin(2 * math.pi * (f0 * t + 40 * (1 - math.exp(-t * 30)) / 30)) * math.exp(-decay * t), int(.35 * SR), gain)


def plink(t0, f, gain):
    put(t0, lambda t: math.sin(2 * math.pi * f * t * (1 - 3 * t)) * math.exp(-130 * t), int(.04 * SR), gain)


def tick(t0, f, gain):
    modes(t0, [f, f * 2.3, f * 3.9], [60, 80, 110], gain, .08)


IMPACT = {
    'stone': lambda t: (thump(t, 85, .9, 16), noise_burst(t, .25, 1400, 18, .5)),
    'clay': lambda t: (thump(t, 150, .7, 26), modes(t, [420, 980], [35, 50], .35, .3), noise_burst(t, .15, 2500, 30, .35)),
    'pewter': lambda t: (modes(t, [523, 1187, 1991, 2873, 3911], [2.4, 3.2, 4.1, 5.5, 7], .32, 1.6), noise_burst(t, .05, 6000, 80, .3), modes(t + .12, [523, 1187, 1991], [5, 7, 9], .12, .6)),
    'china': lambda t: (modes(t, [2093, 3421, 5150, 6900], [9, 11, 14, 18], .3, .6), noise_burst(t, .04, 8000, 90, .25), modes(t + .09, [2093, 3421, 5150], [14, 18, 22], .12, .3)),
    'mug': lambda t: (thump(t, 120, .55, 30), modes(t, [880, 1650, 2700], [16, 22, 30], .3, .4), noise_burst(t, .05, 5000, 70, .25), modes(t + .1, [880, 1650], [25, 30], .1, .2)),
    'paper': lambda t: (thump(t, 140, .6, 28), noise_burst(t, .12, 1200, 30, .45), tick(t + .05, 1600, .25), tick(t + .3, 1300, .12)),
}
RATTLE = {'stone': 900, 'clay': 700, 'pewter': 2200, 'china': 3200, 'mug': 1800, 'paper': 600, 'zerog': 2600}


def splash(t0, size=1.0):
    noise_burst(t0, .9, 1800, 5.5, .55 * size, .006)
    noise_burst(t0 + .02, .5, 600, 7, .4 * size)
    for _ in range(26):
        plink(t0 + R.random() ** 1.6 * .65, 900 + R.random() * 2400, .05 + R.random() * .08)


def ambience(i, t0, dur):
    n = int(dur * SR)
    if i == 0:  # fire: rumble and crackle
        x = lp_noise(n, 300); put(t0, lambda t: x[int(t * SR) % n] * .35, n, 1)
        for _ in range(int(dur * 22)): noise_burst(t0 + R.random() * dur, .006, 9000, 500, .12 + R.random() * .2, .0005, 1500)
    elif i == 1:  # warm wind
        x = lp_noise(n, 500); put(t0, lambda t: x[int(t * SR) % n] * .5 * (.6 + .4 * math.sin(t * 1.3)), n, 1)
    elif i == 2:  # distant monastery bell
        modes(t0 + .15, [220, 440.8, 661, 880, 1234], [.7, .9, 1.1, 1.4, 2], .07, 2.8)
        x = lp_noise(n, 200); put(t0, lambda t: x[int(t * SR) % n] * .15, n, 1)
    elif i == 3:  # clock
        for k in range(6): noise_burst(t0 + .1 + k * .5, .01, 3500, 400, .18 if k % 2 else .12, .0005, 1500)
    elif i == 4:  # machine room hum and a card reader
        put(t0, lambda t: .02 * (math.sin(2 * math.pi * 60 * t) + .6 * math.sin(2 * math.pi * 120 * t) + .3 * math.sin(2 * math.pi * 180 * t)), n, 1)
        for k in range(40): noise_burst(t0 + 1.5 + k * .028, .008, 6000, 300, .05, .0005, 2000)
    elif i == 5:  # PC fan
        x = lp_noise(n, 900); put(t0, lambda t: x[int(t * SR) % n] * .18 + .015 * math.sin(2 * math.pi * 120 * t), n, 1)
    elif i == 6:  # kitchen, a bird outside
        x = lp_noise(n, 250); put(t0, lambda t: x[int(t * SR) % n] * .12, n, 1)
        for tb in (.3, .42, 2.0):
            put(t0 + tb, lambda t: math.sin(2 * math.pi * (3200 * t + 9000 * t * t)) * math.sin(math.pi * t / .07), int(.07 * SR), .025)


for i, s in enumerate(ERA_START):
    zero = i == 7
    dur = 5.45 if zero else 2.6
    a0 = max(0.0, s)
    ambience(i, a0, (s + dur) - a0)
    if i: noise_burst(s - .14, .14, 2500, -6, .05, .1)  # small swell into each cut
    thump(s + .08, 70, .45 if not zero else .2, 28)
    if zero:
        put(s, lambda t: .05 * math.sin(2 * math.pi * 55 * t) + .04 * math.sin(2 * math.pi * 82.6 * t) * (.7 + .3 * math.sin(t * 1.7)), int(dur * SR), 1)
        x = lp_noise(int(dur * SR), 1200); put(s, lambda t: x[int(t * SR)] * .08 * (1 - min(1, max(0, (t - 1.5) * 3))), len(x), 1)
        # the floating coffee: a wobbling bloop that rises as it nears the lens
        put(s + .4, lambda t: math.sin(2 * math.pi * (150 * t + 70 * t * t) + 3 * math.sin(2 * math.pi * 7 * t)) * min(1, t / .25) * (.3 + .5 * t / 1.1), int(1.1 * SR), .14)
        # splat on the lens
        thump(s + 1.5, 60, .9, 12); noise_burst(s + 1.5, .8, 2200, 7, .9, .003); noise_burst(s + 1.5, .3, 7000, 25, .35, .002, 2000)
        for k in range(5): plink(s + 1.7 + k * .17 + R.random() * .05, 700 + R.random() * 500, .06)
        modes(s + 2.3, [523.25, 659.25, 783.99, 1046.5], [.9, 1, 1.1, 1.4], .1, 2.5)  # end card chord
        continue
    m = MATS[i]
    for tt in (.1, .3, .45): tick(s + tt, RATTLE[m], .12)
    IMPACT[m](s + .72)
    splash(s + .74, 1.0)
    if i in (5, 6):  # sparks from the wet electronics
        for _ in range(30): noise_burst(s + (.95 if i == 5 else .92) + R.random() ** 1.5 * .45, .006, 12000, 600, .1 + R.random() * .2, .0003, 3000)

peak = max(abs(v) for v in buf) or 1
out = array.array('h', (int(max(-1, min(1, v / peak * .89)) * 32767) for v in buf))
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'sfx.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('wrote', DUR, 's')
