from PIL import Image, ImageDraw, ImageFilter
import os
import math

images_dir = "docs/images"
os.makedirs(images_dir, exist_ok=True)

# 配色方案：暖调、低饱和
COLORS = {
    'bg1': (250, 247, 242),
    'bg2': (240, 234, 224),
    'bg3': (232, 224, 212),
    'accent1': (139, 115, 85),
    'accent2': (166, 142, 112),
    'accent3': (194, 174, 148),
    'light': (255, 252, 248),
    'soft': (220, 208, 192),
}


def radial_gradient(size, center_color, edge_color):
    """创建径向渐变"""
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    cx, cy = size[0] // 2, size[1] // 2
    max_dist = math.sqrt(cx**2 + cy**2)
    for y in range(size[1]):
        for x in range(0, size[0], 2):
            dist = math.sqrt((x-cx)**2 + (y-cy)**2)
            ratio = dist / max_dist
            r = int(center_color[0] + (edge_color[0] - center_color[0]) * ratio)
            g = int(center_color[1] + (edge_color[1] - center_color[1]) * ratio)
            b = int(center_color[2] + (edge_color[2] - center_color[2]) * ratio)
            draw.point([(x, y), (x+1, y)], fill=(r, g, b))
    return img


def linear_gradient(size, top_color, bottom_color):
    """创建线性渐变"""
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        ratio = y / size[1]
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    return img


def add_soft_blur_circle(img, center, radius, color, blur=20):
    """添加柔和模糊圆"""
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    x, y = center
    draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    overlay = overlay.filter(ImageFilter.GaussianBlur(blur))
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    return img.convert('RGB')


def draw_leaf(draw, x, y, length, width, angle, color, width_line=2):
    """绘制有机叶片"""
    rad = math.radians(angle)
    x1 = x + length * math.cos(rad)
    y1 = y + length * math.sin(rad)
    perp = math.radians(angle + 90)
    w = width / 2
    ax = x + w * math.cos(perp)
    ay = y + w * math.sin(perp)
    bx = x - w * math.cos(perp)
    by = y - w * math.sin(perp)
    cx = x1 + (w*0.3) * math.cos(perp)
    cy = y1 + (w*0.3) * math.sin(perp)
    dx = x1 - (w*0.3) * math.cos(perp)
    dy = y1 - (w*0.3) * math.sin(perp)
    draw.polygon([(ax, ay), (cx, cy), (dx, dy), (bx, by)], fill=color)
    draw.line([(x, y), (x1, y1)], fill=(*color[:3], 80), width=width_line)


def composite_overlay(img, overlay):
    """合成半透明图层"""
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.5))
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    return img.convert('RGB')


def make_cover():
    """封面图：感知之光"""
    size = (800, 280)
    img = radial_gradient(size, COLORS['bg1'], COLORS['bg3'])

    img = add_soft_blur_circle(img, (400, 140), 180, (*COLORS['bg2'], 120), 60)
    img = add_soft_blur_circle(img, (400, 140), 120, (*COLORS['soft'], 80), 40)

    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 抽象人物头部轮廓
    draw.ellipse([360, 100, 440, 180], fill=(*COLORS['accent3'], 60))
    draw.ellipse([370, 110, 430, 170], fill=(*COLORS['bg2'], 90))

    # 感知波纹
    for i, r in enumerate([90, 130, 170, 210]):
        alpha = 25 - i * 4
        draw.ellipse([400-r, 140-r, 400+r, 140+r], outline=(*COLORS['accent2'], alpha), width=1)

    # 植物叶片
    draw_leaf(draw, 680, 220, 70, 28, -70, (*COLORS['accent3'], 70))
    draw_leaf(draw, 650, 240, 55, 22, -60, (*COLORS['accent2'], 55))
    draw_leaf(draw, 120, 220, 65, 24, -110, (*COLORS['accent3'], 65))
    draw_leaf(draw, 160, 240, 50, 20, -120, (*COLORS['accent2'], 50))

    # 漂浮光点
    dots = [((250, 80), 5), ((550, 70), 4), ((680, 120), 3), ((120, 130), 4), ((720, 180), 3), ((90, 190), 2.5)]
    for pos, r in dots:
        draw.ellipse([pos[0]-r, pos[1]-r, pos[0]+r, pos[1]+r], fill=(*COLORS['light'], 200))

    # 顶部柔和光线
    draw.polygon([(0, 0), (300, 0), (150, 280), (0, 280)], fill=(*COLORS['light'], 25))
    draw.polygon([(500, 0), (800, 0), (800, 280), (650, 280)], fill=(*COLORS['light'], 20))

    img = composite_overlay(img, overlay)
    img.save(os.path.join(images_dir, 'cover.jpg'), quality=95)
    print("Generated cover.jpg")


