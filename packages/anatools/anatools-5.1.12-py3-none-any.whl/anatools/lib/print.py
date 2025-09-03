brand = '91e600'
error = 'ff0000'
warning = 'ffaa00'
info = '00ffff'

def print_color(text, color, end='\n', flush=False):
    if color == 'brand': color = brand
    elif color == 'error': color = error
    elif color == 'warning': color = warning
    elif color == 'info': color = info
    else: color = color
    r,g,b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    coloresc = '\033[{};2;{};{};{}m'.format(38, r, g, b)
    resetesc = '\033[0m'
    print(coloresc + text + resetesc, end=end, flush=flush)