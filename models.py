from sqlalchemy import Column, Integer, String, Float, ForeignKey
import database
Base = database.Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False) 

 
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    Age = Column(Integer)
    Gender = Column(String)
    Smoking_History = Column(String)
    BMI = Column(Float)
    FEV1 = Column(Float)
    FVC = Column(Float)
    PEF = Column(Float)
    Oxygen_Saturation = Column(Float)
    Respiratory_Rate = Column(Integer)
    Heart_Rate = Column(Integer)
    Wheezing = Column(Integer)
    Cough = Column(Integer)
    Shortness_of_Breath = Column(Integer)
    Chest_Tightness = Column(Integer)
    Allergen_Exposure = Column(Integer)
    Air_Pollution_Level = Column(Float)
    Family_History_Asthma = Column(Integer)
    FEV1_FVC_Ratio = Column(Float)
    Hospital_Visits = Column(Integer)

    Asthma_Diagnosis = Column(Integer)  # 0 or 1


class HeartPatient(Base):
    __tablename__ = "heart_patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # These are the 13 input features
    age = Column(Integer)
    sex = Column(Integer)
    cp = Column(Integer)
    trestbps = Column(Integer)
    chol = Column(Integer)
    fbs = Column(Integer)
    restecg = Column(Integer)
    thalach = Column(Integer)
    exang = Column(Integer)
    oldpeak = Column(Float)
    slope = Column(Integer)
    ca = Column(Integer)
    thal = Column(Integer)
    
    # This is your prediction column, based on main.py
    Heart_Disease_Diagnosis = Column(Integer) # 0 = No, 1 = Yes