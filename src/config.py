"""Paths used by every script. Everything is relative to the repository root.

Put the source datasets in sources/ as described in sources/README.md.
"""
import os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.environ.get('SCR_SOURCES', os.path.join(ROOT, 'sources'))
BUILD = os.path.join(ROOT, 'build')        # intermediate files (not committed)
DIST = os.path.join(ROOT, 'dist')          # the finished site
DATA = os.path.join(ROOT, 'data')          # open data tables (committed)
SRC = os.path.join(ROOT, 'src')

CR_UNSC = os.path.join(SOURCES, 'cr-unsc')                 # unzipped CR-UNSC files
UN_XML = os.path.join(SOURCES, 'SCresolutions')            # git clone of UNxml/SCresolutions
SCIENCES_PO = os.path.join(SOURCES, 'bd-unsc')             # git clone of AtelierCartographie/bd-unsc
FONTS_WOFF = os.path.join(ROOT, 'node_modules', '@fontsource-variable', 'inter', 'files')
INTER_OTF = os.environ.get('SCR_INTER_OTF', '/usr/share/fonts/opentype/inter')  # Inter .otf files, for the share image

def one(pattern):
    hits = sorted(glob.glob(pattern, recursive=True))
    if not hits:
        raise SystemExit(f'Missing source file: {pattern}\nSee sources/README.md')
    return hits[0]

CR_META = lambda: one(os.path.join(CR_UNSC, '**', '*ALL_CSV_META*.csv'))
CR_GRAPHML = lambda: one(os.path.join(CR_UNSC, '**', '*.graphml'))
CR_TEXT_DIR = lambda: os.path.dirname(one(os.path.join(CR_UNSC, '**', 'S_RES_0001_1946_EN*.txt')))
SCIENCES_PO_CSV = lambda: one(os.path.join(SCIENCES_PO, 'src', 'lib', 'data', '*.csv'))
