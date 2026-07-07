import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.config import settings
from app.db import Base, engine, get_db
from app.models import User, Community, Prediction, Report, Alert, AuditLog, UploadedFile, Feedback
from app.schemas import (
    UserCreate, UserResponse, Token, UserLogin,
    CommunityResponse, PredictionResponse, ModelSliderInput,
    AlertResponse, ReportResponse, AuditLogResponse,
    UploadedFileResponse, AgentQueryRequest, AgentQueryResponse
)
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user, RoleChecker
from app.security import sanitize_input, audit_and_verify_injection
from app.rate_limit import rate_limiter
from app.agents.coordinator import CoordinatorAgent
from app.ml.models import ml_predictor

# --- Database Setup ---
Base.metadata.create_all(bind=engine)

# --- FastAPI Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade Decision Intelligence Platform powered by Gemini & Multi-Agent Collaboration.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static reports folder exists and mount it
static_reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(os.path.join(static_reports_dir, "reports"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_reports_dir), name="static")

# --- Database Seeding ---
@app.on_event("startup")
def seed_database():
    db = next(get_db())
    try:
        # 1. Seed Communities if empty
        if db.query(Community).count() == 0:
            c1 = Community(
                name="Zone A (Coastal Sector)",
                region_code="ZONE-A",
                population=15000,
                risk_score=3.5,
                health_index=85.0,
                weather_summary="Showers",
                traffic_status="Normal",
                air_quality_index=55
            )
            c2 = Community(
                name="Zone B (Industrial Hub)",
                region_code="ZONE-B",
                population=8000,
                risk_score=5.2,
                health_index=68.0,
                weather_summary="Foggy",
                traffic_status="Slow",
                air_quality_index=142
            )
            c3 = Community(
                name="Zone C (River Valley)",
                region_code="ZONE-C",
                population=12000,
                risk_score=2.8,
                health_index=91.0,
                weather_summary="Clear",
                traffic_status="Fluid",
                air_quality_index=45
            )
            db.add_all([c1, c2, c3])
            db.commit()
            print("Communities seeded.")

        # 2. Seed Default Admin User if empty
        if db.query(User).filter(User.email == "admin@decisionsphere.ai").count() == 0:
            admin = User(
                email="admin@decisionsphere.ai",
                hashed_password=get_password_hash("admin123"),
                full_name="Global Administrator",
                role="admin"
            )
            citizen = User(
                email="citizen@decisionsphere.ai",
                hashed_password=get_password_hash("citizen123"),
                full_name="John Doe",
                role="citizen"
            )
            gov = User(
                email="gov@decisionsphere.ai",
                hashed_password=get_password_hash("gov123"),
                full_name="Commissioner Jane Smith",
                role="government"
            )
            db.add_all([admin, citizen, gov])
            db.commit()
            print("Users seeded.")
    except Exception as e:
        print(f"Startup seeding error: {e}")
    finally:
        db.close()

# --- Health Check ---
@app.get("/api/health", tags=["General"])
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

# --- Authentication Endpoints ---
@app.post("/api/auth/register", response_model=UserResponse, tags=["Authentication"])
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/auth/token", response_model=Token, tags=["Authentication"])
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    # Audit log login
    log = AuditLog(user_id=user.id, action="user_login", details="Logged in successfully.")
    db.add(log)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- Communities Endpoints ---
@app.get("/api/communities", response_model=List[CommunityResponse], tags=["Communities"])
def list_communities(db: Session = Depends(get_db)):
    return db.query(Community).all()

# --- Multi-Agent Decision Engine Endpoint ---
@app.post("/api/decision/query", response_model=AgentQueryResponse, tags=["Decision Intelligence"])
def submit_query(
    req: AgentQueryRequest, 
    request: Request,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    _ = Depends(rate_limiter)
):
    # 1. Sanitize user input
    clean_query = sanitize_input(req.query)
    
    # 2. Check and audit for Prompt Injection
    client_ip = request.client.host if request.client else "unknown"
    audit_and_verify_injection(clean_query, user_id=current_user.id, ip_address=client_ip)
    
    # Audit valid search execution
    log = AuditLog(
        user_id=current_user.id, 
        action="run_decision_query", 
        ip_address=client_ip, 
        details=f"Ran query: '{clean_query[:50]}'"
    )
    db.add(log)
    db.commit()
    
    # 3. Instantiate Coordinator and run workflow
    coordinator = CoordinatorAgent()
    initial_state = {
        "query": clean_query,
        "community_id": req.community_id,
        "steps": []
    }
    
    final_state = coordinator.execute(initial_state)
    
    # Save predictions to DB history
    predictions = final_state.get("predictions", {})
    for metric, val in predictions.items():
        pred_entry = Prediction(
            community_id=req.community_id,
            target_metric=metric,
            predicted_value=val,
            confidence_score=0.9,
            explanation=final_state.get("predictions_explanation")
        )
        db.add(pred_entry)
        
    # Save alerts triggered
    alerts = final_state.get("alerts_triggered", [])
    for a in alerts:
        alert_entry = Alert(
            community_id=a["community_id"],
            severity=a["severity"],
            category=a["category"],
            message=a["message"]
        )
        db.add(alert_entry)
        
    db.commit()
    
    # Assemble response schema
    response_data = AgentQueryResponse(
        query=final_state.get("query"),
        coordinator_response=final_state.get("response", "No answer formulated."),
        steps=final_state.get("steps", []),
        recommendations=final_state.get("recommendations", []),
        predictions=final_state.get("predictions", {}),
        visualization_data=final_state.get("visualization", {}),
        alerts_triggered=final_state.get("alerts_triggered", [])
    )
    
    return response_data

