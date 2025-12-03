from pydantic import BaseModel
from typing import Optional

class PatientBase(BaseModel):
    Age: int
    Gender: str
    Smoking_History: str
    BMI: float
    FEV1: float
    FVC: float
    PEF: float
    Oxygen_Saturation: float
    Respiratory_Rate: int
    Heart_Rate: int
    Wheezing: int           # 0 = No, 1 = Yes
    Cough: int
    Shortness_of_Breath: int
    Chest_Tightness: int
    Allergen_Exposure: int
    Air_Pollution_Level: float
    Family_History_Asthma: int
    FEV1_FVC_Ratio: float
    Hospital_Visits: int

class PatientCreateInput(BaseModel):
    Age: int
    Gender: str
    Smoking_History: str
    BMI: float
    FEV1: float
    FVC: float
    PEF: float
    Oxygen_Saturation: float
    Respiratory_Rate: int
    Heart_Rate: int
    Wheezing: int
    Cough: int
    Shortness_of_Breath: int
    Chest_Tightness: int
    Allergen_Exposure: int
    Air_Pollution_Level: float
    Family_History_Asthma: int
    FEV1_FVC_Ratio: float
    Hospital_Visits: int

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    class Config:
        from_attributes = True

class PredictionRequest(PatientBase):
    pass

class PredictionResponse(BaseModel):
    prediction: int
    confidence: float
    prediction_text: str
    risk_level: str
    error: Optional[str] = None


# -------------------------------
# Heart Disease Prediction Models
# -------------------------------

class HeartPatientBase(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int
    target: Optional[int] = 0


class HeartPatientCreate(HeartPatientBase):
    pass


class HeartPatient(HeartPatientBase):
    id: int
    class Config:
        from_attributes = True


class HeartPredictionRequest(HeartPatientBase):
    pass


class HeartPredictionResponse(BaseModel):
    prediction: int
    confidence: float
    prediction_text: str
    risk_level: str
    error: Optional[str] = None
    