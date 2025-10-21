"""版本验证Agent"""
from typing import Dict, Any, Tuple, Optional
from loguru import logger
import json
import os

class VersionValidatorAgent:
    """版本验证Agent - 验证书籍和版本是否存在"""
    
    def __init__(self):
        self.books_metadata = self._load_books_metadata()
    
    def _load_books_metadata(self) -> Dict[str, Any]:
        """加载书籍元数据"""
        metadata_path = os.path.join(os.path.dirname(__file__), "../../data/books_metadata.json")
        
        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"书籍元数据文件不存在: {metadata_path}")
                return {"books": []}
        except Exception as e:
            logger.error(f"加载书籍元数据失败: {e}")
            return {"books": []}
    
    def validate(self, book_name: str, version: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        验证书籍和版本
        
        Args:
            book_name: 书名
            version: 版本号（可选）
            
        Returns:
            (is_valid, message, metadata)
        """
        logger.info(f"验证书籍: {book_name}, 版本: {version}")
        
        # 查找匹配的书籍
        book_info = self._find_book(book_name)
        if not book_info:
            available_books = self._get_available_books()
            return False, f"系统中没有找到《{book_name}》这本书。\n\n可用书籍：\n{available_books}", {}
        
        # 如果没有指定版本，使用最新版本
        if not version:
            latest_version = self._get_latest_version(book_info)
            if latest_version:
                metadata = latest_version.copy()
                metadata["book_name"] = book_info["name"]
                return True, f"未指定版本，自动使用最新版本：第{latest_version['version']}版", metadata
            else:
                return False, f"《{book_name}》没有可用的版本", {}
        
        # 验证指定版本
        version_info = self._find_version(book_info, version)
        if not version_info:
            available_versions = self._get_available_versions(book_info)
            return False, f"《{book_name}》没有第{version}版。\n\n可用版本：\n{available_versions}", {}
        
        # 返回版本信息
        metadata = version_info.copy()
        metadata["book_name"] = book_info["name"]
        
        logger.info(f"✓ 验证通过: {book_info['name']} 第{version}版")
        return True, "", metadata
    
    def get_collection_name(self, book_name: str, version: str) -> str:
        """获取collection名称"""
        book_info = self._find_book(book_name)
        if not book_info:
            return ""
        
        book_id = book_info["id"]
        return f"{book_id}_v{version}"
    
    def list_all_books_and_versions(self) -> str:
        """列出所有可用的书籍和版本"""
        if not self.books_metadata.get("books"):
            return "暂无可用书籍"
        
        result = []
        for book in self.books_metadata["books"]:
            book_name = book["name"]
            versions = [v["version"] for v in book.get("versions", [])]
            if versions:
                version_str = "、".join([f"第{v}版" for v in versions])
                result.append(f"• {book_name}: {version_str}")
            else:
                result.append(f"• {book_name}: 无可用版本")
        
        return "\n".join(result)
    
    def _find_book(self, book_name: str) -> Optional[Dict[str, Any]]:
        """查找匹配的书籍"""
        if not self.books_metadata.get("books"):
            return None
        
        # 精确匹配
        for book in self.books_metadata["books"]:
            if book["name"] == book_name:
                return book
        
        # 模糊匹配
        for book in self.books_metadata["books"]:
            if book_name in book["name"] or book["name"] in book_name:
                return book
        
        return None
    
    def _find_version(self, book_info: Dict[str, Any], version: str) -> Optional[Dict[str, Any]]:
        """查找指定版本"""
        versions = book_info.get("versions", [])
        for v in versions:
            if v["version"] == version:
                return v
        return None
    
    def _get_latest_version(self, book_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取最新版本"""
        versions = book_info.get("versions", [])
        if not versions:
            return None
        
        # 按版本号排序，取最新的
        sorted_versions = sorted(versions, key=lambda x: int(x["version"]), reverse=True)
        return sorted_versions[0]
    
    def _get_available_books(self) -> str:
        """获取可用书籍列表"""
        if not self.books_metadata.get("books"):
            return "暂无可用书籍"
        
        book_names = [book["name"] for book in self.books_metadata["books"]]
        return "、".join(book_names)
    
    def _get_available_versions(self, book_info: Dict[str, Any]) -> str:
        """获取可用版本列表"""
        versions = book_info.get("versions", [])
        if not versions:
            return "无可用版本"
        
        version_list = [f"第{v['version']}版" for v in versions]
        return "、".join(version_list)
    
    def get_book_metadata(self, book_name: str, version: str = None) -> Optional[Dict[str, Any]]:
        """获取书籍元数据"""
        is_valid, _, metadata = self.validate(book_name, version)
        if is_valid:
            return metadata
        return None
    
    def get_all_collections(self) -> list:
        """获取所有可用的collection名称"""
        collections = []
        for book in self.books_metadata.get("books", []):
            for version in book.get("versions", []):
                collection_name = f"{book['id']}_v{version['version']}"
                collections.append(collection_name)
        return collections

# 测试代码
if __name__ == "__main__":
    agent = VersionValidatorAgent()
    
    # 测试验证功能
    test_cases = [
        ("流行病学", "7"),
        ("流行病学", "8"),
        ("流行病学", None),
        ("生理学", "9"),
        ("不存在的书", "1")
    ]
    
    for book_name, version in test_cases:
        is_valid, message, metadata = agent.validate(book_name, version)
        print(f"\n验证: {book_name} 第{version}版")
        print(f"结果: {'✓' if is_valid else '✗'}")
        print(f"消息: {message}")
        if metadata:
            print(f"元数据: {metadata.get('isbn', 'N/A')}")
    
    # 测试collection名称生成
    collection_name = agent.get_collection_name("流行病学", "7")
    print(f"\nCollection名称: {collection_name}")
    
    # 列出所有书籍
    print(f"\n所有可用书籍:\n{agent.list_all_books_and_versions()}")
