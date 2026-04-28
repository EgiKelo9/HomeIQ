import os
import joblib
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.helpers.analytics import _get_cleaned_data
from app.schemas.analytics import ModelMetrics, FeatureImportance, DistributionData, MarketSegment

router = APIRouter()

# Menyesuaikan path
BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / 'models'
DATA_DIR = BASE_DIR / 'data'

@router.get("/metrics", response_model=ModelMetrics)
def get_model_metrics():
    """Mengambil metrik evaluasi model dari artefak yang disimpan setelah training."""
    metadata_path = MODELS_DIR / 'model_metadata.joblib'
    y_scaler_path = MODELS_DIR / 'y_scaler.joblib'
    kmeans_metadata_path = MODELS_DIR / 'kmeans_metadata.joblib'
    
    if not metadata_path.exists() or not y_scaler_path.exists() or not kmeans_metadata_path.exists():
        raise HTTPException(status_code=404, detail="Artefak model tidak ditemukan.")
        
    metadata = joblib.load(metadata_path)
    y_scaler = joblib.load(y_scaler_path)
    kmeans_metadata = joblib.load(kmeans_metadata_path)
    
    test_metrics = metadata.get('test_metrics', {})
    silhouette = kmeans_metadata.get('silhouette_score', 0)
    scale_factor = y_scaler.scale_[0] 
    print("Silhouette Score:", silhouette)
    
    return ModelMetrics(
        r2_score=test_metrics.get('r2', 0),
        rmse=test_metrics.get('rmse', 0) * scale_factor,
        mae=test_metrics.get('mae', 0) * scale_factor,
        silhouette_score=silhouette,
        last_trained=datetime.fromtimestamp(os.path.getmtime(metadata_path)).isoformat()
    )

@router.get("/feature-importance", response_model=list[FeatureImportance])
def get_feature_importance():
    """Mengambil feature importance dari model yang sudah dilatih."""
    metadata_path = MODELS_DIR / 'model_metadata.joblib'
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Metadata tidak ditemukan.")
        
    metadata = joblib.load(metadata_path)
    fi_dict = metadata.get('feature_importance', {})
    sorted_fi = sorted(fi_dict.items(), key=lambda item: item[1], reverse=True)
    
    return [FeatureImportance(feature=k, importance=float(v)) for k, v in sorted_fi]

@router.get("/distribution", response_model=list[DistributionData])
def get_data_distribution():
    """Mengambil distribusi data berdasarkan kota untuk analisis pasar."""
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
    """Mengelompokkan pasar berdasarkan clustering K-Means untuk analisis segmen pasar."""
    metadata_path = MODELS_DIR / 'kmeans_metadata.joblib'
    
    # Jika model K-Means belum di-training, berikan fallback
    if not metadata_path.exists():
         return [
            MarketSegment(cluster_name="Belum Ditraining", count=0, description="Jalankan pipeline training terlebih dahulu.", color="#9ca3af")
        ]
    
    # Load hasil profil yang sudah di-generate oleh ClusterTrainer
    metadata = joblib.load(metadata_path)
    profiles = metadata.get("profiles", [])
    
    segments = []
    for p in profiles:
        segments.append(MarketSegment(
            cluster_name=p["cluster_name"],
            count=p["count"],
            description=p["description"],
            color=p["color"]
        ))
        
    return segments