import sys
import os
import tkinter as tk
import itertools
import random
import pygame
import time
import math

# =========================
# resource_path 函数 —— 兼容 PyInstaller 单文件模式
# =========================
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =========================
# 背景音乐初始化
# =========================
pygame.mixer.init()
try:
    music_file = resource_path("background_music.mp3")
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)
except Exception as e:
    print("警告：无法加载 background_music.mp3，", e)

# =========================
# 以下为原来程序的其余部分（气球、蛋糕、小游戏等），保持不变
# =========================

root = tk.Tk()
root.title("生日快乐")
root.state("zoomed")
root.configure(bg="white")

phase = "flame"
paused = False

candle_count = 4
flame_state = [False] * candle_count

game_target_score = 12
game_time_limit = 30  # 30 秒
game_score = 0
game_remaining_time = game_time_limit
game_timer_id = None
spawn_timer_id = None

gift_ids = []
bomb_ids = []

move_interval = 50

canvas = tk.Canvas(root, bg="white", highlightthickness=0)
canvas.pack(fill="both", expand=True)

balloons = []
balloon_colors = ["red", "orange", "yellow", "green", "blue", "magenta", "cyan", "pink"]

flame_colors = itertools.cycle(["red", "orange"])
flame_shapes = itertools.cycle(["^", "§", "*", "~", "⁕", "ˈˈ", "‘’"])

banner_label = tk.Label(root,
                        text="🎂 生日快乐 ldx 🎂",
                        fg="purple", bg="white",
                        font=("Segoe UI", 28, "bold"))
banner_label.place(relx=0.5, rely=0.03, anchor="n")

exit_button = tk.Button(root, text="退出", font=("Segoe UI", 12), command=root.destroy)
exit_button.place_forget()

pause_button = tk.Button(root, text="暂停", font=("Segoe UI", 12),
                         command=lambda: toggle_pause())
pause_button.place_forget()

def get_canvas_center():
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    return (w / 2, h / 2)

def get_cake_top_y():
    h = canvas.winfo_height()
    return max(80, h * 0.25)

scroll_text_id = None
def start_scrolling_text():
    global scroll_text_id
    canvas.delete("scroll")
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    text = "祝 ldx 生日快乐，愿你天天开心，梦想成真！"
    scroll_text_id = canvas.create_text(w + 10, h - 20,
                                        text=text,
                                        fill="blue",
                                        font=("Segoe UI", 14, "bold"),
                                        tags=("scroll",))
    def tick_scroll():
        if scroll_text_id is None:
            return
        canvas.move(scroll_text_id, -2, 0)
        x, y = canvas.coords(scroll_text_id)
        if x < -len(text) * 8:
            canvas.coords(scroll_text_id, w + 10, y)
        root.after(50, tick_scroll)
    tick_scroll()

def init_balloons():
    balloons.clear()
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    for _ in range(14):
        balloons.append({
            "x": random.randint(50, max(50, w - 50)),
            "y": random.randint(80, max(80, h - 300)),
            "dx": random.choice([-2, -1, 1, 2]),
            "dy": random.choice([-2, -1, 1, 2]),
            "color": random.choice(balloon_colors),
            "r": random.randint(15, 25),
            "phase": random.uniform(0, 2*math.pi)
        })

def draw_balloons():
    canvas.delete("balloon")
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    for b in balloons:
        if paused or phase != "flame":
            x, y, r, col = b["x"], b["y"], b["r"], b["color"]
            canvas.create_oval(x - r, y - r, x + r, y + r,
                               fill=col, outline="", tags=("balloon",))
            continue
        b["x"] += b["dx"]
        b["phase"] += 0.1
        b["y"] += b["dy"] + math.sin(b["phase"]) * 2
        if b["y"] < 60 or b["y"] > h - 200:
            b["dy"] *= -1
        if b["x"] < 40 or b["x"] > w - 40:
            b["dx"] *= -1
        x, y, r, col = b["x"], b["y"], b["r"], b["color"]
        canvas.create_oval(x - r, y - r, x + r, y + r,
                           fill=col, outline="", tags=("balloon",))

