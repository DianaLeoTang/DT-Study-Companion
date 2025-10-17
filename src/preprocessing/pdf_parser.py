"""PDF解析器"""
import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from ..utils.config import Config

class PDFParser:
    """PDF解析器"""
    
    def __init__(self):
        self.chunk_size = Config.PDF_CHUNK_SIZE
        self.chunk_overlap = Config.PDF_CHUNK_OVERLAP
    
    def parse_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        解析PDF文件
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            解析后的文本块列表
        """
        logger.info(f"开始解析PDF: {pdf_path}")
        
        try:
            # 打开PDF文件
            doc = fitz.open(pdf_path)
            
            chunks = []
            current_chapter = ""
            current_section = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                # 识别章节标题
                chapter_info = self._extract_chapter_info(text, page_num)
                if chapter_info:
                    current_chapter = chapter_info["title"]
                    current_section = chapter_info.get("section", "")
                
                # 清理文本
                cleaned_text = self._clean_text(text)
                
                # 分块处理
                page_chunks = self._split_text_into_chunks(
                    cleaned_text, 
                    page_num + 1,
                    current_chapter,
                    current_section
                )
                
                chunks.extend(page_chunks)
            
            doc.close()
            
            logger.info(f"✓ PDF解析完成: {len(chunks)} 个文本块")
            return chunks
            
        except Exception as e:
            logger.error(f"✗ PDF解析失败: {e}")
            raise
    
    def _extract_chapter_info(self, text: str, page_num: int) -> Optional[Dict[str, str]]:
        """提取章节信息"""
        # 章节标题模式
        chapter_patterns = [
            r'第[一二三四五六七八九十\d]+章\s*([^\n]+)',
            r'第[一二三四五六七八九十\d]+节\s*([^\n]+)',
            r'^\s*(\d+\.\d*)\s+([^\n]+)',
            r'^\s*(\d+)\s+([^\n]+)'
        ]
        
        lines = text.split('\n')
        for line in lines[:5]:  # 只检查前5行
            line = line.strip()
            if not line:
                continue
            
            for pattern in chapter_patterns:
                match = re.search(pattern, line)
                if match:
                    if len(match.groups()) == 1:
                        return {"title": match.group(1).strip()}
                    else:
                        return {
                            "title": match.group(2).strip(),
                            "section": match.group(1).strip()
                        }
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除页眉页脚（简单处理）
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 跳过可能的页眉页脚
            if self._is_header_footer(line):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _is_header_footer(self, line: str) -> bool:
        """判断是否为页眉页脚"""
        # 页眉页脚特征
        header_footer_patterns = [
            r'^\d+$',  # 纯数字（页码）
            r'^第\s*\d+\s*页$',  # 第X页
            r'^\d+\s*/\s*\d+$',  # 页码格式
            r'^第[一二三四五六七八九十\d]+章',  # 重复的章节标题
        ]
        
        for pattern in header_footer_patterns:
            if re.match(pattern, line):
                return True
        
        # 过短的行可能是页眉页脚
        if len(line) < 3:
            return True
        
        return False
    
    def _split_text_into_chunks(self, 
                               text: str, 
                               page_num: int,
                               chapter: str,
                               section: str) -> List[Dict[str, Any]]:
        """将文本分割成块"""
        chunks = []
        
        # 按段落分割
        paragraphs = text.split('\n\n')
        current_chunk = ""
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 如果当前块加上新段落会超过大小限制
            if current_length + len(paragraph) > self.chunk_size and current_chunk:
                # 保存当前块
                chunk = self._create_chunk(
                    current_chunk, 
                    page_num, 
                    chapter, 
                    section
                )
                chunks.append(chunk)
                
                # 开始新块（保留重叠部分）
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + paragraph
                current_length = len(current_chunk)
            else:
                # 添加到当前块
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                current_length = len(current_chunk)
        
        # 保存最后一个块
        if current_chunk:
            chunk = self._create_chunk(
                current_chunk, 
                page_num, 
                chapter, 
                section
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, 
                     content: str, 
                     page_num: int,
                     chapter: str,
                     section: str) -> Dict[str, Any]:
        """创建文本块"""
        return {
            "content": content.strip(),
            "metadata": {
                "page": page_num,
                "chapter": chapter or f"第{page_num}页",
                "section": section or "",
                "chunk_type": "text"
            }
        }
    
    def _get_overlap_text(self, text: str) -> str:
        """获取重叠文本"""
        if len(text) <= self.chunk_overlap:
            return text
        
        # 从末尾取重叠部分
        overlap = text[-self.chunk_overlap:]
        
        # 尝试在句子边界分割
        sentences = re.split(r'[。！？]', overlap)
        if len(sentences) > 1:
            # 保留最后一个完整句子
            return sentences[-1] + "。"
        
        return overlap
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """提取PDF元数据"""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            
            result = {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "page_count": len(doc)
            }
            
            doc.close()
            return result
            
        except Exception as e:
            logger.error(f"提取PDF元数据失败: {e}")
            return {}
    
    def get_page_text(self, pdf_path: str, page_num: int) -> str:
        """获取指定页面的文本"""
        try:
            doc = fitz.open(pdf_path)
            if page_num < 1 or page_num > len(doc):
                return ""
            
            page = doc[page_num - 1]
            text = page.get_text()
            doc.close()
            
            return self._clean_text(text)
            
        except Exception as e:
            logger.error(f"获取页面文本失败: {e}")
            return ""

# 测试代码
if __name__ == "__main__":
    parser = PDFParser()
    
    # 测试PDF解析
    pdf_path = "test.pdf"  # 替换为实际的PDF路径
    
    if os.path.exists(pdf_path):
        chunks = parser.parse_pdf(pdf_path)
        print(f"解析完成，共 {len(chunks)} 个文本块")
        
        # 显示前几个块
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n块 {i+1}:")
            print(f"页面: {chunk['metadata']['page']}")
            print(f"章节: {chunk['metadata']['chapter']}")
            print(f"内容: {chunk['content'][:100]}...")
    else:
        print("PDF文件不存在，请提供有效的PDF路径")
