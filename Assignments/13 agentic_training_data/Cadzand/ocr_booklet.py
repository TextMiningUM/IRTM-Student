import winocr
from PIL import Image
import os

png_dir = os.path.join(os.path.dirname(__file__), 'pngs')
out_file = os.path.join(os.path.dirname(__file__), 'cadzand_booklet.txt')

pngs = sorted([f for f in os.listdir(png_dir) if f.lower().endswith('.png')])
all_text = []
for fname in pngs:
    path = os.path.join(png_dir, fname)
    print(f'OCR: {fname}')
    img = Image.open(path)
    result = winocr.recognize_pil_sync(img, 'en')
    text = result['text'] if result else ''
    all_text.append(f'--- {fname} ---\n{text}\n')
with open(out_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_text))
print(f'Written to {out_file}')
