from tkinter import *
from tkinter import messagebox
import json
from datetime import date
import math
import calendar

root = Tk()
spendings = 100

# TODO: Load spendings from a file or database, also calculate for CZK or EUR independently
def get_days_left_in_curr_month() -> int:
    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    days_in_month = calendar.monthrange(year, month)[1]
    return days_in_month - day + 1 # +1 to include today

def get_days_in_curr_month() -> int:
    today = date.today()
    year = today.year
    month = today.month
    days_in_month = calendar.monthrange(year, month)[1]
    return days_in_month

app_states = {
    "budget": 900,
    "currency": "€",
    "reserve_at_end_of_month": 300,
    "daily_allowance": 0, # calculated in code
    "rolling_balance": 0, # calculated in code
    "days_left_in_month": get_days_left_in_curr_month(), # CURRENTLY NOT USED
    "window_bg_color": "#CBCBCB",
    "widget_border_color": "#000000",
    "widget_fill_color": "#FFFFFF",
    "widget_border_width": 2,
    "padding_y": 2,
    "is_fullscreen": False,
    "is_dark_mode": False,
    "dynamic_text_color": "#1B552F",  # This color is used for dynamic text (e.g., changing allowance)
    "reserve_text_color": "#FD3D3D",
    "text_color": "#000000",  # Default text color (black for light mode)
    "spendings": { "18.9.2025": {"item": "Pivo", "price": 50, "currency": "CZK"},
                   "19.9.2025": {"item": "Burger", "price": 150, "currency": "CZK"}
                  }
}

CZK_RATE = 24.32

EXCHANGE_RATES = {
        "€": {"CZK": CZK_RATE},
        "CZK": {"€": 1/CZK_RATE}
    }

def get_padding_x():
    return app_states["padding_y"] / (WINDOW_WIDTH / WINDOW_HEIGHT)

def get(key):
    return app_states[key]

def set_state(key, value):
    app_states[key] = value

def calculate_money_conversion(money: float, currency_before: str, currency_after: str) -> float:
    if currency_before == currency_after: return money
    if currency_before not in EXCHANGE_RATES or currency_after not in EXCHANGE_RATES[currency_before]:
        raise ValueError(f"Conversion rate from {currency_before} to {currency_after} not available.")
    
    conversion_rate = EXCHANGE_RATES[currency_before][currency_after]
    print(conversion_rate)
    return round(money * conversion_rate, 2)

def calculate_daily_allowance(budget: float, reserve: float) -> float:
    days_in_month = get_days_in_curr_month()
    allowance_per_day = (budget - reserve) / days_in_month
    return round(allowance_per_day, 2)

def set_daily_allowance():
    daily_allowance = calculate_daily_allowance(get("budget"), get("reserve_at_end_of_month"))
    set_state("daily_allowance", daily_allowance)

def add_daily_allowance():
    set_state("rolling_balance", round(get("rolling_balance") + get("daily_allowance"), 2))



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
BOLD = 'bold'
ITALIC = 'italic'
TEXT_SIZE_SMALL = 10
TEXT_SIZE_NORMAL = 12
TEXT_SIZE_LARGE = 16
TEXT_SIZE_XLARGE = 20

padding_x = get_padding_x()
# Padding in percentages of window dimensions 
# Padding x is calculated based on the aspect ratio of the window and padding_y to ensure consistent spacing.

# Window configurations
TITLE = "Finanční Podpúrce 3000"

# -------------------------------- #
#       Application Window         #
# -------------------------------- #

canvas = Canvas(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT, bg = get("window_bg_color"))
canvas.pack()

