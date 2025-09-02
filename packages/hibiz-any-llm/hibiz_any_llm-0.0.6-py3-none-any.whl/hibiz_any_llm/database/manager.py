from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from .models import Base, TokenUsageLog
from ..core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced PostgreSQL Database Manager using SQLAlchemy"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.engine = None
        self.Session = None
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize PostgreSQL database connection"""
        try:
            # Build PostgreSQL connection string with connection pooling
            connection_string = (
                f"postgresql://{self.db_config['user']}:"
                f"{self.db_config['password']}@{self.db_config['host']}:"
                f"{self.db_config['port']}/{self.db_config['dbname']}"
            )
            
            self.engine = create_engine(
                connection_string, 
                echo=self.db_config.get('echo', False),
                pool_size=self.db_config.get('pool_size', 10),
                max_overflow=self.db_config.get('max_overflow', 20),
                pool_pre_ping=True
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Connected to PostgreSQL database")
            
        except Exception as e:
            raise DatabaseError(f"Failed to connect to PostgreSQL database: {e}")
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_tables(self) -> None:
        """Create necessary tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("PostgreSQL tables created successfully")
        except Exception as e:
            raise DatabaseError(f"Failed to create PostgreSQL tables: {e}")
    
    def log_token_usage(self, log_data: Dict[str, Any]) -> None:
        """Log token usage to PostgreSQL database"""
        try:
            with self.get_session() as session:
                log_entry = TokenUsageLog(**log_data)
                session.add(log_entry)
                logger.debug(f"Token usage logged for customer {log_data.get('customer_id')}")
        except Exception as e:
            raise DatabaseError(f"Failed to log token usage: {e}")
    
    def get_usage_stats(
        self,
        customer_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        provider: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        try:
            with self.get_session() as session:
                query = session.query(TokenUsageLog)
                
                # Apply filters
                if customer_id:
                    query = query.filter(TokenUsageLog.customer_id == customer_id)
                if organization_id:
                    query = query.filter(TokenUsageLog.organization_id == organization_id)
                if provider:
                    query = query.filter(TokenUsageLog.provider == provider)
                if start_date:
                    query = query.filter(TokenUsageLog.request_timestamp >= start_date)
                if end_date:
                    query = query.filter(TokenUsageLog.request_timestamp <= end_date)
                
                if filters:
                    for key, value in filters.items():
                        if hasattr(TokenUsageLog, key):
                            query = query.filter(getattr(TokenUsageLog, key) == value)
                
                logs = query.all()
                
                # Generate comprehensive statistics
                return self._generate_statistics(logs)
                
        except Exception as e:
            raise DatabaseError(f"Failed to get usage stats: {e}")
    
    def _generate_statistics(self, logs: List[TokenUsageLog]) -> Dict[str, Any]:
        """Generate comprehensive statistics from logs"""
        stats = {
            "summary": {
                "total_requests": len(logs),
                "total_tokens": sum(log.total_tokens for log in logs),
                "total_input_tokens": sum(log.input_tokens for log in logs),
                "total_output_tokens": sum(log.output_tokens for log in logs),
                "avg_response_time_ms": sum(log.response_time_ms for log in logs) / len(logs) if logs else 0,
                "success_rate": len([log for log in logs if log.status == 'success']) / len(logs) if logs else 0
            },
            "by_provider": {},
            "by_model": {},
            "by_app": {},
            "by_request_type": {}
        }
        
        # Group by different dimensions
        for log in logs:
            # By provider
            if log.provider not in stats["by_provider"]:
                stats["by_provider"][log.provider] = {"requests": 0, "tokens": 0}
            stats["by_provider"][log.provider]["requests"] += 1
            stats["by_provider"][log.provider]["tokens"] += log.total_tokens
            
            # By model
            if log.model_name not in stats["by_model"]:
                stats["by_model"][log.model_name] = {"requests": 0, "tokens": 0}
            stats["by_model"][log.model_name]["requests"] += 1
            stats["by_model"][log.model_name]["tokens"] += log.total_tokens
            
            # By app
            if log.app_name and log.app_name not in stats["by_app"]:
                stats["by_app"][log.app_name] = {"requests": 0, "tokens": 0}
            if log.app_name:
                stats["by_app"][log.app_name]["requests"] += 1
                stats["by_app"][log.app_name]["tokens"] += log.total_tokens
            
            # By request type
            if log.request_type not in stats["by_request_type"]:
                stats["by_request_type"][log.request_type] = {"requests": 0, "tokens": 0}
            stats["by_request_type"][log.request_type]["requests"] += 1
            stats["by_request_type"][log.request_type]["tokens"] += log.total_tokens
        
        return stats
    
    def close(self) -> None:
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL database connection closed")