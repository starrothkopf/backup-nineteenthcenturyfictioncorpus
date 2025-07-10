import pandas as pd

df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/tedunderwood/metadata/titlemeta.tsv", sep='\t')
print(df.columns.tolist())

british_irish_codes = [    
    'enk',  # England
    'stk',  # Scotland
    'ie',   # Ireland (inconsistent, might also be used for italy)
    'irl',  # Ireland (ISO-aligned, not standard MARC)
    'xxk',  # United Kingdom (general)
    'uk',   # United Kingdom (nonstandard MARC)
    'wlk',  # Wales
    ]

excluded_genres = set([
        'short stories', 'bibliographies', 'autobiography', 'biography', 'publishers\' advertisements',
        'juvenile audience', 'juvenile works', 'juvenile literature', 'history', 'publishers\' cloth bindings (binding)', 
        'bookplates (provenance)', 'poetry', 'new york', 'new york (state)',
    ])

def filter_by_genre(df):
    def is_valid(genres):
        tags = [tag.strip().lower() for tag in str(genres).split('|')]
        return all(tag not in excluded_genres for tag in tags)

    return df[df['genres'].apply(is_valid)].copy()

def clean_and_filter(df, name):
    print(f"\nProcessing: {name}")
    
    df = df[df['inferreddate'].fillna(0).astype(int) > 0]
    df = df[(df['inferreddate'] >= 1789) & (df['inferreddate'] <= 1913)]

    if 'place' in df.columns:
        df = df[df['place'].str.lower().isin(british_irish_codes)]

    df = filter_by_genre(df)

    df = df.drop_duplicates(subset=['author', 'shorttitle', 'inferreddate'])

    print(f"{name} final count: {len(df)} rows")
    
    outname = f"filtered_{name.replace(' ', '_').lower()}.tsv"
    df.to_csv(outname, sep='\t', index=False)
    print(f"Saved to {outname}")
    
    return df

titlemeta_filtered = clean_and_filter(df, 'titlemeta')
