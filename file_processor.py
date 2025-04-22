import pandas as pd
import re

def clean_price(price_str: str) -> float:
    if not isinstance(price_str, str):
        return float(price_str)
    
    cleaned = re.sub(r'[^\d.,]', '', price_str).replace(',', '.').strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def process_excel_file(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    
    required_columns = ["title", "url", "xpath"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Файл должен содержать колонки: {required_columns}")
    
    df = df.dropna(subset=required_columns)
    df["title"] = df["title"].str.strip()
    df["url"] = df["url"].str.strip()
    df["xpath"] = df["xpath"].str.strip()
    
    return df