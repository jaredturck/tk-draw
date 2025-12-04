from PIL import Image
from potrace import Bitmap

class ImageTracer:
    def __init__(self):
        self.n_colors = 16
        self.min_pixels = 10

    def trace_image(self, mask):
        bm = Bitmap(mask, blacklevel=0.5)
        return bm.trace()
        
    def mask_for_index(self, idx, indices, w, h):
        mask_data = [0 if p == idx else 255 for p in indices]
        mask = Image.new("L", (w, h), 255)
        mask.putdata(mask_data)
        return mask
    
    def build_svg(self, plist, fill):
        svg_paths = []
        for curve in plist:
            parts = []
            fs = curve.start_point
            parts.append(f"M{fs.x},{fs.y}")
            for segment in curve.segments:
                if segment.is_corner:
                    a = segment.c
                    bpt = segment.end_point
                    parts.append(f"L{a.x},{a.y}L{bpt.x},{bpt.y}")
                else:
                    a = segment.c1
                    bpt = segment.c2
                    c = segment.end_point
                    parts.append(f"C{a.x},{a.y} {bpt.x},{bpt.y} {c.x},{c.y}")
            
            parts.append("Z")
            d = "".join(parts)
            svg_paths.append(f'<path d="{d}" fill="{fill}" stroke="none"/>')
        
        return svg_paths

    def preprocess_image(self, input_filename, output_filename):
        img = Image.open(input_filename).convert("RGB")
        q = img.convert("P", palette=Image.ADAPTIVE, colors=self.n_colors)
        w, h = q.size

        palette = q.getpalette()
        index_to_rgb = {}
        for i in range(self.n_colors):
            r, g, b = palette[3*i:3*i+3]
            index_to_rgb[i] = (r, g, b)
        
        indices = list(q.getdata())
        used_indices = sorted(set(indices))
        svg_paths = []

        for idx in used_indices:
            if indices.count(idx) < self.min_pixels:
                continue

            r, g, b = index_to_rgb[idx]
            fill = f"rgb({r},{g},{b})"

            mask = self.mask_for_index(idx, indices, w, h)
            plist = self.trace_image(mask)

            svg_paths.extend(self.build_svg(plist, fill))
        
        with open(output_filename, 'w') as file:
            file.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n')
            for path in svg_paths:
                file.write(f'  {path}\n')
            file.write('</svg>\n')

if __name__ == "__main__":
    tracer = ImageTracer()
    tracer.preprocess_image("examples/image_luning.png", 'examples/output.svg')