def draw_cake_and_flames():
    if phase != "flame":
        return
    canvas.delete("flame")
    canvas.delete("cake")
    canvas.delete("balloon")

    w = canvas.winfo_width()
    top_y = get_cake_top_y()
    cx, _ = get_canvas_center()

    draw_balloons()

    edge =     "❀★❀★❀★❀★❀★❀"
    layer1 =   "▓" * 20
    layer2 =   "░" * 20
    layer3 =   "█" * 28
    layer4 =   "●" * 46
    layer5 =   "■" * 34
    base =     "~" * 48
    canvas.create_text(cx, top_y + 10, text=edge,
                       font=("Segoe UI", 24), fill="pink", tags=("cake",))
    canvas.create_text(cx, top_y + 40, text=layer1,
                       font=("Segoe UI", 22), fill="#FFB380", tags=("cake",))
    canvas.create_text(cx, top_y + 70, text=layer2,
                       font=("Segoe UI", 22), fill="#FFCC99", tags=("cake",))
    canvas.create_text(cx, top_y + 100, text=layer3,
                       font=("Segoe UI", 22), fill="#FF9966", tags=("cake",))
    canvas.create_text(cx, top_y + 130, text=layer4,
                       font=("Segoe UI", 22), fill="#EBD38A", tags=("cake",))
    canvas.create_text(cx, top_y + 160, text=layer5,
                       font=("Segoe UI", 22), fill="#D69F4F", tags=("cake",))
    canvas.create_text(cx, top_y + 190, text=base,
                       font=("Segoe UI", 20), fill="orange", tags=("cake",))

    offsets = [-140, -50, 50, 140]
    color = next(flame_colors)
    shape = next(flame_shapes)
    for i, dx in enumerate(offsets):
        x = cx + dx
        if not flame_state[i]:
            canvas.create_text(x, top_y - 10,
                               text=shape, fill=color,
                               font=("Segoe UI", 28), tags=("flame",))
        canvas.create_text(x, top_y + 10, text="║",
                           font=("Segoe UI", 28), fill="skyblue",
                           tags=("cake",))
        canvas.create_text(x, top_y + 40, text="▐▌",
                           font=("Segoe UI", 20), fill="lightgray",
                           tags=("cake",))

    if all(flame_state):
        go_show_fireworks()
    else:
        root.after(400, draw_cake_and_flames)

def on_canvas_click(event):
    global phase
    if phase == "flame":
        flame_ids = canvas.find_withtag("flame")
        for fid in flame_ids:
            bbox = canvas.bbox(fid)
            if bbox and bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]:
                x0, y0 = canvas.coords(fid)
                cx, _ = get_canvas_center()
                offsets = [-140, -50, 50, 140]
                for i, dx in enumerate(offsets):
                    if abs(x0 - (cx + dx)) < 20:
                        flame_state[i] = True
                        canvas.delete("flame")
                        return
    elif phase == "game" and not paused:
        click_gift_or_bomb(event)

canvas.bind("<Button-1>", on_canvas_click)

def go_show_fireworks():
    global phase
    phase = "fireworks"
    canvas.delete("all")

    w = canvas.winfo_width()
    h = canvas.winfo_height()

    fire_chars = ["★", "✦", "✧", "❀", "*", "+", "o", "·", "°", "✺", "✹"]
    colors = ["red", "orange", "yellow", "green", "magenta", "cyan", "white", "lightblue", "hot pink"]

    def batch_fireworks(batch):
        if batch > 0:
            canvas.delete(f"fire{batch-1}")
        for _ in range(80):
            x0 = random.randint(0, w)
            y0 = random.randint(0, h)
            ch = random.choice(fire_chars)
            color = random.choice(colors)
            size = random.randint(20, 48)
            canvas.create_text(x0, y0,
                               text=ch, fill=color,
                               font=("Segoe UI", size, "bold"),
                               tags=(f"fire{batch}",))
        if batch < 4:
            root.after(150, lambda: batch_fireworks(batch + 1))
        else:
            canvas.create_text(w / 2, h / 2,
                               text="🎉 愿望达成！🎉",
                               fill="white",
                               font=("Segoe UI", 48, "bold"),
                               tags=("fire_text",))
            root.after(1200, start_gift_game)

    batch_fireworks(0)

