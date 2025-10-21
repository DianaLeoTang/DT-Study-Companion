#!/usr/bin/env python3
"""简单的OCR测试脚本"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ocr():
    """测试OCR功能"""
    print("=" * 50)
    print("OCR功能测试")
    print("=" * 50)
    
    # 1. 测试库导入
    print("\n1. 测试库导入...")
    try:
        import pytesseract
        from PIL import Image
        print("✓ pytesseract 和 PIL 导入成功")
    except ImportError as e:
        print(f"✗ 库导入失败: {e}")
        return False
    
    # 2. 测试Tesseract引擎
    print("\n2. 测试Tesseract引擎...")
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract版本: {version}")
    except Exception as e:
        print(f"✗ Tesseract引擎不可用: {e}")
        print("请安装Tesseract OCR引擎:")
        print("  macOS: brew install tesseract tesseract-lang")
        print("  Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim")
        print("  Windows: 下载安装包 https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    
    # 3. 测试语言包
    print("\n3. 测试语言包...")
    try:
        langs = pytesseract.get_languages()
        print(f"✓ 可用语言: {langs}")
        
        if 'chi_sim' in langs:
            print("✓ 中文简体语言包可用")
        else:
            print("⚠ 中文简体语言包不可用，将使用英文")
            
        if 'eng' in langs:
            print("✓ 英文语言包可用")
        else:
            print("✗ 英文语言包不可用")
            return False
            
    except Exception as e:
        print(f"✗ 语言包检查失败: {e}")
        return False
    
    # 4. 测试OCR识别
    print("\n4. 测试OCR识别...")
    try:
        # 创建一个包含文字的测试图像
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建白色背景图像
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # 添加文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            # 使用默认字体
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Hello World", fill='black', font=font)
        draw.text((50, 100), "测试中文", fill='black', font=font)
        
        # 保存测试图像
        img.save("test_ocr_image.png")
        print("✓ 测试图像已创建: test_ocr_image.png")
        
        # 测试英文OCR
        try:
            eng_text = pytesseract.image_to_string(img, lang='eng')
            print(f"✓ 英文OCR结果: '{eng_text.strip()}'")
        except Exception as e:
            print(f"✗ 英文OCR失败: {e}")
        
        # 测试中文OCR（如果可用）
        if 'chi_sim' in langs:
            try:
                chi_text = pytesseract.image_to_string(img, lang='chi_sim')
                print(f"✓ 中文OCR结果: '{chi_text.strip()}'")
            except Exception as e:
                print(f"✗ 中文OCR失败: {e}")
        
        # 测试中英文混合OCR
        try:
            mixed_text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            print(f"✓ 混合OCR结果: '{mixed_text.strip()}'")
        except Exception as e:
            print(f"✗ 混合OCR失败: {e}")
            
    except Exception as e:
        print(f"✗ OCR识别测试失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ OCR功能测试完成！")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_ocr()
    sys.exit(0 if success else 1)
