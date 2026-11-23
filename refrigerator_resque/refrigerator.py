import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
from datetime import datetime
import ctypes
import json
import os

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

window = tk.Tk()
window.title("냉장고 구조대")

SCALE = max(1.0, window.winfo_fpixels("1i") / 96)


def px(value):
    return int(round(value * SCALE))


window_width = min(px(900), window.winfo_screenwidth() - px(40))
window_height = min(px(820), window.winfo_screenheight() - px(80))

window.geometry(str(window_width) + "x" + str(window_height))
window.minsize(min(px(780), window_width), min(px(720), window_height))

background_color = "#F4F6F3"
white_color = "#FFFFFF"
text_color = "#26352D"
subtext_color = "#7B877F"
green_color = "#2F6B4F"
light_green_color = "#E6F0E9"
border_color = "#E6EBE6"
input_bg_color = "#F7F9F7"
row_color = "#F6F8F6"
row_border_color = "#EBEFEB"
selected_row_color = "#E4F0E8"
red_color = "#B03F38"
orange_color = "#A8650C"

status_styles = {
    "기한 지남": ("#FBEAE8", "#A33A33"),
    "임박": ("#FDF0DC", "#945A0C"),
    "여유": ("#E3F1E7", "#25603F")
}

ROW_HEIGHT = px(66)
ROW_GAP = px(10)
BADGE_WIDTH = px(78)
BADGE_HEIGHT = px(28)

row_name_font = tkfont.Font(family="맑은 고딕", size=12, weight="bold")
row_info_font = tkfont.Font(family="맑은 고딕", size=11)
row_dday_font = tkfont.Font(family="맑은 고딕", size=11, weight="bold")
row_badge_font = tkfont.Font(family="맑은 고딕", size=9, weight="bold")
list_header_font = tkfont.Font(family="맑은 고딕", size=9, weight="bold")

window.configure(bg=background_color)

file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "food_data.json"
)

ingredients = []
displayed_ingredients = []
row_canvases = []
selected_index = None
load_error = False


def draw_round_rect(canvas, x1, y1, x2, y2, radius, fill, outline, tags="", outline_width=1):
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1
    ]

    return canvas.create_polygon(
        points,
        smooth=True,
        fill=fill,
        outline=outline,
        width=outline_width,
        tags=tags
    )


def create_card(parent, height, pad_x=18, pad_y=14, radius=16):
    card_pad_x = px(pad_x)
    card_pad_y = px(pad_y)
    card_radius = px(radius)

    card_canvas = tk.Canvas(
        parent,
        height=px(height),
        bg=background_color,
        highlightthickness=0,
        bd=0
    )

    card_inner = tk.Frame(card_canvas, bg=white_color)

    window_id = card_canvas.create_window(
        card_pad_x,
        card_pad_y,
        window=card_inner,
        anchor="nw"
    )

    def redraw_card(event):
        card_canvas.delete("card_background")

        draw_round_rect(
            card_canvas,
            1,
            1,
            event.width - 2,
            event.height - 2,
            card_radius,
            white_color,
            border_color,
            "card_background"
        )

        card_canvas.tag_lower("card_background")

        card_canvas.itemconfig(
            window_id,
            width=max(event.width - card_pad_x * 2, 1),
            height=max(event.height - card_pad_y * 2, 1)
        )

    card_canvas.bind("<Configure>", redraw_card)

    return card_canvas, card_inner


def create_rounded_button(parent, text, command, bg, fg, hover_bg, width, height, button_font, parent_bg):
    button_width = px(width)
    button_height = px(height)

    button_canvas = tk.Canvas(
        parent,
        width=button_width,
        height=button_height,
        bg=parent_bg,
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )

    shape_id = draw_round_rect(
        button_canvas,
        1,
        1,
        button_width - 1,
        button_height - 1,
        px(12),
        bg,
        bg
    )

    button_canvas.create_text(
        button_width / 2,
        button_height / 2,
        text=text,
        fill=fg,
        font=button_font
    )

    def on_click(event):
        command()

    def on_enter(event):
        button_canvas.itemconfig(shape_id, fill=hover_bg, outline=hover_bg)

    def on_leave(event):
        button_canvas.itemconfig(shape_id, fill=bg, outline=bg)

    button_canvas.bind("<Button-1>", on_click)
    button_canvas.bind("<Enter>", on_enter)
    button_canvas.bind("<Leave>", on_leave)

    return button_canvas