def start_gift_game():
    global phase, game_score, game_remaining_time, game_timer_id, spawn_timer_id, move_interval, paused, scroll_text_id
    phase = "game"
    paused = False
    game_score = 0
    move_interval = 50
    game_remaining_time = game_time_limit

    if game_timer_id:
        root.after_cancel(game_timer_id)
    if spawn_timer_id:
        root.after_cancel(spawn_timer_id)

    canvas.delete("all")
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    canvas.create_rectangle(0, 0, w, h, fill="#EEEEEE", outline="", tags=("game_bg",))

    # 进入小游戏后移除横幅与滚动祝福
    banner_label.place_forget()
    if scroll_text_id:
        canvas.delete("scroll")
        scroll_text_id = None

    instruction = f"🎁 点击 {game_target_score} 个礼物盒，限时 {game_time_limit} 秒！"
    canvas.create_text(w / 2, 40,
                       text=instruction,
                       fill="black",
                       font=("Segoe UI", 20, "bold"),
                       tags=("instruction_text",))
    canvas.create_text(w / 2, 80,
                       text=f"得分：{game_score}",
                       fill="darkblue",
                       font=("Segoe UI", 18, "bold"),
                       tags=("score_text",))
    canvas.create_text(w / 2, 120,
                       text=f"剩余时间：{game_remaining_time} 秒",
                       fill="darkblue",
                       font=("Segoe UI", 16, "bold"),
                       tags=("timer_text",))

    pause_button.config(text="暂停")
    pause_button.place(relx=0.75, rely=0.02, anchor="ne")
    exit_button.place(relx=0.95, rely=0.02, anchor="ne")

    gift_ids.clear()
    bomb_ids.clear()

    def spawn_timer():
        global spawn_timer_id
        if phase != "game":
            return
        if not paused and len(gift_ids) + len(bomb_ids) < 6:
            spawn_gift_or_bomb()
        spawn_timer_id = root.after(700, spawn_timer)

    spawn_timer()

    def game_countdown():
        global game_timer_id, game_remaining_time
        if phase != "game":
            return
        if not paused:
            game_remaining_time -= 1
            canvas.delete("timer_text")
            if game_remaining_time <= 0:
                canvas.create_text(w / 2, 120,
                                   text=f"剩余时间：0 秒",
                                   fill="darkblue",
                                   font=("Segoe UI", 16, "bold"),
                                   tags=("timer_text",))
                end_gift_game()
                return
            else:
                canvas.create_text(w / 2, 120,
                                   text=f"剩余时间：{game_remaining_time} 秒",
                                   fill="darkblue",
                                   font=("Segoe UI", 16, "bold"),
                                   tags=("timer_text",))
        game_timer_id = root.after(1000, game_countdown)

    game_countdown()

def spawn_gift_or_bomb():
    if phase != "game" or paused:
        return
    w = canvas.winfo_width()
    y = -20
    x = random.randint(50, w - 50)
    if random.random() < 0.8:
        color = random.choice(["red", "green", "blue", "magenta", "orange", "purple", "navy", "teal"])
        obj_id = canvas.create_text(x, y,
                                    text="🎁", font=("Segoe UI", 32),
                                    fill=color,
                                    tags=("gift",))
        gift_ids.append(obj_id)
    else:
        obj_id = canvas.create_text(x, y,
                                    text="💣", font=("Segoe UI", 32),
                                    fill="black",
                                    tags=("bomb",))
        bomb_ids.append(obj_id)
    move_obj(obj_id)

