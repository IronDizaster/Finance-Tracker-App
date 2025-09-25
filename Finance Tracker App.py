from tkinter import *
from tkinter import messagebox # For displaying message boxes
from tkinter import font
import json # For saving and loading settings
from datetime import date
from datetime import datetime
import math 
import calendar
import os # For checking if a file exists

root = Tk()
spendings = 100

# TODO: Load spendings from a file or database, also calculate for CZK or EUR independently

FINANCE_DATA_PATH = "finance_data.json"
FINANCE_TRANSACTIONS_PATH = "transactions.json"

def get_current_time() -> str:
    now = datetime.now()
    time = now.strftime('%H:%M:%S')
    return time

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

def create_data_json_if_nonexistent(file_path=FINANCE_DATA_PATH):
    default_app_states = {
    "budget": 500,
    "currency": "€",
    "reserve_at_end_of_month": 100,
    "total_monthly_spendings": 0,
    "daily_allowance": 0, # calculated in code
    "rolling_balance": 0, # calculated in code
    "pending_spendings": 0, # accumulates over time of daily balance spendings
    "CZK_RATE": 24.32,
    "days_left_in_month": get_days_left_in_curr_month(), # CURRENTLY NOT USED
    "window_bg_color": "#CBCBCB",
    "widget_border_color": "#000000",
    "widget_fill_color": "#FFFFFF",
    "widget_border_width": 2,
    "widget_text_color": "#000000",
    "button_active_fg": "#222222",
    "button_active_bg": "#E6E6E6",
    "padding_y": 1,
    "WINDOW_SCALING_PERCENT": 100, 
    "is_fullscreen": True,
    "is_dark_mode": False,
    "dynamic_text_color": "#1B552F",  # This color is used for dynamic text (e.g., changing allowance)
    "reserve_text_color": "#FD3D3D",
    "text_color": "#000000",  # Default text color (black for light mode)
}
    
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump(default_app_states, file, indent=4)

def create_transaction_json_if_nonexistent(file_path=FINANCE_TRANSACTIONS_PATH):
    default_transactions = {'next_txn_id': 1}
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump(default_transactions, file, indent=4)

def load_transactions(file_path=FINANCE_TRANSACTIONS_PATH):
    with open(file_path, 'r', encoding='UTF-8') as file:
        return json.load(file)

def load_app_states(file_path=FINANCE_DATA_PATH) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)

def save_transactions(transactions: dict, file_path = FINANCE_TRANSACTIONS_PATH):
    # Uses atomic write to prevent data loss
    temp_file_path = file_path[:file_path.index('.')] + '.tmp'
    with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
        json.dump(transactions, temp_file, indent=4, ensure_ascii=False)
    os.replace(temp_file_path, file_path)

def save_app_states(app_states: dict, file_path=FINANCE_DATA_PATH):
    # Uses atomic write to prevent data loss in the case of crashes mid-write
    temp_file_path = file_path[:file_path.index('.')] + ".tmp"
    with open(temp_file_path, 'w') as temp_file:
        json.dump(app_states, temp_file, indent=4)
    os.replace(temp_file_path, file_path)


create_data_json_if_nonexistent()
create_transaction_json_if_nonexistent()
app_states = load_app_states()
transactions = load_transactions()

EXCHANGE_RATES = {
        "€": {"CZK": app_states["CZK_RATE"]},
        "CZK": {"€": 1/app_states["CZK_RATE"]}
    }

def get_padding_x():
    return app_states["padding_y"] / (WINDOW_WIDTH / WINDOW_HEIGHT)

def get_state(key):
    return app_states[key]

def set_state(key, value):
    app_states[key] = value

def calculate_money_conversion(money: float, currency_before: str, currency_after: str) -> float:
    if currency_before == currency_after: return money
    if currency_before not in EXCHANGE_RATES or currency_after not in EXCHANGE_RATES[currency_before]:
        raise ValueError(f"Conversion rate from {currency_before} to {currency_after} not available.")
    
    conversion_rate = EXCHANGE_RATES[currency_before][currency_after]
    return money * conversion_rate

