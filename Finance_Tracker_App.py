from tkinter import *
from tkinter import messagebox # For displaying message boxes
from tkinter import font
import json # For saving and loading settings
from datetime import date, timedelta
from datetime import datetime
import math 
import calendar
import os # For checking if a file exists

root = Tk()
spendings = 100

# Please note a lot of the code had to be rushed due to time constraints, which is why some of it is
# so spaghetti :)

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
    return days_in_month - day # +1 to include today

def get_days_in_curr_month() -> int:
    today = date.today()
    year = today.year
    month = today.month
    days_in_month = calendar.monthrange(year, month)[1]
    return days_in_month

def get_days_in_month(month: int, year: int) -> int:
    return calendar.monthrange(year, month)[1]

def create_data_json_if_nonexistent(file_path=FINANCE_DATA_PATH):
    default_app_states = {
    "budget": 0,
    "currency": "€",
    "reserve_at_end_of_month": 0,
    "total_monthly_spendings": 0,
    "daily_allowance": 0, # calculated in code
    "rolling_balance": 0, # calculated in code
    "CZK_RATE": 24.25,
    "days_left_in_month": 0, # calculated in code
    "window_bg_color": "#CBCBCB",
    "widget_border_color": "#000000",
    "widget_fill_color": "#FFFFFF",
    "widget_border_width": 2,
    "widget_text_color": "#000000",
    "button_active_fg": "#222222",
    "button_active_bg": "#E6E6E6",
    "current_month": 0, # calculated in code
    "current_year": 0, # calculated in code
    "current_day": 0, # calculated in code
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

def get_padding_x():
    return app_states["padding_y"] / (window_width / window_height)

def get_state(key):
    return app_states[key]

def set_state(key, value):
    app_states[key] = value

def calculate_money_conversion(money: float, currency_before: str, currency_after: str, exchange_rate: float) -> float:
    exchange_rates = {
        "€": {"CZK": exchange_rate},
        "CZK": {"€": 1/exchange_rate}
    }
    if currency_before == currency_after: return money
    if currency_before not in exchange_rates or currency_after not in exchange_rates[currency_before]:
        raise ValueError(f"Conversion rate from {currency_before} to {currency_after} not available.")
    
    conversion_rate = exchange_rates[currency_before][currency_after]
    return money * conversion_rate

def calculate_daily_allowance(budget: float, reserve: float) -> float:
    if get_state('days_left_in_month') == 0:
        allowance_per_day = 0
    else:
        allowance_per_day = (budget - reserve) / get_state('days_left_in_month')
    return allowance_per_day

def set_daily_allowance():
    set_state('days_left_in_month', get_days_left_in_curr_month())
    daily_allowance = calculate_daily_allowance(get_state("budget"), get_state("reserve_at_end_of_month"))
    set_state("daily_allowance", daily_allowance)

def add_daily_allowance():
    set_state("rolling_balance", get_state("rolling_balance") + get_state("daily_allowance"))
    set_state("budget", get_state("budget") - get_state("daily_allowance"))


# Window dimensions and scaling configurations
WINDOW_SCALING_PERCENT = get_state("WINDOW_SCALING_PERCENT") # Percentage of screen size to use for window dimensions
window_width = root.winfo_screenwidth() * (WINDOW_SCALING_PERCENT / 100)
window_height = root.winfo_screenheight() * (WINDOW_SCALING_PERCENT / 100)
WINDOW_X_CENTER = window_width / 2
WINDOW_Y_CENTER = window_height / 2
ONE_PERCENT_HEIGHT = window_height / 100
ONE_PERCENT_WIDTH = window_width / 100

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
def set_year():
    today = datetime.today()
    set_state('current_year', today.year)
    save_app_states(app_states)
def set_month():
    today = datetime.today()
    set_state('current_month', today.month)
    save_app_states(app_states)
def set_today():
    today = datetime.today()
    set_state('current_day', today.day)
    save_app_states(app_states)

if app_states["current_day"] == 0 or app_states["current_month"] == 0 or app_states["current_year"] == 0:
    app_states['days_left_in_month'] = get_days_left_in_curr_month()
    set_today()
    set_month()
    set_year()
    app_states = load_app_states()

def restore_default_values():
    set_state('budget', 0)
    set_state('rolling_balance', 0)
    set_state('reserve_at_end_of_month', 0)
    set_state('total_monthly_spendings', 0)
    save_app_states(app_states)

def check_days_passed_and_set_dates():
    global year_to_show, month_to_show
    today = datetime.today()
    day_today = today.day
    month_today = today.month
    year_today = today.year
    print(f"current (last saved): {get_state('current_day')} {get_state('current_month')} {get_state('current_year')}\nupdated: {day_today} {month_today} {year_today}")

    # calculate day difference
    # First check if a new year has started - if so, reset and inform about savings and reset
    if year_today != get_state('current_year'):
        # New year has started
        messagebox.showinfo('Happy new year!', f"A new year has started. Your budget has been reset.\nIn your last monthly session, you saved {format_number(get_state('budget') + get_state('rolling_balance'))} {get_state('currency')}!\nYou spent a total of {format_number(get_state('total_monthly_spendings'))} {get_state('currency')}.")
        restore_default_values()
    elif month_today != get_state('current_month'):
        # New month has started
        messagebox.showinfo('New month!', f"A new month has started. Your budget has been reset.\nIn your last monthly session, you saved {format_number(get_state('budget') + get_state('rolling_balance'))} {get_state('currency')}!\nYou spent a total of {format_number(get_state('total_monthly_spendings'))} {get_state('currency')}.")
        restore_default_values()
    elif day_today != get_state('current_day'):
        # Calculates day difference
        day_diff = day_today - get_state('current_day')
        if day_diff == 1:
            has_text = 'has'
            day_txt = 'day'
        else:
            has_text = 'have'
            day_txt = 'days'
        for i in range(day_diff):
            add_daily_allowance()
        messagebox.showinfo('Your daily allowance has increased!', f"{day_diff} {day_txt} {has_text} passed since the last time you opened the app. During that time, your daily allowance increased by {format_number(get_state('daily_allowance') * day_diff)} {get_state('currency')}! Happy spendings!")

    set_today()
    set_month()
    set_year()
    year_to_show = get_state('current_year')
    month_to_show = get_state('current_month')
    redraw_ui()

canvas = Canvas(root, width = window_width, height = window_height, bg = get_state("window_bg_color"))
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
    x = (screen_width / 2) - (window_width / 2)
    y = (screen_height / 2) - (window_height / 2)

    root.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))
    TM = ' (Samuel Ondroš 2025 ©)'
    root.title(TITLE + TM)

