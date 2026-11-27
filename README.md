# Security Council Record

**80 years of the UN Security Council, counted from the documents.**

[securitycouncilrecord.org](https://securitycouncilrecord.org) reads all 2,835 resolutions the Security Council adopted from 1946 to 2026, every recorded vote and all 270 vetoes, and shows what they add up to: patterns in themes, voting and language across eight political eras.

This repository holds the code that builds the site, the open data tables behind it, and a script that recounts every figure from the raw sources.

## What the data shows

1. **The Council went from recommending to ordering.** "Decides" appears in 20% of resolutions in the founding era and 96% since 2022. "Acting under Chapter VII" went from about 1% of resolutions before 1988 to 50%.
2. **The vocabulary of war changed.** "Aggression" peaked in 1975 to 1987, mostly about South Africa, then all but disappeared. "Breach of the peace" was found for only four wars, the last in 1990. "Threat to the peace" became the routine trigger: 2% of resolutions in the founding era, 55% today.
3. **The veto map flipped twice.** The USSR cast most vetoes until 1960, the United States from the 1970s to the 1990s, Russia and China since 2011.
4. **Unity rose and is now falling.** Unanimous adoption climbed from 39% in the founding years to 93% in 2001 to 2010, then fell to 61% in 2025. On contested votes the US and Russia now agree 8% of the time, against 57% around 1990.
5. **From wars between states to wars inside them.** Civilians, women, children and sexual violence were almost absent before 1999. Women now appear in 59% of resolutions and civilians in 38%.
6. **Africa took over the agenda.** It went from 0% of resolutions in the founding era to 52% in 2011 to 2021.

Each finding has its own page on the site with the charts and the resolutions behind it.

## The data

The [`data/`](data/) folder has six CSV files, also downloadable from the site's [About page](https://securitycouncilrecord.org/about/#download-the-data):

| File | Rows | What's in it |
|---|---|---|
| `resolutions.csv` | 2,835 | One row per resolution: date, era, subject, region, vote counts, Charter terms, themes, citations |
| `votes.csv` | 46,393 | Every member's vote on every recorded draft since 1946, adopted, vetoed or failed |
| `drafts.csv` | 393 | Drafts that were vetoed (270) or didn't get enough votes (123) |
| `citations.csv` | 16,197 | Which resolution cites which |
| `eras.csv` | 8 | The figures for each era shown on the site |
| `countries.csv` | 136 | Every country that has sat on the Council, with its voting record |

Every column is explained in [`data/README.md`](data/README.md).

## Rebuild it yourself

You need Python 3.10 or later with Pillow, and Node.js 18 or later.

```
git clone https://github.com/funkyfreedom/unsc.git
cd unsc
npm install
pip install pillow
```

Download the three sources into `sources/` as described in [`sources/README.md`](sources/README.md). Then:

```
npm run build     # merge the sources, write the pages, build search, export the CSVs
npm run verify    # recount every figure from the raw files and compare with the pages
```

The site lands in `dist/`. Serve it with any static host, or locally with `python3 -m http.server --directory dist`.

`npm run verify` should report 52 checks passed and 0 failed. It also lists one known gap in a source: the Sciences Po vote file has no row for resolution 2760 (2024, adopted unanimously), so the site shows 2024 as 65% unanimous where the full year is 67%. Security Council Report gives 65.2%.

### How the code is laid out

- `src/config.py`: every path, relative to the repository
- `src/prep.py`: reads the three sources and merges them into `build/data.json`
- `src/build.py` and `src/lib.py`: write every page, chart and table into `dist/`
- `src/search.js`: Super search, with filters for era, region, theme, Charter wording, vote and country, on top of [Pagefind](https://pagefind.app)
- `src/lab.js`: the Language lab, which charts any word's share of resolutions year by year
- `src/export.py`: writes the CSV files to `data/` and `dist/data/`
- `src/share.py` and `src/icons.py`: the social share image, favicons and logo
- `src/verify.py`: the independent check

`dist/` is committed so Cloudflare Pages can serve it without a build step (build command empty, output directory `dist`).

## Sources and credits

- **Corpus of Resolutions: UN Security Council (CR-UNSC)**, Seán Fobbe, Lorenzo Gasbarri and Niccolò Ridi, version 2026-08-19, CC0. [doi:10.5281/zenodo.7319780](https://doi.org/10.5281/zenodo.7319780). Texts, metadata and citation network of resolutions 1 to 2815.
- **UNSC votes since 1946 database**, Benoît Martin, Sciences Po Atelier de cartographie and GRAM, 2026, CC BY 4.0. [github.com/AtelierCartographie/bd-unsc](https://github.com/AtelierCartographie/bd-unsc). Every recorded vote, including vetoed and failed drafts.
- **Machine-readable Security Council resolutions** (AKN4UN XML), United Nations. [github.com/UNxml/SCresolutions](https://github.com/UNxml/SCresolutions). Texts and metadata of resolutions adopted after January 2026. The United Nations is the source of this information.

The resolution texts are the UN's own words, reproduced as published. None has been summarised or rewritten by AI.

## Reuse it

- The analysis, charts, text and data tables: [CC BY 4.0](LICENSE-DATA.md)
- The code: [MIT](LICENSE)

Just quote us: *Security Council Record (securitycouncilrecord.org), Daniel D'Esposito, 2026*. The sources keep their own licences, so please credit them too. [`CITATION.cff`](CITATION.cff) has the details in a format GitHub and reference managers can read.

Spotted a mistake? [Open an issue](https://github.com/funkyfreedom/unsc/issues) or write to daniel.desposito@gmail.com.

Made by [Daniel D'Esposito](https://www.linkedin.com/in/ddesposito) with Claude, Anthropic's AI. An independent project, not affiliated with or endorsed by the United Nations.