def make_author():
    """作者图：静谧阅读"""
    size = (800, 220)
    img = linear_gradient(size, COLORS['bg1'], COLORS['bg2'])

    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 左侧书本
    book_x, book_y = 180, 80
    draw.polygon([(book_x, book_y), (book_x+80, book_y+20), (book_x+80, book_y+100), (book_x, book_y+80)], fill=(*COLORS['accent3'], 80))
    draw.polygon([(book_x+80, book_y+20), (book_x+160, book_y), (book_x+160, book_y+80), (book_x+80, book_y+100)], fill=(*COLORS['accent2'], 70))
    draw.line([(book_x+80, book_y+20), (book_x+80, book_y+100)], fill=(*COLORS['accent1'], 60), width=2)
    for i in range(3):
        y = book_y + 35 + i * 14
        draw.line([(book_x+15, y), (book_x+70, y+5)], fill=(*COLORS['light'], 120), width=2)
        draw.line([(book_x+90, y+5), (book_x+145, y)], fill=(*COLORS['light'], 120), width=2)

    # 右侧茶杯
    cup_x, cup_y = 520, 90
    draw.ellipse([cup_x, cup_y+40, cup_x+60, cup_y+70], fill=(*COLORS['accent3'], 70))
    draw.arc([cup_x+55, cup_y+50, cup_x+80, cup_y+80], 270, 90, fill=(*COLORS['accent2'], 80), width=3)
    for i, offset in enumerate([0, 20, 40]):
        x = cup_x + 15 + offset
        draw.arc([x, cup_y-25, x+15, cup_y+10], 200, 340, fill=(*COLORS['light'], 80), width=2)

    # 装饰叶片
    draw_leaf(draw, 680, 160, 45, 18, -75, (*COLORS['accent3'], 50))
    draw_leaf(draw, 100, 160, 40, 16, -105, (*COLORS['accent2'], 45))

    img = add_soft_blur_circle(img, (400, 110), 150, (*COLORS['soft'], 60), 50)
    img = composite_overlay(img, overlay)
    img.save(os.path.join(images_dir, 'author.jpg'), quality=95)
    print("Generated author.jpg")


def make_traits():
    """四种样貌图：四重视角"""
    size = (800, 220)
    img = linear_gradient(size, COLORS['bg1'], COLORS['bg2'])

    overlay = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    centers = [(140, 110), (310, 110), (480, 110), (650, 110)]

    # 1. 过度刺激 - 波纹与闪电
    cx, cy = centers[0]
    draw.ellipse([cx-45, cy-45, cx+45, cy+45], fill=(*COLORS['bg2'], 120))
    for r in [15, 28, 40]:
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(*COLORS['accent2'], 60), width=1)
    draw.polygon([(cx-5, cy-25), (cx+8, cy-5), (cx+2, cy-5), (cx+6, cy+20), (cx-8, cy), (cx-2, cy), (cx-5, cy-25)], fill=(*COLORS['accent1'], 80))

    # 2. 情绪强烈 - 心形
    cx, cy = centers[1]
    draw.ellipse([cx-45, cy-45, cx+45, cy+45], fill=(*COLORS['bg2'], 120))
    heart = []
    for t in range(100):
        t_val = t / 100.0 * 2 * math.pi
        x = 16 * math.sin(t_val)**3
        y = -(13 * math.cos(t_val) - 5 * math.cos(2*t_val) - 2 * math.cos(3*t_val) - math.cos(4*t_val))
        heart.append((cx + x*1.8, cy + y*1.8 - 5))
    draw.polygon(heart, fill=(*COLORS['accent2'], 85))

    # 3. 高度共情 - 连接
    cx, cy = centers[2]
    draw.ellipse([cx-45, cy-45, cx+45, cy+45], fill=(*COLORS['bg2'], 120))
    draw.ellipse([cx-22, cy-8, cx-8, cy+8], fill=(*COLORS['accent3'], 80))
    draw.ellipse([cx+8, cy-8, cx+22, cy+8], fill=(*COLORS['accent3'], 80))
    draw.ellipse([cx-6, cy-6, cx+6, cy+6], fill=(*COLORS['accent1'], 90))
    draw.line([(cx-15, cy), (cx-6, cy)], fill=(*COLORS['accent2'], 100), width=2)
    draw.line([(cx+6, cy), (cx+15, cy)], fill=(*COLORS['accent2'], 100), width=2)

    # 4. 追求深度 - 阶梯/星光
    cx, cy = centers[3]
    draw.ellipse([cx-45, cy-45, cx+45, cy+45], fill=(*COLORS['bg2'], 120))
    for i in range(4):
        y = cy + 25 - i * 14
        x1 = cx - 25 + i * 5
        x2 = cx + 25 - i * 5
        draw.line([(x1, y), (x2, y)], fill=(*COLORS['accent2'], 80), width=3)
    draw.ellipse([cx-4, cy-38, cx+4, cy-30], fill=(*COLORS['light'], 200))
    draw.ellipse([cx-25, cy-25, cx-21, cy-21], fill=(*COLORS['light'], 120))
    draw.ellipse([cx+20, cy-28, cx+24, cy-24], fill=(*COLORS['light'], 100))

    img = add_soft_blur_circle(img, (400, 110), 200, (*COLORS['soft'], 40), 60)
    img = composite_overlay(img, overlay)
    img.save(os.path.join(images_dir, 'traits.jpg'), quality=95)
    print("Generated traits.jpg")


if __name__ == "__main__":
    make_cover()
    make_author()
    make_traits()
