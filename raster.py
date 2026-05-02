import argparse
from PIL import Image
import numpy as np
import yaml
import typing

def handle_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--textgrid", required=True)
    ap.add_argument("--colormap", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--block", required=False, default=1, type=int)
    ap.add_argument("--reverse", action="store_true", default=False)
    return ap.parse_args()

def reverse_dict(d: dict[str, int]) -> dict[int, str]:
    result = {}
    for k, v in d.items():
        result[v] = k
    return result

def raster(colormap: dict[int, str], textgrid: list[str], block_size: int, fi: typing.IO) -> None:
    width = len(textgrid[0]) * block_size
    height = len(textgrid) * block_size
    img = Image.new("RGBA", (width, height))
    for r in range(len(textgrid)):
        row = textgrid[r]
        for c in range(len(row)):
            char = row[c]
            color = colormap[char]
            R = (color & 0xFF0000) >> (2 * 8)
            G = (color & 0x00FF00) >> (1 * 8)
            B = (color & 0x0000FF) >> (0 * 8)
            A = 0xFF
            bands = (R, G, B, A)
            for x in range(block_size):
                for y in range(block_size):
                    pos = (c * block_size + x, r * block_size + y)
                    img.putpixel(pos, bands)
    img.save(fi, format="bmp")

def unraster(mapcolor: dict[str, int], image_path: str) -> list[str]:
    result = []
    with Image.open(image_path) as img:
        w, h = img.size
        for r in range(h):
            row = ""
            for c in range(w):
                # TODO: what about alpha channel?
                R, G, B = img.getpixel((c, r))
                color = 0
                color |= R << (2 * 8)
                color |= G << (1 * 8)
                color |= B << (0 * 8)
                char = mapcolor[color]
                row += char
            result.append(row)
    return result

def main() -> None:
    args = handle_args()

    with open(args.colormap, mode="r") as f:
        colormap = yaml.safe_load(f)

    if not args.reverse:
        textgrid: list[str] = []
        with open(args.textgrid, mode="r") as f:
            for line in f.readlines():
                stripped = line.strip()
                if len(stripped) > 0:
                    textgrid.append(stripped)

        with open(args.image, mode="wb") as f:
            raster(colormap, textgrid, args.block, f)
    else:
        textgrid = unraster(reverse_dict(colormap), args.image)
        with open(args.textgrid, mode="w") as f:
            f.write("\n".join(textgrid))

if __name__ == "__main__":
    main()
