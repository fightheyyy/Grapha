from PIL import Image
import numpy as np

# 打开图片
image = Image.open('captcha.png')

# 将图片转换为numpy数组
array = np.array(image)

# 验证码的坐标范围（根据计算结果调整）
x_start, y_start, x_end, y_end = 344, 465, 491, 524

# 裁剪验证码
captcha = array[y_start:y_end+1, x_start:x_end+1]  # +1确保包含右下角像素

# 保存裁剪后的验证码
cropped_image = Image.fromarray(captcha)
cropped_image.save('裁剪后的验证码.png')