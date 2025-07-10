import gender_guesser.detector as gender
import pandas as pd
import re

df = pd.read_csv('/Users/starrothkopf/Desktop/HDW/noveltmmeta/corpusbuilding/filtered_titlemeta.tsv', sep='\t', encoding='utf-8')

detector = gender.Detector()

def extract_first_name(author):
    if pd.isna(author):
        return None

    author = author.strip()
    author = re.sub(r'(?i)\b(baron|countess|freiherr|comtesse|marquise|madame|mademoiselle|sir|lord|lady|mr|mrs|ms|dr|vicomte|earl)\b[^,]*,', '', author)

    if ',' in author:
        parts = [part.strip() for part in author.split(',')]
        if len(parts) > 1:
            first_part = parts[1]
        else:
            first_part = parts[0]
    else:
        first_part = author

    # prefer name in parentheses if available
    match = re.search(r'\(([^)]+)\)', first_part)
    if match:
        first_part = match.group(1)

    first_part = re.sub(r'[^a-zA-Z\s\-]', '', first_part)

    # split on hyphen and space
    words = re.split(r'[-\s]', first_part)
    words = [w for w in words if w]

    if not words:
        return None

    return words[0].capitalize()

df['first_name'] = df['author'].apply(extract_first_name)
#print("\nSample extracted first names:")
#print(df[['author', 'first_name']].dropna().head(20))

def get_gender_from_author(author):
    first = extract_first_name(author)
    return detector.get_gender(first) if first else 'unknown'

def simplify_gender(g):
    if g in ['male', 'mostly_male']:
        return 'm'
    elif g in ['female', 'mostly_female']:
        return 'f'
    else:
        return 'unknown'

df['estimated_gender'] = df['author'].apply(get_gender_from_author).apply(simplify_gender)
df.to_csv('filtered_titlemeta_with_gender.tsv', sep='\t', index=False)

print("\nEstimated gender distribution:")
print(df['estimated_gender'].value_counts(dropna=False))

#print("\nSample of authors with unknown gender:")
#print(df[df['estimated_gender'] == 'unknown'][['author', 'first_name']].dropna().head(20))