root.attributes("-fullscreen", get_state("is_fullscreen"))

def exit_app(event):
    '''Exits the app.'''
    q = messagebox.askyesno('Warning', 'Are you sure you want to exit the application?')
    if q == True:
        save_app_states(app_states)
        root.destroy()

def toggle_dark_mode():
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
    canvas.delete('tooltip')
    padding_x = get_padding_x()
    padding_y = get_state("padding_y")
    set_daily_allowance()
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
                        text="Transaction History", 
                        tag="trans",
                        font=(FONT, TEXT_SIZE_LARGE),
                        fill=get_state("text_color"))

    canvas.create_text(x1 + 10, (y2_currency + y2_trans) / 2, 
                        text="LMB = show full transaction info", 
                        tag="trans",
                        font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                        fill=get_state("dynamic_text_color"),
                        anchor='w')
    
    canvas.create_text(x2 - 10, (y2_currency + y2_trans) / 2, 
                        text="RMB = delete transaction", 
                        tag="trans",
                        font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                        fill=get_state("dynamic_text_color"),
                        anchor='e')
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
        create_trnsc(key, transaction_frame, label_width, char_width, transaction)

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

selected_txn = None
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Delete", command=lambda: delete_transaction(selected_txn))

def create_trnsc(txn_key, transaction_frame, label_width, char_width, transaction, before=None):
    date = transaction["date"]
    year = date[:4]
    month = date[5:7]
    day = date[8:]

    budget_hit = transaction['budget_hit']
    date_text = f' {day}.{month}.{year} │ {transaction["time"][:-3]} │ ' 
    date_text_length = get_width_of_text(TRANSACTION_FONT, date_text, TEXT_SIZE_TRANSACTION)

    item_text = transaction["item"]
    item_text_length = get_width_of_text(TRANSACTION_FONT, item_text, TEXT_SIZE_TRANSACTION)

    empty_spaces_left = round(label_width - date_text_length) // char_width
    if budget_hit != 0:
        budget_b = ' (B!)'
    else:
        budget_b = ''
    price_text = f'  {format_number(transaction["price"])} {transaction["currency"]}{budget_b}'
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
    label.update_idletasks()
    label.txn_id = txn_key
    label.bind("<Button-3>", lambda e, lbl = label: show_context_menu(e, lbl))
    label.bind("<Button-1>", lambda e, lbl = label: show_info_in_toolbar(e, lbl))
    if before == None:
        transaction_history_widgets.append(label)
    else:
        transaction_history_widgets.insert(1, label) 
        # very very sloppy code but this is to account for scrolling up to optimize (terribleness)

info_box = None
def show_info_in_toolbar(event, label):
    global selected_txn, info_box
    selected_txn = label.txn_id
    if info_box and info_box.winfo_exists():
        info_box.destroy()
        info_box = None
    # TXN INFO:
    txn_text = transactions[selected_txn]['item']
    txn_date = transactions[selected_txn]['date']
    year = txn_date[:4]
    month = txn_date[5:7]
    day = txn_date[8:]
    txn_date_text = f'{day}.{month}.{year}'
    txn_time = transactions[selected_txn]['time']
    txn_exch = transactions[selected_txn]['czk_exchange_rate']

    txn_currency = transactions[selected_txn]['currency']
    txn_budget_hit = transactions[selected_txn]['budget_hit']
    txn_da_hit = transactions[selected_txn]['rolling_bal_hit']
    if txn_currency == '€':
        txn_price_in_eur = format_number(transactions[selected_txn]['price'])
        txn_price_in_czk = format_number(calculate_money_conversion(transactions[selected_txn]['price'], '€', 'CZK', txn_exch))
        txn_bh_in_eur = format_number(txn_budget_hit)
        txn_bh_in_czk = format_number(calculate_money_conversion(txn_budget_hit, '€', 'CZK', txn_exch))
        txn_da_in_eur = format_number(txn_da_hit)
        txn_da_in_czk = format_number(calculate_money_conversion(txn_da_hit, '€', 'CZK', txn_exch))
        txn_price_text = f'{txn_price_in_eur} € ({txn_price_in_czk} CZK)'
        txn_bh_text = f'{txn_bh_in_eur} € ({txn_bh_in_czk} CZK)'
        txn_da_text = f'{txn_da_in_eur} € ({txn_da_in_czk} CZK)'
    else:
        # its in czk
        txn_price_in_czk = format_number(transactions[selected_txn]['price'])
        txn_price_in_eur = format_number(calculate_money_conversion(transactions[selected_txn]['price'], 'CZK', '€', txn_exch))
        txn_bh_in_eur = format_number(calculate_money_conversion(txn_budget_hit, 'CZK', '€', txn_exch))
        txn_bh_in_czk = format_number(txn_budget_hit)
        txn_da_in_czk = format_number(txn_da_hit)
        txn_da_in_eur = format_number(calculate_money_conversion(txn_da_hit, 'CZK', '€', txn_exch))
        txn_price_text = f'{txn_price_in_czk} CZK ({txn_price_in_eur} €)'
        txn_bh_text = f'{txn_bh_in_czk} CZK ({txn_bh_in_eur} €)'
        txn_da_text = f'{txn_da_in_czk} CZK ({txn_da_in_eur} €)'

    x = label.winfo_rootx() + label.winfo_width() + 5  # right of label
    y = label.winfo_rooty()
    info_box = Toplevel(root)
    info_box.wm_overrideredirect(True)  # no window frame
    info_box.geometry(f"+{x}+{y}")

    Label(info_box, text=f'Full name : {txn_text}\nInput date : {txn_date_text}\nInput time : {txn_time}\nTransaction exchange rate : 1€ = {format_number(txn_exch)} CZK\nPrice : {txn_price_text}\n------------------------------------------------\n(B!) Spent from budget : {txn_bh_text}\nSpent from daily allowance: {txn_da_text}', 
             bg="lightyellow", justify='left',
             relief="solid", borderwidth=1, wraplength=400,
             font=(TRANSACTION_FONT, TEXT_SIZE_SMALL)).pack(ipadx=6, ipady=6)
    
    for l in transaction_history_widgets[1:]:
        l.config(bg=get_state('window_bg_color'))
    label.config(bg='lightblue')
    root.bind('<Button-1>', click_away)
    root.bind('<Button-2>', click_away)
    root.bind('<Button-3>', click_away)

