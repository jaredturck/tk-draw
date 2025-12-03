import pygame, sys, time

class DrawApp:
    def __init__(self):
        pygame.init()
        self.window_size = (800, 600)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Drawing Window")
        self.font = pygame.font.SysFont(None, 24)
        self.clicks = []
        self.triangles = []
        self.selection_points = []
        self.line_width = 5
        self.color = (0, 0, 0)
        self.last_click = time.time()
        self.offset = (0, 0)
        self.zoom_level = 1

        self.palette_size = (256, 256)
        self.palette_surface = pygame.Surface(self.palette_size)
        self.palette_rect = self.palette_surface.get_rect()
        self.palette_rect.bottomright = (self.window_size[0] - 10, self.window_size[1] - 50)
        self.build_palette()

    def build_palette(self):
        w, h = self.palette_size
        for x in range(w):
            for y in range(h):
                hue = (x / (w - 1)) * 360.0
                sat = (y / (h - 1)) * 100.0
                val = 100.0

                c = pygame.Color(0, 0, 0)
                c.hsva = (hue, sat, val, 100)
                self.palette_surface.set_at((x, y), c)

    def handle_draw_shape(self, event):
        x, y = event.pos
        self.clicks.append((x, y))
        self.selection_points.append((x, y))
        self.last_click = time.time()

        if len(self.clicks) == 3:
            self.triangles.append([self.clicks, self.color, self.line_width])
            self.clicks = []
            self.selection_points = []
    
    def draw_shapes(self):
        for triangle, color, line_width in self.triangles:
            pygame.draw.polygon(self.screen, color, triangle, line_width)
        for point in self.selection_points:
            pygame.draw.circle(self.screen, (255,0,0), point, self.line_width)
        
        if time.time() - self.last_click > 3:
            self.selection_points = []
            self.clicks = []
            self.last_click = time.time()
    
    def draw_cursor(self):
        pygame.draw.circle(self.screen, self.color, pygame.mouse.get_pos(), self.line_width)
        pygame.mouse.set_visible(False)
    
    def draw_labels(self):
        # line width label
        label = self.font.render(f'line width: {self.line_width}', True, (0,0,0))
        rect = label.get_rect()
        rect.bottomleft = (self.window_size[0] - 110, self.window_size[1] - 10)
        self.screen.blit(label, rect)

    def draw_palette(self):
        self.screen.blit(self.palette_surface, self.palette_rect)
    
    def handle_zoom(self, event):
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
        if pygame.mouse.get_pressed()[0]:
            new_offset = pygame.mouse.get_pos()
            x = new_offset[0] - self.start_offset[0]
            y = new_offset[1] - self.start_offset[1]

            # Update all traingles
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
    
    def main(self):
        running = True
        while running:
            self.handle_panning()
            for event in pygame.event.get():
                mods = pygame.key.get_mods()

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mods & pygame.KMOD_CTRL:
                        self.handle_draw_shape(event)
                    
                    self.start_offset = pygame.mouse.get_pos()
                
                self.handle_line_thickness(event)
                self.handle_undo(event, mods)
                self.handle_zoom(event)

            self.screen.fill((255, 255, 255))
            self.draw_shapes()
            self.draw_labels()
            self.draw_palette()
            self.draw_cursor()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DrawApp()
    app.main()
