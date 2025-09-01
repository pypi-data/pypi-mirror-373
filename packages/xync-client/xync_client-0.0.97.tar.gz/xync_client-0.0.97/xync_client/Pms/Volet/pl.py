from os.path import dirname

from PIL import Image, ImageDraw, ImageFont

# Загрузка изображения
image = Image.open(dirname(__file__) + "/xtr_captcha.png")  # Замените на путь к вашему изображению
draw = ImageDraw.Draw(image)

# Размеры изображения
width, height = image.size

# Отступы (2% от размеров изображения)
offset_x = width * 0.02
offset_y = height * 0.02

# Количество делений сетки
grid_size = 10

# Ширина и высота ячеек с учетом отступов
step_x = (width - 2 * offset_x) // grid_size
step_y = (height - 2 * offset_y) // grid_size

# Цвет сетки (например, черный) и цвет текста
grid_color = (0, 0, 0)

# Нарисуем вертикальные и горизонтальные линии с отступами
for i in range(1, grid_size):
    # Вертикальные линии
    draw.line((offset_x + i * step_x, offset_y, offset_x + i * step_x, height - offset_y), fill=grid_color)
    # Горизонтальные линии
    draw.line((offset_x, offset_y + i * step_y, width - offset_x, offset_y + i * step_y), fill=grid_color)

# Добавим метки на оси
font = ImageFont.load_default()  # Можно заменить на шрифт по желанию

# Метки по оси X
for i in range(grid_size + 1):
    label = str(i * 10)
    # Вычисление размера текста с использованием textbbox
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        (offset_x + i * step_x - text_width // 2, height - offset_y - text_height), label, fill=(180, 0, 0), font=font
    )

# Метки по оси Y
for i in range(grid_size + 1):
    label = str(i * 10)
    # Вычисление размера текста с использованием textbbox
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text((offset_x - text_width - 2, offset_y + i * step_y - text_height // 2), label, fill=(0, 0, 180), font=font)

# Сохранить или отобразить изображение
image.show()  # Показать изображение
# image.save("output_image.jpg")  # Сохранить изображение
