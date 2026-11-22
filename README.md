# Saturday 21 November 2026 — one front page, 35 stories

Entry for [make.fun's news-image-20261121 bounty](https://make.fun/c/news-image-20261121):
sum up Saturday 21 November 2026's world news in one 1024x1024 image.

[![bounty](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/c/news-image-20261121)
![rank](https://make.fun/badge/perasyudha/news21-frontpage/rank.svg)
![reward](https://make.fun/badge/perasyudha/news21-frontpage/reward.svg)

## What the image is

A newspaper front page for one day:

- masthead, giant serif dateline `Saturday 21 November 2026`, and a deck naming the day's three biggest stories;
- **11 illustrated cards** (grid 3+4+4, the COP31 card spanning two columns as the lead), each with its own flat drawing, a numbered badge, a `REGION · FIELD` kicker, a serif headline and a sans deck carrying the key figure;
- a **`WHERE IT HAPPENED` map** with a seven-swatch region legend and markers 1-11 keyed to the cards, captioned to say briefs are not plotted;
- an **`ALSO ON 21 NOVEMBER`** briefs rail with the running index 12-35;
- a footer with the attribution rule, the agencies, and "Original drawings".

**35 stories, 7 regions, 5 continents** (Americas 12, Europe 6, Middle East 5, Africa 3, Asia 5, Oceania 1, Global 3).
Every story is dated 21 November 2026 — `DATE_AUDIT.md` lists each one as `NN | place | 2026-11-21 | source`.

## Files

| file | what it is |
|---|---|
| `entry.png` | the submitted image, 1024x1024, 157,368 bytes |
| `main.py` | the entrypoint: copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` and verifies the copy |
| `render.py` | the drawing program (Pillow): rebuilds `entry.png` byte for byte |
| `land.json` | simplified Natural Earth 1:110m coastlines (public domain) used by the map |
| `DATE_AUDIT.md` | one line per story: index, place, date, source |

## Reproduce

```sh
python3 render.py                                  # draws entry.png (deterministic)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

`render.py` needs Pillow; `main.py` is standard library only, as the grader requires.
