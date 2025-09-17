from tkinter import *
from tkinter import messagebox
import json
import datetime
import math

root = Tk()
# -------------------------------- #
#   Constants and Configurations   #
# -------------------------------- #

# Window dimensions and scaling configurations
WINDOW_SCALING_PERCENT = 100 # Percentage of screen size to use for window dimensions
WINDOW_WIDTH = root.winfo_screenwidth() * (WINDOW_SCALING_PERCENT / 100)
WINDOW_HEIGHT = root.winfo_screenheight() * (WINDOW_SCALING_PERCENT / 100)
WINDOW_X_CENTER = WINDOW_WIDTH / 2
WINDOW_Y_CENTER = WINDOW_HEIGHT / 2
ONE_PERCENT_HEIGHT = WINDOW_HEIGHT / 100
ONE_PERCENT_WIDTH = WINDOW_WIDTH / 100

# Text configurations
FONT = 'Arial'
text_color = 'red'
TEXT_SIZE_NORMAL = 12
TEXT_SIZE_LARGE = 16
TEXT_SIZE_XLARGE = 20

# Flags
is_fullscreen = False
is_dark_mode = False

# Window configurations
# Light mode and dark mode background colors
TITLE = "Finanční Podpúrce 3000"
window_bg_color = "#CBCBCB"
widget_border_color = "#000000"
widget_fill_color = "#FFFFFF"
widget_border_width = 2
padding_y = 1
padding_x = padding_y / (WINDOW_WIDTH / WINDOW_HEIGHT)

# Padding in percentages of window dimensions 
# The padding is used to create space between the window border and the UI windows.
# The padding is applied around each window so that the total padding added together is equal to the padding percentage.
# Padding x is calculated based on the aspect ratio of the window and padding_y to ensure consistent spacing.

# -------------------------------- #
#       Application Window         #
# -------------------------------- #

canvas = Canvas(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT, bg = window_bg_color)
canvas.pack()

def switch_dark_mode_colors(is_dark_mode: bool):
    global window_bg_color, widget_border_color, text_color, widget_fill_color
    '''Switches the color scheme of the application between dark mode and light mode.'''

    if is_dark_mode:
        window_bg_color = "#000000"
        widget_fill_color = "#313131"
        widget_border_color = "#FFFFFF"
        text_color = "#FFFFFF"
    else:
        window_bg_color = "#CBCBCB"
        widget_fill_color = "#FFFFFF"
        widget_border_color = "#000000"
        text_color = "#000000"
    canvas.config(bg=window_bg_color)
    redraw_ui()

def center_screen():
    '''Centers the application window on the user's screen and sets the window title.'''
    screen_width = root.winfo_screenwidth()  # Width of the user screen.
    screen_height = root.winfo_screenheight() # Height of the user screen.

    # Starting X & Y window positions:
    x = (screen_width / 2) - (WINDOW_WIDTH / 2)
    y = (screen_height / 2) - (WINDOW_HEIGHT / 2)

    root.geometry('%dx%d+%d+%d' % (WINDOW_WIDTH, WINDOW_HEIGHT, x, y))
    TM = ' (Samuel Ondroš 2025 ©)'
    root.title(TITLE + TM)

root.attributes("-fullscreen", is_fullscreen)
def toggle_fullscreen(event):
    '''Toggles fullscreen mode for the application window.
    Args:
        event (tkinter.Event): The event that triggered fullscreen toggle.
    '''
    global is_fullscreen
    is_fullscreen = not is_fullscreen 
    root.attributes("-fullscreen", is_fullscreen)

def toggle_dark_mode(event):
    '''Toggles dark mode for the application window.
    Args:
        event (tkinter.Event): The event that triggered dark mode toggle.
    '''
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    switch_dark_mode_colors(is_dark_mode)

def redraw_ui():
    global is_dark_mode, padding_x, padding_y
    # Clear the canvas and redraw all UI elements with updated colors.
    # TODO: Implement UI redraw logic.
    create_allowance_window(padding_x, padding_y, is_dark_mode)

def create_allowance_window(padding_x, padding_y, is_dark_mode):
    '''Creates a new window for setting allowances.'''
    canvas.delete('allowance_window') # Remove existing allowance window if it exists (to avoid duplicates when redrawing UI)
    width = calculate_width_in_percent(padding_x, 40) # Width in percentages of window dimensions
    height = calculate_height_in_percent(padding_y, 50) # Height in percentages of window dimensions
    x1 = ONE_PERCENT_WIDTH * padding_x / 2
    y1 = ONE_PERCENT_HEIGHT * padding_y / 2
    x2 = x1 + width - (padding_x * ONE_PERCENT_WIDTH / 2)
    y2 = y1 + height - (padding_y * ONE_PERCENT_HEIGHT / 2)
    canvas.create_rectangle(x1, y1, x2, y2, 
                            fill=widget_fill_color,
                            outline=widget_border_color,
                            width=widget_border_width,
                            tag="allowance_window",
                            )

def calculate_width_in_percent(padding_x: float, percentage: float) -> float:
    '''Calculates the width in percentages of window dimensions based on padding and a given percentage.'''
    return ONE_PERCENT_WIDTH * (percentage - padding_x)

def calculate_height_in_percent(padding_y: float, percentage: float) -> float:
    '''Calculates the height in percentages of window dimensions based on padding and a given percentage.'''
    return ONE_PERCENT_HEIGHT * (percentage - padding_y)

def increase_padding(event):
    '''Increases the padding around UI elements.'''
    global padding_x, padding_y
    if padding_y < 10: # Limit maximum padding to 10%
        padding_y += 0.5
        padding_x = padding_y / (WINDOW_WIDTH / WINDOW_HEIGHT)
        redraw_ui()

def decrease_padding(event):
    '''Decreases the padding around UI elements.'''
    global padding_x, padding_y
    if padding_y > 0: # Limit minimum padding to 0%
        padding_y -= 0.5
        padding_x = padding_y / (WINDOW_WIDTH / WINDOW_HEIGHT)
        redraw_ui()
    
create_allowance_window(padding_x, padding_y, is_dark_mode)

root.bind("w", increase_padding)
root.bind("s", decrease_padding)
root.bind("<Escape>", toggle_fullscreen)
root.bind("<D>", toggle_dark_mode)
root.bind("<d>", toggle_dark_mode)

center_screen()
root.mainloop()
