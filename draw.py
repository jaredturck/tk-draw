import pygame, sys, time

class DrawApp:
    def __init__(self):
        pygame.init()
        self.window_size = (800, 600)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Drawing Window')
        self.font = pygame.font.SysFont(None, 24)
        self.clicks = []
        self.triangles = []
        self.selection_points = []
        self.line_width = 5

        self.color = (0, 0, 0)
        self.canvas_color = (255, 255, 255)
        self.fill_color = None
        self.color_mode = 'border'
        self.show_border = True

        self.last_click = time.time()
        self.offset = (0, 0)
        self.zoom_level = 1

        self.palette_height = 20
        self.palette_width = self.window_size[0] - 10
        self.palette_size = (self.palette_width, self.palette_height)

        self.palette_surface = pygame.Surface(self.palette_size)
        self.palette_rect = self.palette_surface.get_rect()
        self.palette_rect.midbottom = (self.window_size[0] // 2, self.window_size[1] - 5)
        self.build_palette()

        self.border_label_rect = pygame.Rect(0, 0, 0, 0)
        self.background_label_rect = pygame.Rect(0, 0, 0, 0)
        self.border_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.canvas_label_rect = pygame.Rect(0, 0, 0, 0)

    def build_palette(self):
        ''' Create a horizontal color palette surface. '''
        w, h = self.palette_size
        for x in range(w):
            hue = (x / (w - 1)) * 360.0
            sat = 100.0
            val = 100.0

            c = pygame.Color(0, 0, 0)
            c.hsva = (hue, sat, val, 100)
            for y in range(h):
                self.palette_surface.set_at((x, y), c)

    def handle_draw_shape(self, event):
        ''' Record clicks and draw triangle after 3 clicks. '''
        x, y = event.pos
        self.clicks.append((x, y))
        self.selection_points.append((x, y))
        self.last_click = time.time()

        if len(self.clicks) == 3:
            self.triangles.append([self.clicks, self.color, self.line_width, self.fill_color, self.show_border])
            self.clicks = []
            self.selection_points = []
    
    def draw_shapes(self):
        ''' Draw all triangles and selection points '''
        for triangle, border_color, line_width, fill_color, show_border in self.triangles:
            if fill_color is not None:
                pygame.draw.polygon(self.screen, fill_color, triangle, 0)
            if show_border:
                pygame.draw.polygon(self.screen, border_color, triangle, line_width)

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
        box_height = 110
        box_x = self.window_size[0] - box_width - 5
        box_y = self.window_size[1] - box_height - 35

        pygame.draw.rect(self.screen, (255, 255, 255), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height), 2)

        base_x = self.window_size[0] - 150 - 7

        lw_label = self.font.render(f'line width: {self.line_width}', True, (0, 0, 0))
        lw_rect = lw_label.get_rect()
        lw_rect.bottomleft = (base_x, self.window_size[1] - 40)
        self.screen.blit(lw_label, lw_rect)

        if self.show_border:
            toggle_text = 'border: on'
        else:
            toggle_text = 'border: off'

        toggle_label = self.font.render(toggle_text, True, (0, 0, 0))
        toggle_rect = toggle_label.get_rect()
        toggle_rect.bottomleft = (base_x, lw_rect.top - 5)
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

    def draw_palette(self):
        ''' Draw the color palette at the bottom of the screen '''
        self.screen.blit(self.palette_surface, self.palette_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.palette_rect, 2)
    
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

            for i in range(len(self.triangles)):
                self.triangles[i][0][0] = (cx + (self.triangles[i][0][0][0] - cx) * s, cy + (self.triangles[i][0][0][1] - cy) * s)
                self.triangles[i][0][1] = (cx + (self.triangles[i][0][1][0] - cx) * s, cy + (self.triangles[i][0][1][1] - cy) * s)
                self.triangles[i][0][2] = (cx + (self.triangles[i][0][2][0] - cx) * s, cy + (self.triangles[i][0][2][1] - cy) * s)
    
    def handle_panning(self):
        ''' Pan the view when left mouse button is held and mouse is moved '''
        if pygame.mouse.get_pressed()[0]:
            new_offset = pygame.mouse.get_pos()
            x = new_offset[0] - self.start_offset[0]
            y = new_offset[1] - self.start_offset[1]

            # Update all triangles
            for i in range(len(self.triangles)):
                self.triangles[i][0][0] = self.triangles[i][0][0][0] + x, self.triangles[i][0][0][1] + y
                self.triangles[i][0][1] = self.triangles[i][0][1][0] + x, self.triangles[i][0][1][1] + y
                self.triangles[i][0][2] = self.triangles[i][0][2][0] + x, self.triangles[i][0][2][1] + y
            
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
                if self.triangles:
                    self.triangles.pop()
    
    def handle_color_pick(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.palette_rect.collidepoint(event.pos):
                picked = self.palette_surface.get_at(
                    (event.pos[0] - self.palette_rect.x,
                     event.pos[1] - self.palette_rect.y)
                )

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

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mods & pygame.KMOD_CTRL:
                        self.handle_draw_shape(event)
                    
                    self.start_offset = pygame.mouse.get_pos()
                
                self.handle_line_thickness(event)
                self.handle_undo(event, mods)
                self.handle_zoom(event)

            self.screen.fill(self.canvas_color)
            self.draw_shapes()
            self.draw_labels()
            self.draw_palette()
            self.draw_cursor()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    app = DrawApp()
    app.main()
