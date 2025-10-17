"""
用户认证模块
"""
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.security import HTTPBearer
from .models import User, UserSession
from .database import get_db
import os
from loguru import logger

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """认证服务"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Token验证失败: {e}")
            return None
    
    def create_user_session(self, db: Session, user_id: str) -> str:
        """创建用户会话"""
        # 生成新的token
        token_data = {"sub": user_id, "type": "access"}
        token = self.create_access_token(token_data)
        
        # 计算过期时间
        expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # 创建会话记录
        session = UserSession(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"用户会话创建成功: user_id={user_id}")
        return token
    
    def get_user_by_token(self, db: Session, token: str) -> Optional[User]:
        """通过token获取用户"""
        # 验证token
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # 检查会话是否有效
        session = db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            return None
        
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        return user
    
    def logout_user(self, db: Session, token: str) -> bool:
        """用户登出"""
        session = db.query(UserSession).filter(UserSession.token == token).first()
        if session:
            session.is_active = False
            db.commit()
            logger.info(f"用户登出成功: user_id={session.user_id}")
            return True
        return False

# 安全方案
security = HTTPBearer()

# 全局认证服务实例
auth_service = AuthService()

def get_current_user(token: str = Depends(security), db: Session = Depends(get_db)) -> Optional[User]:
    """获取当前用户（依赖注入用）"""
    return auth_service.get_user_by_token(db, token.credentials)