def create_entry_box(parent, bg_color, textvariable=None, width=0):
    entry_box = tk.Frame(
        parent,
        bg=bg_color,
        width=px(width),
        height=px(38),
        highlightthickness=1,
        highlightbackground=border_color,
        highlightcolor=green_color
    )
    entry_box.pack_propagate(False)

    entry = tk.Entry(
        entry_box,
        textvariable=textvariable,
        font=("맑은 고딕", 10),
        relief="flat",
        bd=0,
        highlightthickness=0,
        bg=bg_color,
        fg=text_color,
        insertbackground=green_color
    )
    entry.pack(fill="both", expand=True, padx=px(12), pady=px(6))

    def on_focus_in(event):
        entry_box.config(highlightbackground=green_color)

    def on_focus_out(event):
        entry_box.config(highlightbackground=border_color)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    return entry_box, entry


main_frame = tk.Frame(window, bg=background_color)
main_frame.pack(fill="both", expand=True, padx=px(30), pady=px(18))

header_frame = tk.Frame(main_frame, bg=background_color)
header_frame.pack(fill="x", pady=(0, px(14)))

title_label = tk.Label(
    header_frame,
    text="🧊 냉장고 구조대 🚑",
    font=("맑은 고딕", 21, "bold"),
    fg=text_color,
    bg=background_color
)
title_label.pack(anchor="w")

subtitle_label = tk.Label(
    header_frame,
    text="식재료를 간편하게 관리하고 소비기한을 확인하세요.",
    font=("맑은 고딕", 9),
    fg=subtext_color,
    bg=background_color
)
subtitle_label.pack(anchor="w", pady=(px(2), 0))

dashboard_frame = tk.Frame(main_frame, bg=background_color)
dashboard_frame.pack(fill="x", pady=(0, px(12)))

for column in range(4):
    dashboard_frame.columnconfigure(column, weight=1, uniform="dashboard")

total_count_card, total_count_inner = create_card(dashboard_frame, 76, 16, 10)
total_count_card.grid(row=0, column=0, sticky="nsew", padx=(0, px(6)))
total_quantity_card, total_quantity_inner = create_card(dashboard_frame, 76, 16, 10)
total_quantity_card.grid(row=0, column=1, sticky="nsew", padx=px(6))
soon_count_card, soon_count_inner = create_card(dashboard_frame, 76, 16, 10)
soon_count_card.grid(row=0, column=2, sticky="nsew", padx=px(6))
expired_count_card, expired_count_inner = create_card(dashboard_frame, 76, 16, 10)
expired_count_card.grid(row=0, column=3, sticky="nsew", padx=(px(6), 0))

total_count_title = tk.Label(
    total_count_inner,
    text="🥛전체 종류",
    font=("맑은 고딕", 9),
    anchor="w",
    fg=subtext_color,
    bg=white_color
)
total_count_title.pack(fill="x")

total_count_label = tk.Label(
    total_count_inner,
    text="0개",
    font=("맑은 고딕", 18, "bold"),
    anchor="w",
    fg=text_color,
    bg=white_color
)
total_count_label.pack(fill="x")

total_quantity_title = tk.Label(
    total_quantity_inner,
    text="🥬전체 수량",
    font=("맑은 고딕", 9),
    anchor="w",
    fg=subtext_color,
    bg=white_color
)
total_quantity_title.pack(fill="x")

total_quantity_label = tk.Label(
    total_quantity_inner,
    text="0개",
    font=("맑은 고딕", 18, "bold"),
    anchor="w",
    fg=green_color,
    bg=white_color
)
total_quantity_label.pack(fill="x")

soon_count_title = tk.Label(
    soon_count_inner,
    text="🍎소비기한 임박",
    font=("맑은 고딕", 9),
    anchor="w",
    fg=subtext_color,
    bg=white_color
)
soon_count_title.pack(fill="x")

soon_count_label = tk.Label(
    soon_count_inner,
    text="0개",
    font=("맑은 고딕", 18, "bold"),
    anchor="w",
    fg=orange_color,
    bg=white_color
)
soon_count_label.pack(fill="x")

expired_count_title = tk.Label(
    expired_count_inner,
    text="🥚기한 지남",
    font=("맑은 고딕", 9),
    anchor="w",
    fg=subtext_color,
    bg=white_color
)
expired_count_title.pack(fill="x")

