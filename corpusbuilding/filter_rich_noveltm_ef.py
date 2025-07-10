import pandas as pd
import ast

df = pd.read_csv("/Users/starrothkopf/Desktop/HDW/noveltmmeta/rich_noveltm_ef.csv")

def parse_list(val):
    if pd.isna(val) or val.strip() in ("", "[]"):
        return []
    try:
        parsed = ast.literal_eval(val)
        return [str(x).strip().lower() for x in parsed]
    except:
        return [val.strip().lower()]

df['genre_tag'] = df['genre_tag'].apply(parse_list)
df['lcc_category'] = df['lcc_category'].apply(parse_list)

# blocked genres and LCC categories
blocked_genres = {
    "biography", "autobiography", "bibliography", "dictionary", "encyclopedia",
    "survey of literature", "legal article", "government publication",
    "law report or digest", "catalog"
}

blocked_lcc = {
    "french literature - italian literature - spanish literature - portuguese literature",
    "american literature",
    "france - andorra - monaco",
    "german literature - dutch literature - flemish literature since 1830 - afrikaans literature - scandinavian literature - old norse literature:old icelandic and old norwegian - modern icelandic literature - faroese literature - danish literature - norwegian literature - swedish literature",
    "asia", "africa", "hunting sports", "oceania (south seas)",
    "history (general)", "psychology",
    "languages and literatures of eastern asia, africa, oceania",
    "history of the americas",
    "oriental languages and literatures",
    "british america (including canada)",
    "latin america. spanish america",
    "united states local history",
    "indo-iranian languages and literatures",
    "spain - portugal",
    "social pathology. social and public welfare. criminology",
    "geography (general). atlases. maps",
    "zoology", "folklore",
    "greek language and literature. latin language and literature",
    "biography",
    "united states",
    "literature on music",
    "russia. soviet union. former soviet republics - poland",
    "drawing. design. illustration",
    "socialism. communism. anarchism",
    "religions. mythology. rationalism",
    "italy - malta",
    "austria - liechtenstein - hungary - czechoslovakia",
    "anthropology",
    "germany",
    "natural history - biology",
    "modern languages. celtic languages",
    "the bible",
    "balkan peninsula",
    "aquaculture. fisheries. angling",
    "slavic languages. baltic languages. albanian language",
    "genealogy",
    "motor vehicles. aeronautics. astronautics",
    "periodicals",
    "military science (general)",
    "northern europe. scandinavia",
    "christian denominations",
    "law in general. comparative and uniform law. jurisprudence",
    "individual institutions - europe",
    "collections. series. collected works",
    "recreation. leisure",
    "political theory",
    "painting",
    "manners and customs (general)",
    "naval science (general)",
    "internal medicine",
    "architecture",
    "decorative arts",
    "animal culture",
    "industries. land use. labor",
    "switzerland",
    "west germanic languages",
    "education (general)",
    "islam. bahaism. theosophy, etc.",
    "practical theology",
    "special aspects of education",
    "armies:organization, distribution, military situation",
    "history of education",
    "christianity",
    "ethics"
}

df = df[~df['genre_tag'].apply(lambda genres: any(g in blocked_genres for g in genres))]
df = df[~df['lcc_category'].apply(lambda lccs: any(l in blocked_lcc for l in lccs))]

df.to_csv("rich_noveltm_ef_filtered.csv", index=False)
print("filtered dataset saved as ef_rich_features_filtered.csv")
