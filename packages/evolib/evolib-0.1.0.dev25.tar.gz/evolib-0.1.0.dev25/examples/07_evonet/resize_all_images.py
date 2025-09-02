from pathlib import Path
from PIL import Image

# Zielgröße (muss zu deiner ffmpeg-Auflösung passen)
TARGET_SIZE = (640, 480)
INPUT_GLOB = "gen_*.png"
OUTPUT_DIR = Path("03_frames_resized")
OUTPUT_DIR.mkdir(exist_ok=True)

# PNGs finden
input_files = sorted(Path("03_frames").glob(INPUT_GLOB))

for path in input_files:
    img = Image.open(path).convert("RGBA")

    # Bild skalieren und mittig einpassen
    img.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)

    # Neues weißes Canvas
    canvas = Image.new("RGBA", TARGET_SIZE, (255, 255, 255, 255))
    offset = ((TARGET_SIZE[0] - img.width) // 2, (TARGET_SIZE[1] - img.height) // 2)
    canvas.paste(img, offset)

    # Speichern unter gleichem Namen
    out_path = OUTPUT_DIR / path.name
    canvas.save(out_path)

print(f"Alle Bilder auf {TARGET_SIZE} skaliert → {OUTPUT_DIR}/")
