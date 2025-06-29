#!/usr/bin/env python3
"""
创建Discord Bot Manager的图标文件
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    """创建应用程序图标"""
    try:
        # 创建256x256的图像
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制背景圆形
        margin = 20
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=(88, 101, 242), outline=(67, 56, 202), width=8)
        
        # 绘制机器人图标（简化版）
        # 头部
        head_size = 60
        head_x = size // 2 - head_size // 2
        head_y = size // 2 - head_size // 2 - 20
        draw.rectangle([head_x, head_y, head_x + head_size, head_y + head_size], 
                      fill=(255, 255, 255), outline=(200, 200, 200), width=2)
        
        # 眼睛
        eye_size = 12
        left_eye_x = head_x + 15
        right_eye_x = head_x + head_size - 15 - eye_size
        eye_y = head_y + 20
        draw.ellipse([left_eye_x, eye_y, left_eye_x + eye_size, eye_y + eye_size], 
                    fill=(88, 101, 242))
        draw.ellipse([right_eye_x, eye_y, right_eye_x + eye_size, eye_y + eye_size], 
                    fill=(88, 101, 242))
        
        # 身体
        body_width = 40
        body_height = 50
        body_x = size // 2 - body_width // 2
        body_y = head_y + head_size + 5
        draw.rectangle([body_x, body_y, body_x + body_width, body_y + body_height], 
                      fill=(255, 255, 255), outline=(200, 200, 200), width=2)
        
        # 手臂
        arm_width = 8
        arm_height = 30
        # 左臂
        left_arm_x = body_x - arm_width - 2
        arm_y = body_y + 10
        draw.rectangle([left_arm_x, arm_y, left_arm_x + arm_width, arm_y + arm_height], 
                      fill=(255, 255, 255), outline=(200, 200, 200), width=2)
        # 右臂
        right_arm_x = body_x + body_width + 2
        draw.rectangle([right_arm_x, arm_y, right_arm_x + arm_width, arm_y + arm_height], 
                      fill=(255, 255, 255), outline=(200, 200, 200), width=2)
        
        # 保存为不同大小的图标
        sizes = [16, 32, 48, 64, 128, 256]
        
        # 保存为ICO文件（Windows）
        ico_images = []
        for icon_size in sizes:
            resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            ico_images.append(resized)
        
        img.save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
        print("创建图标文件: icon.ico")
        
        # 保存为PNG文件（通用）
        img.save('icon.png', format='PNG')
        print("创建图标文件: icon.png")
        
        # 保存为ICNS文件（macOS）
        try:
            img.save('icon.icns', format='ICNS')
            print("创建图标文件: icon.icns")
        except Exception:
            print("注意: 无法创建ICNS文件，可能需要安装pillow-icns")
        
        return True
        
    except ImportError:
        print("需要安装Pillow库来创建图标:")
        print("pip install Pillow")
        return False
    except Exception as e:
        print(f"创建图标失败: {e}")
        return False

def main():
    """主函数"""
    print("Discord Bot Manager 图标生成器")
    print("=" * 40)
    
    if create_icon():
        print("\n图标创建成功！")
        print("文件位置:")
        print("- icon.ico (Windows)")
        print("- icon.png (通用)")
        print("- icon.icns (macOS, 如果支持)")
    else:
        print("\n图标创建失败")

if __name__ == "__main__":
    main()