def switch_dark_mode_colors(is_dark_mode: bool):
    '''Switches the color scheme of the application between dark mode and light mode.'''

    if is_dark_mode:
        set_state("window_bg_color", "#000000")
        set_state("widget_fill_color", "#313131")
        set_state("widget_border_color", "#FFFFFF")
        set_state("text_color", "#FFFFFF")
        set_state("dynamic_text_color", "#81FCAC")
    else:
        set_state("window_bg_color", "#CBCBCB")
        set_state("widget_fill_color", "#FFFFFF")
        set_state("widget_border_color", "#000000")
        set_state("text_color", "#000000")
        set_state("dynamic_text_color", "#1F5236")
    canvas.config(bg=get("window_bg_color"))
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

root.attributes("-fullscreen", get("is_fullscreen"))

def toggle_fullscreen(event):
    '''Toggles fullscreen mode for the application window.
    Args:
        event (tkinter.Event): The event that triggered fullscreen toggle.
    '''
    set_state("is_fullscreen", not get("is_fullscreen"))
    root.attributes("-fullscreen", get("is_fullscreen"))

def toggle_dark_mode(event):
    '''Toggles dark mode for the application window.
    Args:
        event (tkinter.Event): The event that triggered dark mode toggle.
    '''
    set_state("is_dark_mode", not get("is_dark_mode"))
    switch_dark_mode_colors(get("is_dark_mode"))

def redraw_ui():
    # Clear the canvas and redraw all UI elements with updated colors.
    # TODO: Implement UI redraw logic.
    padding_x = get_padding_x()
    padding_y = get("padding_y")
    create_allowance_window(padding_x, padding_y)

def create_allowance_window(padding_x, padding_y):
    '''Creates a new window for setting allowances.'''
    canvas.delete('allowance_window') # Remove existing allowance window if it exists (to avoid duplicates when redrawing UI)
    width = calculate_width_in_percent(padding_x, 50) # Width in percentages of window dimensions
    height = calculate_height_in_percent(padding_y, 75) # Height in percentages of window dimensions
    x1 = ONE_PERCENT_WIDTH * padding_x / 2
    y1 = ONE_PERCENT_HEIGHT * padding_y / 2
    x2 = x1 + width - (padding_x * ONE_PERCENT_WIDTH / 2)
    y2 = y1 + height - (padding_y * ONE_PERCENT_HEIGHT / 2)
    main_rect_id = canvas.create_rectangle(x1, y1, x2, y2, 
                            fill=get("widget_fill_color"),
                            outline=get("widget_border_color"),
                            width=get("widget_border_width"),
                            tag="allowance_window",
                            )

    create_allowance_label(x1, x2, y1, y2, main_rect_id)

