# clear() - Очищает экран.

# show() - Обновляет экран, отображая все изменения.

# text(text, x, y, align="left") - Выводит текст на экран. text: Текст для отображения. x, y: Координаты начала текста. align: Выравнивание текста ("left", "center", "right").

# rect(x, y, width, height, fill=False) - Рисует прямоугольник. x, y: Координаты верхнего левого угла. width, height: Ширина и высота прямоугольника. fill: Заливка (True/False).

# line(x1, y1, x2, y2) - Рисует линию. x1, y1: Начальная точка. x2, y2: Конечная точка.

# circle(x, y, radius, fill=False) - Рисует круг. x, y: Координаты центра. radius: Радиус круга. fill: Заливка (True/False).

# triangle(x1, y1, x2, y2, x3, y3, fill=False) - Рисует треугольник. x1, y1: Координаты первой вершины. x2, y2: Координаты второй вершины. x3, y3: Координаты третьей вершины. fill: Заливка (True/False).

# bitmap(x, y, data, width, height) - Отображает bitmap-изображение. x, y: Координаты верхнего левого угла. data: Данные изображения (список байтов). width, height: Ширина и высота изображения.

# bitmap_data = [0b00011000, 0b00111100, 0b01111110, 0b11111111, 0b11111111, 0b01111110, 0b00111100, 0b00011000]
# oled.bitmap(10, 10, bitmap_data, 8, 8)
# contrast(value) - Устанавливает контраст дисплея. value: Значение контраста (0-255).

# power(on=True) - Включает или выключает дисплей. on: Включение (True) или выключение (False).

# invert(invert=True) - Инвертирует цвета дисплея. invert: Инверсия (True) или нормальный режим (False).


from machine import I2C, Pin
from sillyOled import SillyOled

def init_display():
    # Инициализация I2C
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))

    # Инициализация дисплея
    oled = SillyOled(i2c, width=128, height=64, address=0x3C)
    return oled

def display_message(oled, message):
    oled.clear()
    oled.text(message, 20, 30)
    oled.show()

def display_control(oled, status):
    oled.power(status)
    