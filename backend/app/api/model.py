from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.model import TrainResponse, PredictRequest, PredictResponse
from app.helpers.model import _execute_training, TRAINING_STATE
from app.ml_pipeline.predict import HousePricePredictor

router = APIRouter()

_THIS_DIR = Path(__file__).parent.parent
DATA_DIR = _THIS_DIR.parent / "data"
MODELS_DIR = _THIS_DIR.parent / "models"

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/train", response_model=TrainResponse)
def trigger_training(background_tasks: BackgroundTasks):
    """
    Memicu proses pelatihan model Random Forest. 
    Proses berjalan di background dan memerlukan beberapa saat.
    """
    global TRAINING_STATE
    if TRAINING_STATE["status"] == "RUNNING":
        raise HTTPException(
            status_code=400, 
            detail="Proses training masih berjalan. Silakan cek /model/status secara berkala."
        )
        
    background_tasks.add_task(_execute_training, MODELS_DIR, DATA_DIR)
    
    return TrainResponse(
        message="Task training berhasil ditambahkan ke antrean process. Silakan gunakan endpoint /status untuk memantau.",
        status="QUEUED"
    )

@router.get("/status")
def get_training_status():
    """
    Cek status proses training yang sedang berjalan atau hasil iterasi terakhir.
    """
    return TRAINING_STATE


@router.post("/predict", response_model=PredictResponse)
def predict_house_price(payload: PredictRequest):
    """Melakukan prediksi harga rumah menggunakan model yang sudah diekspor."""
    try:
        predictor = HousePricePredictor(models_dir=str(MODELS_DIR))
        predicted_price = predictor.predict(
            bedrooms=payload.bedrooms,
            bathrooms=payload.bathrooms,
            building_size_m2=payload.building_size_m2,
            land_size_m2=payload.land_size_m2,
            city=payload.city,
            district=payload.district,
        )
        return PredictResponse(predicted_price=predicted_price)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Artefak model belum ditemukan. Jalankan endpoint /model/train terlebih dahulu.",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Input tidak valid untuk model: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal melakukan prediksi: {exc}",
        )
