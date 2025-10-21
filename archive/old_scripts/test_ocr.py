'''
Author: Diana Tang
Date: 2025-10-20 10:41:01
LastEditors: Diana Tang
Description: some description
FilePath: /DT-Study-Companion/test_ocr.py
'''
#!/usr/bin/env python3
"""测试OCR功能"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import fitz  # PyMuPDF

def test_ocr():
    """测试OCR功能"""
    pdf_path = "./data/流行病学第8版.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    print(f"开始OCR测试: {pdf_path}")
    
    try:
        # 检查OCR库
        try:
            import pytesseract
            from PIL import Image
            import io
            print("✓ OCR库已安装")
        except ImportError as e:
            print(f"✗ OCR库未安装: {e}")
            print("请运行: pip install pytesseract pillow")
            return
        
        doc = fitz.open(pdf_path)
        print(f"PDF页数: {len(doc)}")
        
        # 测试第一页的OCR
        page = doc[0]
        print("\n=== OCR测试第1页 ===")
        
        # 将页面转换为图片
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍缩放
        img_data = pix.tobytes("png")
        
        # 转换为PIL图像
        image = Image.open(io.BytesIO(img_data))
        print(f"图片尺寸: {image.size}")
        
        # 执行OCR
        print("执行OCR识别...")
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        print(f"OCR结果长度: {len(text)}")
        print(f"OCR结果预览: {text[:300]}...")
        
        if text.strip():
            print("✓ OCR识别成功")
        else:
            print("✗ OCR识别失败")
        
        doc.close()
        
    except Exception as e:
        print(f"OCR测试失败: {e}")

if __name__ == "__main__":
    test_ocr()
