import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="citizen")  # admin, government, ngo, citizen
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    reports = relationship("Report", back_populates="creator")
    feedbacks = relationship("Feedback", back_populates="user")
    uploaded_files = relationship("UploadedFile", back_populates="uploader")
    audit_logs = relationship("AuditLog", back_populates="user")


class Community(Base):
    __tablename__ = "communities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    region_code = Column(String, nullable=False)
    population = Column(Integer, default=1000)
    risk_score = Column(Float, default=0.0)      # 0.0 to 10.0
    health_index = Column(Float, default=100.0)   # 0.0 to 100.0
    weather_summary = Column(String, default="Clear")
    traffic_status = Column(String, default="Normal")
    air_quality_index = Column(Integer, default=50)
    water_consumption = Column(Float, default=0.0)
    energy_consumption = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    predictions = relationship("Prediction", back_populates="community")
    alerts = relationship("Alert", back_populates="community")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)
    target_metric = Column(String, nullable=False)  # flood, traffic, air_quality, disease, crime, water, energy
    input_features = Column(JSON, nullable=True)
    predicted_value = Column(Float, nullable=False)
    confidence_score = Column(Float, default=0.9)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    community = relationship("Community", back_populates="predictions")
    feedbacks = relationship("Feedback", back_populates="prediction")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False)    # executive, citizen, government, disaster
    file_path = Column(String, nullable=False)
    format = Column(String, default="PDF")          # PDF, CSV
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="reports")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)
    severity = Column(String, default="info")       # info, warning, danger
    category = Column(String, default="general")     # weather, traffic, health, crime, water, energy, disaster
    message = Column(Text, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    community = relationship("Community", back_populates="alerts")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)        # 1 to 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    prediction = relationship("Prediction", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)          # user_login, run_prediction, trigger_alert, download_report, prompt_injection
    ip_address = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    analysis_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    uploader = relationship("User", back_populates="uploaded_files")
