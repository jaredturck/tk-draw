from PIL import Image
from potrace import Bitmap

class ImageTracer:
    def __init__(self):
        self.quality_presets = {
            0.1: ( 8, 260, 40, 1.20, 0.70, 0.30, 1),
            0.2: (12, 220, 32, 1.13, 0.64, 0.35, 1),
            0.3: (16, 180, 24, 1.07, 0.58, 0.45, 2),
            0.4: (24, 140, 18, 1.00, 0.52, 0.55, 2),
            0.5: (32, 100, 14, 0.93, 0.46, 0.65, 3),
            0.6: (40,  80, 10, 0.87, 0.39, 0.75, 3),
            0.7: (48,  60,  8, 0.80, 0.33, 0.85, 3),
            0.8: (64,  45,  6, 0.73, 0.27, 0.90, 4),
            0.9: (80,  35,  4, 0.67, 0.21, 0.95, 4),
            1.0: (96,  25,  2, 0.60, 0.15, 1.00, 4),
        }
        self.opticurve = True
        self.configure_quality(0.5)

    def configure_quality(self, level):
        ''' Configure tracing parameters based on quality level '''
        n_colors, min_pixels, turdsize, alphamax, opttolerance, downscale, decimals = self.quality_presets[level]
        self.n_colors = n_colors
        self.min_pixels = min_pixels
        self.turdsize = turdsize
        self.alphamax = alphamax
        self.opttolerance = opttolerance
        self.downscale = downscale
        self.decimals = decimals
    
    def rv(self, v):
        ''' Round the value to the specified number of decimals '''
        v = round(v, self.decimals)
        if v % 1 == 0:
            return str(int(v))
        return str(v)

    def trace_image(self, mask):
        ''' Trace the bitmap image and return a list of paths '''
        bm = Bitmap(mask, blacklevel=0.5)
        return bm.trace(turdsize=self.turdsize, alphamax=self.alphamax, opticurve=self.opticurve, opttolerance=self.opttolerance)

    def mask_for_index(self, idx, indices, w, h):
        ''' Create a binary mask for the given palette index '''
        mask_data = [0 if p == idx else 255 for p in indices]
        mask = Image.new('L', (w, h), 255)
        mask.putdata(mask_data)
        return mask

    def build_svg(self, plist, fill):
        ''' Build SVG path elements from the traced paths '''
        svg_paths = []
        for curve in plist:
            parts = []
            fs = curve.start_point
            parts.append(f"M{self.rv(fs.x)},{self.rv(fs.y)}")
            for segment in curve.segments:
                if segment.is_corner:
                    a = segment.c
                    bpt = segment.end_point
                    parts.append(f"L{self.rv(a.x)},{self.rv(a.y)}L{self.rv(bpt.x)},{self.rv(bpt.y)}")
                else:
                    a = segment.c1
                    bpt = segment.c2
                    c = segment.end_point
                    parts.append(f"C{self.rv(a.x)},{self.rv(a.y)} {self.rv(bpt.x)},{self.rv(bpt.y)} {self.rv(c.x)},{self.rv(c.y)}")

            parts.append('Z')
            d = ''.join(parts)
            svg_paths.append(f"<path d='{d}' fill='{fill}' stroke='none'/>")
        
        return svg_paths

    def process_image(self, input_filename, output_filename, quality=0.5):
        ''' Process the input image and save the traced SVG output '''
        self.configure_quality(quality)
        img = Image.open(input_filename).convert('RGB')
        if self.downscale != 1.0:
            new_w = max(1, int(img.width * self.downscale))
            new_h = max(1, int(img.height * self.downscale))
            img = img.resize((new_w, new_h), Image.LANCZOS)

        q = img.convert('P', palette=Image.ADAPTIVE, colors=self.n_colors)
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
            fill = f'rgb({r},{g},{b})'

            mask = self.mask_for_index(idx, indices, w, h)
            plist = self.trace_image(mask)

            svg_paths.extend(self.build_svg(plist, fill))
        
        with open(output_filename, 'w') as file:
            file.write(f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>\n")
            for path in svg_paths:
                file.write(f'  {path}\n')
            file.write('</svg>\n')


if __name__ == '__main__':
    tracer = ImageTracer()
    tracer.process_image('examples/image_luning.png', 'examples/output.svg', quality=0.5)