def click_away(event):
    global info_box
    if not info_box:
        return
    
    info_box.destroy()
    info_box = None
    for l in transaction_history_widgets[1:]:
        l.config(bg=get_state('window_bg_color'))
    root.unbind('<Button-1>')
    root.unbind('<Button-2>')
    root.unbind('<Button-3>')
def show_context_menu(event, label):
    global selected_txn
    selected_txn = label.txn_id
    for l in transaction_history_widgets[1:]:
        l.config(bg=get_state('window_bg_color'))
    label.config(bg='lightblue')
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()
        label.config(bg=get_state("window_bg_color"))

def delete_transaction(txn_id):
    global start_idx

    transaction = transactions[txn_id]
    rolling_bal_hit = transaction['rolling_bal_hit']
    budget_hit = transaction['budget_hit']
    currency_used = transaction['currency']
    czk_rate = transaction['czk_exchange_rate']

    current_currency = get_state('currency')
    price = transaction['price']

    if currency_used != current_currency:
        rolling_bal_hit = calculate_money_conversion(rolling_bal_hit, currency_used, current_currency, czk_rate)
        budget_hit = calculate_money_conversion(budget_hit, currency_used, current_currency, czk_rate)
        price = calculate_money_conversion(price, currency_used, current_currency, czk_rate)

    if budget_hit > 0:
        budget_refund_text = f' and add {format_number(budget_hit)} {current_currency} to the budget'
    else:
        budget_refund_text = ''
    result = messagebox.askyesno('Are you sure?', f'Deleting this transaction will refund you {format_number(rolling_bal_hit)} {current_currency} in daily allowance{budget_refund_text}. Deletion cannot be reverted!')
    if result == False: return None
    # Refund
    set_state('budget', get_state('budget') + budget_hit)
    set_state('rolling_balance', get_state('rolling_balance') + rolling_bal_hit)
    set_state('total_monthly_spendings', max(0, get_state('total_monthly_spendings') - price))

    transactions.pop(txn_id, None)
    # lord forgive me for this:
    for i, label in enumerate(transaction_history_widgets):
        if i == 0: continue
        if label.txn_id == txn_id:
            label.destroy()
            transaction_history_widgets.pop(i)
            break
    if start_idx > 0: start_idx -= 1
    save_transactions(transactions)
    set_daily_allowance()
    redraw_ui()

month_to_show = get_state("current_month")
year_to_show = get_state("current_year")

bar_tooltip_id = None
rect_tooltip_id = None
# 603
    
def on_enter(event):
    global bar_tooltip_id
    global rect_tooltip_id
    c = event.widget
    bar_id = c.find_withtag("current")[0]
    tags = c.gettags(bar_id)
    price_tag = tags[1]
    price_tag_f = price_tag.replace(',', '.')
    price_tag_f = price_tag_f[:price_tag_f.index(' ')]
    if event.x > window_width * 0.75:
        anchor = 'ne'
        x_offset = -10
    else:
        anchor = 'nw'
        x_offset = 10

    text_clr = c.itemcget(bar_id, 'outline')
    bar_tooltip_id = c.create_text(event.x + x_offset, event.y + 20,
                                        text=f'{price_tag}',
                                        anchor=anchor,
                                        fill=text_clr,
                                        font=f'{FONT} {TEXT_SIZE_SMALL} {BOLD} {ITALIC}',
                                        tag = 'tooltip')
    bbox = c.bbox(bar_tooltip_id)
    rect_tooltip_id = c.create_rectangle(bbox, 
                                              fill=get_state('widget_fill_color'), 
                                              outline=text_clr, 
                                              tag='tooltip')
    canvas.tag_raise(bar_tooltip_id, rect_tooltip_id)
    #c.create_rectangle()
def on_leave(event):
    global bar_tooltip_id
    global rect_tooltip_id
    if bar_tooltip_id:
        canvas.delete('tooltip')
        event.widget.delete(bar_tooltip_id)
        event.widget.delete(rect_tooltip_id)
        rect_tooltip_id = None
        bar_tooltip_id = None
def on_motion(event):
    global bar_tooltip_id
    global rect_tooltip_id
    if bar_tooltip_id:
        event.widget.coords(bar_tooltip_id, event.x, event.y + 20)
    if rect_tooltip_id:
        bbox = canvas.bbox(bar_tooltip_id)
        event.widget.coords(rect_tooltip_id, bbox)

graph_header_id = None
last_midnight_check = None
def initiate_timer():
    global last_midnight_check, month_to_show, year_to_show
    canvas.delete('timer')
    today = datetime.today()
    upd_day = today.day
    upd_month = today.month
    upd_year = today.year
    today_str = date.today().isoformat()
    current_time = get_current_time()
    x1, y1, x2, y2 = canvas.coords(graph_header_id)
    canvas.create_text(x2 - 10, y2 - abs(y1 - y2) / 2,
                       text=current_time,
                       anchor='e',
                       tag="timer",
                       font=(FONT, TEXT_SIZE_LARGE),
                       fill=get_state("dynamic_text_color"))
    canvas.create_text(x1 + 10, y2 - abs(y1 - y2) / 2,
                       text=f"{get_state('current_day')}.{get_state('current_month')}.{get_state('current_year')}",
                       anchor='w',
                       tag="timer",
                       font=(FONT, TEXT_SIZE_LARGE),
                       fill=get_state("dynamic_text_color"))
    # Check each second if day, month or year updated (horrible I know)
    if current_time == '00:00:00' and last_midnight_check != today_str:
        print('I RAN')
        last_midnight_check = today_str
        if get_state('current_year') != upd_year:
            # Year changed
            messagebox.showinfo('Happy new year!', f"A new year has started. Your budget has been reset.\nIn your last monthly session, you saved {format_number(get_state('budget') + get_state('rolling_balance'))} {get_state('currency')}!\nYou spent a total of {format_number(get_state('total_monthly_spendings'))} {get_state('currency')}.")
            restore_default_values()
        elif get_state('current_month') != upd_month:
            # month changed
            messagebox.showinfo('New month!', f"A new month has started. Your budget has been reset.\nIn your last monthly session, you saved {format_number(get_state('budget') + get_state('rolling_balance'))} {get_state('currency')}!\nYou spent a total of {format_number(get_state('total_monthly_spendings'))} {get_state('currency')}.")
            restore_default_values()
        elif get_state('current_day') != upd_day:
            # day changed
            add_daily_allowance()
            messagebox.showinfo('Daily allowance increased!', f"Your daily allowance has increased by {format_number(get_state('daily_allowance'))} {get_state('currency')}")
        
        set_today()
        set_month()
        set_year()
        set_daily_allowance()
        year_to_show = get_state('current_year')
        month_to_show = get_state('current_month')
        redraw_ui()
    canvas.after(1000, initiate_timer)

    