expired_count_label = tk.Label(
    expired_count_inner,
    text="0개",
    font=("맑은 고딕", 18, "bold"),
    anchor="w",
    fg=red_color,
    bg=white_color
)
expired_count_label.pack(fill="x")

search_frame = tk.Frame(main_frame, bg=background_color)
search_frame.pack(fill="x", pady=(0, px(12)))

search_var = tk.StringVar()
filter_var = tk.StringVar(value="전체 보기")

search_label = tk.Label(
    search_frame,
    text="식재료 검색",
    font=("맑은 고딕", 9, "bold"),
    fg=subtext_color,
    bg=background_color
)
search_label.pack(side="left", padx=(0, px(10)))

search_box, search_entry = create_entry_box(
    search_frame,
    white_color,
    search_var,
    280
)
search_box.pack(side="left", padx=(0, px(10)))

filter_box = tk.Frame(
    search_frame,
    bg=white_color,
    width=px(130),
    height=px(38),
    highlightthickness=1,
    highlightbackground=border_color
)
filter_box.pack_propagate(False)
filter_box.pack(side="left", padx=(0, px(10)))

filter_menu = tk.OptionMenu(
    filter_box,
    filter_var,
    "전체 보기",
    "임박",
    "기한 지남",
    "여유",
    command=lambda value: update_listbox()
)
filter_menu.config(
    font=("맑은 고딕", 10),
    anchor="w",
    padx=px(12),
    bg=white_color,
    fg=text_color,
    activebackground=light_green_color,
    activeforeground=green_color,
    relief="flat",
    bd=0,
    highlightthickness=0,
    cursor="hand2"
)
filter_menu["menu"].config(
    font=("맑은 고딕", 10),
    bg=white_color,
    fg=text_color,
    activebackground=light_green_color,
    activeforeground=green_color
)
filter_menu.pack(fill="both", expand=True)

reset_button = create_rounded_button(
    search_frame,
    "🔄 초기화",
    lambda: reset_search_filter(),
    "#E9EDE9",
    text_color,
    "#DDE5DE",
    80,
    38,
    ("맑은 고딕", 9),
    background_color
)
reset_button.pack(side="left")

input_card, input_frame = create_card(main_frame, 188)
input_card.pack(fill="x", pady=(0, px(12)))

input_title = tk.Label(
    input_frame,
    text="식재료 입력",
    font=("맑은 고딕", 11, "bold"),
    fg=text_color,
    bg=white_color
)
input_title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, px(8)))

for column in range(3):
    input_frame.columnconfigure(column, weight=1, uniform="input")

name_label = tk.Label(
    input_frame,
    text="식재료 이름",
    font=("맑은 고딕", 9),
    fg=subtext_color,
    bg=white_color
)
name_label.grid(row=1, column=0, sticky="w", padx=(0, px(8)), pady=(0, px(4)))

quantity_label = tk.Label(
    input_frame,
    text="수량",
    font=("맑은 고딕", 9),
    fg=subtext_color,
    bg=white_color
)
quantity_label.grid(row=1, column=1, sticky="w", padx=px(4), pady=(0, px(4)))

date_label = tk.Label(
    input_frame,
    text="소비기한 (YYYY-MM-DD)",
    font=("맑은 고딕", 9),
    fg=subtext_color,
    bg=white_color
)
date_label.grid(row=1, column=2, sticky="w", padx=(px(8), 0), pady=(0, px(4)))

name_box, name_entry = create_entry_box(input_frame, input_bg_color)
name_box.grid(row=2, column=0, sticky="ew", padx=(0, px(8)))

quantity_box, quantity_entry = create_entry_box(input_frame, input_bg_color)
quantity_box.grid(row=2, column=1, sticky="ew", padx=px(4))

date_box, date_entry = create_entry_box(input_frame, input_bg_color)
date_box.grid(row=2, column=2, sticky="ew", padx=(px(8), 0))

button_frame = tk.Frame(input_frame, bg=white_color)
button_frame.grid(row=3, column=0, columnspan=3, sticky="e", pady=(px(12), 0))

add_button = create_rounded_button(
    button_frame,
    "➕ 등록",
    lambda: add_ingredient(),
    green_color,
    white_color,
    "#244936",
    92,
    38,
    ("맑은 고딕", 9, "bold"),
    white_color
)
add_button.pack(side="left", padx=(0, px(6)))

