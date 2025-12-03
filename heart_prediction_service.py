# heart_prediction_service.py
import joblib
import pandas as pd
from pathlib import Path
from typing import Dict, Any

class HeartPredictionService:
    def __init__(self, model_path: str = "heart_prediction_rf[1].pkl"): # <-- Load your 85% model
        self.model_path = Path(model_path)
        self.model = None
        self.load_model()

    def load_model(self):
        """Load the trained heart disease model"""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                print(f"✅ Heart disease model loaded successfully from {self.model_path}")
            else:
                print(f"⚠️ Model file not found at {self.model_path}")
        except Exception as e:
            print(f"❌ Error loading heart model: {e}")

    # --- NO MANUAL PREPROCESSING IS NEEDED ---
    # Your model file 'heart_prediction_rf[1].pkl' already has
    # the ColumnTransformer, StandardScaler, and OneHotEncoder
    # built into it.

    def predict(self, patient_data: Dict[str, Any]):
        """Make prediction"""
        if self.model is None:
            return {"error": "Model not loaded", "prediction": None, "confidence": 0.0}
        
        try:
            # Convert input dict → DataFrame
            df = pd.DataFrame(patient_data, index=[0])
            
            # Model prediction
            prediction = self.model.predict(df)[0]
            
            confidence = (
                float(max(self.model.predict_proba(df)[0]))
                if hasattr(self.model, "predict_proba")
                else 0.0
            )

            # -----------------------------
            # NEW: Heart Disease Risk Mapping
            # -----------------------------
            if prediction == 0:
                # No heart disease predicted
                if confidence < 0.40:
                    risk = "Normal"
                elif confidence < 0.70:
                    risk = "Elevated"
                else:
                    risk = "Elevated"
            else:
                # Heart disease predicted
                if confidence < 0.40:
                    risk = "Elevated"
                elif confidence < 0.70:
                    risk = "High"
                else:
                    risk = "Critical"

            return {
                "prediction": int(prediction),
                "confidence": confidence,
                "prediction_text": "Heart Disease" if prediction == 1 else "No Heart Disease",
                "risk_level": risk,     # <-- NEW FIELD
                "error": None
            }

        except Exception as e:
            return {"error": str(e), "prediction": None, "confidence": 0.0}

# Create a single instance for your app to import
heart_prediction_service = HeartPredictionService()