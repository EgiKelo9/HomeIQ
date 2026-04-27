import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, root_mean_squared_error, r2_score
from app.ml_pipeline.cleaner import DataCleaner

class ModelTrainer:
    def __init__(self, models_dir: str = 'models'):
        if models_dir == 'models':
            self.models_dir = Path(__file__).resolve().parents[2] / 'models'
        else:
            self.models_dir = Path(models_dir).resolve()
        
        # Encoders & Scalers
        self.furnishing_encoder = None
        self.city_encoder = LabelEncoder()
        self.district_encoder = LabelEncoder()
        self.certificate_encoder = LabelEncoder()
        self.X_scaler = RobustScaler()
        self.y_scaler = RobustScaler()

        # Best Model & Params
        self.best_model = None
        self.metadata = {}
        
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        encoded_df = df.copy()
        
        if 'furnishing' in encoded_df.columns:
            furnishing_ordinal = encoded_df['furnishing'].unique()
            self.furnishing_encoder = OrdinalEncoder(categories=[furnishing_ordinal], dtype=int)
            encoded_df['furnishing_encoded'] = self.furnishing_encoder.fit_transform(encoded_df[['furnishing']])
            
        if 'city' in encoded_df.columns:
            encoded_df['city_encoded'] = self.city_encoder.fit_transform(encoded_df[['city']])
            
        if 'district' in encoded_df.columns:
            encoded_df['district_encoded'] = self.district_encoder.fit_transform(encoded_df[['district']])
            
        if 'certificate' in encoded_df.columns:
            encoded_df['certificate_encoded'] = self.certificate_encoder.fit_transform(encoded_df[['certificate']])
            
        # Drop original categorical columns
        cols_to_drop = ['city', 'district', 'certificate', 'furnishing']
        existing_cols_to_drop = [col for col in cols_to_drop if col in encoded_df.columns]
        encoded_df = encoded_df.drop(columns=existing_cols_to_drop)
            
        return encoded_df

    def train(self, df: pd.DataFrame):
        # 1. Cleaning
        print("Cleaning data...")
        cleaner = DataCleaner()
        df_cleaned = cleaner.run_cleaning_pipeline(df, is_training=True)
        
        # 2. Encoding
        print("Encoding categorical variables...")
        df_encoded = self.encode_categorical(df_cleaned)

        # 3. Splitting
        drop_cols = ['price_in_rp']
        if 'furnishing_encoded' in df_encoded.columns:
            drop_cols.append('furnishing_encoded')
        if 'certificate_encoded' in df_encoded.columns:
            drop_cols.append('certificate_encoded')
            
        features = df_encoded.drop(drop_cols, axis=1)
        prices = df_encoded['price_in_rp']
        
        X_train, X_test, y_train, y_test = train_test_split(
            features, 
            prices, 
            test_size=0.2, 
            random_state=42, 
            stratify=df_encoded['city_encoded'] if 'city_encoded' in df_encoded.columns else None
        )
        
        # 4. Scaling
        print("Scaling features and target...")
        X_train_scaled = self.X_scaler.fit_transform(X_train)
        X_test_scaled = self.X_scaler.transform(X_test)
        
        y_train_scaled = self.y_scaler.fit_transform(y_train.values.reshape(-1, 1)).flatten()
        y_test_scaled = self.y_scaler.transform(y_test.values.reshape(-1, 1)).flatten()

        # 5. Model Configuration
        print("Using predefined Best Parameters for Random Forest Regression...")
        
        # Atur langsung parameter terbaik yang didapatkan dari proses trial di notebook
        best_params = {
            'n_estimators': 300,
            'max_depth': 30,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'max_features': 'sqrt'
        }

        print(f"\nModel parameters: {best_params}")
        
        # 6. Train model
        print("Training Random Forest model...")
        self.best_model = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
        self.best_model.fit(X_train_scaled, y_train_scaled)
        
        # 7. Evaluate
        y_pred_train = self.best_model.predict(X_train_scaled)
        y_pred_test = self.best_model.predict(X_test_scaled)
        
        train_mae = mean_absolute_error(y_train_scaled, y_pred_train)
        test_mae = mean_absolute_error(y_test_scaled, y_pred_test)
        
        self.metadata = {
            'model_type': 'RandomForestRegressor',
            'best_parameters': best_params,
            'best_cv_score': None,
            'test_metrics': {
                'mae': test_mae,
                'rmse': root_mean_squared_error(y_test_scaled, y_pred_test),
                'r2': r2_score(y_test_scaled, y_pred_test),
                'mape': mean_absolute_percentage_error(y_test_scaled, y_pred_test)
            },
            'train_metrics': {
                'mae': train_mae,
                'rmse': root_mean_squared_error(y_train_scaled, y_pred_train),
                'r2': r2_score(y_train_scaled, y_pred_train),
                'mape': mean_absolute_percentage_error(y_train_scaled, y_pred_train)
            },
            'feature_names': list(X_train.columns),
            'feature_importance': dict(zip(X_train.columns, self.best_model.feature_importances_))
        }

        print("\nModel Evaluation:")
        print(f"Test R²: {self.metadata['test_metrics']['r2']:.4f}")
        print(f"Test MAE: {self.metadata['test_metrics']['mae']:.4f}")

    def export_artifacts(self):
        print(f"\nExporting artifacts to {self.models_dir}...")
        os.makedirs(self.models_dir, exist_ok=True)
        
        joblib.dump(self.best_model, self.models_dir / 'best_rf_model.joblib')
        joblib.dump(self.X_scaler, self.models_dir / 'X_scaler.joblib')
        joblib.dump(self.y_scaler, self.models_dir / 'y_scaler.joblib')
        joblib.dump(self.city_encoder, self.models_dir / 'city_encoder.joblib')
        joblib.dump(self.district_encoder, self.models_dir / 'district_encoder.joblib')
        joblib.dump(self.metadata, self.models_dir / 'model_metadata.joblib')
        print("Export complete ✅")