edit_button = create_rounded_button(
    button_frame,
    "✏️ 수정",
    lambda: edit_ingredient(),
    light_green_color,
    green_color,
    "#D6E6DB",
    92,
    38,
    ("맑은 고딕", 9, "bold"),
    white_color
)
edit_button.pack(side="left", padx=px(3))

delete_button = create_rounded_button(
    button_frame,
    "🗑️ 삭제",
    lambda: delete_ingredient(),
    "#F9ECEA",
    "#A33A33",
    "#F2D9D6",
    92,
    38,
    ("맑은 고딕", 9, "bold"),
    white_color
)
delete_button.pack(side="left", padx=px(3))

clear_button = create_rounded_button(
    button_frame,
    "🧹 입력 초기화",
    lambda: clear_input(),
    "#E9EDE9",
    text_color,
    "#DDE5DE",
    104,
    38,
    ("맑은 고딕", 9),
    white_color
)
clear_button.pack(side="left", padx=(px(3), 0))

list_card, list_frame = create_card(main_frame, 200, 20, 16)
list_card.pack(fill="both", expand=True)

list_title = tk.Label(
    list_frame,
    text="식재료 목록",
    font=("맑은 고딕", 11, "bold"),
    fg=text_color,
    bg=white_color
)
list_title.pack(anchor="w", pady=(0, px(8)))

list_content_frame = tk.Frame(list_frame, bg=white_color)
list_content_frame.pack(fill="both", expand=True)

list_content_frame.columnconfigure(0, weight=1)
list_content_frame.rowconfigure(1, weight=1)

header_canvas = tk.Canvas(
    list_content_frame,
    height=px(24),
    bg=white_color,
    highlightthickness=0,
    bd=0
)
header_canvas.grid(row=0, column=0, sticky="ew")

list_canvas = tk.Canvas(
    list_content_frame,
    height=px(80),
    bg=white_color,
    highlightthickness=0,
    bd=0,
    yscrollincrement=px(20)
)
list_canvas.grid(row=1, column=0, sticky="nsew")

listbox_scrollbar = tk.Scrollbar(
    list_content_frame,
    orient="vertical",
    command=list_canvas.yview,
    bg="#F0F3F0",
    troughcolor=white_color,
    activebackground="#C8D4CB",
    relief="flat",
    bd=0,
    width=px(11),
    highlightthickness=0
)
listbox_scrollbar.grid(row=1, column=1, sticky="ns", padx=(px(6), 0))

list_canvas.configure(yscrollcommand=listbox_scrollbar.set)

rows_frame = tk.Frame(list_canvas, bg=white_color)
rows_window = list_canvas.create_window(0, 0, window=rows_frame, anchor="nw")

empty_result_label = tk.Label(
    list_canvas,
    text="조건에 맞는 식재료가 없습니다.",
    font=("맑은 고딕", 10),
    fg=subtext_color,
    bg=white_color
)


def save_data():
    if load_error:
        messagebox.showwarning(
            "저장 제한",
            "기존 JSON 파일을 정상적으로 읽지 못했습니다.\n"
            "기존 파일 보호를 위해 자동 저장을 중단합니다."
        )
        return False

    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                ingredients,
                file,
                ensure_ascii=False,
                indent=4
            )
        return True

    except (OSError, TypeError, ValueError) as e:
        messagebox.showerror(
            "저장 오류",
            "JSON 파일을 저장하지 못했습니다.\n" + str(e)
        )
        return False


