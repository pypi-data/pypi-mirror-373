import math
import sys
import time

RESET = '\033[0m'
BOLD = '\033[1m'
ITALIC = '\033[3m'

def gradient_print(text, colors, style="normal"):
    style_code = ""
    if style == "bold":
        style_code = BOLD
    elif style == "italic":
        style_code = ITALIC

    gradient_text = ""
    for i, char in enumerate(text):
        gradient_text += f"{style_code}{colors[i % len(colors)]}{char}"

    sys.stdout.write(gradient_text + RESET + '\n')
    sys.stdout.flush()

def rainbow_gradient_print(text, colors, style="normal"):
    style_code = ""
    if style == "bold":
        style_code = BOLD
    elif style == "italic":
        style_code = ITALIC

    gradient_text = ""
    for i, char in enumerate(text):
        gradient_text += f"{style_code}{colors[i % len(colors)]}{char}"

    sys.stdout.write(gradient_text + RESET + '\r')
    sys.stdout.flush()

def generate_gradient(start_rgb, end_rgb, length):
    gradient = []
    for i in range(length):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / max(length-1,1))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / max(length-1,1))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / max(length-1,1))
        gradient.append(f'\033[38;2;{r};{g};{b}m')
    return gradient

GRADIENTS = {
    "red":    ((255,120,120), (180,30,30)),
    "green":  ((120,255,120), (30,140,30)),
    "blue":   ((120,180,255), (50,90,180)),
    "yellow": ((255,255,150), (180,180,70)),
    "orange": ((255,200,120), (180,100,30)),
    "pink":   ((255,200,220), (255,160,200)),
    "purple": ((220,180,255), (140,50,180)),
    "cyan":   ((120,255,255), (50,180,180)),
    "magenta":((255,150,255), (180,60,180)),
    "lime":   ((200,255,120), (100,180,50)),
    "aqua":   ((160,255,240), (120,220,255)),
    "gold":   ((255,215,100), (160,120,20)),
    "silver": ((220,220,220), (150,150,150)),
    "brown":  ((180,120,80), (100,60,30)),
    "teal":   ((100,220,200), (50,150,120)),
    "indigo": ((160,120,255), (80,50,140)),
    "grey":   ((180,180,180), (100,100,100)),
    "white":  ((255,255,255), (200,200,200)),
}

def make_gradient_functions():
    funcs = {}
    for name, (start, end) in GRADIENTS.items():
        for style in ["normal", "bold", "italic"]:
            def f(text, s=style, st=start, en=end):
                colors = generate_gradient(st, en, len(text))
                gradient_print(text, colors, style=s)
            funcs[f"{name}_{style}"] = f
    return funcs

globals().update(make_gradient_functions())

def rainbow_colors(length, offset=0):
    colors = []
    for i in range(length):
        r = int((math.sin(i*0.3 + offset) * 127 + 128))
        g = int((math.sin(i*0.3 + 2 + offset) * 127 + 128))
        b = int((math.sin(i*0.3 + 4 + offset) * 127 + 128))
        colors.append(f'\033[38;2;{r};{g};{b}m')
    return colors

def rainbow_animate(text, duration=5, style="normal", speed=0.05):
    start_time = time.time()
    offset = 0
    while time.time() - start_time < duration:
        colors = rainbow_colors(len(text), offset)
        rainbow_gradient_print(text, colors, style=style)
        offset += 0.3
        time.sleep(speed)
    sys.stdout.write('\n')

# --- Funkcja wyświetlająca wszystkie kolory + nazwy funkcji ---
def check_available_colors():
    test_text = "🌟 Test Gradient 🌟"
    for color_name in GRADIENTS.keys():
        print(f"\n--- {color_name.upper()} ---")
        for style in ["normal", "bold", "italic"]:
            func_name = f"{color_name}_{style}"
            func = globals().get(func_name)
            if func:
                func(f"{test_text} ({style}) — import as: {func_name}")
    print("\n--- RAINBOW ANIMATION ---")
    rainbow_animate("🌈 Rainbow Animation! 🌈 - import as rainbow_animate", 5, style="bold", speed=0.05)
# --- Test ---
# if __name__ == "__main__":
#     check_available_colors()
