import os
import logging
import pandas as pd
from pathlib import Path
from app.ml_pipeline.train import ModelTrainer

logger = logging.getLogger(__name__)

# State global untuk tracking proses training yang dibaca oleh router API
TRAINING_STATE = {
    "status": "IDLE",  # IDLE, RUNNING, SUCCESS, FAILED
    "message": "Belum ada training yang dijalankan sejak server menyala.",
    "metrics": None,
}

def _load_dataset(DATA_DIR: Path) -> pd.DataFrame:
    """Memuat semua file .jsonl dari folder data."""
    dfs = []
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Folder data tidak ditemukan di: {DATA_DIR}")
        
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".jsonl"):
            filepath = DATA_DIR / filename
            try:
                temp_df = pd.read_json(filepath, lines=True)
                if not temp_df.empty:
                    dfs.append(temp_df)
            except Exception as e:
                logger.error(f"Melewati {filename} saat load data. Error: {e}")
                
    if not dfs:
        raise ValueError("Tidak ada data yang berhasil dimuat. Pastikan scraper sudah dijalankan.")
        
    return pd.concat(dfs, ignore_index=True)


def _execute_training(MODELS_DIR: Path, DATA_DIR: Path):
    """Background task untuk menjalankan pipeline training."""
    global TRAINING_STATE
    TRAINING_STATE["status"] = "RUNNING"
    TRAINING_STATE["message"] = "Proses training sedang berjalan..."
    TRAINING_STATE["metrics"] = None
    
    try:
        logger.info("Memulai load dataset untuk training...")
        df = _load_dataset(DATA_DIR)
        
        logger.info("Dataset berhasil dimuat. Menginisialisasi ModelTrainer...")
        trainer = ModelTrainer(models_dir=str(MODELS_DIR))
        
        logger.info("Menjalankan pipeline training (Clean, Encode, Split, Scale, Train)...")
        trainer.train(df)
        
        logger.info("Mengekspor artefak model ke disk...")
        trainer.export_artifacts()
        
        TRAINING_STATE["status"] = "SUCCESS"
        TRAINING_STATE["message"] = "Training berhasil diselesaikan."
        TRAINING_STATE["metrics"] = {
            "train_metrics": trainer.metadata.get("train_metrics", {}),
            "test_metrics": trainer.metadata.get("test_metrics", {}),
        }
        logger.info("Training selesai dengan sukses!")
        
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat proses training: {e}", exc_info=True)
        TRAINING_STATE["status"] = "FAILED"
        TRAINING_STATE["message"] = f"Gagal saat training: {str(e)}"