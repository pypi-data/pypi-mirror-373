from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TokenUsageLog(Base):
    __tablename__ = 'any_llm_token_usage_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(255), nullable=False, index=True)
    organization_id = Column(String(255), nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)
    model_name = Column(String(255), nullable=False, index=True)
    app_name = Column(String(255), nullable=True, index=True)
    module_name = Column(String(255), nullable=True)
    function_name = Column(String(255), nullable=True)
    request_type = Column(String(50), nullable=False, index=True)
    request_params = Column(JSON)
    response_params = Column(JSON)
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    request_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    response_time_ms = Column(Integer, nullable=False, default=0)
    status = Column(String(50), default='success', index=True)
    request_id = Column(String(255), nullable=True)
    cost_info = Column (JSON, nullable=True)
    
    # Add composite indexes for common queries
    __table_args__ = (
        Index('idx_customer_date', 'customer_id', 'request_timestamp'),
        Index('idx_org_model', 'organization_id', 'model_name'),
        Index('idx_app_module', 'app_name', 'module_name'),
    )