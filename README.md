# Security Council Record

An independent record of every UN Security Council resolution, vote and veto since 1946: securitycouncilrecord.org

- `dist/` is the finished static site (HTML, assets and the Pagefind search index). Cloudflare Pages serves it as is.
- `src/` holds the generator: `prep.py` merges the sources into one dataset, `build.py` and `lib.py` write the pages and charts, `search.js` and `lab.js` run Super search and the Language lab, `share.py` draws the share image and `icons.py` the favicons and logo. Order: `prep.py`, `build.py`, `npx pagefind --site dist`, `share.py`, `icons.py`.

## Cloudflare Pages settings

- Framework preset: None
- Build command: (leave empty)
- Build output directory: `dist`

## Sources

- CR-UNSC corpus, Fobbe, Gasbarri and Ridi, version 2026-08-19, CC0 (doi:10.5281/zenodo.7319780)
- UN machine-readable Security Council resolutions (github.com/UNxml/SCresolutions)
- UNSC votes since 1946 database, Benoît Martin, Sciences Po Atelier de cartographie and GRAM, 2026, CC BY 4.0

Not affiliated with or endorsed by the United Nations. Site, data and code in the public domain.
