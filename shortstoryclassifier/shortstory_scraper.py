import requests
from bs4 import BeautifulSoup
import csv

url = "https://www.victorianresearch.org/atcl/show_genre.php?gid=18"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

section = soup.find("section", class_="show-page", attrs={"aria-labelledby": "genre"})
if not section:
    raise ValueError("Could not find the 'show-page' section")

ol = section.find("ol")
if not ol:
    raise ValueError("Could not find the ordered list in the section")

items = ol.find_all("li")

# extract relevant data from each <li>
# Author. <em><a href="...">Title</a></em>. Vol info. Publisher info, year.
rows = []
for li in items:
    text = li.get_text(separator=" ", strip=True)
    author_part = li.text.split('.', 1)[0].strip()
    
    a_tag = li.find("a")
    title = a_tag.text if a_tag else ""
    
    remainder = text
    if author_part:
        remainder = remainder.replace(author_part, '', 1).strip()
    if title:
        remainder = remainder.replace(title, '', 1).strip()
    
    rows.append([author_part, title, remainder])

with open("short_story_collections.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Author", "Title", "Details"])
    writer.writerows(rows)

print(f"saved {len(rows)} records to short_story_collections.csv")
