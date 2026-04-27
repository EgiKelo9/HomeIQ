import joblib
import numpy as np
import pandas as pd
from pathlib import Path

class HousePricePredictor:
    """
    Kelas untuk memuat artefak model dan melakukan prediksi harga rumah 
    berdasarkan fitur yang diberikan.
    """
    def __init__(self, models_dir: str = 'models'):
        if models_dir == 'models':
            self.models_dir = Path(__file__).resolve().parents[2] / 'models'
        else:
            self.models_dir = Path(models_dir).resolve()
        self._load_artifacts()

    def _load_artifacts(self):
        """Memuat seluruh pre-trained model, scaler, encoder, dan metadata."""
        self.model = joblib.load(self.models_dir / 'best_rf_model.joblib')
        self.X_scaler = joblib.load(self.models_dir / 'X_scaler.joblib')
        self.y_scaler = joblib.load(self.models_dir / 'y_scaler.joblib')
        self.city_encoder = joblib.load(self.models_dir / 'city_encoder.joblib')
        self.district_encoder = joblib.load(self.models_dir / 'district_encoder.joblib')
        self.metadata = joblib.load(self.models_dir / 'model_metadata.joblib')
        
        # Mengekstrak nama urutan fitur asli selama training
        self.feature_names = self.metadata.get('feature_names', None)

    def predict(self, 
                bedrooms: float, 
                bathrooms: float, 
                building_size_m2: float, 
                land_size_m2: float, 
                city: str, 
                district: str) -> float:
        """
        Memprediksi harga rumah menggunakan model Random Forest Regressor yang sudah dilatih.
        """
        # Melakukan encoding ke tipe numerik
        city_encoded = self.city_encoder.transform([city])[0]
        district_encoded = self.district_encoder.transform([district])[0]
        
        # Mempersiapkan fitur input sebagai dictionary
        # Pastikan key yang ditulis sesuai dengan nama kolom pada Pandas di pipeline pembersihan awal.
        input_dict = {
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'building_size_m2': building_size_m2,
            'land_size_m2': land_size_m2,
            'city_encoded': city_encoded,
            'district_encoded': district_encoded
        }
        
        # Mengkonversi ke DataFrame untuk menjamin urutan fitur (column order)
        # sesuai dengan yang dibutuhkan oleh model pelatihan.
        if self.feature_names:
            input_df = pd.DataFrame([input_dict], columns=self.feature_names)
        else:
            input_df = pd.DataFrame([input_dict])
            
        # Transformasi fitur input menggunakan scaler fitur
        input_scaled = self.X_scaler.transform(input_df)
        
        # Menghitung prediksi pada rasio ter-scaling (normalized)
        prediction_scaled = self.model.predict(input_scaled)
        
        # Mengembalikan target ke sekala harga aktual (inverse transform)
        predicted_price = self.y_scaler.inverse_transform(prediction_scaled.reshape(-1, 1))[0][0]
        
        return float(predicted_price)