# TODO: Calculate daily allowance ONLY whenever the budget is changed!! 
# Maybe create a function that initializes the budget (later)

def calculate_daily_allowance(budget: float, reserve: float) -> float:
    days_left_in_month = get_days_left_in_curr_month()
    allowance_per_day = (budget - reserve) / days_left_in_month
    return allowance_per_day

def set_daily_allowance():
    daily_allowance = calculate_daily_allowance(get_state("budget"), get_state("reserve_at_end_of_month"))
    set_state("daily_allowance", daily_allowance)

def add_daily_allowance():
    set_state("rolling_balance", get_state("rolling_balance") + get_state("daily_allowance"))


# Window dimensions and scaling configurations
WINDOW_SCALING_PERCENT = get_state("WINDOW_SCALING_PERCENT") # Percentage of screen size to use for window dimensions
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
TEXT_SIZE_XSMALL = round(9 / (100 / get_state("WINDOW_SCALING_PERCENT")))
TEXT_SIZE_SMALL = round(10 / (100 / get_state("WINDOW_SCALING_PERCENT")))
TEXT_SIZE_NORMAL = round(12 / (100 / get_state("WINDOW_SCALING_PERCENT")))
TEXT_SIZE_LARGE = round(16 / (100 / get_state("WINDOW_SCALING_PERCENT")))
TEXT_SIZE_XLARGE = round(20 / (100 / get_state("WINDOW_SCALING_PERCENT")))

padding_x = get_padding_x()
# Padding in percentages of window dimensions 
# Padding x is calculated based on the aspect ratio of the window and padding_y to ensure consistent spacing.

# Window configurations
TITLE = "Finanční Podpúrce 3000"

# -------------------------------- #
#       Application Window         #
# -------------------------------- #

canvas = Canvas(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT, bg = get_state("window_bg_color"))
canvas.pack()

def switch_dark_mode_colors(is_dark_mode: bool):
    '''Switches the color scheme of the application between dark mode and light mode.'''

    if is_dark_mode:
        set_state("window_bg_color", "#000000")
        set_state("widget_fill_color", "#313131")
        set_state("widget_border_color", "#FFFFFF")
        set_state("text_color", "#FFFFFF")
        set_state("dynamic_text_color", "#81FCAC")
        set_state("widget_text_color", "#FFFFFF")
        set_state("button_active_fg", "#FFFFFF")
        set_state("button_active_bg", "#303030")
    else:
        set_state("window_bg_color", "#CBCBCB")
        set_state("widget_fill_color", "#FFFFFF")
        set_state("widget_border_color", "#000000")
        set_state("text_color", "#000000")
        set_state("dynamic_text_color", "#1F5236")
        set_state("widget_text_color", "#000000")
        set_state("button_active_fg", '#222222')
        set_state("button_active_bg", '#E6E6E6')

    canvas.config(bg=get_state("window_bg_color"))
    redraw_ui()

def format_number(num: float) -> str:
    formatted_number = f'{num:,.2f}'
    formatted_number = formatted_number.replace(',',' ').replace('.', ',')
    return formatted_number

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

root.attributes("-fullscreen", get_state("is_fullscreen"))

def toggle_fullscreen(event):
    '''Toggles fullscreen mode for the application window.
    Args:
        event (tkinter.Event): The event that triggered fullscreen toggle.
    '''
    set_state("is_fullscreen", not get_state("is_fullscreen"))
    root.attributes("-fullscreen", get_state("is_fullscreen"))
    save_app_states(app_states)

def toggle_dark_mode(event):
    '''Toggles dark mode for the application window.
    Args:
        event (tkinter.Event): The event that triggered dark mode toggle.
    '''
    set_state("is_dark_mode", not get_state("is_dark_mode"))
    switch_dark_mode_colors(get_state("is_dark_mode"))
    save_app_states(app_states)

