#!/usr/bin/env python3
"""测试PDF解析"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import fitz  # PyMuPDF

def test_pdf_parsing():
    """测试PDF解析"""
    pdf_path = "./data/流行病学第8版.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    print(f"开始解析PDF: {pdf_path}")
    
    try:
        doc = fitz.open(pdf_path)
        print(f"PDF页数: {len(doc)}")
        
        # 解析前几页
        for page_num in range(min(3, len(doc))):
            page = doc[page_num]
            text = page.get_text()
            
            print(f"\n=== 第 {page_num + 1} 页 ===")
            print(f"原始文本长度: {len(text)}")
            print(f"文本内容预览: {text[:200]}...")
            
            # 检查是否有文本
            if text.strip():
                print("✓ 页面有文本内容")
            else:
                print("✗ 页面无文本内容")
                
                # 尝试OCR
                print("尝试OCR识别...")
                try:
                    # 将页面转换为图片
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    
                    # 这里需要安装pytesseract和PIL
                    # 暂时跳过OCR，直接使用图片
                    print("页面是图片格式，需要OCR处理")
                except Exception as e:
                    print(f"OCR处理失败: {e}")
        
        doc.close()
        
    except Exception as e:
        print(f"解析失败: {e}")

if __name__ == "__main__":
    test_pdf_parsing()
