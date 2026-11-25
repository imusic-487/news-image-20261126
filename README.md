[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/c/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/imusic-487/news-image-20261126/rank.svg)](https://make.fun/c/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/imusic-487/news-image-20261126/reward.svg)](https://make.fun/c/news-image-20261126)

# The World in One Day — Thursday 26 November 2026

One image summing up 26 November 2026 world news, drawn by `main.py`
(Python 3.13 standard library only, no network, fully deterministic:
two runs write byte-identical PNGs).

## The image

- **Masthead** — Thursday 26 November 2026, 50 stories from every continent.
- **UTC timeline** — the day's beats: Hong Kong fire anniversary, Delhi
  Constitution Day, Nepal talks, the Macy's parade, Chess Game 3,
  Canada's aid plan, the storm peak.
- **Schematic world map** — 12 numbered locations, keyed below the map.
- **Four information graphics** — US tariffs bar chart, chess scoreboard,
  Thanksgiving travel numbers, Bangladesh garment wage.
- **16 lead stories + 34 more (50 total)**, each with a named source.
- **DATE CHECK box** — what counts as 26 November, what was reported on
  26 November but happened on 25 November (marked `*`), and the
  earlier-date traps that do not count (ICJ Myanmar ruling 19 Nov,
  COP31 collapse 22 Nov, EU sanctions 23 Nov, Shenzhen summit 19 Nov).
- **Grading** — CONFIRMED means two or more sources or an official
  source; CLAIM means a single source or an announcement only.

## Lead stories (verified 26 Nov 2026)

- US Thanksgiving nor'easter peaks: rain, 50–60 mph gusts, moderate–major
  coastal flooding Georgia to Long Island; 100th Macy's parade dry at the
  8:30am start (Reuters, CNN, weather.com).
- Record Thanksgiving travel: FAA busiest in 16 years, 417,000+ flights
  over 9 days; AAA 81.5M travellers.
- India Constitution Day; IITs to add 6,000 seats in robotics, AI and
  space tech from 2027.
- World Chess Championship, Geneva: Game 3 today, Sindarov–Gukesh level
  1–1 after two draws; $2.5M prize fund, 14 games (FIDE).
- Hong Kong marks one year since the Wang Fuk Court fire (168 killed,
  Nov 2025) — anniversary, not a new fire.
- Canada: PM Carney about to announce steel and lumber aid (CBC).
- Reported 26 Nov, happened 25 Nov: US Section 301 tariffs (+20% China,
  15% cap allies), Shenzhou-24 docking with the first Pakistani in orbit,
  Bangladesh garment wage +36%, Cartagena siege rescue, North Korea
  ordering the Swiss office shut, Sooryavanshi's 204 off 53 balls,
  Champions League results.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png — 1024x1024 PNG, under 1 MiB
```

## License

MIT — see [LICENSE](LICENSE).