def create_allowance_label(x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    canvas.delete('allowance') # Remove existing allowance label if it exists (to avoid duplicates when redrawing UI)
    height_percentage_label = 12
    y2_label = y1 + (calculate_height_of_item(main_rect_id) / 100 * height_percentage_label)
    # Label background
    canvas.create_rectangle(x1, y1, x2, y2_label,
                            fill=get("widget_fill_color"),
                            outline=get("widget_border_color"),
                            width=get("widget_border_width"),
                            tag="allowance")
    
    # Centered text inside the label
    canvas.create_text((x1 + x2) / 2, (y1 + y2_label) / 2, 
                       text="Daily allowance:", 
                       tag="allowance",
                       font=(FONT, TEXT_SIZE_LARGE),
                       fill=get("text_color"))

    create_allowance_currency(x1, x2, y1, y2_label, main_rect_id)

def create_allowance_currency(x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    '''Creates a section for displaying the currency of the allowance.'''

    # Currency section (rectangle below the label)
    canvas.delete('allowance_currency') # Remove existing allowance currency if it exists (to avoid duplicates when redrawing UI)
    height_percentage_currency = 24 # Height of the currency section in percentages of the allowance window height
    y1_currency = y2
    y2_currency = y1_currency + (calculate_height_of_item(main_rect_id) / 100 * height_percentage_currency)
    canvas.create_rectangle(x1, y1_currency, x2, y2_currency,
                            fill=get("widget_fill_color"),
                            outline=get("widget_border_color"),
                            width=get("widget_border_width"),
                            tag="allowance_currency")

    # Centered text inside the currency section
    rolling_balance = get("rolling_balance")
    canvas.create_text((x1 + x2) / 2, (y1_currency + y2_currency) / 2, 
                       text=f'{rolling_balance} {get("currency")}', 
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_XLARGE, BOLD),
                       fill=get("dynamic_text_color"))
    
    # Text on the top right corner of the currency section indicating current daily allowance increase
    daily_allowance = get("daily_allowance")
    canvas.create_text(x2 - 10, y1_currency + 10, 
                       text=f'Tomorrow: +{daily_allowance} {get("currency")}', 
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                       fill=get("dynamic_text_color"),
                       anchor="ne")
    
    # Text on the top left corner of the currency section indicating budget
    budget = get("budget")
    canvas.create_text(x1 + 10, y1_currency + 10,
                       text=f'Budget: {budget} {get("currency")}',
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                       fill=get("dynamic_text_color"),
                       anchor="nw")
    
    # Text on the bottom left corner of the currency section indicating reserve at end of month
    reserve = get("reserve_at_end_of_month")
    canvas.create_text(x1 + 10, y2_currency - 10,
                       text=f'Reserve: {reserve} {get("currency")}',
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                       fill=get("reserve_text_color"),
                       anchor="sw")


def switch_currency(event):
    if get("currency") == "€":
        new_currency = "CZK"
    else:
        new_currency = "€"
    money_amount = calculate_money_conversion(get("budget"), get("currency"), new_currency)
    reserve_amount = calculate_money_conversion(get("reserve_at_end_of_month"), get("currency"), new_currency)
    rolling_balance = calculate_money_conversion(get("rolling_balance"), get("currency"), new_currency)
    set_state("currency", new_currency)
    set_state("budget", money_amount)
    set_state("reserve_at_end_of_month", reserve_amount)
    set_state("rolling_balance", rolling_balance)
    set_daily_allowance() # Recalculate daily allowance based on new budget and reserve amounts
    redraw_ui()

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
    if get("padding_y") < 10: # Limit maximum padding to 10%
        set_state("padding_y", get("padding_y") + 0.5)
        redraw_ui()

def decrease_padding(event):
    '''Decreases the padding around UI elements.'''
    if get("padding_y") > 0: # Limit minimum padding to 0%
        set_state("padding_y", get("padding_y") - 0.5)
        redraw_ui()

def add(event):
    add_daily_allowance()
    redraw_ui()
set_daily_allowance()
create_allowance_window(get_padding_x(), get("padding_y"))

root.bind("w", increase_padding)
root.bind("s", decrease_padding)
root.bind("<Escape>", toggle_fullscreen)

root.bind("<D>", toggle_dark_mode)
root.bind("<d>", toggle_dark_mode)
root.bind("a", add)
root.bind("<C>", switch_currency)
root.bind("<c>", switch_currency)

center_screen()
root.mainloop()

# TODO TODO!!!! MOST IMPORTANT!! SET UP A JSON FILE ASAP. CANT CONTINUE WITHOUT IT!

# TODO: Add a way to log spendings and view them in a list, possibly with dates and categories.
# TODO: When user adds a spending, check whether its larger than their rolling balance. If so, allow them to choose
#       whether they want to reduce their rolling balance to the negatives, or let it impact the budget for the rest of the month.
#       (in which case daily allowance would be reduced for the rest of the month)
# TODO: Add a way to save and load user settings (budget, reserve, currency, dark mode preference, spendings) to/from a file.
# TODO: Add a way to reset the rolling balance to the initial budget at the start of a new month.
# TODO: Calculate rolling balance based on current date.
# TODO: Add graphs to visualize spendings over time.
# TODO: Reset daily allowance and rolling balance at the start of a new month (with notifications how much they saved).
# TODO: 