def load_data():
    global load_error

    if not os.path.exists(file_path):
        return True

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            loaded_data = json.load(file)

        if type(loaded_data) != list:
            raise ValueError("JSON 데이터의 형식이 올바르지 않습니다.")

        for item in loaded_data:
            if type(item) != dict:
                raise ValueError("식재료 데이터의 형식이 올바르지 않습니다.")

            if "name" not in item or "quantity" not in item or "date" not in item:
                raise ValueError("식재료 데이터에 필요한 항목이 없습니다.")

            if type(item["name"]) != str or item["name"].strip() == "":
                raise ValueError("식재료 이름이 올바르지 않습니다.")

            if type(item["quantity"]) != int or item["quantity"] <= 0:
                raise ValueError("식재료 수량이 올바르지 않습니다.")

            date_text = item["date"]

            if type(date_text) != str:
                raise ValueError("소비기한 형식이 올바르지 않습니다.")

            if (
                len(date_text) != 10
                or date_text[4] != "-"
                or date_text[7] != "-"
            ):
                raise ValueError("소비기한은 YYYY-MM-DD 형식이어야 합니다.")

            datetime.strptime(date_text, "%Y-%m-%d")

        ingredients.clear()
        ingredients.extend(loaded_data)

        return True

    except (OSError, json.JSONDecodeError, ValueError, TypeError) as e:
        load_error = True

        messagebox.showerror(
            "불러오기 오류",
            "JSON 파일을 정상적으로 불러오지 못했습니다.\n"
            "기존 파일 보호를 위해 자동 저장을 중단합니다.\n\n"
            + str(e)
        )

        return False


def get_expiry_info(date_text):
    today = datetime.now().date()
    expiry_date = datetime.strptime(date_text, "%Y-%m-%d").date()

    remaining_days = (expiry_date - today).days

    if remaining_days > 0:
        d_day = "D-" + str(remaining_days)
    elif remaining_days == 0:
        d_day = "D-Day"
    else:
        d_day = "D+" + str(abs(remaining_days))

    if remaining_days < 0:
        status = "기한 지남"
    elif remaining_days <= 3:
        status = "임박"
    else:
        status = "여유"

    return remaining_days, d_day, status


def update_dashboard():
    total_count = len(ingredients)
    total_quantity = 0
    soon_count = 0
    expired_count = 0

    for item in ingredients:
        total_quantity += item["quantity"]

        remaining_days, d_day, status = get_expiry_info(item["date"])

        if status == "임박":
            soon_count += 1
        elif status == "기한 지남":
            expired_count += 1

    total_count_label.config(
        text=str(total_count) + "개"
    )

    total_quantity_label.config(
        text=str(total_quantity) + "개"
    )

    soon_count_label.config(
        text=str(soon_count) + "개"
    )

    expired_count_label.config(
        text=str(expired_count) + "개"
    )


def get_column_positions(width):
    positions = {
        "name": px(22),
        "quantity": int(width * 0.38),
        "date": int(width * 0.50),
        "dday": int(width * 0.69),
        "badge_center": width - px(20) - BADGE_WIDTH // 2
    }

    return positions


def shorten_text(text, font_object, max_width):
    if font_object.measure(text) <= max_width:
        return text

    while len(text) > 1 and font_object.measure(text + "…") > max_width:
        text = text[:-1]

    return text + "…"


def draw_list_header(event):
    header_canvas.delete("all")

    positions = get_column_positions(event.width)
    center_y = px(12)

    header_canvas.create_text(
        positions["name"],
        center_y,
        text="식재료",
        anchor="w",
        font=list_header_font,
        fill=subtext_color
    )
    header_canvas.create_text(
        positions["quantity"],
        center_y,
        text="수량",
        anchor="w",
        font=list_header_font,
        fill=subtext_color
    )
    header_canvas.create_text(
        positions["date"],
        center_y,
        text="소비기한",
        anchor="w",
        font=list_header_font,
        fill=subtext_color
    )
    header_canvas.create_text(
        positions["dday"],
        center_y,
        text="D-Day",
        anchor="w",
        font=list_header_font,
        fill=subtext_color
    )
    header_canvas.create_text(
        positions["badge_center"],
        center_y,
        text="상태",
        anchor="center",
        font=list_header_font,
        fill=subtext_color
    )


