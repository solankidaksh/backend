from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Database + models
import models
import schemas
import database

# Prediction services
from prediction_service import prediction_service as asthma_service
from heart_prediction_service import heart_prediction_service

# --- NEW: OpenAI AI Coach ---
from pydantic import BaseModel
from openai import OpenAI

# -------------------------------
# FASTAPI INITIALIZATION
# -------------------------------
app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

# DB dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------
# ROOT
# -------------------------------
@app.get("/")
def read_root():
    return {"message": "API for Asthma, Heart Disease & AI Health Coach is running!"}


# ============================================================
#    ASTHMA ROUTES
# ============================================================

@app.post("/patients/", response_model=schemas.Patient)
def create_asthma_patient(patient: schemas.PatientCreateInput, db: Session = Depends(get_db)):
    result = asthma_service.predict(patient.dict())
    if result.get("error"):
        raise HTTPException(status_code=500, detail=f"Asthma prediction failed: {result['error']}")

    data = patient.dict()
    data["Asthma_Diagnosis"] = result["prediction"]

    db_patient = models.Patient(**data)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.get("/patients/", response_model=List[schemas.Patient])
def read_asthma_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Patient).offset(skip).limit(limit).all()


@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_asthma_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Asthma patient not found")
    return patient


@app.put("/patients/{patient_id}", response_model=schemas.Patient)
def update_asthma_patient(patient_id: int, patient: schemas.PatientCreateInput, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Asthma patient not found")

    result = asthma_service.predict(patient.dict())
    if result.get("error"):
        raise HTTPException(status_code=500, detail="Asthma prediction failed")

    data = patient.dict()
    data["Asthma_Diagnosis"] = result["prediction"]

    for key, value in data.items():
        setattr(db_patient, key, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.delete("/patients/{patient_id}")
def delete_asthma_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Asthma patient not found")
    db.delete(patient)
    db.commit()
    return {"message": f"Asthma patient {patient_id} deleted successfully"}


@app.delete("/patients/")
def delete_all_asthma_patients(db: Session = Depends(get_db)):
    count = db.query(models.Patient).count()
    db.query(models.Patient).delete()
    db.commit()
    return {"message": f"Deleted {count} asthma patients successfully"}


@app.post("/predict_asthma/", response_model=schemas.PredictionResponse)
def predict_asthma(patient: schemas.PredictionRequest):
    result = asthma_service.predict(patient.dict())
    if result.get("error"):
        raise HTTPException(status_code=500, detail="Asthma prediction failed")
    return schemas.PredictionResponse(**result)


# ============================================================
#    HEART DISEASE ROUTES
# ============================================================

@app.post("/heart_patients/", response_model=schemas.HeartPatient)
def create_heart_patient(patient: schemas.HeartPatientCreate, db: Session = Depends(get_db)):
    result = heart_prediction_service.predict(patient.dict())
    if result.get("error"):
        raise HTTPException(status_code=500, detail="Heart disease prediction failed")

    data = patient.dict()
    data["Heart_Disease_Diagnosis"] = result["prediction"]

    db_patient = models.HeartPatient(**data)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.get("/heart_patients/", response_model=List[schemas.HeartPatient])
def read_heart_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.HeartPatient).offset(skip).limit(limit).all()


@app.get("/heart_patients/{patient_id}", response_model=schemas.HeartPatient)
def read_heart_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.HeartPatient).filter(models.HeartPatient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Heart patient not found")
    return patient


@app.put("/heart_patients/{patient_id}", response_model=schemas.HeartPatient)
def update_heart_patient(patient_id: int, patient: schemas.HeartPatientCreate, db: Session = Depends(get_db)):
    db_patient = db.query(models.HeartPatient).filter(models.HeartPatient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Heart patient not found")

    result = heart_prediction_service.predict(patient.dict())
    if result.get("error"):
        raise HTTPException(status_code=500, detail="Heart prediction failed")

    data = patient.dict()
    data["Heart_Disease_Diagnosis"] = result["prediction"]

    for key, value in data.items():
        setattr(db_patient, key, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.delete("/heart_patients/{patient_id}")
def delete_heart_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.HeartPatient).filter(models.HeartPatient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Heart patient not found")
    db.delete(patient)
    db.commit()
    return {"message": f"Heart patient {patient_id} deleted successfully"}


@app.post("/predict_heart/", response_model=schemas.HeartPredictionResponse)
def predict_heart(patient: schemas.HeartPredictionRequest):
    result = heart_prediction_service.predict(patient.dict())
    if result.get("error"):
        raise HTTPException(status_code=500, detail="Heart prediction failed")
    return schemas.HeartPredictionResponse(**result)

# ============================================================
#          NEW AI HEALTH COACH (Gemini — Short Answers)
# ============================================================

from pydantic import BaseModel
import google.generativeai as genai

class CoachRequest(BaseModel):
    message: str

# Configure Gemini (your API key)
genai.configure(api_key="AIzaSyBVE2_ymq3Q96t23VrpMWshbdYVLfmm2Pk")

# Select model
model = genai.GenerativeModel("models/gemini-2.0-flash")

@app.post("/coach")
async def ai_coach(req: CoachRequest):
    """
    Ultra-concise AI health coach.
    Gives short, clear, useful advice.
    Safe for general lifestyle guidance.
    """

    try:
        response = model.generate_content(
            f"""
You are a SHORT, PRECISE AI Health Coach.

RESPONSE RULES:
- Maximum 2–3 bullet points.
- Each bullet point must be 3–8 words.
- No long sentences.
- No paragraphs.
- No emojis.
- No diagnosis.
- No medical instructions.

User message:
{req.message}
"""
        )

        return {"reply": response.text.strip()}

    except Exception as e:
        return {"error": str(e)}
