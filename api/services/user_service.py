"""
用户服务模块
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models import User, QueryHistory
from ..auth import auth_service
from loguru import logger
import re

class UserService:
    """用户服务"""
    
    def __init__(self):
        self.auth_service = auth_service
    
    def validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        # 中国大陆手机号正则
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    def create_user(self, db: Session, phone: str, nickname: Optional[str] = None) -> User:
        """创建新用户"""
        # 验证手机号格式
        if not self.validate_phone(phone):
            raise ValueError("手机号格式不正确")
        
        # 检查手机号是否已存在
        existing_user = db.query(User).filter(User.phone == phone).first()
        if existing_user:
            if existing_user.is_active:
                raise ValueError("该手机号已注册")
            else:
                # 重新激活用户
                existing_user.is_active = True
                db.commit()
                db.refresh(existing_user)
                logger.info(f"用户重新激活: {phone}")
                return existing_user
        
        # 创建新用户
        user = User(
            phone=phone,
            nickname=nickname or f"用户{phone[-4:]}"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"新用户创建成功: {phone}")
        return user
    
    def get_user_by_phone(self, db: Session, phone: str) -> Optional[User]:
        """通过手机号获取用户"""
        return db.query(User).filter(User.phone == phone, User.is_active == True).first()
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """通过ID获取用户"""
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    def update_user_profile(self, db: Session, user_id: str, **kwargs) -> Optional[User]:
        """更新用户资料"""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # 允许更新的字段
        allowed_fields = ['nickname', 'avatar_url']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"用户资料更新成功: {user_id}")
        return user
    
    def get_user_query_history(self, db: Session, user_id: str, limit: int = 20, offset: int = 0) -> List[QueryHistory]:
        """获取用户查询历史"""
        return db.query(QueryHistory).filter(
            QueryHistory.user_id == user_id
        ).order_by(desc(QueryHistory.created_at)).offset(offset).limit(limit).all()
    
    def add_query_history(self, db: Session, user_id: str, query: str, answer: str = None, 
                         book_name: str = None, version: str = None, 
                         confidence: str = None, agent_type: str = None) -> QueryHistory:
        """添加查询历史"""
        history = QueryHistory(
            user_id=user_id,
            query=query,
            answer=answer,
            book_name=book_name,
            version=version,
            confidence=confidence,
            agent_type=agent_type
        )
        
        db.add(history)
        db.commit()
        db.refresh(history)
        
        return history
    
    def delete_query_history(self, db: Session, user_id: str, history_id: str) -> bool:
        """删除查询历史"""
        history = db.query(QueryHistory).filter(
            QueryHistory.id == history_id,
            QueryHistory.user_id == user_id
        ).first()
        
        if history:
            db.delete(history)
            db.commit()
            logger.info(f"查询历史删除成功: {history_id}")
            return True
        return False
    
    def get_user_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        # 总查询次数
        total_queries = db.query(QueryHistory).filter(QueryHistory.user_id == user_id).count()
        
        # 最近7天查询次数
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_queries = db.query(QueryHistory).filter(
            QueryHistory.user_id == user_id,
            QueryHistory.created_at >= week_ago
        ).count()
        
        # 最常查询的书籍
        from sqlalchemy import func
        popular_books = db.query(
            QueryHistory.book_name,
            func.count(QueryHistory.book_name).label('count')
        ).filter(
            QueryHistory.user_id == user_id,
            QueryHistory.book_name.isnot(None)
        ).group_by(QueryHistory.book_name).order_by(desc('count')).limit(5).all()
        
        return {
            "total_queries": total_queries,
            "recent_queries": recent_queries,
            "popular_books": [{"name": book[0], "count": book[1]} for book in popular_books]
        }
