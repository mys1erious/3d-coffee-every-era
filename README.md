# Spilling coffee on your work, in every era of human history

The same cup goes over eight times, from ochre hand stencils on a cave stone (30,000 BC) to a zero-gravity station (2400), and each era loses something: a beer ration ledger, eleven months of calligraphy, 2,000 FORTRAN cards in order, everything since the last commit. One three.js page (three@0.170.0 from jsdelivr): every prop, texture and the coffee itself (cup tipping, splash droplets, a translucent puddle with a meniscus) are made in code; no image or video model. The narrator is ElevenLabs ("Daniel"), the sound effects are synthesised in `sfx.py`.

Answers [Kevin Drops the Chili in Every Era of Human History](https://x.com/GORMTHEOLD25/status/2117283464718463078) by @GORMTHEOLD25.

Open: `python3 -m http.server` in this folder, then `/index.html`. Tap the desk to knock the cup, tap again for the next era, or use the arrows and "Play all". `?play` self-plays all eras, `?clean` hides the UI, `?t=<s>` freezes the play timeline at a moment.

Re-record (local server running): `node ../../../x-trend-ideas/_tools/record.mjs "http://127.0.0.1:<port>/<path>/?clean&play" silent.mp4 --seconds 23.15 --fps 30 --w 1080 --h 1350 --warmup 2.5`, then `sh mix.sh silent.mp4 video/coffee-every-era.mp4` adds the SFX and the narrator lines in `vo/` and normalises to -14 LUFS.
