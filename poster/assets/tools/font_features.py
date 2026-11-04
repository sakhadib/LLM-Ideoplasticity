"""Report OpenType features and glyph coverage of the poster fonts."""
import sys

from fontTools.ttLib import TTFont

sys.stdout.reconfigure(encoding='utf-8')
CHECK = '→≈×∼≤≥∈⟨⟩†∗−–—⊂ℝℙ‖·αβγ⟶°±∞√…’“”é à'
for p in sys.argv[1:]:
    f = TTFont(p, lazy=True)
    feats = set()
    if 'GSUB' in f and f['GSUB'].table.FeatureList:
        feats |= {r.FeatureTag for r in f['GSUB'].table.FeatureList.FeatureRecord}
    cmap = f.getBestCmap()
    missing = [c for c in CHECK if c != ' ' and ord(c) not in cmap]
    want = ['smcp', 'c2sc', 'tnum', 'pnum', 'lnum', 'onum', 'liga', 'calt', 'frac', 'ss01', 'zero']
    print(p.replace('\\', '/').split('/')[-1], '| kinds', 'CFF' if 'CFF ' in f else 'TrueType', '| features:', ' '.join(w for w in want if w in feats), '| glyphs', len(f.getGlyphOrder()), '| missing:', ''.join(missing))