def create_graph(padding_x: float, padding_y: float, x1: float, x2: float, y1: float, y2: float, main_rect_id: int):
    global graph_header_id
    # OH GOD MONSTER FUNCTION INBOUND I REPEAT MO
    canvas.delete('graph')
    canvas.delete('bar')
    canvas.delete('white_line')
    canvas.delete('line_cost')
    canvas.delete('bar_cost')
    width = calculate_width_in_percent(padding_x, 100)
    height = calculate_height_in_percent(padding_y, 44.5)
    height_header = calculate_height_in_percent(0, 5.5)
    x1_g = ONE_PERCENT_WIDTH * padding_x
    y1_g = height * 1.247191011235955 + ONE_PERCENT_HEIGHT * padding_y
    x2_g = width
    y2_g = height * 2.247191011235955 + ONE_PERCENT_HEIGHT * padding_y
    # .247191011235955 because 100 / 44.5 = (whatever).247191011235955
    today = datetime.now()
    current_day = today.day
    current_month = today.month
    current_year = today.year
    month_num = month_to_show
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month_text = months[month_num - 1] 
    
    main_box = canvas.create_rectangle(x1_g, y1_g, x2_g, y2_g,
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"),
                            tag="graph",
                            )
    
    graph_header_id = canvas.create_rectangle(x1_g, y1_g - height_header, x2_g, y1_g, 
                                     fill=get_state("widget_fill_color"),
                                     outline=get_state("widget_border_color"),
                                     width=get_state("widget_border_width"),
                                     tag="graph")
    
    canvas.create_text(abs(x1_g + x2_g) / 2, abs(2 * y1_g - height_header) / 2, 
                       text=f'{month_text} {year_to_show} Daily Spendings',
                        tag="graph",
                        font=(FONT, TEXT_SIZE_LARGE),
                        fill=get_state("text_color"))

    initiate_timer()
    day_amount = get_days_in_month(month_to_show, year_to_show)
    start_date = date(year_to_show, month_to_show, 1)

    date_range = [(start_date + timedelta(days=i)).isoformat() for i in range(day_amount)]
    date_price_sums = {}

    # Calculate how much money was spent on each day
    current_currency = get_state('currency')
    for key, transaction in transactions.items():
        if key == 'next_txn_id': continue
        txn_date = transaction['date']
        if txn_date in date_range:
            price = transaction['price']
            trans_currency = transaction['currency']
            exch_rate = transaction['czk_exchange_rate']
            if trans_currency != current_currency:
                price = calculate_money_conversion(price, trans_currency, current_currency, exch_rate)
            if txn_date in date_price_sums.keys():
                date_price_sums[txn_date] += price
            else:
                date_price_sums[txn_date] = price

    w = calculate_width_of_item(main_box)
    interval = w / (day_amount)
    
    x_offset = 3
    y_offset = 17
    total_budget = get_state('budget') + get_state('total_monthly_spendings') + get_state('rolling_balance') - get_state('reserve_at_end_of_month')

    if date_price_sums != {}:
        highest_day_sum = max(list(date_price_sums.values()))
    else:
        highest_day_sum = 0

    if get_state('daily_allowance') > 0:
        # There are still days left in month
        initial_max = get_state('daily_allowance') * 4
    else:
        # 0 days left - calculate initial max as 75 € or converted czk value
        if get_state('currency') == '€':
            initial_max = 50
        else:
            initial_max = calculate_money_conversion(50, '€', 'CZK', get_state('CZK_RATE'))
    # TODO: fix this
    max_graph_amount = max(initial_max, highest_day_sum)
    min_lines = 8
    max_lines = 15
    min_amount = initial_max
    max_amount = total_budget
    
    if max_amount == min_amount:
        line_amount = min_lines
    else:
        scale = (max_graph_amount - min_amount) / (max_amount - min_amount)
        scale = max(0, min(1, scale))  # Clamp between 0 and 1
        line_amount = round(min_lines + (max_lines - min_lines) * scale)
    height_interval = height / line_amount

    for i, dates in enumerate(date_range):
        day = dates[8:]
        month = dates[5:7]
        year = dates[:4]
        if int(day) == current_day and int(month) == current_month and int(year) == current_year:
            day_clr = get_state('reserve_text_color')
        else:
            day_clr = get_state('text_color')
        canvas.create_text(x1_g + interval * i + interval / 2 - x_offset, y2_g - y_offset, 
                           text=f'{day}.{month}', 
                           tag='graph',
                           font=f'{FONT} {TEXT_SIZE_XSMALL} {BOLD}',
                           anchor='center',
                           fill=day_clr)
        if dates in date_price_sums.keys():
            if date_price_sums[dates] < get_state('daily_allowance') and month_to_show == get_state('current_month') and year_to_show == get_state('current_year'):
                fill_clr_bar = "#83CC95"
                outline_bar = get_state('dynamic_text_color')
                if get_state('is_dark_mode') == True:
                    fill_clr_bar = "#37954E"
            else:
                fill_clr_bar = "#601A1A"
                outline_bar = get_state('reserve_text_color')
                if get_state('is_dark_mode') == False:
                    outline_bar, fill_clr_bar = fill_clr_bar, outline_bar
            bar_x1 = x1_g + interval * i - x_offset + interval * 0.2
            bar_y1 = y2_g - height_interval
            bar_x2 = x1_g + interval * i + interval - x_offset - interval * 0.2
            bar_y2 = y2_g - height_interval - ((height - height_interval * 2) / max_graph_amount) * date_price_sums[dates]
            bar = canvas.create_rectangle(bar_x1, bar_y1, bar_x2, bar_y2,
                                    fill=fill_clr_bar,
                                    width=get_state('widget_border_width'),
                                    outline=outline_bar,
                                    tag=('bar', f'{format_number(date_price_sums[dates])} {get_state("currency")}'))
            
            canvas.tag_bind(bar, "<Enter>", on_enter)
            canvas.tag_bind(bar, "<Leave>", on_leave)
            canvas.tag_bind(bar, "<Motion>", on_motion)

    # creates lines and their text for spendings
    for j in range(day_amount - 1):
        canvas.create_line(x1_g - x_offset + interval * (j+1), 
                           y2_g - 1, 
                           x1_g - x_offset + interval * (j+1),
                           y1_g + 1 + height_interval,
                           tag='graph',
                           fill = get_state('window_bg_color'),
                           width = get_state('widget_border_width'))
    
    for i in range(line_amount - 1):
        if i == 0: # First line:
            fill_clr = get_state('widget_border_color')
            fill_clr_text = "#474747" if get_state('is_dark_mode') == True else "#DCC5C5"
            tag = 'white_line'
        elif i == line_amount - 2: # Last line:
            fill_clr = get_state('reserve_text_color')
            fill_clr_text = get_state('reserve_text_color')
            tag = 'graph'
        else:
            fill_clr = get_state('window_bg_color')
            fill_clr_text = "#474747" if get_state('is_dark_mode') == True else "#DCC5C5"
            tag = 'graph'
        canvas.create_text(x2_g - x_offset, y2_g - height_interval * (i + 1) - y_offset, 
                           text=f'{format_number((max_graph_amount / (line_amount - 2)) * i)} {get_state("currency")}',
                           tag='line_cost',
                           font=f'{FONT} {TEXT_SIZE_XSMALL} {BOLD} {ITALIC}',
                           anchor='ne',
                           fill=fill_clr_text)
        
        canvas.create_line(x1_g + 1, y2_g - height_interval * (i + 1), x2_g - 1, y2_g - height_interval * (i + 1),
                           tag = tag,
                           fill = fill_clr,
                           width = get_state('widget_border_width'))
    
    # Create daily allowance line (below it = green)
    # only on current month and year
    if month_to_show == get_state('current_month') and year_to_show == get_state('current_year'):
        if get_state('daily_allowance') < max_graph_amount: # dont draw the DA line if it is out of bounds
            y2_da = ((height - height_interval * 2) / max_graph_amount) * get_state('daily_allowance')
            canvas.create_line(x1_g + 1, y2_g - height_interval - y2_da, x2_g - 1, y2_g - height_interval - y2_da,
                               tag='graph',
                               fill = get_state('dynamic_text_color'),
                               width = get_state('widget_border_width'))
    
    canvas.tag_raise('line_cost')
    canvas.tag_raise('bar')
    canvas.tag_raise('white_line')

