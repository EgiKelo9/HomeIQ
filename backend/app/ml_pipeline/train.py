import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, root_mean_squared_error, r2_score, silhouette_score
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
        
class ClusterTrainer:
    """
    Class untuk melakukan segmentasi pasar secara dinamis menggunakan K-Means.
    Jumlah cluster (K) ditentukan otomatis berdasarkan Silhouette Score terbaik.
    """
    def __init__(self, models_dir: str = 'models'):
        if models_dir == 'models':
            self.models_dir = Path(__file__).resolve().parents[2] / 'models'
        else:
            self.models_dir = Path(models_dir).resolve()
            
        self.scaler = RobustScaler()
        self.city_encoder = LabelEncoder()
        self.district_encoder = LabelEncoder()
        self.best_model = None
        self.metadata = {}

    def train(self, df: pd.DataFrame, max_clusters: int = 6):
        print("\nMemulai proses K-Means Clustering untuk Segmentasi Pasar...")
        
        # 1. Cleaning khusus untuk kebutuhan clustering
        cleaner = DataCleaner()
        df_cleaned = cleaner.run_cleaning_pipeline(df, is_training=True)
        
        features_raw = ['price_in_rp', 'building_size_m2', 'land_size_m2', 'bedrooms', 'bathrooms', 'city', 'district']
        
        # Drop data yang tidak lengkap untuk fitur clustering
        df_cluster = df_cleaned.dropna(subset=features_raw).copy()
        
        if len(df_cluster) < max_clusters:
            print("Data terlalu sedikit untuk clustering.")
            return

        # 2. Encoding fitur kategorikal (City & District)
        df_cluster['city_encoded'] = self.city_encoder.fit_transform(df_cluster['city'])
        df_cluster['district_encoded'] = self.district_encoder.fit_transform(df_cluster['district'])
        
        features_numeric = ['price_in_rp', 'building_size_m2', 'land_size_m2', 'bedrooms', 'bathrooms', 'city_encoded', 'district_encoded']
        X = df_cluster[features_numeric]

        # 3. Scaling (Sangat penting karena K-Means berbasis jarak euclidean)
        X_scaled = self.scaler.fit_transform(X)

        # 4. Mencari jumlah cluster (K) paling optimal menggunakan Silhouette Score
        best_k = 3
        best_score = -1
        
        print(f"Mencari nilai K paling optimal (3 hingga {max_clusters})...")
        for k in range(3, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            print(f" - K={k} | Silhouette Score: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_k = k
                self.best_model = kmeans

        print(f"✅ Cluster optimal ditemukan pada K={best_k} (Skor: {best_score:.4f})")
        
        # 5. Menganalisis profil setiap cluster untuk generate metadata
        df_cluster['cluster'] = self.best_model.labels_
        cluster_profiles = []
        
        # Sorting cluster berdasarkan rata-rata harga agar lebih mudah dilabeli
        cluster_centers = df_cluster.groupby('cluster')['price_in_rp'].mean().sort_values()
        
        # Palet warna dinamis
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6"]
        
        for idx, (original_cluster_id, avg_price) in enumerate(cluster_centers.items()):
            c_data = df_cluster[df_cluster['cluster'] == original_cluster_id]
            
            # Kita buat label dinamis: Cluster 1 (Termurah) -> Cluster N (Termahal)
            label = f"Segmen {idx + 1}"
            if idx == 0: label = "Entry Level"
            elif idx == best_k - 1: label = "Premium"
            elif best_k == 3 and idx == 1: label = "Mid Range"
            
            desc = f"Harga rata-rata Rp {(avg_price/1_000_000_000):.2f} M. Rata-rata LB {c_data['building_size_m2'].mean():.0f}m², LT {c_data['land_size_m2'].mean():.0f}m² dengan {c_data['bedrooms'].mean():.0f} KT dan {c_data['bathrooms'].mean():.0f} KM."
            
            cluster_profiles.append({
                "cluster_name": label,
                "count": int(len(c_data)),
                "description": desc,
                "color": colors[idx % len(colors)]
            })
            
        self.metadata = {
            "optimal_k": best_k,
            "silhouette_score": float(best_score),
            "features_used": features_numeric,
            "profiles": cluster_profiles
        }

    def export_artifacts(self):
        print(f"Exporting clustering artifacts to {self.models_dir}...")
        os.makedirs(self.models_dir, exist_ok=True)
        joblib.dump(self.best_model, self.models_dir / 'kmeans_model.joblib')
        joblib.dump(self.scaler, self.models_dir / 'kmeans_scaler.joblib')
        joblib.dump(self.city_encoder, self.models_dir / 'kmeans_city_encoder.joblib')
        joblib.dump(self.district_encoder, self.models_dir / 'kmeans_district_encoder.joblib')
        joblib.dump(self.metadata, self.models_dir / 'kmeans_metadata.joblib')
        print("Export complete ✅")