import pygame, sys, time, math
import tkinter as tk
from tkinter import filedialog

class DrawApp:
    def __init__(self):
        pygame.init()
        self.window_size = (800, 600)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Drawing Window')
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        self.clicks = []
        self.shapes = []
        self.selection_points = []
        self.line_width = 5

        self.color = (0, 0, 0)
        self.canvas_color = (255, 255, 255)
        self.fill_color = None
        self.color_mode = 'border'
        self.show_border = True
        self.selected_shape = 'triangle'

        self.last_click = time.time()
        self.zoom_level = 1

        self.grid_spacing = 10
        self.grid_offset_x = 0.0
        self.grid_offset_y = 0.0

        self.palette_height = 20
        self.palette_width = self.window_size[0] - 10
        self.palette_size = (self.palette_width, self.palette_height)

        self.palette_surface = pygame.Surface(self.palette_size)
        self.palette_rect = self.palette_surface.get_rect()
        self.palette_rect.midbottom = (self.window_size[0] // 2, self.window_size[1] - 5)

        self.current_hue = 0.0
        self.palette_cursor_x = None
        self.show_grid = False

        self.build_palette()

        self.sv_size = (100, 100)
        self.sv_surface = pygame.Surface(self.sv_size)
        self.sv_rect = self.sv_surface.get_rect()
        self.sv_rect.bottomright = (self.window_size[0] - 200, self.window_size[1] - 40)
        self.sv_cursor_pos = None
        self.build_sv_box()

        self.grid_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.border_label_rect = pygame.Rect(0, 0, 0, 0)
        self.background_label_rect = pygame.Rect(0, 0, 0, 0)
        self.border_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.canvas_label_rect = pygame.Rect(0, 0, 0, 0)
        self.export_label_rect = pygame.Rect(0, 0, 0, 0)

    def build_palette(self):
        ''' Create a horizontal color palette surface (hue bar). '''
        w, h = self.palette_size
        for x in range(w):
            hue = (x / (w - 1)) * 360.0
            sat = 100.0
            val = 100.0
            c = pygame.Color(0, 0, 0)
            c.hsva = (hue, sat, val, 100)
            for y in range(h):
                self.palette_surface.set_at((x, y), c)

    def build_sv_box(self):
        ''' Build the 2D saturation/value box for the current hue. '''
        w, h = self.sv_size
        for x in range(w):
            sat = (x / (w - 1)) * 100.0
            for y in range(h):
                val = 100.0 - (y / (h - 1)) * 100.0
                c = pygame.Color(0, 0, 0)
                c.hsva = (self.current_hue, sat, val, 100)
                self.sv_surface.set_at((x, y), c)

    def handle_draw_shape(self, event):
        '''Record clicks and add a shape to the stack when enough points are collected. '''
        x, y = event.pos
        self.clicks.append((x, y))
        self.selection_points.append((x, y))
        self.last_click = time.time()

        # triangle
        if self.selected_shape == 'triangle' and len(self.clicks) == 3:
            shape = ['triangle', self.clicks, self.color, self.line_width, self.fill_color, self.show_border]
            self.shapes.append(shape)
            self.clicks = []
            self.selection_points = []

        # rectangle
        elif self.selected_shape == 'rectangle' and len(self.clicks) == 4:
            shape = ['rectangle', self.clicks, self.color, self.line_width, self.fill_color, self.show_border]
            self.shapes.append(shape)
            self.clicks = []
            self.selection_points = []
        
        # circle
        elif self.selected_shape == 'circle' and len(self.clicks) == 3:
            (x1, y1), (x2, y2), (x3, y3) = self.clicks

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            left  = min(x1, x2)
            right = max(x1, x2)
            half_height = abs(y3 - cy)
            top    = cy - half_height
            bottom = cy + half_height

            points = [
                (int(left),  int(top)),
                (int(right), int(top)),
                (int(right), int(bottom)),
                (int(left),  int(bottom)),
            ]

            shape = ['circle', points, self.color, self.line_width, self.fill_color, self.show_border]
            self.shapes.append(shape)
            self.clicks = []
            self.selection_points = []
    
    def draw_shapes(self):
        '''Draw all shapes (triangles, rectangles, ovals) and selection points.'''
        for shape in self.shapes:
            shape_type, points, border_color, line_width, fill_color, show_border = shape

            if shape_type == 'circle':
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                left, right = min(xs), max(xs)
                top, bottom = min(ys), max(ys)
                rect = pygame.Rect(left, top, right - left, bottom - top)

                if fill_color is not None:
                    pygame.draw.ellipse(self.screen, fill_color, rect, 0)
                if show_border:
                    pygame.draw.ellipse(self.screen, border_color, rect, line_width)

            else:
                if fill_color is not None:
                    pygame.draw.polygon(self.screen, fill_color, points, 0)
                if show_border:
                    pygame.draw.polygon(self.screen, border_color, points, line_width)

        for point in self.selection_points:
            pygame.draw.circle(self.screen, self.color, point, self.line_width)

        if time.time() - self.last_click > 3:
            self.selection_points = []
            self.clicks = []
        self.last_click = time.time()
    
    def draw_cursor(self):
        ''' Draw a circle at the mouse position to represent the cursor '''
        pygame.draw.circle(self.screen, self.color, pygame.mouse.get_pos(), self.line_width)
        pygame.mouse.set_visible(False)
    
    def draw_labels(self):
        ''' Draw labels for line width, border toggle, and color modes '''
        
        box_width = 172
        box_height = 130
        box_x = self.window_size[0] - box_width - 5
        box_y = self.window_size[1] - box_height - 35

        pygame.draw.rect(self.screen, (255, 255, 255), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height), 2)

        base_x = self.window_size[0] - 150 - 7

        lw_label = self.font.render(f'line width: {self.line_width}', True, (0, 0, 0))
        lw_rect = lw_label.get_rect()
        lw_rect.bottomleft = (base_x, self.window_size[1] - 40)
        self.screen.blit(lw_label, lw_rect)

        if self.show_grid:
            grid_text = 'grid: on'
        else:
            grid_text = 'grid: off'

        grid_label = self.font.render(grid_text, True, (0, 0, 0))
        grid_rect = grid_label.get_rect()
        grid_rect.bottomleft = (base_x, lw_rect.top - 5)
        self.screen.blit(grid_label, grid_rect)

        if self.show_border:
            toggle_text = 'border: on'
        else:
            toggle_text = 'border: off'

        toggle_label = self.font.render(toggle_text, True, (0, 0, 0))
        toggle_rect = toggle_label.get_rect()
        toggle_rect.bottomleft = (base_x, grid_rect.top - 5)
        self.screen.blit(toggle_label, toggle_rect)

        border_colour = self.color
        bg_colour = self.fill_color or (0, 0, 0)

        border_label = self.font.render('border colour', True, border_colour)
        border_rect = border_label.get_rect()
        border_rect.bottomleft = (base_x, toggle_rect.top - 5)
        self.screen.blit(border_label, border_rect)

        bg_label = self.font.render('background colour', True, bg_colour)
        bg_rect = bg_label.get_rect()
        bg_rect.bottomleft = (base_x, border_rect.top - 5)
        self.screen.blit(bg_label, bg_rect)

        canvas_label = self.font.render('canvas colour', True, (0, 0, 0))
        canvas_rect = canvas_label.get_rect()
        canvas_rect.bottomleft = (base_x, bg_rect.top - 5)
        self.screen.blit(canvas_label, canvas_rect)

        radius = 5
        if self.color_mode == 'border':
            circle_y = border_rect.centery
        elif self.color_mode == 'background':
            circle_y = bg_rect.centery
        else:
            circle_y = canvas_rect.centery

        circle_x = base_x - 2 * radius
        pygame.draw.circle(self.screen, (0, 0, 0), (circle_x, circle_y), radius)

        self.border_label_rect = border_rect
        self.background_label_rect = bg_rect
        self.border_toggle_rect = toggle_rect
        self.canvas_label_rect = canvas_rect
        self.grid_toggle_rect = grid_rect

    def draw_palette(self):
        ''' Draw the color palette (hue bar) at the bottom of the screen '''
        self.screen.blit(self.palette_surface, self.palette_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.palette_rect, 1)

        if self.palette_cursor_x is not None:
            x = self.palette_cursor_x
            y1 = self.palette_rect.top
            y2 = self.palette_rect.bottom
            pygame.draw.line(self.screen, (0, 0, 0), (x, y1), (x, y2), 2)

    def draw_sv_box(self):
        ''' Draw the saturation/value box. '''
        self.screen.blit(self.sv_surface, self.sv_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.sv_rect, 1)

        if self.sv_cursor_pos is not None:
            x, y = self.sv_cursor_pos
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 4, 1)
    
    def draw_grid_lines(self):
        ''' Draw gray grid lines that follow panning and zoom '''
        if not self.show_grid:
            return
        grid_color = (180, 180, 180)

        spacing = self.grid_spacing * self.zoom_level
        if spacing <= 0:
            return

        width, height = self.window_size

        first_x = (self.grid_offset_x % spacing) - spacing
        x = first_x
        while x < width:
            pygame.draw.line(self.screen, grid_color, (int(x), 0), (int(x), height), 1)
            x += spacing

        first_y = (self.grid_offset_y % spacing) - spacing
        y = first_y
        while y < height:
            pygame.draw.line(self.screen, grid_color, (0, int(y)), (width, int(y)), 1)
            y += spacing
    
    def draw_shape_labels(self):
        '''Draw small shape preview labels (triangle + rectangle + circle).'''
        box_margin = 5
        box_width = 35
        box_height = 35

        box_y = self.palette_rect.top - box_height - box_margin

        first_x = box_margin
        second_x = first_x + box_width + box_margin
        third_x = second_x + box_width + box_margin

        box_rects = [
            pygame.Rect(first_x,  box_y, box_width, box_height),
            pygame.Rect(second_x, box_y, box_width, box_height),
            pygame.Rect(third_x,  box_y, box_width, box_height),
        ]

        for i, box_rect in enumerate(box_rects):
            if i == 0 and self.selected_shape == 'triangle':
                bg_color = (220, 220, 220)
            elif i == 1 and self.selected_shape == 'rectangle':
                bg_color = (220, 220, 220)
            elif i == 2 and self.selected_shape == 'circle':
                bg_color = (220, 220, 220)
            else:
                bg_color = (255, 255, 255)

            pygame.draw.rect(self.screen, bg_color, box_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), box_rect, 1)

        border_color = self.color
        fill_color = self.fill_color

        center_x = box_rects[0].centerx
        base_y = box_rects[0].bottom - 10
        half_base = 20 / math.sqrt(3)

        p1 = (int(center_x - half_base), int(base_y))
        p2 = (int(center_x + half_base), int(base_y))
        p3 = (int(center_x), int(base_y - 20))

        tri_points = [p1, p2, p3]

        if fill_color is not None:
            pygame.draw.polygon(self.screen, fill_color, tri_points)
        pygame.draw.polygon(self.screen, border_color, tri_points, 2)

        rect_box = box_rects[1]
        inset = 7
        inner_rect = pygame.Rect(
            rect_box.x + inset,
            rect_box.y + inset,
            rect_box.width - 2 * inset,
            rect_box.height - 2 * inset
        )

        if fill_color is not None:
            pygame.draw.rect(self.screen, fill_color, inner_rect)
        pygame.draw.rect(self.screen, border_color, inner_rect, 2)

        circ_box = box_rects[2]
        circle_rect = pygame.Rect(
            circ_box.x + inset,
            circ_box.y + inset,
            circ_box.width - 2 * inset,
            circ_box.height - 2 * inset
        )

        if fill_color is not None:
            pygame.draw.ellipse(self.screen, fill_color, circle_rect)
        pygame.draw.ellipse(self.screen, border_color, circle_rect, 2)
    
    def draw_mouse_position(self):
        x, y = pygame.mouse.get_pos()
        label = self.small_font.render(f"x: {x}, y: {y}", True, (0, 0, 0))
        self.screen.blit(label, (5, 5))
    
    def draw_export_label(self):
        font = getattr(self, "small_font", self.font)
        label_surface = font.render("export", True, (0, 0, 0))
        label_rect = label_surface.get_rect()
        label_rect.topright = (self.window_size[0] - 5, 5)

        self.screen.blit(label_surface, label_rect)
        self.export_label_rect = label_rect

    def handle_zoom(self, event):
        ''' Zoom in and out with mouse wheel '''
        if event.type == pygame.MOUSEWHEEL:
            old_zoom = self.zoom_level
            if event.y > 0:
                self.zoom_level += 1
            elif event.y < 0:
                self.zoom_level -= 1
                self.zoom_level = max(1, self.zoom_level)
            
            s = self.zoom_level / old_zoom
            cx = self.window_size[0] / 2
            cy = self.window_size[1] / 2

            for shape in self.shapes:
                points = shape[1]
                for i, (px, py) in enumerate(points):
                    points[i] = (cx + (px - cx) * s, cy + (py - cy) * s)

            self.grid_offset_x = cx + (self.grid_offset_x - cx) * s
            self.grid_offset_y = cy + (self.grid_offset_y - cy) * s
    
    def handle_panning(self):
        ''' Pan the view when left mouse button is held and mouse is moved '''
        if pygame.mouse.get_pressed()[0]:
            new_offset = pygame.mouse.get_pos()
            x = new_offset[0] - self.start_offset[0]
            y = new_offset[1] - self.start_offset[1]

            for shape in self.shapes:
                points = shape[1]
                for i, (px, py) in enumerate(points):
                    points[i] = (px + x, py + y)

            self.grid_offset_x += x
            self.grid_offset_y += y

            self.start_offset = new_offset
    
    def handle_line_thickness(self, event):
        ''' Change the line thickness with [ and ] keys '''
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFTBRACKET:
                self.line_width -= 1
                self.line_width = max(1, self.line_width)
            elif event.key == pygame.K_RIGHTBRACKET:
                self.line_width += 1
    
    def handle_undo(self, event, mods):
        ''' Undo last shape with Ctrl+Z '''
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and (mods & pygame.KMOD_CTRL):
                if self.shapes:
                    self.shapes.pop()
    
    def handle_color_pick(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.palette_rect.collidepoint(event.pos):
                local_x = event.pos[0] - self.palette_rect.x
                self.palette_cursor_x = event.pos[0]

                self.current_hue = (local_x / (self.palette_width - 1)) * 360.0
                self.build_sv_box()

                picked = self.palette_surface.get_at((local_x, event.pos[1] - self.palette_rect.y))

                if self.color_mode == 'border':
                    self.color = picked
                elif self.color_mode == 'background':
                    self.fill_color = picked
                else:
                    self.canvas_color = picked

            elif self.sv_rect.collidepoint(event.pos):
                local_x = event.pos[0] - self.sv_rect.x
                local_y = event.pos[1] - self.sv_rect.y
                picked = self.sv_surface.get_at((local_x, local_y))

                self.sv_cursor_pos = event.pos

                if self.color_mode == 'border':
                    self.color = picked
                elif self.color_mode == 'background':
                    self.fill_color = picked
                else:
                    self.canvas_color = picked

    def handle_color_mode_click(self, event):
        ''' Switch color mode when labels are clicked '''
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.border_label_rect.collidepoint(event.pos):
                self.color_mode = 'border'
            elif self.background_label_rect.collidepoint(event.pos):
                self.color_mode = 'background'
            elif self.canvas_label_rect.collidepoint(event.pos):
                self.color_mode = 'canvas'

    def handle_border_toggle_click(self, event):
        ''' Toggle border visibility when label is clicked '''
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.border_toggle_rect.collidepoint(event.pos):
                self.show_border = not self.show_border
    
    def handle_shape_selection(self, event):
        '''Set selected_shape based on which shape label box was clicked.'''
        if event.type == pygame.MOUSEBUTTONDOWN:
            box_margin = 5
            box_width = 35
            box_height = 35

            box_y = self.palette_rect.top - box_height - box_margin

            first_x = box_margin
            second_x = first_x + box_width + box_margin
            third_x = second_x + box_width + box_margin

            triangle_rect = pygame.Rect(first_x,  box_y, box_width, box_height)
            rectangle_rect = pygame.Rect(second_x, box_y, box_width, box_height)
            circle_rect = pygame.Rect(third_x,  box_y, box_width, box_height)

            mx, my = event.pos

            if triangle_rect.collidepoint(mx, my):
                self.selected_shape = 'triangle'
            elif rectangle_rect.collidepoint(mx, my):
                self.selected_shape = 'rectangle'
            elif circle_rect.collidepoint(mx, my):
                self.selected_shape = 'circle'
    
    def handle_grid_toggle_click(self, event):
        ''' Toggle grid visibility when label is clicked '''
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.grid_toggle_rect.collidepoint(event.pos):
                self.show_grid = not self.show_grid
    
    def color_to_hex(self, c):
        if c is None:
            return ""
        r, g, b = int(c[0]), int(c[1]), int(c[2])
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def handle_export_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.export_label_rect.collidepoint(event.pos):
                print("clicked")

                lines = []
                for shape in self.shapes:
                    shape_type, points, border_color, line_width, fill_color, show_border = shape
                    outline = self.color_to_hex(border_color) if show_border and line_width > 0 else ""
                    fill = self.color_to_hex(fill_color) if fill_color is not None else ""
                    width = line_width if show_border else 0

                    if shape_type == 'rectangle':
                        xs = [p[0] for p in points]
                        ys = [p[1] for p in points]
                        x0, y0 = min(xs), min(ys)
                        x1, y1 = max(xs), max(ys)
                        line = f'canvas.create_rectangle({x0}, {y0}, {x1}, {y1}, outline="{outline}", fill="{fill}", width={width})'
                        lines.append(line)

                    elif shape_type == 'circle':
                        xs = [p[0] for p in points]
                        ys = [p[1] for p in points]
                        x0, y0 = min(xs), min(ys)
                        x1, y1 = max(xs), max(ys)
                        line = f'canvas.create_oval({x0}, {y0}, {x1}, {y1}, outline="{outline}", fill="{fill}", width={width})'
                        lines.append(line)

                    elif shape_type == 'triangle':
                        (x1, y1), (x2, y2), (x3, y3) = points
                        line = f'canvas.create_polygon({x1}, {y1}, {x2}, {y2}, {x3}, {y3}, outline="{outline}", fill="{fill}", width={width})'
                        lines.append(line)

                # open file dialog
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".py",
                    filetypes=[("Python files", "*.py"), ("All files", "*.*")],
                    title="Export script as..."
                )

                root.destroy()
                if file_path:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write('import tkinter as tk\n')
                        file.write('root = tk.Tk()\n')
                        file.write('root.title("Tkinter Canvas")\n')
                        file.write(f'canvas = tk.Canvas(root, width={self.window_size[0]}, height={self.window_size[1]}, bg="{self.color_to_hex(self.canvas_color)}")\n')
                        file.write('canvas.pack()\n\n')
                        file.write("\n".join(lines))
                        file.write('\n\nroot.mainloop()\n')
                    print("Exported to:", file_path)
    
    def main(self):
        running = True
        while running:
            self.handle_panning()
            for event in pygame.event.get():
                mods = pygame.key.get_mods()

                if event.type == pygame.QUIT:
                    running = False

                self.handle_color_mode_click(event)
                self.handle_color_pick(event)
                self.handle_border_toggle_click(event)
                self.handle_grid_toggle_click(event)
                self.handle_shape_selection(event)
                self.handle_export_click(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mods & pygame.KMOD_CTRL:
                        self.handle_draw_shape(event)
                    
                    self.start_offset = pygame.mouse.get_pos()
                
                self.handle_line_thickness(event)
                self.handle_undo(event, mods)
                self.handle_zoom(event)

            self.screen.fill(self.canvas_color)
            self.draw_grid_lines()
            self.draw_shapes()
            self.draw_sv_box()
            self.draw_labels()
            self.draw_palette()
            self.draw_export_label()
            self.draw_shape_labels()
            self.draw_cursor()
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    app = DrawApp()
    app.main()