def draw_row(index):
    if index >= len(row_canvases) or index >= len(displayed_ingredients):
        return

    row_canvas = row_canvases[index]
    item = displayed_ingredients[index]

    width = row_canvas.winfo_width()

    if width < px(50):
        return

    row_canvas.delete("all")

    remaining_days, d_day, status = get_expiry_info(item["date"])
    badge_bg, badge_fg = status_styles[status]

    if index == selected_index:
        fill_color = selected_row_color
        outline_color = green_color
        outline_width = 2
    else:
        fill_color = row_color
        outline_color = row_border_color
        outline_width = 1

    draw_round_rect(
        row_canvas,
        2,
        2,
        width - 3,
        ROW_HEIGHT - 3,
        px(14),
        fill_color,
        outline_color,
        "",
        outline_width
    )

    positions = get_column_positions(width)
    center_y = ROW_HEIGHT // 2

    max_name_width = positions["quantity"] - positions["name"] - px(16)
    name_text = shorten_text(item["name"], row_name_font, max_name_width)

    row_canvas.create_text(
        positions["name"],
        center_y,
        text=name_text,
        anchor="w",
        font=row_name_font,
        fill=text_color
    )

    row_canvas.create_text(
        positions["quantity"],
        center_y,
        text=str(item["quantity"]) + "개",
        anchor="w",
        font=row_info_font,
        fill=text_color
    )

    row_canvas.create_text(
        positions["date"],
        center_y,
        text=item["date"],
        anchor="w",
        font=row_info_font,
        fill="#55645A"
    )

    row_canvas.create_text(
        positions["dday"],
        center_y,
        text=d_day,
        anchor="w",
        font=row_dday_font,
        fill=badge_fg
    )

    badge_left = positions["badge_center"] - BADGE_WIDTH // 2
    badge_right = positions["badge_center"] + BADGE_WIDTH // 2

    draw_round_rect(
        row_canvas,
        badge_left,
        center_y - BADGE_HEIGHT // 2,
        badge_right,
        center_y + BADGE_HEIGHT // 2,
        BADGE_HEIGHT // 2,
        badge_bg,
        badge_bg
    )

    row_canvas.create_text(
        positions["badge_center"],
        center_y,
        text=status,
        anchor="center",
        font=row_badge_font,
        fill=badge_fg
    )


def create_row(index):
    row_canvas = tk.Canvas(
        rows_frame,
        height=ROW_HEIGHT,
        bg=white_color,
        highlightthickness=0,
        bd=0,
        cursor="hand2"
    )
    row_canvas.pack(fill="x", pady=(0, ROW_GAP))

    row_canvas.bind(
        "<Configure>",
        lambda event, row_index=index: draw_row(row_index)
    )
    row_canvas.bind(
        "<Button-1>",
        lambda event, row_index=index: select_ingredient(row_index)
    )

    row_canvases.append(row_canvas)


def update_listbox():
    global displayed_ingredients
    global row_canvases
    global selected_index

    for child in rows_frame.winfo_children():
        child.destroy()

    row_canvases = []
    selected_index = None
    displayed_ingredients = []

    sorted_ingredients = sorted(
        ingredients,
        key=lambda item: item["date"]
    )

    search_text = search_var.get().strip().lower()
    selected_filter = filter_var.get()

    for item in sorted_ingredients:
        name = item["name"]

        if search_text not in name.lower():
            continue

        remaining_days, d_day, status = get_expiry_info(item["date"])

        if selected_filter == "임박" and status != "임박":
            continue

        if selected_filter == "기한 지남" and status != "기한 지남":
            continue

        if selected_filter == "여유" and status != "여유":
            continue

        displayed_ingredients.append(item)

    for index in range(len(displayed_ingredients)):
        create_row(index)

    if len(displayed_ingredients) == 0:
        empty_result_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )
    else:
        empty_result_label.place_forget()

    update_dashboard()


def scroll_to_row(index):
    window.update_idletasks()

    total_height = rows_frame.winfo_height()

    if total_height <= 0 or index >= len(row_canvases):
        return

    row_top = row_canvases[index].winfo_y()
    row_bottom = row_top + ROW_HEIGHT

    view_top = list_canvas.canvasy(0)
    view_height = list_canvas.winfo_height()

    if row_top < view_top:
        list_canvas.yview_moveto(row_top / total_height)
    elif row_bottom > view_top + view_height:
        list_canvas.yview_moveto((row_bottom - view_height) / total_height)


def on_mousewheel(event):
    try:
        widget = window.winfo_containing(event.x_root, event.y_root)
    except KeyError:
        return

    while widget is not None and widget is not list_content_frame:
        widget = widget.master

    if widget is None:
        return

    if rows_frame.winfo_height() <= list_canvas.winfo_height():
        return

    if event.num == 4 or event.delta > 0:
        list_canvas.yview_scroll(-2, "units")
    else:
        list_canvas.yview_scroll(2, "units")


def update_scroll_region(event):
    list_canvas.configure(scrollregion=list_canvas.bbox("all"))


def resize_rows_frame(event):
    list_canvas.itemconfig(rows_window, width=event.width)


