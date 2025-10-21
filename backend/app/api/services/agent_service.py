"""
Agent服务模块
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import AgentConfig
from loguru import logger
import json

class AgentService:
    """Agent服务"""
    
    def __init__(self):
        pass
    
    def get_all_agents(self, db: Session) -> List[AgentConfig]:
        """获取所有可用的Agent"""
        return db.query(AgentConfig).filter(AgentConfig.is_active == True).all()
    
    def get_agent_by_name(self, db: Session, name: str) -> Optional[AgentConfig]:
        """通过名称获取Agent"""
        return db.query(AgentConfig).filter(
            AgentConfig.name == name,
            AgentConfig.is_active == True
        ).first()
    
    def create_agent(self, db: Session, name: str, display_name: str, 
                    description: str = None, icon: str = None, 
                    config: Dict[str, Any] = None) -> AgentConfig:
        """创建新的Agent配置"""
        agent = AgentConfig(
            name=name,
            display_name=display_name,
            description=description,
            icon=icon,
            config=json.dumps(config) if config else None
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        logger.info(f"Agent创建成功: {name}")
        return agent
    
    def update_agent(self, db: Session, name: str, **kwargs) -> Optional[AgentConfig]:
        """更新Agent配置"""
        agent = self.get_agent_by_name(db, name)
        if not agent:
            return None
        
        # 允许更新的字段
        allowed_fields = ['display_name', 'description', 'icon', 'config', 'is_active']
        for field, value in kwargs.items():
            if field in allowed_fields:
                if field == 'config' and isinstance(value, dict):
                    setattr(agent, field, json.dumps(value))
                else:
                    setattr(agent, field, value)
        
        db.commit()
        db.refresh(agent)
        
        logger.info(f"Agent更新成功: {name}")
        return agent
    
    def init_default_agents(self, db: Session = None):
        """初始化默认Agent配置"""
        if db is None:
            from ..database import SessionLocal
            db = SessionLocal()
            should_close = True
        else:
            should_close = False
        
        try:
            default_agents = [
                {
                    "name": "epidemiology_expert",
                    "display_name": "流行病学专家",
                    "description": "专门回答流行病学相关问题，包括研究设计、疾病监测、病因推断等",
                    "icon": "🦠",
                    "config": {
                        "specialty": "epidemiology",
                        "books": ["流行病学"],
                        "expertise_level": "expert"
                    }
                },
                {
                    "name": "physiology_expert", 
                    "display_name": "生理学专家",
                    "description": "专门回答生理学相关问题，包括器官功能、生理机制、调节过程等",
                    "icon": "❤️",
                    "config": {
                        "specialty": "physiology",
                        "books": ["生理学"],
                        "expertise_level": "expert"
                    }
                },
                {
                    "name": "pathology_expert",
                    "display_name": "病理学专家", 
                    "description": "专门回答病理学相关问题，包括疾病机制、病理变化、诊断要点等",
                    "icon": "🔬",
                    "config": {
                        "specialty": "pathology",
                        "books": ["病理学"],
                        "expertise_level": "expert"
                    }
                },
                {
                    "name": "general_medical",
                    "display_name": "综合医学助手",
                    "description": "综合回答各类医学问题，涵盖多个学科领域",
                    "icon": "🏥",
                    "config": {
                        "specialty": "general",
                        "books": ["流行病学", "生理学", "病理学"],
                        "expertise_level": "general"
                    }
                }
            ]
            
            for agent_data in default_agents:
                # 检查是否已存在
                existing = self.get_agent_by_name(db, agent_data["name"])
                if not existing:
                    self.create_agent(
                        db=db,
                        name=agent_data["name"],
                        display_name=agent_data["display_name"],
                        description=agent_data["description"],
                        icon=agent_data["icon"],
                        config=agent_data["config"]
                    )
                    logger.info(f"默认Agent创建成功: {agent_data['name']}")
                else:
                    logger.info(f"Agent已存在，跳过: {agent_data['name']}")
        
        finally:
            if should_close and db is not None:
                db.close()
    
    def get_agent_config(self, agent: AgentConfig) -> Dict[str, Any]:
        """获取Agent配置"""
        if agent.config:
            try:
                return json.loads(agent.config)
            except json.JSONDecodeError:
                logger.warning(f"Agent配置JSON解析失败: {agent.name}")
                return {}
        return {}
    
    def format_agent_for_api(self, agent: AgentConfig) -> Dict[str, Any]:
        """格式化Agent信息用于API返回"""
        return {
            "id": agent.id,
            "name": agent.name,
            "display_name": agent.display_name,
            "description": agent.description,
            "icon": agent.icon,
            "config": self.get_agent_config(agent),
            "created_at": agent.created_at.isoformat() if agent.created_at else None
        }
