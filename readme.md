Filtered Subset of NovelTM Dataset for English-Language Fiction, 1789-1913
==========================================================

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3766610.svg)](https://doi.org/10.5281/zenodo.3766610)

rich_noveltm_ef_filtered.csv
-
Metadata for 9,906 volumes in HathiTrust that have been identified as likely to contain English-language British/Irish fiction. All of the aquisition code belongs to Ted Underwood et. al and is grouped in /tedunderwood. My additions are further filtering and analysis.

Metadata from NovelTM
-
docid,oldauthor,author,authordate,inferreddate,latestcomp,datetype,startdate,enddate,imprint,imprintdate,contents,genres,subjects,geographics,locnum,oclc,place,recordid,instances,allcopiesofwork,copiesin25yrs,enumcron,volnum,title,parttitle,earlyedition,shorttitle,nonficprob,juvenileprob
- "genres" are very incomplete from the Library of Congress, see the top 5:
novel: 62
electronic books: 5
dime novels: 5
mixed: 3
translations: 3
three deckers: 3
- "nonficprob" ranges around 0.1-0.3
- For a fuller description of this data, see [the accompanying article in the *Journal of Cultural Analytics* by Ted Underwood, Patrick Kimutis, and Jessica Witte.](https://culturalanalytics.org/article/13147-noveltm-datasets-for-english-language-fiction-1700-2009) Levels of error are described statistically in that article. The authors do not plan to correct details in the dataset. This is a snapshot of a particular (imperfect) state of our knowledge circa 2019, not a resource we intend to update and maintain in perpetuity.
- Appears to have no volumes published in Ireland (Dublin):                        city  count
0                    london   8820
1                 edinburgh    387
2              london [etc.     48
3                  new york     43
4                   glasgow     40
5                    oxford     30
6               westminster     25
7                   bristol     24
8                     lond.     17
9                manchester     16
10                   boston      9
11                  london       9
12                cambridge      9
13            london, [eng.      8
14                 chiswick      7
15      london and new york      7
16                liverpool      7
17          edinburgh [etc.      7
18  london|hutchinson|19--?      6
19         london, new york      6

Metadata from HathiTrust Extracted Features
-
avg_sentence_count,var_sentence_count,avg_line_count,var_line_count,avg_tokens_per_page,var_tokens_per_page,cap_alpha_freq,genre_tag,lcc_category
- "genre_tag" labels from Hathi Trust are either "fiction" or "unknown" (fiction: 5682, unknown: 4178)
- blocked_genres = {
    "biography", "autobiography", "bibliography", "dictionary", "encyclopedia",
    "survey of literature", "legal article", "government publication",
    "law report or digest", "catalog"
}
- "lcc_category" labels are again very incomplete (unknown: 8356) from the Library of Congress, see the top 3:
fiction and juvenile belles lettres: 932
english literature: 609
great britain: 38
literature (general): 30
the family. marriage. women: 7
- blocked_lcc = {
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

Basic Analytics
-
number of authors: 4089

--- estimated gender distribution ---
https://pypi.org/project/gender-guesser/
estimated_gender
m          5401
f          2305
unknown    2200

--- publication year distribution by decade ---
year_bucket
1780       9
1790     104
1800     267
1810     306
1820     556
1830     561
1840     612
1850     639
1860     770
1870     850
1880    1273
1890    1737
1900    1608
1910     614

avg nonfiction probability: 0.26
avg juvenile probability: 0.17

--- textual features summary ---
       avg_sentence_count  avg_line_count  ...  var_tokens_per_page  cap_alpha_freq
count         9904.000000     9906.000000  ...         9.906000e+03     9906.000000
mean            13.481955       31.980547  ...         8.886300e+03        2.352107
std              9.160406       17.004703  ...         2.629906e+04        1.777580
min              1.062500        4.286957  ...         6.138677e+00        0.000000
25%              8.357319       24.780179  ...         2.000017e+03        1.700000
50%             11.250402       28.577789  ...         3.992647e+03        2.100000
75%             16.059465       34.562380  ...         7.794762e+03        2.600000
max            327.942987      580.456916  ...         1.125610e+06       41.700000


The [metadata itself](https://github.com/tedunderwood/noveltmmeta/tree/master/metadata)
-------------------

The dataset we have created is multifaceted. Instead of offering a single list of volumes, we provide seven lists constructed in different ways. Researchers can choose the list most suited to their needs--or, better still, choose several lists, in order to compare results.

All seven lists can be found in the **/metadata** subdirectory. They are tab-separated tables in UTF-8 encoding.

All this metadata is drawn ultimately from HathiTrust, and keyed to volume IDs in that library. But we have made an effort to standardize some columns (e.g. author name), so they may not correpond precisely to the values in Hathi. Many new columns have also been added, either through inference from the original metadata, or (in three cases) by manually adding new information.

Code directiories
==============

The code we used to create the metadata has been archived in subdirectories, so that researchers can understand where this information is coming from.

However, please note that this is not a situation where you can simply push a button and expect to re-run the entire pipeline. That definitely will not work. This was a several-year process; there was a lot of manual intervention along the way, and files had to be renamed and moved at the end for reasons of expository clarity, which broke a lot of path names in earlier scripts. Please understand the code as documentation of what we did, not as a reproducible workflow. To be honest, "reproducing" this project would involve several years of labor; you'd be better off just making your own dataset and comparing it to our results.

eda
-------
Ipython notebooks doing some exploratory analysis on the manually corrected data, and producing figures that were used in the report.

makemaster
----------

Describes the process used to construct the largest dataset: volumemeta.tsv.

dedup
-----

Contains code documenting the deduplication process that moved us from the largest list (volumemeta) down to recordmeta and titlemeta.

manuallists
-----------

Documents the process that produced smaller, manually checked subsets (the manual_title_subset, gender_balanced_subset, and frequently_reprinted_subset).

get_EF
------

Code used to download extracted features, which were used as part of the dedup process, in order to decide when two volumes (or records) were so similar as to be probably "the same work." I have not stored the extracted-feature data itself in the repo; it comes to several gigabytes.


Other directories
=================

plans
-----
Early draft plans for this project.

missing
-------
Sketches toward a list of titles surprisingly missing in Hathi. May be out of date.

incopyrightpagepredicts
-----------------------
Page-level genre predictions for volumes after 1923. Before 1923, see [the Figshare repository.](https://figshare.com/articles/Page_Level_Genre_Metadata_for_English_Language_Volumes_in_HathiTrust_1700_1922/1279201)

Note that I am not aggressively publicizing page-level data, because I don't yet have any way to ensure that it reflects current page IDs for these volumes. HathiTrust doesn't yet have persistent page identifiers.