def search_ingredient(event):
    update_listbox()


def reset_search_filter():
    search_var.set("")
    filter_var.set("전체 보기")
    update_listbox()


def check_input():
    name = name_entry.get().strip()
    quantity = quantity_entry.get().strip()
    date = date_entry.get().strip()

    if name == "" or quantity == "" or date == "":
        messagebox.showwarning(
            "입력 오류",
            "모든 항목을 입력해주세요."
        )
        return False

    if not quantity.isdigit():
        messagebox.showwarning(
            "입력 오류",
            "수량은 숫자로 입력해주세요."
        )
        return False

    if int(quantity) <= 0:
        messagebox.showwarning(
            "입력 오류",
            "수량은 1개 이상 입력해주세요."
        )
        return False

    if (
        len(date) != 10
        or date[4] != "-"
        or date[7] != "-"
    ):
        messagebox.showwarning(
            "입력 오류",
            "소비기한은 YYYY-MM-DD 형식으로 입력해주세요."
        )
        return False

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        messagebox.showwarning(
            "입력 오류",
            "실제 존재하는 날짜를 입력해주세요."
        )
        return False

    return True


def add_ingredient():
    if not check_input():
        return

    name = name_entry.get().strip()
    quantity = int(quantity_entry.get().strip())
    date = date_entry.get().strip()

    ingredient = {
        "name": name,
        "quantity": quantity,
        "date": date
    }

    ingredients.append(ingredient)

    if not save_data():
        ingredients.pop()
        return

    update_listbox()
    clear_input()

    messagebox.showinfo(
        "등록 완료",
        "식재료가 등록되었습니다."
    )


def clear_input():
    name_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)


def delete_ingredient():
    if selected_index is None:
        messagebox.showwarning(
            "선택 오류",
            "삭제할 식재료를 선택해주세요."
        )
        return

    selected_item = displayed_ingredients[selected_index]

    original_index = -1

    for i in range(len(ingredients)):
        if ingredients[i] is selected_item:
            original_index = i
            break

    if original_index == -1:
        messagebox.showwarning(
            "삭제 오류",
            "선택한 식재료를 찾을 수 없습니다."
        )
        return

    ingredients.pop(original_index)

    if not save_data():
        ingredients.insert(original_index, selected_item)
        return

    update_listbox()
    clear_input()

    messagebox.showinfo(
        "삭제 완료",
        "식재료가 삭제되었습니다."
    )


def select_ingredient(index):
    global selected_index

    if index >= len(displayed_ingredients):
        return

    old_index = selected_index
    selected_index = index

    if old_index is not None:
        draw_row(old_index)

    draw_row(index)

    item = displayed_ingredients[index]

    clear_input()

    name_entry.insert(0, item["name"])
    quantity_entry.insert(0, str(item["quantity"]))
    date_entry.insert(0, item["date"])


def edit_ingredient():
    if selected_index is None:
        messagebox.showwarning(
            "선택 오류",
            "수정할 식재료를 선택해주세요."
        )
        return

    if not check_input():
        return

    selected_item = displayed_ingredients[selected_index]

    old_name = selected_item["name"]
    old_quantity = selected_item["quantity"]
    old_date = selected_item["date"]

    selected_item["name"] = name_entry.get().strip()
    selected_item["quantity"] = int(quantity_entry.get().strip())
    selected_item["date"] = date_entry.get().strip()

    if not save_data():
        selected_item["name"] = old_name
        selected_item["quantity"] = old_quantity
        selected_item["date"] = old_date

        update_listbox()
        return

    update_listbox()

    for i in range(len(displayed_ingredients)):
        if displayed_ingredients[i] is selected_item:
            select_ingredient(i)
            scroll_to_row(i)
            break

    messagebox.showinfo(
        "수정 완료",
        "식재료 정보가 수정되었습니다."
    )


search_var.trace_add("write", lambda *args: update_listbox())
rows_frame.bind("<Configure>", update_scroll_region)
list_canvas.bind("<Configure>", resize_rows_frame)
header_canvas.bind("<Configure>", draw_list_header)
window.bind_all("<MouseWheel>", on_mousewheel)
window.bind_all("<Button-4>", on_mousewheel)
window.bind_all("<Button-5>", on_mousewheel)

load_data()
update_listbox()

window.mainloop()