def move_obj(obj_id):
    if phase != "game":
        if obj_id in gift_ids:
            gift_ids.remove(obj_id)
            canvas.delete(obj_id)
        if obj_id in bomb_ids:
            bomb_ids.remove(obj_id)
            canvas.delete(obj_id)
        return

    if paused:
        root.after(move_interval, lambda oid=obj_id: move_obj(oid))
        return

    coords = canvas.bbox(obj_id)
    if not coords:
        return
    x1, y1, x2, y2 = coords
    h = canvas.winfo_height()
    if y2 < h - 80:
        canvas.move(obj_id, 0, 5)
        root.after(move_interval, lambda oid=obj_id: move_obj(oid))
    else:
        if obj_id in gift_ids:
            gift_ids.remove(obj_id)
            canvas.delete(obj_id)
        if obj_id in bomb_ids:
            bomb_ids.remove(obj_id)
            canvas.delete(obj_id)
        spawn_gift_or_bomb()

def click_gift_or_bomb(event):
    global game_score, move_interval
    w = canvas.winfo_width()

    for bid in bomb_ids.copy():
        coords = canvas.bbox(bid)
        if coords:
            x1, y1, x2, y2 = coords
            if (x1 - 10) <= event.x <= (x2 + 10) and (y1 - 10) <= event.y <= (y2 + 10):
                canvas.delete(bid)
                bomb_ids.remove(bid)
                game_score = 0
                canvas.delete("score_text")
                canvas.create_text(w / 2, 80,
                                   text=f"得分：{game_score}",
                                   fill="darkblue",
                                   font=("Segoe UI", 18, "bold"),
                                   tags=("score_text",))
                canvas.delete("bomb_info")
                canvas.create_text(w / 2, 160,
                                   text="💥 点到炸弹，分数归零！",
                                   fill="red",
                                   font=("Segoe UI", 18, "bold"),
                                   tags=("bomb_info",))
                root.after(2000, lambda: canvas.delete("bomb_info"))
                spawn_gift_or_bomb()
                return

    for gid in gift_ids.copy():
        coords = canvas.bbox(gid)
        if coords:
            x1, y1, x2, y2 = coords
            if (x1 - 10) <= event.x <= (x2 + 10) and (y1 - 10) <= event.y <= (y2 + 10):
                canvas.delete(gid)
                gift_ids.remove(gid)
                game_score += 1
                canvas.delete("score_text")
                canvas.create_text(w / 2, 80,
                                   text=f"得分：{game_score}",
                                   fill="darkblue",
                                   font=("Segoe UI", 18, "bold"),
                                   tags=("score_text",))
                if move_interval > 15:
                    move_interval = max(15, move_interval - 3)
                spawn_gift_or_bomb()
                return

def end_gift_game():
    global phase
    phase = "end"
    if game_timer_id:
        root.after_cancel(game_timer_id)
    if spawn_timer_id:
        root.after_cancel(spawn_timer_id)

    canvas.delete("gift")
    canvas.delete("bomb")
    canvas.delete("timer_text")
    canvas.delete("score_text")
    canvas.delete("bomb_info")

    w = canvas.winfo_width()
    if game_score >= game_target_score and game_remaining_time >= 0:
        msg = f"🎉 恭喜！{game_score} 分，挑战成功！"
    else:
        msg = f"挑战结束，你得了 {game_score} 分。"

    canvas.create_text(w / 2, 200,
                       text=msg, fill="darkblue",
                       font=("Segoe UI", 24, "bold"),
                       tags=("end_text",))

    pause_button.place_forget()
    exit_button.place(relx=0.95, rely=0.02, anchor="ne")

def toggle_pause():
    global paused
    if phase != "game":
        return
    paused = not paused
    if paused:
        pause_button.config(text="继续")
        canvas.delete("bomb_info")
    else:
        pause_button.config(text="暂停")

def on_startup(event=None):
    init_balloons()
    start_scrolling_text()
    draw_cake_and_flames()

canvas.bind("<Configure>", on_startup)

root.mainloop()
