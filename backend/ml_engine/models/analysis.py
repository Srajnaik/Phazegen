from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class HGTAnalysis(Base):
    __tablename__ = "hgt_analyses"
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(String, unique=True, index=True)
    filename = Column(String)
    risk_score = Column(Integer)
    risk_level = Column(String)
    detected_elements = Column(JSON)  # Store as JSONB in PostgreSQL
    recommendations = Column(JSON)
    raw_results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "filename": self.filename,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "detected_elements": self.detected_elements,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }

# Install SQLAlchemy
pip install sqlalchemy