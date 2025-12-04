from PIL import Image
from potrace import Bitmap

class ImageTracer:
    def __init__(self):
        self.quality_presets = {
            0.1: (3,  250, 40, 1.20, 0.70, 0.30),
            0.2: (4,  200, 32, 1.13, 0.64, 0.35),
            0.3: (6,  150, 24, 1.07, 0.58, 0.45),
            0.4: (8,  100, 18, 1.00, 0.52, 0.55),
            0.5: (12,  70, 14, 0.93, 0.46, 0.65),
            0.6: (16,  50, 10, 0.87, 0.39, 0.75),
            0.7: (20,  35,  8, 0.80, 0.33, 0.85),
            0.8: (24,  25,  6, 0.73, 0.27, 0.90),
            0.9: (28,  15,  4, 0.67, 0.21, 0.95),
            1.0: (32,   8,  2, 0.60, 0.15, 1.00),
        }
        self.opticurve = True
        self.configure_quality(0.5)

    def configure_quality(self, level):
        ''' Configure tracing parameters based on quality level '''
        n_colors, min_pixels, turdsize, alphamax, opttolerance, downscale = self.quality_presets[level]
        self.n_colors = n_colors
        self.min_pixels = min_pixels
        self.turdsize = turdsize
        self.alphamax = alphamax
        self.opttolerance = opttolerance
        self.downscale = downscale

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
            parts.append(f'M{fs.x},{fs.y}')
            for segment in curve.segments:
                if segment.is_corner:
                    a = segment.c
                    bpt = segment.end_point
                    parts.append(f'L{a.x},{a.y}L{bpt.x},{bpt.y}')
                else:
                    a = segment.c1
                    bpt = segment.c2
                    c = segment.end_point
                    parts.append(f'C{a.x},{a.y} {bpt.x},{bpt.y} {c.x},{c.y}')
            
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
    tracer.process_image('examples/image_luning.png', 'examples/output.svg', quality=0.2)
