import pandas as pd
from collections import Counter
import ast

df = pd.read_csv('rich_noveltm_ef_filtered.csv')
print("this is a subset of NovelTM: nineteenth century (1789-1913) British/Irish volumes very likely to be fiction")
print(f"\ntotal entries: {len(df)}")

def parse_list(val):
    if pd.isna(val) or val.strip() in ("", "[]"):
        return []
    try:
        parsed = ast.literal_eval(val)
        return [str(x).strip().lower() for x in parsed]
    except:
        return [val.strip().lower()]

all_contents = df['contents']
contents_counts = Counter([g for g in all_contents]).most_common(20)

all_genres = sum(df['genre_tag'], [])
genre_counts = Counter([g for g in all_genres]).most_common(2)

all_genres2 = sum(df['genres'], [])
genre_counts2 = Counter([g for g in all_genres2]).most_common(20)

all_lcc = sum(df['lcc_category'], [])
lcc_counts = Counter([c for c in all_lcc]).most_common(10)

df['imprint'] = df['imprint'].astype(str)
df['imprint_city'] = df['imprint'].str.lower().str.extract(r'^\s*([^;]+)')
city_counts = df['imprint_city'].value_counts().reset_index()
city_counts.columns = ['city', 'count']
print(city_counts.head(20))

gender_counts = df['estimated_gender'].str.lower().value_counts(dropna=True)
author_counts = df['author'].str.lower().value_counts(dropna=True)

df['year_bucket'] = (df['inferreddate'] // 10 * 10).astype(int)

nonfic_avg = df['nonficprob'].mean()
juvenile_avg = df['juvenileprob'].mean()

text_stats = df[[
    'avg_sentence_count', 'avg_line_count', 'avg_tokens_per_page',
    'var_sentence_count', 'var_line_count', 'var_tokens_per_page', 'cap_alpha_freq'
]].describe()

print("\n--- top genres ---")
for genre, count in genre_counts:
    print(f"{genre}: {count}")

print("\n--- top genres2 ---")
for genre, count in genre_counts2:
    print(f"{genre}: {count}")

print("\n--- top LCC categories ---")
for lcc, count in lcc_counts:
    print(f"{lcc}: {count}")

print("\n--- authors ---")
print(f"number of authors: {len(author_counts)}")

print("\n--- estimated gender distribution ---")
print(gender_counts)

print("\n--- publication year distribution by decade ---")
print(df['year_bucket'].value_counts().sort_index())

print(f"\navg nonfiction probability: {nonfic_avg:.2f}")
print(f"avg juvenile probability: {juvenile_avg:.2f}")

print("\n--- textual features summary ---")
print(text_stats)

"""
total entries: 10519
fiction: 5797
unknown: 4656
novel: 66
england: 5
electronic books: 5
dime novels: 5
mixed: 4
novels: 3
london: 3
fantasy fiction: 3
translations: 3
three deckers: 3
love stories: 3
adventure fiction: 3
mystery and detective fiction: 3
science fiction: 3
illustrated works: 2
historical fiction: 2
great britain: 2
encyclopedia: 2
dictionary: 2
christian fiction: 2
criticism, interpretation, etc: 2
folklore: 2
domestic fiction: 2

publication year distribution by decade:
year_bucket
1780       9
1790     112
1800     283
1810     320
1820     589
1830     599
1840     637
1850     668
1860     803
1870     896
1880    1342
1890    1849
1900    1732
1910     680
Name: count, dtype: int64

most common authors:
author
Oliphant                                    60
Scott, Walter, Sir                          55
James, G. P. R. (George Payne Rainsford)    54
Balzac, Honoré de                           49
Braddon, M. E. (Mary Elizabeth)             49
Defoe, Daniel                               46
Edgeworth, Maria                            44
Wood, Ellen                                 42
Whyte-Melville, G. J. (George John)         41
Yonge, Charlotte M. (Charlotte Mary)        40
Reid, Mayne                                 39
Dickens, Charles                            38
Martineau, Harriet                          34
Ainsworth, William Harrison                 34
Grant, James                                34
Name: count, dtype: int64

most common MARC country codes:
place
enk    10033
stk      466
xxk       18
wlk        2
Name: count, dtype: int64

genre
Fiction    0.208442
unknown    0.354554
Name: nonficprob, dtype: float64

estimated_gender
m          5770
f          2403
unknown    2346
Name: count, dtype: int64

"""