def create_toolbar(padding_x, padding_y, x1, x2, y1, y2):
    canvas.delete('toolbar')
    width = calculate_width_in_percent(padding_x, 25)
    height = calculate_height_in_percent(padding_y, 50)
    x1_t = x1 + width + ONE_PERCENT_WIDTH * padding_x
    y1_t = ONE_PERCENT_HEIGHT * padding_y
    x2_t = x2 + width + ONE_PERCENT_WIDTH * padding_x
    y2_t = y1_t + height - ONE_PERCENT_HEIGHT * padding_y
    
    main_rect_id = canvas.create_rectangle(x1_t, y1_t, x2_t, y2_t, 
                            tag='toolbar',
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"))
    
    header_y2 = y1 + (abs(y2_t - y1_t) / 100) * 12 # 24%

    canvas.create_rectangle(x1_t, y1_t, x2_t, header_y2, 
                            tag='toolbar',
                            fill=get_state("widget_fill_color"),
                            outline=get_state("widget_border_color"),
                            width=get_state("widget_border_width"))
    # create header text
    canvas.create_text((x1_t + x2_t) / 2, (header_y2 + y1_t) / 2, 
                            text="Toolbar", 
                            tag="toolbar",
                            font=(FONT, TEXT_SIZE_LARGE),
                            fill=get_state("text_color"))
    
    create_toolbar_widgets(x1_t, header_y2, x2_t, y2_t, main_rect_id)
    

toolbar_widgets = []
def create_toolbar_widgets(x1, y1, x2, y2, main_rect_id):
    for widget in toolbar_widgets:
        widget.destroy()
    toolbar_widgets.clear()
    
    text_offset = 15

    rect_area_height = y2 - y1
    rect_area_width = x2 - x1

    x_bdgt_labels = x1 + rect_area_width / 25
    x_bdgt_buttons = x2 - rect_area_width / 25
    y_interval = rect_area_height / 10
    y_set_budget = y1 + y_interval
    y_set_reserve = y1 + y_interval * 3
    y_set_exchange = y1 + y_interval * 5
    y_separation_line = y1 + y_interval * 7

    widget_width = rect_area_width / 2
    widget_height = rect_area_height / 8

    button_width = widget_height
    button_height = widget_height

    # Create entry field for increasing budget:
    #--------------------------------------------
    set_budget_entry = Entry(root, justify='left', font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
                        bd=get_state("widget_border_width") + 2,
                        relief='ridge',
                        foreground=get_state("widget_text_color"),
                        bg=get_state("window_bg_color"),
                        insertbackground=get_state("widget_text_color"))
    
    set_budget_entry.place(x = x_bdgt_labels, y = y_set_budget,
                      width = widget_width,
                      height = widget_height,
                      anchor = 'nw')
    toolbar_widgets.append(set_budget_entry)
    # And its text above:
    canvas.create_text(x_bdgt_labels + widget_width / 2, y_set_budget - text_offset, 
                       text="Set monthly budget to:", 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_NORMAL, BOLD),
                       fill=get_state("dynamic_text_color"),
                       anchor = 'center')
    
    # And the currency text next to it:
    canvas.create_text(x_bdgt_labels + widget_width + 10, y_set_budget + widget_height / 2, 
                       text=get_state("currency"), 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_NORMAL, BOLD),
                       fill=get_state("text_color"),
                       anchor = 'w')

    # And the button:
    set_budget_button = Button(root, text='+', justify='center', 
                             font=f'{FONT} {TEXT_SIZE_XLARGE} {BOLD}',
                             bd=get_state("widget_border_width") + 2,
                             relief='ridge',
                             foreground=get_state('dynamic_text_color'),
                             bg=get_state("window_bg_color"),
                             cursor='hand2',
                             activebackground=get_state('button_active_bg'),
                             activeforeground=get_state("button_active_fg"),
                             command=lambda: set_budget(set_budget_entry))
                             
    set_budget_button.place(x = x_bdgt_buttons, y = y_set_budget,
                          width = button_width, height = button_height,
                          anchor='ne')
    toolbar_widgets.append(set_budget_button)


    #--------------------------------------------
    # Create entry field for setting monthly reserve:
    #--------------------------------------------
    set_reserve_entry = Entry(root, justify='left', font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
                        bd=get_state("widget_border_width") + 2,
                        relief='ridge',
                        foreground=get_state("widget_text_color"),
                        bg=get_state("window_bg_color"),
                        insertbackground=get_state("widget_text_color"))
    
    set_reserve_entry.place(x = x_bdgt_labels, y = y_set_reserve,
                      width = widget_width,
                      height = widget_height,
                      anchor = 'nw')
    toolbar_widgets.append(set_reserve_entry)
    # And its text above:
    canvas.create_text(x_bdgt_labels + widget_width / 2, y_set_reserve - text_offset, 
                       text="Set monthly reserve to:",
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_NORMAL, BOLD),
                       fill=get_state("reserve_text_color"),
                       anchor = 'center')
    # And the currency text next to it:
    canvas.create_text(x_bdgt_labels + widget_width + 10, y_set_reserve + widget_height / 2, 
                       text=get_state("currency"), 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_NORMAL, BOLD),
                       fill=get_state("text_color"),
                       anchor = 'w')

    # And the button:
    set_reserve_button = Button(root, text='+', justify='center', 
                             font=f'{FONT} {TEXT_SIZE_XLARGE} {BOLD}',
                             bd=get_state("widget_border_width") + 2,
                             relief='ridge',
                             foreground=get_state('reserve_text_color'),
                             bg=get_state("window_bg_color"),
                             cursor='hand2',
                             activebackground=get_state('button_active_bg'),
                             activeforeground=get_state("button_active_fg"),
                             command=lambda: set_reserve(set_reserve_entry))
                             
    set_reserve_button.place(x = x_bdgt_buttons, y = y_set_reserve,
                          width = button_width, height = button_height,
                          anchor='ne')
    toolbar_widgets.append(set_reserve_button)
    #--------------------------------------------------
    # Create set eur to czk exchange rate
    # --------------------------------------------------
    set_czk_exchange = Entry(root, justify='left', font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
                        bd=get_state("widget_border_width") + 2,
                        relief='ridge',
                        foreground=get_state("widget_text_color"),
                        bg=get_state("window_bg_color"),
                        insertbackground=get_state("widget_text_color"))
    
    set_czk_exchange.place(x = x_bdgt_labels, y = y_set_exchange,
                      width = widget_width,
                      height = widget_height,
                      anchor = 'nw')
    toolbar_widgets.append(set_czk_exchange)
    # text above
    canvas.create_text(x_bdgt_labels, y_set_exchange - text_offset, 
                       text="1 € → CZK exchange rate:", 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_NORMAL, BOLD),
                       fill=get_state("text_color"),
                       anchor = 'w')
    # current text
    canvas.create_text(x_bdgt_labels, y_set_exchange + widget_height + 10, 
                       text=f"1 € = {format_number(get_state('CZK_RATE'))} CZK", 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_XSMALL, BOLD, ITALIC),
                       fill=get_state("dynamic_text_color"),
                       anchor = 'w')
    
    # the buttone
    set_exchange_button = Button(root, text='+', justify='center', 
                             font=f'{FONT} {TEXT_SIZE_XLARGE} {BOLD}',
                             bd=get_state("widget_border_width") + 2,
                             relief='ridge',
                             foreground=get_state('text_color'),
                             bg=get_state("window_bg_color"),
                             cursor='hand2',
                             activebackground=get_state('button_active_bg'),
                             activeforeground=get_state("button_active_fg"),
                             command=lambda: set_exchange(set_czk_exchange))
                             
    set_exchange_button.place(x = x_bdgt_buttons, y = y_set_exchange,
                          width = button_width, height = button_height,
                          anchor='ne')
    toolbar_widgets.append(set_exchange_button)

    # Create separation line for next buttons
    canvas.create_line(x1, y_separation_line, x2, y_separation_line,
                       tag='toolbar',
                       fill=get_state("widget_border_color"),
                       width=get_state("widget_border_width"))
    
    # create switch currency button
    if get_state('currency') == 'CZK':
        txt = '€'
    else:
        txt = 'CZK'
    switch_curr_button = Button(root, text=txt, justify='center', 
                             font=f'{FONT} {TEXT_SIZE_NORMAL} {BOLD}',
                             bd=get_state("widget_border_width") + 2,
                             relief='ridge',
                             foreground=get_state('text_color'),
                             bg=get_state("window_bg_color"),
                             cursor='hand2',
                             activebackground=get_state('button_active_bg'),
                             activeforeground=get_state("button_active_fg"),
                             command=switch_currency)
                             
    switch_curr_button.place(x = x_bdgt_labels + button_width * 2 + text_offset, y = y1 + y_interval * 7.5,
                          width = button_width, height = button_height,
                          anchor='ne')
    toolbar_widgets.append(switch_curr_button)

    # create dark mode button
    if get_state('is_dark_mode') == True:
        txt = '☀'
    else:
        txt = '☾'
    dark_mode_button = Button(root, text=txt, justify='center', 
                             font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
                             bd=get_state("widget_border_width") + 2,
                             relief='ridge',
                             foreground=get_state('text_color'),
                             bg=get_state("window_bg_color"),
                             cursor='hand2',
                             activebackground=get_state('button_active_bg'),
                             activeforeground=get_state("button_active_fg"),
                             command=toggle_dark_mode)
                             
    dark_mode_button.place(x = x_bdgt_labels, y = y1 + y_interval * 7.5,
                          width = button_width, height = button_height,
                          anchor='nw')
    toolbar_widgets.append(dark_mode_button)

    # create restore default button
    reset_button = Button(root, text='↺', justify='center', 
                             font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
                             bd=get_state("widget_border_width") + 2,
                             relief='ridge',
                             foreground=get_state('text_color'),
                             bg=get_state("window_bg_color"),
                             cursor='hand2',
                             activebackground=get_state('button_active_bg'),
                             activeforeground=get_state("button_active_fg"),
                             command=reset_defaults)
                             
    reset_button.place(x = x_bdgt_labels + button_width * 3.33333 + text_offset, y = y1 + y_interval * 7.5,
                          width = button_width, height = button_height,
                          anchor='ne')
    toolbar_widgets.append(reset_button)
    # Create controls text
    offst = 1.025
    canvas.create_text((x1 + x2) / 2 * offst, y1 + y_interval * 7.5, 
                       text=f"Controls:", 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD),
                       fill=get_state("dynamic_text_color"),
                       anchor = 'w')
    # <- ->
    canvas.create_text((x1 + x2) / 2 * offst, y1 + y_interval * 8.1, 
                       text=f"← → = change graph \nmonth", 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_XSMALL, BOLD),
                       fill=get_state("text_color"),
                       anchor = 'w')
    
    # up down
    canvas.create_text((x1 + x2) / 2 * offst, y1 + y_interval * 8.7, 
                       text=f"↑ ↓ = change padding", 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_XSMALL, BOLD),
                       fill=get_state("text_color"),
                       anchor = 'w')

    # ESC
    canvas.create_text((x1 + x2) / 2 * offst, y1 + y_interval * 9.3, 
                       text=f"ESC = close app", 
                       tag="toolbar",
                       font=(FONT, TEXT_SIZE_XSMALL, BOLD),
                       fill=get_state("reserve_text_color"),
                       anchor = 'w')
