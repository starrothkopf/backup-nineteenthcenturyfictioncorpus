import pandas as pd

titlemeta = pd.read_csv('metadata/titlemeta.tsv', sep='\t', encoding='utf-8')
manual = pd.read_csv('metadata/manual_title_subset.tsv', sep='\t', encoding='utf-8')

british_irish_codes = [    
    'enk',  # England
    'stk',  # Scotland
    'ie',   # Ireland (inconsistent, might also be used for italy)
    'irl',  # Ireland (ISO-aligned, not standard MARC)
    'xxk',  # United Kingdom (general)
    'uk',   # United Kingdom (nonstandard MARC)
    'wlk',  # Wales
    'nui',  # Northern Ireland (rare)
    'e-ir', # Eire/Ireland (rare)
    ]

excluded_genres = set([
        'short stories', 'bibliographies', 'autobiography', 'biography', 'publishers\' advertisements',
        'juvenile audience', 'juvenile works', 'history', 'publishers\' cloth bindings (binding)', 
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
    elif 'nationality' in df.columns:
        df = df[df['nationality'].str.lower().isin(british_irish_codes)]

    if 'category' in df.columns:
        df = df[df['category'] == 'longfiction']

    df = filter_by_genre(df)

    df = df.drop_duplicates(subset=['author', 'shorttitle', 'inferreddate'])

    cols_to_keep = ['docid','author', 'inferreddate', 'gender', 'enumcron', 'volnum', 'nonficprob', 'nationality', 'place', 'category', 'genres']
    df = df[[col for col in cols_to_keep if col in df.columns]]
    
    print(f"{name} final count: {len(df)} rows")
    
    outname = f"filtered_{name.replace(' ', '_').lower()}.tsv"
    df.to_csv(outname, sep='\t', index=False)
    print(f"Saved to {outname}")
    
    return df

titlemeta_filtered = clean_and_filter(titlemeta, 'TitleMeta')
manual_filtered = clean_and_filter(manual, 'ManualTitleSubset')
