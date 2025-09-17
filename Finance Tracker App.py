from tkinter import *
from tkinter import messagebox
import json
import datetime
import math

root = Tk()
# -------------------------------- #
#   Constants and Configurations   #
# -------------------------------- #

# Money related variables
money_amount = 614 # Default money amount
currency = "€" # Default currency symbol
reserve_at_end_of_month = 0 # Amount to reserve at the end of the month
daily_allowance = money_amount / 30

EXCHANGE_RATES = {
        "€": {"CZK": 24.32},
        "CZK": {"€": 1/24.32}
    }

# Window dimensions and scaling configurations
WINDOW_SCALING_PERCENT = 75 # Percentage of screen size to use for window dimensions
WINDOW_WIDTH = root.winfo_screenwidth() * (WINDOW_SCALING_PERCENT / 100)
WINDOW_HEIGHT = root.winfo_screenheight() * (WINDOW_SCALING_PERCENT / 100)
WINDOW_X_CENTER = WINDOW_WIDTH / 2
WINDOW_Y_CENTER = WINDOW_HEIGHT / 2
ONE_PERCENT_HEIGHT = WINDOW_HEIGHT / 100
ONE_PERCENT_WIDTH = WINDOW_WIDTH / 100

# Text configurations
FONT = 'Arial'
text_color_dynamic = "#81FCAC" # This color changes based on dark mode or light mode
text_color = "#000000" # Default text color (black for light mode)
TEXT_SIZE_SMALL = 8
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
    create_allowance_window(padding_x, padding_y)

def create_allowance_window(padding_x, padding_y):
    '''Creates a new window for setting allowances.'''
    canvas.delete('allowance_window') # Remove existing allowance window if it exists (to avoid duplicates when redrawing UI)
    width = calculate_width_in_percent(padding_x, 40) # Width in percentages of window dimensions
    height = calculate_height_in_percent(padding_y, 50) # Height in percentages of window dimensions
    x1 = ONE_PERCENT_WIDTH * padding_x / 2
    y1 = ONE_PERCENT_HEIGHT * padding_y / 2
    x2 = x1 + width - (padding_x * ONE_PERCENT_WIDTH / 2)
    y2 = y1 + height - (padding_y * ONE_PERCENT_HEIGHT / 2)
    main_rect_id = canvas.create_rectangle(x1, y1, x2, y2, 
                            fill=widget_fill_color,
                            outline=widget_border_color,
                            width=widget_border_width,
                            tag="allowance_window",
                            )

    create_allowance_label(x1, x2, y1, y2, main_rect_id)

def create_allowance_label(x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    canvas.delete('allowance') # Remove existing allowance label if it exists (to avoid duplicates when redrawing UI)
    height_percentage_label = 12
    y2_label = y1 + (calculate_height_of_item(main_rect_id) / 100 * height_percentage_label)
    # Label background
    canvas.create_rectangle(x1, y1, x2, y2_label,
                            fill=widget_fill_color,
                            outline=widget_border_color,
                            width=widget_border_width,
                            tag="allowance")
    
    # Centered text inside the label
    canvas.create_text((x1 + x2) / 2, (y1 + y2_label) / 2, 
                       text="Daily allowance:", 
                       tag="allowance",
                       font=(FONT, TEXT_SIZE_LARGE),
                       fill=text_color)

    create_allowance_currency(x1, x2, y1, y2_label, main_rect_id)

def create_allowance_currency(x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    '''Creates a section for displaying the currency of the allowance.'''

    # Currency section (rectangle below the label)
    canvas.delete('allowance_currency') # Remove existing allowance currency if it exists (to avoid duplicates when redrawing UI)
    height_percentage_currency = 24 # Height of the currency section in percentages of the allowance window height
    y1_currency = y2
    y2_currency = y1_currency + (calculate_height_of_item(main_rect_id) / 100 * height_percentage_currency)
    canvas.create_rectangle(x1, y1_currency, x2, y2_currency,
                            fill=widget_fill_color,
                            outline=widget_border_color,
                            width=widget_border_width,
                            tag="allowance_currency")

    # Centered text inside the currency section
    canvas.create_text((x1 + x2) / 2, (y1_currency + y2_currency) / 2, 
                       text=f'{daily_allowance} {currency}', 
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_XLARGE),
                       fill=text_color)
    
def calculate_money_conversion(money: float, currency_before: str, currency_after: str) -> float:
    if currency_before == currency_after: return money
    if currency_before not in EXCHANGE_RATES or currency_after not in EXCHANGE_RATES[currency_before]:
        raise ValueError(f"Conversion rate from {currency_before} to {currency_after} not available.")
    
    conversion_rate = EXCHANGE_RATES[currency_before][currency_after]
    print(conversion_rate)
    return round(money * conversion_rate, 2)

def switch_currency(event):
    global currency, money_amount
    if currency == "€":
        new_currency = "CZK"
    else:
        new_currency = "€"
    money_amount = calculate_money_conversion(money_amount, currency, new_currency)
    currency = new_currency
    update_money_variables()
    redraw_ui()

def update_money_variables():
    pass
    daily_allowance = money_amount / 30

def calculate_height_of_item(item_id: int) -> float:
    y1 = canvas.bbox(item_id)[1]
    y2 = canvas.bbox(item_id)[3]
    return y2 - y1

def calculate_width_of_item(item_id: int) -> float:
    x1 = canvas.bbox(item_id)[0]
    x2 = canvas.bbox(item_id)[2]
    return x2 - x1

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

create_allowance_window(padding_x, padding_y)

root.bind("w", increase_padding)
root.bind("s", decrease_padding)
root.bind("<Escape>", toggle_fullscreen)

root.bind("<D>", toggle_dark_mode)
root.bind("<d>", toggle_dark_mode)

root.bind("<C>", switch_currency)
root.bind("<c>", switch_currency)
center_screen()
root.mainloop()
