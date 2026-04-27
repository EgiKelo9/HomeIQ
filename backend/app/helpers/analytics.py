import os
import logging
import pandas as pd
from pathlib import Path
from app.ml_pipeline.cleaner import DataCleaner

logger = logging.getLogger(__name__)

def _load_dataset_analytics(data_dir: Path) -> pd.DataFrame:
    """
    Implementasi pengambilan data mentah yang sama persis dengan _load_dataset di model.py.
    """
    dfs = []
    if not data_dir.exists():
        logger.error(f"Folder data tidak ditemukan di: {data_dir}")
        return pd.DataFrame()
        
    for filename in os.listdir(data_dir):
        if filename.endswith(".jsonl"):
            filepath = data_dir / filename
            try:
                temp_df = pd.read_json(filepath, lines=True)
                if not temp_df.empty:
                    dfs.append(temp_df)
            except Exception as e:
                logger.error(f"Gagal memuat file {filename}: {e}")
                
    if not dfs:
        logger.warning("Tidak ada file .jsonl ditemukan di folder data.")
        return pd.DataFrame()
        
    return pd.concat(dfs, ignore_index=True)

def _get_cleaned_data(DATA_DIR: Path) -> pd.DataFrame:
    """
    Mengambil data mentah lalu menjalankan DataCleaner 
    untuk mendapatkan kolom numerik seperti price_in_rp.
    """
    raw_df = _load_dataset_analytics(DATA_DIR)
    
    if raw_df.empty:
        return pd.DataFrame()
        
    try:
        cleaner = DataCleaner()
        # is_training=True diperlukan agar DataCleaner memproses 
        # string harga menjadi numerik price_in_rp
        cleaned_df = cleaner.run_cleaning_pipeline(raw_df, is_training=True)
        return cleaned_df
    except Exception as e:
        logger.error(f"Error saat membersihkan data untuk analitik: {e}")
        return pd.DataFrame()