def format_num_to_calc_ready(num: str) -> str:
    num = num.replace(',', '.')
    num = num.replace(' ', '')
    return num

def reset_defaults():
    askyesno = messagebox.askyesno('Are you sure?', 'Do you want to RESET your budget, daily allowance balance and total spendings? This action is irreversible!\nYour transaction history will remain unchanged.')
    if askyesno == True:
        restore_default_values()
        redraw_ui()
def set_exchange(exch_entry_widget):
    exch_amount = exch_entry_widget.get()
    if not exch_amount:
        messagebox.showerror("Error", "Please fill in the field.")
        return None
    else:
        exch_amount = format_num_to_calc_ready(exch_amount)
        try:
            exch_amount = float(exch_amount)
            if math.isnan(exch_amount) or math.isinf(exch_amount): # Just in case a cheeky user tries to add inf, -inf or NaN
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Exchange rate must be a number.")
            return None
    if round(exch_amount, 2) <= 0:
        messagebox.showerror("Error", "Exchange rate must be greater than 0.")
        return None
    askyesno = messagebox.askyesno('Are you sure?', f'Do you want to set your € - CZK exchange rate to 1€ = {format_number(exch_amount)} CZK? Please ensure it is accurate.')
    if askyesno == False:
        return None
    
    if get_state('currency') == 'CZK':
        switch_currency() # Switch to eur
        set_state('CZK_RATE', exch_amount) # Set rate
        switch_currency() # Recalculate
    else:
        set_state('CZK_RATE', exch_amount)
    save_app_states(app_states)
    redraw_ui()