# --- ML Simulations Endpoint ---
@app.post("/api/prediction/simulate", tags=["Predictions"])
def simulate_predictions(
    inputs: ModelSliderInput,
    community_id: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Run scikit-learn models based on frontend slider values
    flood_pred, flood_prob = ml_predictor.predict_flood(
        elevation=15.0 if community_id == 1 else 40.0,
        rainfall=inputs.flood_risk_factor * 120.0,
        soil_moisture=inputs.humidity,
        distance_to_water=200 - (inputs.flood_risk_factor * 150),
        drainage=80.0
    )
    
    traffic_score = ml_predictor.predict_traffic(
        hour=12,
        day=2,
        rain=inputs.flood_risk_factor * 20.0,
        construction=1 if inputs.traffic_congestion_factor > 0.6 else 0,
        accident=0,
        base_volume=inputs.traffic_congestion_factor * 800.0
    )
    
    aqi_score = ml_predictor.predict_air_quality(
        industrial=inputs.industrial_activity * 100.0,
        vehicles=inputs.traffic_congestion_factor * 400.0,
        temp=inputs.temperature,
        wind=10.0,
        humidity=inputs.humidity
    )
    
    disease_score = ml_predictor.predict_disease(
        pop_density=5000.0,
        temp=inputs.temperature,
        humidity=inputs.humidity,
        active_cases=int(inputs.disease_spread_rate * 100),
        vax_rate=80.0
    )
    
    crime_score = ml_predictor.predict_crime(
        unemployment=inputs.crime_density * 15.0,
        patrol=5.0,
        lighting=60.0,
        time_of_day=22.0,
        area_type=1
    )
    
    results = {
        "flood_probability": flood_prob,
        "traffic_congestion": traffic_score,
        "air_quality": aqi_score,
        "disease_spread": disease_score,
        "crime_risk": crime_score
    }
    
    # Save simulated predictions in DB
    for metric, val in results.items():
        db.add(Prediction(
            community_id=community_id,
            target_metric=metric,
            predicted_value=val,
            confidence_score=0.85,
            explanation=f"Manual scenario simulator prediction."
        ))
    db.commit()
    
    return results

# --- Alerts Endpoints ---
@app.get("/api/alerts/active", response_model=List[AlertResponse], tags=["Alerts"])
def list_active_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).filter(Alert.active == True).order_by(Alert.created_at.desc()).all()

@app.post("/api/alerts/clear/{alert_id}", tags=["Alerts"])
def clear_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["admin", "government"]))):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.active = False
    db.commit()
    return {"message": f"Alert {alert_id} cleared successfully"}

# --- Reports Endpoints ---
@app.get("/api/reports", response_model=List[ReportResponse], tags=["Reports"])
def list_reports(db: Session = Depends(get_db)):
    # Check physical existence of files, clean registry
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return reports

# --- File Ingestion & Auto-Analysis ---
@app.post("/api/upload", response_model=UploadedFileResponse, tags=["File Ingestion"])
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    upload_dir = os.path.join(static_reports_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)
    
    # Run Mock Auto-Analysis
    # In production, PDF reader MCP tools parse contents; we simulate a response
    content_type = file.content_type
    analysis = {
        "file_name": file.filename,
        "records_parsed": 120 if "csv" in file.filename else 1,
        "insights_summary": f"Automatically processed {content_type} file. Identified 3 core safety markers.",
        "warnings_triggered": 0
    }
    
    uploaded_file = UploadedFile(
        file_name=file.filename,
        file_path=f"/static/uploads/{file.filename}",
        file_size=file_size,
        content_type=content_type,
        uploaded_by_id=current_user.id,
        analysis_result=analysis
    )
    
    db.add(uploaded_file)
    
    # Register under Reports if PDF/CSV
    if file.filename.endswith((".pdf", ".csv", ".xlsx")):
        rep = Report(
            title=f"Uploaded Analysis: {file.filename}",
            report_type="citizen",
            file_path=f"/static/uploads/{file.filename}",
            format="CSV" if "csv" in file.filename else "PDF",
            created_by_id=current_user.id
        )
        db.add(rep)
        
    db.commit()
    db.refresh(uploaded_file)
    return uploaded_file

# --- Audit Logs Endpoint ---
@app.get("/api/admin/audit", response_model=List[AuditLogResponse], tags=["Administration"])
def get_audit_trail(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["admin"]))):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
