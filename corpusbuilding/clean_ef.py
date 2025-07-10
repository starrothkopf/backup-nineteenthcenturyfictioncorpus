import pandas as pd
import ast
import numpy as np
import re

# Load CSV
df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/corpusbuilding/ef_rich_features_summary.csv", dtype=str)

# Convert numeric columns
numeric_cols = [
    'avg_sentence_count', 'var_sentence_count',
    'avg_line_count', 'var_line_count',
    'avg_tokens_per_page', 'var_tokens_per_page',
    'page_count'
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

def extract_mean_cap_alpha(val):
    if isinstance(val, str):
        # find all numbers at the end of lines (after whitespace)
        numbers = re.findall(r'\s+(\d+)$', val, flags=re.MULTILINE)
        if numbers:
            values = [int(n) for n in numbers]
            return np.mean(values)
    try:
        return float(val)
    except:
        return np.nan

df['cap_alpha_freq'] = df['cap_alpha_freq'].apply(extract_mean_cap_alpha)

def parse_list(val):
    if pd.isna(val) or val.strip() in ("", "[]"):
        return []
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            return parsed
        else:
            return [parsed]
    except Exception:
        return [val.strip()]

df['genre_tag'] = df['genre_tag'].apply(parse_list)
df['lcc_category'] = df['lcc_category'].apply(parse_list)

# Re-parse genre_tag list
def clean_genres(val):
    if isinstance(val, list):
        genres = val
    elif pd.isna(val) or val.strip() in ("", "[]"):
        return ['unknown']
    else:
        try:
            genres = ast.literal_eval(val)
            if isinstance(genres, str):
                genres = [genres]
        except:
            genres = [val.strip()]
    
    genres = [g.lower() for g in genres if g.lower() != 'document (computer)']
    return genres if genres else ['unknown']


df['genre_tag'] = df['genre_tag'].apply(clean_genres)

df = df.drop(columns=['page_count', 'access_rights', 'part_of_journal'], errors='ignore') # would take 4 hours to fetch

# Convert lcc_category to lowercase list
def clean_lcc(val):
    if isinstance(val, list):
        lcc = val
    elif pd.isna(val) or val.strip() in ("", "[]"):
        return ['unknown']
    else:
        try:
            lcc = ast.literal_eval(val)
            if isinstance(lcc, str):
                lcc = [lcc]
        except:
            lcc = [val.strip()]
    
    lcc = [entry.lower() for entry in lcc if entry.strip()]
    return lcc if lcc else ['unknown']


df['lcc_category'] = df['lcc_category'].apply(clean_lcc)

for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].apply(lambda x: x.lower() if isinstance(x, str) else x)

df.to_csv("ef_rich_features_cleaned.csv", index=False)
print("Cleaned CSV saved as ef_rich_features_cleaned.csv")
