import pandas as pd
from sklearn.impute import SimpleImputer

class DataCleaner:
    def __init__(self):
        # Sesuai dengan workflow: electricity dan carports didrop
        self.drop_columns = ['source', 'url', 'title', 'address', 'scraped_at', 'hash_id', 'electricity', 'carports']
        
        # Kolom yang didrop jika ada missing values
        self.dropna_subset = ['district', 'city', 'bedrooms', 'bathrooms', 'land_size_m2', 'building_size_m2']
        
        # Kolom kategori yang diisi dengan modus
        self.categorical_features = ['district', 'city', 'certificate', 'furnishing']
        
        # Batas logis outlier sesuai workflow
        self.outlier_columns = ['price_in_rp', 'land_size_m2', 'building_size_m2', 'bedrooms', 'bathrooms']

    def drop_unused_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Menghapus kolom yang tidak diperlukan untuk pemodelan, termasuk kolom >40% null."""
        existing_cols_to_drop = [col for col in self.drop_columns if col in df.columns]
        return df.drop(columns=existing_cols_to_drop)

    def drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Menghapus baris data yang duplikat."""
        return df.drop_duplicates()

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Menghapus row dengan list subset missing dan mengisi kategori dengan modus."""
        res_df = df.copy()
        
        # A. Hande Less Missing Values in Columns dengan dropna (berdasarkan subsetnya)
        existing_dropna_cols = [col for col in self.dropna_subset if col in res_df.columns]
        if existing_dropna_cols:
            res_df = res_df.dropna(subset=existing_dropna_cols)
            
        # B. Fill with Most Frequent for Categorical Columns
        existing_cat_cols = [col for col in self.categorical_features if col in res_df.columns]
        if existing_cat_cols:
            imputer_cat = SimpleImputer(strategy='most_frequent')
            res_df[existing_cat_cols] = imputer_cat.fit_transform(res_df[existing_cat_cols])
            
        return res_df

    def handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter outlier dengan threshold statis sesuai workflow notebook."""
        df_no_outliers = df.copy()
        
        # 1. Threshold logis / Statis (Seperti di filter workflow)
        if all(col in df_no_outliers.columns for col in ['price_in_rp', 'bedrooms', 'bathrooms', 'building_size_m2', 'land_size_m2']):
            df_no_outliers = df_no_outliers[
                (df_no_outliers['price_in_rp'] >= 3e8) & (df_no_outliers['price_in_rp'] <= 5e10) & 
                (df_no_outliers['bedrooms'] <= 20) & (df_no_outliers['bathrooms'] <= 20) &
                (df_no_outliers['building_size_m2'] <= 2000) & (df_no_outliers['land_size_m2'] <= 2000)
            ]
            
        return df_no_outliers

    def run_cleaning_pipeline(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        Menjalankan seluruh pembersihan data. 
        Parameter is_training digunakan untuk menghindari penghapusan outliers pada saat prediction.
        """
        df_cleaned = df.copy()
        
        df_cleaned = self.drop_unused_columns(df_cleaned)
        df_cleaned = self.drop_duplicates(df_cleaned)
        df_cleaned = self.handle_missing_values(df_cleaned)
        
        if is_training:
            df_cleaned = self.handle_outliers(df_cleaned)
            
        return df_cleaned

