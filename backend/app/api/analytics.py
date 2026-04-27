import os
import joblib
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from app.helpers.analytics import _get_cleaned_data
from app.schemas.analytics import ModelMetrics, FeatureImportance, DistributionData, MarketSegment

router = APIRouter()

# Menyesuaikan path
BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / 'models'
DATA_DIR = BASE_DIR / 'data'

@router.get("/metrics", response_model=ModelMetrics)
def get_model_metrics():
    metadata_path = MODELS_DIR / 'model_metadata.joblib'
    y_scaler_path = MODELS_DIR / 'y_scaler.joblib'
    
    if not metadata_path.exists() or not y_scaler_path.exists():
        raise HTTPException(status_code=404, detail="Artefak model tidak ditemukan.")
        
    metadata = joblib.load(metadata_path)
    y_scaler = joblib.load(y_scaler_path)
    
    test_metrics = metadata.get('test_metrics', {})
    scale_factor = y_scaler.scale_[0] 
    
    return ModelMetrics(
        r2_score=test_metrics.get('r2', 0),
        rmse=test_metrics.get('rmse', 0) * scale_factor,
        mae=test_metrics.get('mae', 0) * scale_factor,
        last_trained=datetime.fromtimestamp(os.path.getmtime(metadata_path)).isoformat()
    )

@router.get("/feature-importance", response_model=list[FeatureImportance])
def get_feature_importance():
    metadata_path = MODELS_DIR / 'model_metadata.joblib'
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Metadata tidak ditemukan.")
        
    metadata = joblib.load(metadata_path)
    fi_dict = metadata.get('feature_importance', {})
    sorted_fi = sorted(fi_dict.items(), key=lambda item: item[1], reverse=True)
    
    return [FeatureImportance(feature=k, importance=float(v)) for k, v in sorted_fi]

@router.get("/distribution", response_model=list[DistributionData])
def get_data_distribution():
    df = _get_cleaned_data(DATA_DIR)
    
    # Jika hasil cleaning kosong, kirim fallback response
    if df.empty or 'city' not in df.columns or 'price_in_rp' not in df.columns:
        return [DistributionData(city="Data Belum Tersedia", count=0, avg_price=0)]
        
    agg_df = df.groupby('city').agg(
        count=('price_in_rp', 'count'),
        avg_price=('price_in_rp', 'mean')
    ).reset_index().sort_values(by='count', ascending=False)
    
    return [
        DistributionData(
            city=row['city'],
            count=int(row['count']),
            avg_price=float(row['avg_price'] / 1_000_000) # Satuan Juta
        )
        for _, row in agg_df.iterrows()
    ]

@router.get("/segments", response_model=list[MarketSegment])
def get_market_segments():
    df = _get_cleaned_data(DATA_DIR)
    features = ['price_in_rp', 'building_size_m2', 'land_size_m2']
    
    if df.empty or len(df) < 3 or not all(col in df.columns for col in features):
         return [
            MarketSegment(cluster_name="N/A", count=0, description="Data tidak cukup", color="#gray")
        ]
    
    df_cluster = df.dropna(subset=features).copy()
    scaled_features = StandardScaler().fit_transform(df_cluster[features])
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df_cluster['cluster'] = kmeans.fit_predict(scaled_features)
    
    centers = df_cluster.groupby('cluster')['price_in_rp'].mean().sort_values()
    labels = ["Entry Level", "Mid Range", "Premium"]
    colors = ["#3b82f6", "#10b981", "#f59e0b"]
    
    segments = []
    for idx, (cid, _) in enumerate(centers.items()):
        c_data = df_cluster[df_cluster['cluster'] == cid]
        segments.append(MarketSegment(
            cluster_name=labels[idx],
            count=len(c_data),
            description=f"Segmen {labels[idx]} berdasarkan harga dan luas.",
            color=colors[idx]
        ))
    return segments