def redraw_ui():
    # Clear the canvas and redraw all UI elements with updated colors.
    canvas.delete('success_text')
    padding_x = get_padding_x()
    padding_y = get_state("padding_y")
    create_windows(padding_x, padding_y)
    save_app_states(app_states)

HEIGHT_PERCENTAGE_LABEL = 12
HEIGHT_PERCENTAGE_TRANS_LABEL = 12
HEIGHT_PERCENTAGE_CURRENCY = 24

def create_transaction_history_label(x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    canvas.delete('trans')
    main_rect_width = calculate_height_of_item(main_rect_id)
    y2_label = y1 + (main_rect_width / 100 * HEIGHT_PERCENTAGE_LABEL)
    y2_currency = y2_label + (main_rect_width / 100 * HEIGHT_PERCENTAGE_CURRENCY)
    y2_trans = y2_currency + (main_rect_width / 100 * HEIGHT_PERCENTAGE_TRANS_LABEL)
    canvas.create_rectangle(x1, y2_currency, x2, y2_trans, 
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"),
                            tag='trans')
    
    canvas.create_text((x1 + x2) / 2, (y2_currency + y2_trans) / 2, 
                        text="Transaction history:", 
                        tag="trans",
                        font=(FONT, TEXT_SIZE_LARGE),
                        fill=get_state("text_color"))

    create_transaction_history(x1, x2, y2_currency, y2_trans, main_rect_id)

TRANSACTION_FONT = 'Consolas' # MUST BE MONOSPACE OTHERWISE EMPTY SPACE CALCULATING WILL FAIL
TEXT_SIZE_TRANSACTION = TEXT_SIZE_NORMAL
def get_width_of_text(font_to_use: str, text: str, text_size: str) -> int:
    font_used = font.Font(family=font_to_use, size=text_size)
    char_width = font_used.measure('0')
    return len(text) * char_width

transaction_history_widgets = []
visible_count = 9
start_idx = 0
SCROLLBAR_X_OFFSET = 25 

def create_transaction_history(x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    global visible_count
    global start_index
    main_rect_y2 = canvas.bbox(main_rect_id)[3]
    transaction_frame = Frame(root, bg=get_state('widget_fill_color'))
    transaction_frame.place(x=x1 + 1, y=y2 + 1, width=(x2 - x1) - SCROLLBAR_X_OFFSET, height=(main_rect_y2 - y2) - 3)
    num_of_transactions = len(transactions) - 1
    root.update_idletasks()

    for widget in transaction_history_widgets:
        widget.destroy()
    transaction_history_widgets.clear()
    transaction_history_widgets.append(transaction_frame)
    draw_scrollbar()
    if num_of_transactions == 0: return None
    #TODO: optimize if runs slowly

    label_width = (x2 - x1) - SCROLLBAR_X_OFFSET
    my_font = font.Font(family=TRANSACTION_FONT, size=TEXT_SIZE_TRANSACTION)
    char_width = my_font.measure('0')
    
    txn_keys = [k for k in reversed(transactions) if k != 'next_txn_id']

    for key in txn_keys[start_idx:start_idx + visible_count]:
        transaction = transactions[key]
        create_trnsc(transaction_frame, label_width, char_width, transaction)

def draw_scrollbar():
    global start_idx
    frame_width = transaction_history_widgets[0].winfo_width()
    frame_x = transaction_history_widgets[0].winfo_x()
    frame_y = transaction_history_widgets[0].winfo_y()
    frame_height = transaction_history_widgets[0].winfo_height()

    x1 = frame_x + frame_width
    y1 = frame_y - 1
    x2 = frame_x + frame_width + SCROLLBAR_X_OFFSET - 1
    y2 = frame_y + frame_height + 1
    print(x1, y1, x2, y2)
    # scrollbar border
    canvas.create_rectangle(x1, y1, x2, y2,
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"),
                            tag='trans')

    # scrollbar point
    canvas.delete('scroll')
    padding = 4
    width = SCROLLBAR_X_OFFSET - 1
    num_of_transactions = len(transactions) - 1
    point_height = 40  # Set your desired constant height here
    scroll_area = (y2 - y1) - point_height
    max_scroll = max(1, num_of_transactions - visible_count + 1)

    if max_scroll == 1:
        point_y = y1
    else:
        point_y = y1 + (scroll_area * start_idx / (max_scroll - 1))

    canvas.create_rectangle(x1 + padding, point_y + padding, x1 + width - padding, point_y + point_height - padding,
        fill=get_state("window_bg_color"),
        outline=get_state("widget_border_color"),
        width=get_state("widget_border_width"),
        tag='scroll')
    
def create_trnsc(transaction_frame, label_width, char_width, transaction, before=None):
    date = transaction["date"]
    year = date[:4]
    month = date[5:7]
    day = date[8:]

    date_text = f' {day}.{month}.{year} │ {transaction["time"][:-3]} │ ' 
    date_text_length = get_width_of_text(TRANSACTION_FONT, date_text, TEXT_SIZE_TRANSACTION)

    item_text = transaction["item"]
    item_text_length = get_width_of_text(TRANSACTION_FONT, item_text, TEXT_SIZE_TRANSACTION)

    empty_spaces_left = round(label_width - date_text_length) // char_width

    price_text = f'  {format_number(transaction["price"])} {transaction["currency"]}'
    price_text_length = get_width_of_text(TRANSACTION_FONT, price_text, TEXT_SIZE_TRANSACTION)

    spaces_for_item_text = (empty_spaces_left - (price_text_length // char_width) - 4)

    if item_text_length // char_width >= spaces_for_item_text:
        item_text = item_text[:spaces_for_item_text] + '...'
    else:
        item_text = item_text + ' ' * (spaces_for_item_text - len(item_text) + 3)
    label = Label(transaction_frame, 
                      text=f'{date_text}{item_text}{price_text}', 
                      font=f'{TRANSACTION_FONT} {TEXT_SIZE_TRANSACTION} {BOLD}',
                      bg=get_state('window_bg_color'),
                      fg=get_state('widget_text_color'),
                      bd=2,
                      relief='ridge',
                      justify='left',
                      anchor='w')
    label.pack(fill='x', before=before)
    root.update_idletasks()
    if before == None:
        transaction_history_widgets.append(label)
    else:
        transaction_history_widgets.insert(1, label) 
        # very very sloppy code but this is to account for scrolling up to optimize (terribleness)

def create_windows(padding_x: float, padding_y: float):
    '''Creates windows of the app.'''
    canvas.delete('allowance_window') # Remove existing allowance window if it exists (to avoid duplicates when redrawing UI)
    width = calculate_width_in_percent(padding_x, 50) # Width in percentages of window dimensions
    height = calculate_height_in_percent(padding_y, 50) # Height in percentages of window dimensions
    x1 = ONE_PERCENT_WIDTH * padding_x
    y1 = ONE_PERCENT_HEIGHT * padding_y
    x2 = width
    y2 = height
    main_rect_id = canvas.create_rectangle(x1, y1, x2, y2, 
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"),
                            tag="allowance_window",
                            )

    create_allowance_label(x1, x2, y1, y2, main_rect_id)
    create_transaction_window(padding_x, padding_y, x1, y1, x2, y2)
    create_transaction_history_label(x1, x2, y1, y2, main_rect_id)

def create_allowance_label(x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    canvas.delete('allowance') # Remove existing allowance label if it exists (to avoid duplicates when redrawing UI)
    y2_label = y1 + (calculate_height_of_item(main_rect_id) / 100 * HEIGHT_PERCENTAGE_LABEL)
    # Label background
    canvas.create_rectangle(x1, y1, x2, y2_label,
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"),
                            tag="allowance")
    
    # Centered text inside the label
    canvas.create_text((x1 + x2) / 2, (y1 + y2_label) / 2, 
                       text="Daily allowance:", 
                       tag="allowance",
                       font=(FONT, TEXT_SIZE_LARGE),
                       fill=get_state("text_color"))

    create_allowance_currency(x1, x2, y1, y2_label, main_rect_id)

def create_allowance_currency(x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    '''Creates a section for displaying the currency of the allowance.'''

    # Currency section (rectangle below the label)
    canvas.delete('allowance_currency') # Remove existing allowance currency if it exists (to avoid duplicates when redrawing UI)
    # Height of the currency section in percentages of the allowance window height
    y1_currency = y2
    y2_currency = y1_currency + (calculate_height_of_item(main_rect_id) / 100 * HEIGHT_PERCENTAGE_CURRENCY)
    canvas.create_rectangle(x1, y1_currency, x2, y2_currency,
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"),
                            tag="allowance_currency")

    # Centered text inside the currency section
    rolling_balance = format_number(get_state("rolling_balance"))
    canvas.create_text((x1 + x2) / 2, (y1_currency + y2_currency) / 2, 
                       text=f'{rolling_balance} {get_state("currency")}', 
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_XLARGE, BOLD),
                       fill=get_state("dynamic_text_color"))
    
    # Text on the top right corner of the currency section indicating current daily allowance increase
    daily_allowance = format_number(get_state("daily_allowance"))
    canvas.create_text(x2 - 10, y1_currency + 10, 
                       text=f'Tomorrow: +{daily_allowance} {get_state("currency")}', 
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                       fill=get_state("dynamic_text_color"),
                       anchor="ne")
    
    # Text on the top left corner of the currency section indicating budget
    budget = format_number(get_state("budget") - get_state("pending_spendings"))
    canvas.create_text(x1 + 10, y1_currency + 10,
                       text=f'Monthly budget left: {budget} {get_state("currency")}',
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                       fill=get_state("dynamic_text_color"),
                       anchor="nw")

    # Text on the top left corner of the currency section indicating pending spendings below the budget
    total_spent = format_number(get_state("total_monthly_spendings"))
    canvas.create_text(x2 - 10, y2_currency - 10,
                       text=f'- {total_spent} {get_state("currency")} total spendings',
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_XSMALL, BOLD, ITALIC),
                       fill=get_state("reserve_text_color"),
                       anchor="se")
    
    # Text on the bottom left corner of the currency section indicating reserve at end of month
    reserve = get_state("reserve_at_end_of_month")
    canvas.create_text(x1 + 10, y2_currency - 10,
                       text=f'Monthly reserve: {reserve:.2f} {get_state("currency")}',
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                       fill=get_state("reserve_text_color"),
                       anchor="sw")

def create_transaction_window(padding_x: float, padding_y: float, x1_prev: float, y1_prev: float, x2_prev: float, y2_prev: float):
    canvas.delete('transaction_window')

    # Create the transaction window
    width = calculate_width_in_percent(padding_x, 25)
    height = calculate_height_in_percent(padding_y, 50)
    x1 = x2_prev + ONE_PERCENT_WIDTH * padding_x
    y1 = y1_prev
    x2 = x1 + width
    y2 = y1 + height - ONE_PERCENT_HEIGHT * padding_y # Needs to be subtracted because it carries over from y1_prev
    main_rect_id = canvas.create_rectangle(x1, y1, x2, y2, 
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"),
                            tag="transaction_window",
                            )
    
    create_transaction_label(x1, y1, x2, y2, main_rect_id)

def create_transaction_label(x1: float, y1: float, x2: float, y2: float, main_rect_id: int):
    height_percentage_label = 12
    y2_label = y1 + (calculate_height_of_item(main_rect_id) / 100 * height_percentage_label)
    canvas.create_rectangle(x1, y1, x2, y2_label,
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"),
                            tag="transaction_window",
                            )
    canvas.create_text((x1 + x2) / 2, (y1 + y2_label) / 2, 
                       text="Add transaction:", 
                       tag="transaction_window",
                       font=(FONT, TEXT_SIZE_LARGE),
                       fill=get_state("text_color"))

    create_transaction_widgets(x1, y2_label, x2, y2, main_rect_id)

transaction_widgets = []
def create_transaction_widgets(x1: float, y1: float, x2: float, y2: float, main_rect_id: int):
    # Destroy old transaction widgets:
    for widget in transaction_widgets:
        widget.destroy()
    transaction_widgets.clear()

    # Calculate width, height and positions
    x_middle = (x1 + x2) / 2
    y_middle = (y1 + y2) / 2
    y_one_fourth = y1 + (y2 - y1) / 4.5 # 4.5 just works ok
    y_one_eighth = y1 + (y2 - y1) / 8
    y_two_fifths = y1 + (y2 - y1) * 0.4
    y_three_fourths = y1 + (y2 - y1) * 0.75
    y_bottom = y1 + (y2 - y1) * 0.9
    widget_width = (x2 - x1) / 2
    widget_height = (y2 - y1) / 8

    button_width = x1 / (8 + y1 / 25)
    button_height = button_width
    # Item Name Entry Text Window:
    item_name_entry = Entry(root, justify='center', font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
                        bd=get_state("widget_border_width") + 2,
                        relief='ridge',
                        foreground=get_state("widget_text_color"),
                        bg=get_state("window_bg_color"),
                        insertbackground=get_state("widget_text_color"))
    
    item_name_entry.place(x = x_middle, y = y_one_fourth,
                      width = widget_width,
                      height = widget_height,
                      anchor = 'center',)
    transaction_widgets.append(item_name_entry)

    # Text above the item entry window:
    canvas.create_text(x_middle, y_one_eighth, 
                       text="Transaction name:", 
                       tag="transaction_window",
                       font=(FONT, TEXT_SIZE_NORMAL, BOLD),
                       fill=get_state("text_color"))
    
    # Price Entry Text Window:
    price_entry = Entry(root, justify='center', font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
                        bd=get_state("widget_border_width") + 2,
                        relief='ridge',
                        foreground=get_state("widget_text_color"),
                        bg=get_state("window_bg_color"),
                        insertbackground=get_state("widget_text_color"))
    price_entry.place(x = x_middle, y = y_middle, 
                      width = widget_width,
                      height = widget_height,
                      anchor = 'center')
    transaction_widgets.append(price_entry)

    # Text above the price entry window:
    canvas.create_text(x_middle, y_two_fifths, 
                       text='Transaction price:', 
                       tag="transaction_window",
                       font=(FONT, TEXT_SIZE_NORMAL, BOLD),
                       fill=get_state("text_color"))
    
    x_currency_offset = widget_width / 2 + 10
    # Currency text next to the price entry window:
    canvas.create_text(x_middle + x_currency_offset, y_middle, 
                       text=f'{get_state("currency")}', 
                       tag="transaction_window",
                       font=(FONT, TEXT_SIZE_NORMAL, BOLD),
                       fill=get_state("text_color"),
                       anchor="w")

    # Add Transaction Button (+)
    add_tran_button = Button(root, text='+', justify='center', 
                             font=f'{FONT} {TEXT_SIZE_XLARGE} {BOLD}',
                             bd=get_state("widget_border_width") + 2,
                             relief='ridge',
                             foreground=get_state('widget_text_color'),
                             bg=get_state("window_bg_color"),
                             cursor='hand2',
                             activebackground=get_state('button_active_bg'),
                             activeforeground=get_state("button_active_fg"),
                             command=lambda: add_transaction(item_name_entry, price_entry, x_middle, y_bottom))
                             
    add_tran_button.place(x = x_middle, y = y_three_fourths,
                          width = button_width, height = button_height,
                          anchor='center',)
    transaction_widgets.append(add_tran_button)


def add_transaction(item_name_entry, price_entry, x_middle, y_bottom):
    item_name = item_name_entry.get()
    price = price_entry.get()
    price = price.replace(',','.') # Replace , with a . in case the user entered something like 20,45€
    # Check for edge cases:
    if not item_name or not price:
        messagebox.showerror("Error", "Please fill in all fields.")
        return None
    else:
        try:
            price = float(price)
            if math.isnan(price) or math.isinf(price): # Just in case a cheeky user tries to add inf, -inf or NaN
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Price must be a number.")
            return None
    if round(price, 2) <= 0:
        messagebox.showerror("Error", "Price must be greater than 0.")
        return None
    
    if price > get_state("rolling_balance"):
        messagebox.showwarning("Warning", "This transaction's price exceeds your daily allowance, meaning it will impact your future daily earnings.")
    rolling_bal_before = app_states["rolling_balance"]
    rolling_bal_after = max(0, rolling_bal_before - price) # Cap it at 0
    rolling_bal_hit = rolling_bal_before - rolling_bal_after
    set_state("pending_spendings", get_state("pending_spendings") + rolling_bal_hit) 
    if price >= rolling_bal_before:
        budget_hit = price - rolling_bal_before + get_state("pending_spendings")
        set_state("pending_spendings", 0)
        set_state("budget", app_states["budget"] - budget_hit)
        set_daily_allowance()
    else:
        budget_hit = 0
    # TODO: pending spendings likely will cause bugs later when deleting transactions, investigate
    # TODO: convert pending spendings between CZK and eur
    # TODO: fix bug where when a transaction in czk hits the allowance converting it back to eur and back to czk returns
    # a smaller value
    today = date.today().isoformat()
    current_time = get_current_time()
    # Create transaction as a dictionary:
    transaction_id = transactions['next_txn_id']
    transaction = {"date": today,
                   "time": current_time, 
                   "item": item_name, 
                   "price": price, 
                   "currency": get_state("currency"),
                   "czk_exchange_rate": get_state("CZK_RATE"),
                   "rolling_bal_hit": rolling_bal_hit,
                   "budget_hit": budget_hit}
    
    item_name_entry.delete(0, END)
    price_entry.delete(0, END)

    # TODO: Add more meta-data so that in the future when a transaction gets reverted, the program knows
    #       how much it took from the daily allowance and from the budget - then add it to the budget & daily allowance
    #       and recalculate
    
    # Add the transaction into transactions json with its own id:
    transactions[transaction_id] = transaction
    transactions['next_txn_id'] += 1

    # Subtract from rolling balance and/or budget:
    set_state("rolling_balance", app_states["rolling_balance"] - rolling_bal_hit)
    set_state("total_monthly_spendings", get_state("total_monthly_spendings") + price)
    save_transactions(transactions)
    save_app_states(app_states)
    redraw_ui()
    
    # Create success text confirming the item has been added
    canvas.delete('success_text')
    canvas.create_text(x_middle, y_bottom, 
                       text=f'Your transaction has been added to the history.\nPrice: {format_number(price)} {get_state("currency")}',
                       tag="success_text",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD),
                       fill=get_state("dynamic_text_color"),
                       anchor='center',
                       justify='center')

def switch_currency(event):
    if get_state("currency") == "€":
        new_currency = "CZK"
    else:
        new_currency = "€"
    money_amount = calculate_money_conversion(get_state("budget"), get_state("currency"), new_currency)
    reserve_amount = calculate_money_conversion(get_state("reserve_at_end_of_month"), get_state("currency"), new_currency)
    rolling_balance = calculate_money_conversion(get_state("rolling_balance"), get_state("currency"), new_currency)
    pending_spendings = calculate_money_conversion(get_state("pending_spendings"), get_state("currency"), new_currency)
    total_monthly_spendings = calculate_money_conversion(get_state("total_monthly_spendings"), get_state("currency"), new_currency)
    set_state("currency", new_currency)
    set_state("budget", money_amount)
    set_state("reserve_at_end_of_month", reserve_amount)
    set_state("rolling_balance", rolling_balance)
    set_state("pending_spendings", pending_spendings)
    set_state("total_monthly_spendings", total_monthly_spendings)
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
    if get_state("padding_y") < 10: # Limit maximum padding to 10%
        set_state("padding_y", get_state("padding_y") + 0.5)
        redraw_ui()

def decrease_padding(event):
    '''Decreases the padding around UI elements.'''
    if get_state("padding_y") > 0: # Limit minimum padding to 0%
        set_state("padding_y", get_state("padding_y") - 0.5)
        redraw_ui()

def add(event):
    add_daily_allowance()
    redraw_ui()

def scroll_transactions(event):
    global start_idx
    num_transactions = len(transactions) - 1
    if num_transactions == 0: return
    label_width = transaction_history_widgets[1].winfo_width()
    widget_under_mouse = root.winfo_containing(event.x_root, event.y_root)
    if widget_under_mouse in transaction_history_widgets:
        print(transaction_history_widgets)
        print(label_width)
        transaction_frame = transaction_history_widgets[0]
        my_font = font.Font(family=TRANSACTION_FONT, size=TEXT_SIZE_TRANSACTION)
        char_width = my_font.measure('0')

        if event.delta < 0 and start_idx + visible_count < num_transactions:
            transaction_history_widgets[1].destroy()
            transaction_history_widgets.pop(1)
            next_key = list(reversed([k for k in transactions if k != 'next_txn_id']))[start_idx + visible_count]
            transaction = transactions[next_key]
            create_trnsc(transaction_frame, label_width, char_width, transaction)
            start_idx += 1
            draw_scrollbar()

        elif event.delta > 0 and start_idx > 0:
            start_idx -= 1
            draw_scrollbar()
            transaction_history_widgets[-1].destroy()
            transaction_history_widgets.pop(-1)
            prev_key = list(reversed([k for k in transactions if k != 'next_txn_id']))[start_idx]
            transaction = transactions[prev_key]
            create_trnsc(transaction_frame, label_width, char_width, transaction, transaction_history_widgets[1])

set_daily_allowance()
create_windows(get_padding_x(), get_state("padding_y"))
draw_scrollbar()

root.bind("w", increase_padding)
root.bind("s", decrease_padding)
root.bind("<Escape>", toggle_fullscreen)

root.bind("<D>", toggle_dark_mode)
root.bind("<d>", toggle_dark_mode)
root.bind("a", add)
root.bind("<C>", switch_currency)
root.bind("<c>", switch_currency)
root.bind("<MouseWheel>", scroll_transactions)
center_screen()
root.mainloop()

# TODO: Save transactions inside a separate transactions JSON file.
# TODO: When implementing transaction history log, make sure to redraw it only if strictly necessary 
#       (during conversions & light/darkmode changes)
#       Possible optimization : load only the last 30 days of transactions, maybe even just 14 days
# TODO: Add a way to log spendings and view them in a list, with dates.
# TODO: When user adds a spending, check whether its larger than their rolling balance.
#       if not, add the amount of spendings to pending_spendings variable.
#       If yes, subtract pending_spendings + the remainder from price from budget.
#       Afterwards, recalculate daily budget based on days left in the month. 
#       ALWAYS RECALCULATE DAILY ALLOWANCE INCREASE **ONLY IF** THE BUDGET CHANGES VALUE!!!

# TODO: Add a way to reset the rolling balance to the initial budget at the start of a new month.
# TODO: Calculate rolling balance based on current date.
# TODO: Add graphs to visualize spendings over time.
# TODO: Reset daily allowance and rolling balance at the start of a new month (with notifications how much they saved).
# TODO: 
