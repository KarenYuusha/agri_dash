import pandas as pd
import numpy as np

regions_to_remove = [
    "Cả Nước",
    "Đồng bằng sông Hồng",
    "Trung du và miền núi phía Bắc",
    "Bắc Trung Bộ và Duyên hải miền Trung",
    "Tây Nguyên",
    "Đông Nam Bộ",
    "Đồng bằng sông Cửu Long"
]

unit_mapping = {
    'nghìn tấn': ('tấn', 1000),
    'tấn': ('tấn', 1),
    'nghìn ha': ('ha', 1000),
    'ha': ('ha', 1),
    'tạ/ha': ('tấn/ha', 0.1),
    'triệu đồng': ('đồng', 1000000)
}

def remove_province(df, remove=True):
    if remove:
        df = df[~df['Province'].isin(regions_to_remove)]
    
    return df

def normalize_value(df):
    # Clean columns
    df['Unit'] = df['Unit'].str.strip().str.lower()
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

    # Map units
    df[['Unit_std', 'Multiplier']] = df['Unit'].map(unit_mapping).apply(pd.Series)

    # Handle missing mappings
    df['Multiplier'] = df['Multiplier'].fillna(1)
    df['Unit_std'] = df['Unit_std'].fillna(df['Unit'])

    # Convert values
    df['Value'] = df['Value'] * df['Multiplier']

    # Replace unit column
    df['Unit'] = df['Unit_std']

    # Drop helper columns
    df.drop(columns=['Unit_std', 'Multiplier'], inplace=True)

    return df

def prepare_agri_df(remove=True):
    df = pd.read_csv('data/agri_merged.csv')
    df = remove_province(df, remove)
    df = normalize_value(df)
    
    return df

def weather_yearly_features(df):
    df = df.copy()

    # =========================
    # 1. BASIC PREPROCESSING
    # =========================
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    # Ensure numeric
    numeric_cols = [
        'T2M','RH2M','T2M_MAX','T2M_MIN',
        'CLOUD_AMT','PRECTOTCORR','GWETPROF','CLRSKY_SFC_SW_DWN'
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # =========================
    # 2. DAILY FEATURE FLAGS
    # =========================
    df['hot_day'] = (df['T2M_MAX'] > 35).astype(int)
    df['cold_day'] = (df['T2M_MIN'] < 10).astype(int)

    df['rainy_day'] = (df['PRECTOTCORR'] > 1).astype(int)
    df['heavy_rain'] = (df['PRECTOTCORR'] > 20).astype(int)
    df['dry_day'] = (df['PRECTOTCORR'] == 0).astype(int)

    df['low_moisture'] = (df['GWETPROF'] < 0.3).astype(int)

    # Growing Degree Days (GDD)
    base_temp = 10
    df['GDD'] = (df['T2M'] - base_temp).clip(lower=0)

    # =========================
    # 3. YEARLY AGGREGATION
    # =========================
    yearly = df.groupby(['Province','Year']).agg({
        # Temperature
        'T2M': ['mean','std','max','min'],
        'T2M_MAX': 'max',
        'T2M_MIN': 'min',

        # Humidity & cloud
        'RH2M': ['mean','std'],
        'CLOUD_AMT': 'mean',

        # Rainfall
        'PRECTOTCORR': ['sum','max','std'],

        # Soil moisture & radiation
        'GWETPROF': 'mean',
        'CLRSKY_SFC_SW_DWN': 'mean',

        # Engineered counts
        'hot_day': 'sum',
        'cold_day': 'sum',
        'rainy_day': 'sum',
        'heavy_rain': 'sum',
        'dry_day': 'sum',

        # GDD
        'GDD': 'sum'
    })

    # Flatten column names
    yearly.columns = ['_'.join(col) if isinstance(col, tuple) else col for col in yearly.columns]
    yearly = yearly.reset_index()

    # =========================
    # 4. DERIVED FEATURES
    # =========================
    yearly['rain_intensity'] = yearly['PRECTOTCORR_sum'] / (yearly['rainy_day_sum'] + 1)
    yearly['dry_ratio'] = yearly['dry_day_sum'] / 365
    yearly['hot_ratio'] = yearly['hot_day_sum'] / 365

    # =========================
    # 5. LAG FEATURES (VERY IMPORTANT)
    # =========================
    yearly = yearly.sort_values(['Province','Year'])

    for col in ['PRECTOTCORR_sum', 'T2M_mean', 'GDD_sum']:
        yearly[f'{col}_lag1'] = yearly.groupby('Province')[col].shift(1)

    # =========================
    # 6. HANDLE MISSING VALUES
    # =========================
    yearly = yearly.fillna(0)

    return yearly