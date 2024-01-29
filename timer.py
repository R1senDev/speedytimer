from ctypes.wintypes import POINT
from ctypes          import windll, byref
from time            import time


import pyglet


def mouse_position():
    cursor = POINT()
    windll.user32.GetCursorPos(byref(cursor))
    return (int(cursor.x), int(cursor.y))


config = {
    'transparency': False
}


# Важные константы
X_OFFSET = 5
Y_OFFSET = 5
RGBA_BG  = (0, 0, 0, 204 if config['transparency'] else 255)
RGBA_GREEN  = (0, 255, 0, 255)
RGBA_CYAN   = (0, 255, 255, 255)
RGBA_E64C0C = (230, 76, 12, 255)

# Важные переменные
running = False
swapped = False
last_checkout = 0
elapsed = 0


# Всё для взаимодействия с GUI
screen = pyglet.canvas.Display().get_default_screen()
window = pyglet.window.Window(
    width = 400,
    height = 80,
    style = 'overlay'
)


batch = pyglet.graphics.Batch()
# Квадрат заднего фона
bg_rect = pyglet.shapes.Rectangle(
    x = 0,
    y = 0,
    width = window.width,
    height = window.height,
    color = RGBA_BG,
    batch = batch
)
# Текст на таймере
timer_text = pyglet.text.Label(
    text = '=> Пробел <=',
    font_name = 'Consolas',
    font_size = 40,
    color = RGBA_GREEN,
    x = window.width // 2,
    y = window.height // 2,
    anchor_x = 'center',
    anchor_y = 'center',
    batch = batch
)


window.set_location(X_OFFSET, Y_OFFSET)


# Настройка воспроизведения звука
player = pyglet.media.Player()
player.loop = True
media_source = pyglet.media.load('data/music.mp3')
player.queue(media_source)


@window.event
def on_draw():
    global elapsed, last_checkout

    x, y = mouse_position()
    if window.get_location()[0] <= x <= window.get_location()[0] + window.width \
        and window.get_location()[1] <= y <= window.get_location()[1] + window.height:
        swap_side()

    window.clear()

    if running:
        current_time = time()
        elapsed += current_time - last_checkout
        last_checkout = current_time

        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        timer_text.text = f'{str(round(h)).zfill(2)}:{str(round(m)).zfill(2)}:{str(strict_round(s, 3)).zfill(6)}'

    batch.draw()


# Обработчик нажатий клавиш клавиатуры
@window.event
def on_key_press(keyid, mod):
    print('on_key_press', keyid, mod, sep = '\t')
    global elapsed

    # Space or Ctrl + Space - start
    # Ctrl + Space - stop or continue
    if keyid == 32 and (mod in [18, 258] or elapsed == 0):
            global running, last_checkout

            running = not running

            if running:
                last_checkout = time()
                timer_text.color = RGBA_E64C0C
                player.play()
            else:
                timer_text.color = RGBA_CYAN
                player.pause()

    # Ctrl + R - refresh
    if keyid == 114 and mod in [18, 258]:
        timer_text.text = '00:00:00.000'
        elapsed = 0
        running = False
        timer_text.color = RGBA_GREEN
        player.pause()
        

# Телепортирует окно на противоположный край экрана
def swap_side():
    global swapped

    swapped = not swapped

    if swapped:
        window.set_location(screen.width - (window.width + X_OFFSET), window.get_location()[1])
    else:
        window.set_location(X_OFFSET, window.get_location()[1])


# Округляет РОВНО до указанного количества знаков после точки, а не как round в идиотской стандартной библиотеке
def strict_round(n: float, digits: int) -> str:
    out = str(round(n, digits))
    if '.' not in out: out += '.'
    while len(out.split('.')[1]) < digits: out += '0'
    return out


pyglet.app.run()
