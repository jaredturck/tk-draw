# 1. Rectangle
# (x1, y1, x2, y2)
canvas.create_rectangle(
    50, 50, 150, 120,
    outline="black",
    fill="lightblue",
    width=2
)

# 2. Oval (inside the bounding box x1,y1,x2,y2)
canvas.create_oval(
    200, 50, 320, 150,
    outline="black",
    fill="lightgreen",
    width=2
)

# 3. Line
canvas.create_line(
    50, 200, 250, 250,
    width=3
)

# 4. Polygon (normal, not smooth) – e.g. triangle
canvas.create_polygon(
    350, 50,   # point 1
    450, 150,  # point 2
    300, 150,  # point 3
    outline="black",
    fill="pink",
    width=2
)

# 5. Smooth polygon (curved shape)
canvas.create_polygon(
    350, 200,  # point 1
    400, 250,  # point 2
    450, 220,  # point 3
    500, 260,  # point 4
    550, 230,  # point 5
    smooth=True,
    outline="black",
    fill="",   # no fill, just outline
    width=2
)

# 6. Text object
canvas.create_text(
    150, 300,
    text="Hello, Tkinter!",
    font=("Arial", 16),
)

# 7. Arc (part of an oval)
canvas.create_arc(
    300, 260, 420, 360,  # bounding box
    start=0,             # starting angle in degrees
    extent=180,          # sweep angle
    style=tk.ARC,        # just the arc outline
    width=3
)