def set_budget(budget_entry_widget):
    # handle if num <= 0, inf or -inf, NaN
    budget_amount = budget_entry_widget.get()
    if not budget_amount:
        messagebox.showerror("Error", "Please fill in the field.")
        return None
    else:
        budget_amount = format_num_to_calc_ready(budget_amount)
        try:
            budget_amount = float(budget_amount)
            if math.isnan(budget_amount) or math.isinf(budget_amount): # Just in case a cheeky user tries to add inf, -inf or NaN
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Budget must be a number.")
            return None
    if round(budget_amount, 2) <= 0:
        messagebox.showerror("Error", "Budget must be greater than 0.")
        return None
    
    if get_state('currency') == '€':
        budget_limit = 1_000_000
    else:
        budget_limit = calculate_money_conversion(1_000_000, '€', 'CZK', get_state('CZK_RATE'))

    if round(budget_amount, 2) > budget_limit:
        messagebox.showerror("Error", f"Budget is too high. Maximum allowed budget is\n{format_number(budget_limit)} {get_state('currency')}")
        return None
    askyesno = messagebox.askyesno('Are you sure?', f'Do you want to set your monthly budget to {format_number(budget_amount)} {get_state("currency")}? This process is irreversible!')
    if askyesno == False:
        return None
    set_state('budget', budget_amount)
    if get_state('rolling_balance') == 0 and get_state('days_left_in_month') != 0:
        rolling_bal_addon = get_state('rolling_balance') + ((get_state('budget') - get_state('reserve_at_end_of_month')) / (get_days_left_in_curr_month() + 1))
        q = messagebox.askyesno('Add daily allowance for today?', f'Your current daily allowance is 0,00 {get_state("currency")}. Do you want to add +{format_number(rolling_bal_addon)} {get_state("currency")} to your daily allowance for today?')
        if q == True:
            set_daily_allowance()
            set_state('rolling_balance', rolling_bal_addon)
            set_state('budget', get_state('budget') - rolling_bal_addon)
    if get_state('days_left_in_month') == 0:
        rolling_bal_addon = get_state('rolling_balance') + ((get_state('budget') - get_state('reserve_at_end_of_month')) / (get_days_left_in_curr_month() + 1))
        messagebox.showinfo('Budget added to daily allowance', f'It\'s the last day of the month. Due to monthly resets, your newly set budget got added to your daily allowance.')
        set_daily_allowance()
        set_state('rolling_balance', rolling_bal_addon)
        set_state('budget', get_state('budget') - rolling_bal_addon)
    save_app_states(app_states)
    redraw_ui()

