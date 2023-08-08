# TUM Master Informatics, DEA: Offered Lectures
This document aims to provide a **list of elective lectures** that are being offered this semester for the Informatics and DEA masters at TUM, grouped by area of specialization:

- **Informatics master**:
    - List of courses [offered in summer semester 2023](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/old-semesters/informatics-ss23.html)/[Winter semester 2023/24 (preliminary)](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/informatics-ws23-24.html)
    - [List of all courses and when last offered in the last 5 years](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/informatics-all.html)
- **DEA master**:
    - List of courses [offered in summer semester 2023](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/old-semesters/dea-ss23.html)/[Winter semester 2023/24 (preliminary)](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/dea-ws23-24.html)
    - [List of all courses and when last offered in the last 5 years](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/dea-all.html)

*This list is not official, might be incomplete or have errors. Use with care!*

I created the list by scraping data from the TUM online curriculum tree view (all lectures sorted by area) and merging it with the data from the TUM online courses tabs, which gives me the currently offered lectures. 

# Contributing
If you find a mistake, like a lecture missing, you can create an issue.

If you find the list is out of date because some information changed in TUM online, you can recreate the table by running the scripts:

1. Create a `src/.env` file with your TUM online credentials: This is needed to fetch an English-language curriculum table.
```
TUMONLINE_USERNAME="yourusername"
TUMONLINE_PASSWORD="yourpassword"
```
2. Fetch data from the curriculum tree view by running `python fetch_tumonline_tree.py --curriculum master-informatics` (or `--master-dea`)
3. Regenerate HTML tables - e.g. for Informatics:
    - `python print_html_table.py --termid 198 --curriculum master-informatics --output ../informatics-ss23.html` for current semester table
    - `python print_html_table.py --termid 198 --curriculum master-informatics --oldtermsfrom 188 --output ../informatics-all.html` for last offered table
    - replace the term IDs: 198 is summer term 2023, 199 is winter term 2023/24, etc.
    
You can also regenerate all tables by running `sh src/regenerate-alls.sh`.

If you want a similar list for other study programs, I'm happy to collaborate! Just open an issue and we can have a look. The scripts should be easy to generalize to other programs.
