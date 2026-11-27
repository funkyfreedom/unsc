# Sources

The build reads three open datasets from this folder. They aren't committed here because they belong to their authors and add up to about 250 MB. Download them like this, from the repository root:

```
cd sources

# 1. CR-UNSC corpus (Zenodo, CC0): download these three files from
#    https://doi.org/10.5281/zenodo.7319780 (version 2026-08-19)
#      CR-UNSC_2026-08-19_EN_TXT_BEST.zip
#      CR-UNSC_2026-08-19_ALL_CSV_META.zip
#      CR-UNSC_2026-08-19_CITATIONS_GRAPHML.zip
#    and unzip them into sources/cr-unsc/
mkdir cr-unsc && cd cr-unsc
for f in ../CR-UNSC_*.zip; do unzip -q "$f" -d "$(basename "$f" .zip)"; done
cd ..

# 2. UN machine-readable resolutions (United Nations)
git clone https://github.com/UNxml/SCresolutions.git

# 3. Sciences Po UNSC votes since 1946 (CC BY 4.0)
git clone https://github.com/AtelierCartographie/bd-unsc.git
```

You should end up with:

```
sources/
  cr-unsc/       the three unzipped CR-UNSC folders (the scripts search inside for the files)
  SCresolutions/ UNxml clone, with data_extract/ and one folder per year
  bd-unsc/       Sciences Po clone, with src/lib/data/*.csv
```

The site at securitycouncilrecord.org was built from CR-UNSC version 2026-08-19, SCresolutions at commit `8a657d0` (23 November 2026) and bd-unsc at commit `a7e64be` (19 June 2026). Newer versions should work; the counts will change as new resolutions are added.

To keep the sources somewhere else, set `SCR_SOURCES=/path/to/folder` before running the build.

The share image needs the Inter font as .otf files. On Debian or Ubuntu, `apt install fonts-inter` puts them where the build looks. Elsewhere, set `SCR_INTER_OTF` to the folder that holds them.
