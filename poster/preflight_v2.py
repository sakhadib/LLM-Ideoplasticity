"""Print/export preflight for the two final v2 PDFs."""
from pathlib import Path
import json
import io
import sys

import numpy as np
import pymupdf
from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
sys.path.append(str(Path.home() / 'AppData/Local/Temp/claude/c--Users-rifat-Desktop-GitHub-LLM-Ideoplasticity/e7e551d2-b5db-4696-b913-c2aad2b77245/scratchpad/pylibs'))
import zxingcpp

FILES = [ROOT / 'LLM-Ideoplasticity_Poster_A0_v2.pdf', ROOT / 'LLM-Ideoplasticity_Poster_A0_v2_flattened.pdf']
EXPECTED_URL = 'https://sakhadib.github.io/LLM-Ideoplasticity/'
report = {'files': [], 'checks': []}
renders = []
for index, path in enumerate(FILES):
    doc = pymupdf.open(path)
    assert len(doc) == 1
    page = doc[0]
    assert abs(page.rect.width - 841 * 72 / 25.4) < .5
    assert abs(page.rect.height - 1189 * 72 / 25.4) < .5
    assert path.stat().st_size < 20_000_000
    assert not list(page.widgets() or [])
    fonts = page.get_fonts(full=True)
    assert all(f[2] != 'Type3' for f in fonts)
    assert all(len(doc.extract_font(f[0])[3]) > 0 for f in fonts)
    reader = PdfReader(path)
    assert not reader.get_fields()
    if index == 1:
        assert len(page.get_images()) == 1
        assert not page.get_text().strip()
        assert not page.get_links()
        assert not fonts
    qr = []
    for dpi in (72, 200):
        clip = pymupdf.Rect(725, 5, 826, 116) * (72 / 25.4)
        pix = page.get_pixmap(dpi=dpi, clip=clip, alpha=False)
        arr = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
        decoded = [x.text for x in zxingcpp.read_barcodes(arr)]
        assert EXPECTED_URL in decoded, (path.name, dpi, decoded)
        qr.append({'dpi': dpi, 'decoded': EXPECTED_URL})
    pix = page.get_pixmap(dpi=60, alpha=False)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).resize((1682, 2378), Image.Resampling.LANCZOS)
    renders.append(np.asarray(im).astype(np.int16))
    if index == 1:
        im.save(ROOT / 'build_v2' / 'flattened_preview.png')
    report['files'].append({'name': path.name, 'bytes': path.stat().st_size,
                            'page_size_pt': [page.rect.width, page.rect.height],
                            'embedded_fonts': len(fonts), 'images': len(page.get_images()), 'qr': qr})
# Compare at the flattening resolution. Comparing a 60 dpi vector raster with
# a resampled 240 dpi image confounds JPEG fidelity with font antialiasing.
with pymupdf.open(FILES[0]) as source:
    pix = source[0].get_pixmap(dpi=240, alpha=False)
    shape = (pix.height, pix.width, 3)
    sample_source = np.frombuffer(pix.samples, np.uint8).reshape(shape)[::4, ::4].copy()
    del pix
with pymupdf.open(FILES[1]) as flat:
    data = flat.extract_image(flat[0].get_images()[0][0])['image']
    with Image.open(io.BytesIO(data)) as jpeg:
        assert (jpeg.height, jpeg.width, 3) == shape
        sample_flat = np.asarray(jpeg.convert('RGB'))[::4, ::4].copy()
diff = np.abs(sample_source.astype(np.int16) - sample_flat.astype(np.int16))
mae = float(diff.mean())
large_difference = float((diff.max(axis=2) > 35).mean())
assert mae < 2, mae
assert large_difference < .015, large_difference
report['checks'] = ['one A0 portrait page each', 'both below 20 MB', 'fonts embedded in regular PDF',
                    'flattened PDF has a single image and no text, forms or links',
                    'both QR codes decode at 72 and 200 dpi', 'regular and flattened render comparison passes']
report['render_comparison'] = {'native_dpi': 240, 'sample_stride': 4,
                              'mean_absolute_rgb_difference_255': mae, 'fraction_pixels_difference_over_35': large_difference}
report['status'] = 'PASS'
(ROOT / 'build_v2' / 'print_preflight.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