def set_reserve(reserve_entry_widget):
    # handle if num <= 0, inf or -inf, NaN
    reserve_amount = reserve_entry_widget.get()
    if not reserve_amount:
        messagebox.showerror("Error", "Please fill in the field.")
        return None
    else:
        reserve_amount = format_num_to_calc_ready(reserve_amount)
        try:
            reserve_amount = float(reserve_amount)
            if math.isnan(reserve_amount) or math.isinf(reserve_amount): # Just in case a cheeky user tries to add inf, -inf or NaN
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Reserve must be a number.")
            return None
    if reserve_amount > get_state('budget'):
        messagebox.showerror('Error', 'Monthly reserve cannot be greater than monthly budget.')
        return None
    if round(reserve_amount, 2) < 0:
        messagebox.showerror("Error", "Reserve must be greater than or equal to 0.")
        return None
    askyesno = messagebox.askyesno('Are you sure?', f'Do you want to set your monthly reserve to {format_number(reserve_amount)} {get_state("currency")}? This process is irreversible!')
    if askyesno == False:
        return None

    set_state('reserve_at_end_of_month', reserve_amount)
    save_app_states(app_states)
    redraw_ui()

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
    item_name_entry = Entry(root, justify='left', font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
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
    price_entry = Entry(root, justify='left', font=f'{FONT} {TEXT_SIZE_LARGE} {BOLD}',
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
    create_graph(padding_x, padding_y, x1, x2, y1, y2, main_rect_id)

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
                       text="Daily Allowance", 
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
    budget = format_number(get_state("budget"))
    canvas.create_text(x1 + 10, y1_currency + 10,
                       text=f'Monthly budget left: {budget} {get_state("currency")}',
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                       fill=get_state("dynamic_text_color"),
                       anchor="nw")

    # Text on the top left corner of the currency section indicating pending spendings below the budget
    total_spent = format_number(get_state("total_monthly_spendings"))
    canvas.create_text(x2 - 10, y2_currency - 10,
                       text=f'- {total_spent} {get_state("currency")} total monthly spendings',
                       tag="allowance_currency",
                       font=(FONT, TEXT_SIZE_SMALL, BOLD, ITALIC),
                       fill=get_state("reserve_text_color"),
                       anchor="se")
    
    # Text on the bottom left corner of the currency section indicating reserve at end of month
    reserve = get_state("reserve_at_end_of_month")
    canvas.create_text(x1 + 10, y2_currency - 10,
                       text=f'Monthly reserve: {format_number(reserve)} {get_state("currency")}',
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
    create_toolbar(padding_x, padding_y, x1, x2, y1, y2)

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
                       text="Add Transaction", 
                       tag="transaction_window",
                       font=(FONT, TEXT_SIZE_LARGE),
                       fill=get_state("text_color"))

    create_transaction_widgets(x1, y2_label, x2, y2, main_rect_id)




def add_transaction(item_name_entry, price_entry, x_middle, y_bottom):
    item_name = item_name_entry.get()
    price = price_entry.get()
    price = price.replace(',','.') # Replace , with a . in case the user entered something like 20,45€
    # Check for edge cases:
    if not item_name or not price:
        messagebox.showerror("Error", "Please fill in all fields.")
        return None
    else:
        price = format_num_to_calc_ready(price)
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
    if get_state('budget') + get_state('rolling_balance') < price:
        messagebox.showerror("Error", "This transaction's price is greater than your budget. Please increase your budget to input this transaction.")
        return None
    if get_state('budget') + get_state('rolling_balance') - price <= get_state('reserve_at_end_of_month'):
        askyesno = messagebox.askyesno("Warning", "This transaction's price will push your budget below the monthly reserve. The reserve will be cleared (set to 0). You will have to set a new reserve manually. Do you wish to proceed?")
        if askyesno == True:
            set_state('reserve_at_end_of_month', 0)
        else: 
            return None

    if price > get_state("rolling_balance"):
        messagebox.showwarning("Warning", "This transaction's price exceeds your daily allowance, meaning it will impact your future daily earnings.")
    rolling_bal_before = app_states["rolling_balance"]
    rolling_bal_after = max(0, rolling_bal_before - price) # Cap it at 0
    rolling_bal_hit = rolling_bal_before - rolling_bal_after
    if price >= rolling_bal_before:
        budget_hit = price - rolling_bal_before
        set_state("budget", app_states["budget"] - budget_hit)
        set_daily_allowance()
    else:
        budget_hit = 0

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

def switch_currency():
    if get_state("currency") == "€":
        new_currency = "CZK"
    else:
        new_currency = "€"
    money_amount = calculate_money_conversion(get_state("budget"), get_state("currency"), new_currency, get_state('CZK_RATE'))
    reserve_amount = calculate_money_conversion(get_state("reserve_at_end_of_month"), get_state("currency"), new_currency, get_state('CZK_RATE'))
    rolling_balance = calculate_money_conversion(get_state("rolling_balance"), get_state("currency"), new_currency, get_state('CZK_RATE'))
    total_monthly_spendings = calculate_money_conversion(get_state("total_monthly_spendings"), get_state("currency"), new_currency, get_state('CZK_RATE'))
    set_state("currency", new_currency)
    set_state("budget", money_amount)
    set_state("reserve_at_end_of_month", reserve_amount)
    set_state("rolling_balance", rolling_balance)
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
    if get_state("padding_y") < 4: # Limit maximum padding to 4%
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
        transaction_frame = transaction_history_widgets[0]
        my_font = font.Font(family=TRANSACTION_FONT, size=TEXT_SIZE_TRANSACTION)
        char_width = my_font.measure('0')

        if event.delta < 0 and start_idx + visible_count < num_transactions:
            transaction_history_widgets[1].destroy()
            transaction_history_widgets.pop(1)
            next_key = list(reversed([k for k in transactions if k != 'next_txn_id']))[start_idx + visible_count]
            transaction = transactions[next_key]
            create_trnsc(next_key, transaction_frame, label_width, char_width, transaction)
            start_idx += 1
            draw_scrollbar()

        elif event.delta > 0 and start_idx > 0:
            start_idx -= 1
            draw_scrollbar()
            transaction_history_widgets[-1].destroy()
            transaction_history_widgets.pop(-1)
            prev_key = list(reversed([k for k in transactions if k != 'next_txn_id']))[start_idx]
            transaction = transactions[prev_key]
            create_trnsc(prev_key, transaction_frame, label_width, char_width, transaction, transaction_history_widgets[1])

def lower_graph_month(event):
    global month_to_show
    global year_to_show

    if month_to_show == 1:
        year_to_show -= 1
        month_to_show = 12
    else:
        month_to_show -= 1
    redraw_ui()

def increase_graph_month(event):
    global month_to_show
    global year_to_show

    if month_to_show == 12:
        year_to_show += 1
        month_to_show = 1
    else:
        month_to_show += 1
    redraw_ui()

create_windows(get_padding_x(), get_state("padding_y"))
check_days_passed_and_set_dates()
draw_scrollbar()

root.bind("<Up>", increase_padding)
root.bind("<Down>", decrease_padding)
root.bind("<Escape>", exit_app)

# root.bind("<D>", toggle_dark_mode)
# root.bind("<d>", toggle_dark_mode)
# root.bind("<C>", switch_currency)
# root.bind("<c>", switch_currency)
root.bind("<MouseWheel>", scroll_transactions)
root.bind("<Left>", lower_graph_month)
root.bind("<Right>", increase_graph_month)
center_screen()
root.mainloop()