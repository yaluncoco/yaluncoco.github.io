from pathlib import Path
import json

wallpaper_dir = Path("/home/lsl/hugo/blog/static/images/wallpapers")

output = Path("/home/lsl/hugo/blog/static/wallpapers.json")

exts = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".JPG",
    ".JPEG",
    ".PNG",
}

files = sorted(
    f.name
    for f in wallpaper_dir.iterdir()
    if f.is_file() and f.suffix in exts
)

with output.open("w", encoding="utf-8") as f:
    json.dump(files, f, ensure_ascii=False, indent=2)

print(f"Generate {len(files)} wallpapers.")