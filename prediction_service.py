import numpy as np
from pathlib import Path
from typing import Dict, Any
import joblib
from sklearn.preprocessing import LabelEncoder

class PredictionService:
    def __init__(self, model_path: str = f"asthma_prediction_rf[1].pkl"):
        self.model = None
        self.model_path = Path(model_path)
        self.label_encoders = {}
        self.feature_count = 19  # total features expected by the trained model
        self.load_model()
     
    def load_model(self):
        """Load the trained model using joblib"""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                print(f"Model loaded successfully from {self.model_path}")
            else:
                print(f"Model file not found at {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def preprocess_data(self, patient_data: Dict[str, Any]) -> np.ndarray:
        """Preprocess patient data for prediction"""
        # Categorical fields
        categorical_mappings = {
            'Gender': ['Male', 'Female', 'Other'],
            'Smoking_History': ['Never', 'Former', 'Current']
        }
        
        # Initialize label encoders if not already
        for col, values in categorical_mappings.items():
            if col not in self.label_encoders:
                le = LabelEncoder()
                le.fit(values)
                self.label_encoders[col] = le
        
        features = []

        # 1️⃣ Numeric fields in model order
        numeric_fields = ['Age', 'BMI', 'FEV1', 'FVC', 'PEF', 'Oxygen_Saturation', 'Hospital_Visits']
        for field in numeric_fields:
            features.append(patient_data.get(field, 0))

        # 2️⃣ Binary fields (frontend sends 0/1)
        binary_fields = ['Wheezing', 'Cough', 'Shortness_of_Breath', 'Chest_Tightness', 'Allergen_Exposure', 'Family_History_Asthma']
        for field in binary_fields:
            features.append(patient_data.get(field, 0))

        # 3️⃣ Remaining numeric fields
        remaining_numeric = ['Respiratory_Rate', 'Heart_Rate', 'FEV1_FVC_Ratio', 'Air_Pollution_Level']
        for field in remaining_numeric:
            features.append(patient_data.get(field, 0))

        # 4️⃣ Categorical fields
        gender = patient_data.get('Gender', 'Male')
        features.append(self.label_encoders['Gender'].transform([gender])[0] 
                        if gender in self.label_encoders['Gender'].classes_ else 0)
        smoking = patient_data.get('Smoking_History', 'Never')
        features.append(self.label_encoders['Smoking_History'].transform([smoking])[0] 
                        if smoking in self.label_encoders['Smoking_History'].classes_ else 0)

        # ✅ Ensure feature count matches the model
        if len(features) != self.feature_count:
            raise ValueError(f"Feature mismatch: {len(features)} features, expected {self.feature_count}")

        return np.array(features).reshape(1, -1)
    
    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction for a patient"""
        if self.model is None:
            return {"error": "Model not loaded", "prediction": None, "confidence": 0.0}
        
        try:
            X = self.preprocess_data(patient_data)
            
            # Ensure model is valid
            if not hasattr(self.model, 'predict'):
                return {"error": "Loaded object is not a valid model", "prediction": None, "confidence": 0.0}
            
            prediction = self.model.predict(X)[0]
            confidence = float(max(self.model.predict_proba(X)[0])) if hasattr(self.model, 'predict_proba') else 0.0
            
            return {
                "prediction": int(prediction),
                "confidence": confidence,
                "prediction_text": "Asthma" if prediction == 1 else "No Asthma"
            }
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}", "prediction": None, "confidence": 0.0}


# Global instance
prediction_service = PredictionService()
