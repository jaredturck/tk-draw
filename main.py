import tkinter as tk

class ChristmasDrawing:
    def __init__(self):
        self.stroke = 14
        self.y_base = 120

        self.root = tk.Tk()
        self.root.title("Tkinter Drawer")
        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg="white")
        self.canvas.pack()
    
    def draw_in_reverse(self, *func):
        for row in reversed(func):
            row[0](*row[1:])
    
    def draw_cloud(self):
        ''' Draws a cloud shape with 2 bumps and rounded ends '''
        self.canvas.create_arc(60, self.y_base - 40, 132, self.y_base, start=90, extent=180, style=tk.ARC, width=self.stroke) # left rounded end
        self.canvas.create_arc(96, self.y_base - 80, 240, self.y_base, start=0, extent=180, style=tk.ARC, width=self.stroke)  # first bump
        self.canvas.create_arc(204, self.y_base - 60, 348, self.y_base, start=0, extent=140, style=tk.ARC, width=self.stroke) # second bump
        self.canvas.create_arc(312, self.y_base - 40, 384, self.y_base, start=-90, extent=180, style=tk.ARC, width=self.stroke) # right rounded end
        self.canvas.create_line(78, self.y_base, 366, self.y_base, width=self.stroke, capstyle=tk.ROUND) # flat bottom, stretched to match
    
    def draw_triangle(self, x, y, w, h):
        ''' Draws a triangle with shading, w=width, h=height '''
        self.canvas.create_polygon(x, y - h, x + w/2, y, x, y, outline="", fill="black") # right dark half
        self.canvas.create_polygon(x - w/2, y, x, y, x, y - h, outline="", fill="white") # left light half
        self.canvas.create_polygon(x - w/2, y, x + w/2, y, x, y - h, outline="black", fill="", width=h*0.2, joinstyle=tk.ROUND) # thick outline
    
    def draw_arc(self, x, y, w, h, r):
        ''' Draws a half-arc (half ellipse) centred at (x,y), rotated by r degrees '''
        self.canvas.create_arc(x - w/2, y - h/2, x + w/2, y + h/2, start=270 + r, extent=180, style=tk.ARC, width=self.stroke)
    
    def draw_rectangle(self, x, y, w, h):
        ''' Draws a filled rectangle, w=width, h=height '''
        self.canvas.create_rectangle(x - w/2, y, x + w/2, y + h, outline="", fill="black")
    
    def draw_tree(self, x, y, s):
        ''' Draws a tree '''
        w, h = s, s * 0.7
        self.draw_rectangle(x, y + 3*h, s * 0.275, s * 0.7)
        self.draw_in_reverse(
            (self.draw_triangle, x, y, w, h), # 1st tier
            (self.draw_triangle, x, y + h, s*1.4, s*0.8),  # 2nd tier
            (self.draw_triangle, x, y + 2*h, s*1.9, s*0.9),  # 3rd tier
            (self.draw_triangle, x, y + 3*h, s*2.4, s*1.0)   # 4th tier
        )
    
    def draw_mountain(self, x, y, s):
        ''' Draws a mountain with a 4-triangle snow cap '''
        w, h = s * 0.7, s
        
        # self.canvas.create_polygon(x, y, x - w, y, x, y - h, outline="black", fill="#695034")
        # self.canvas.create_polygon(x, y, x + w, y, x, y - h, outline="black", fill="#44331F")

        self.canvas.create_polygon(100, 0, 0, 100, 80, 80, outline="black", fill="white")
        self.canvas.create_polygon(0, 0, 100, 100, 20, 80, outline="black", fill="white")

    
    def main(self):
        # self.draw_tree(x=200, y=140, s=100)
        self.draw_mountain(x=200, y=220, s=120)
        self.root.mainloop()

if __name__ == "__main__":
    app = ChristmasDrawing()
    app.main()
