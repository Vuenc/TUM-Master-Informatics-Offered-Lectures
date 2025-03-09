# TUM Master Informatics, DEA: Offered Lectures

This document aims to provide a **list of elective lectures** that are being offered this semester for the Informatics and DEA masters at TUM, grouped by area of specialization:

- **Informatics master**:
  - List of courses [offered in summer semester 2025](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/informatics-ss25.html)
  - [List of all courses and when last offered](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/informatics-all.html)
- **DEA master**:
  - List of **elective** courses [offered in summer semester 2025](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/dea-ss25.html)
  - [List of all courses and when last offered](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/dea-all.html)

_This list is not official, might be incomplete or have errors. Use with care!_

I created the list by scraping data from the TUM online curriculum tree view (all lectures sorted by area) and merging it with the data from the TUM online courses tabs, which gives me the currently offered lectures.

<a href='https://ko-fi.com/K3K6135GAH' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

**If you want a similar list for other study programs, I'm happy to collaborate! Just open an issue and we can have a look. The scripts should be easy to generalize to other study programs.**

# Contributing

If you find a mistake, like a lecture missing, you can create an issue.

If you find the list is out of date because some information changed in TUM online, you can recreate the table by running the scripts:

1. Create a `src/.env` file with your TUM online credentials: This is needed to fetch an English-language curriculum table. You also should set your language to English in TUM online. If you are not logged in, TUM online will display the German version of the curriculum only.

```
TUMONLINE_USERNAME="yourusername"
TUMONLINE_PASSWORD="yourpassword"
```

2. Create a virtual environment and install the required packages:

```sh
virtualenv .fetchcourses-env
source .fetchcourses-env/bin/activate
pip install -r requirements.txt
```

3. Regenerate all tables using the provided script: This takes a couple of minutes and regenerates the tables for all curriculums. If the semester has changed, you need to update the TERMID and TERMNAME variables in the script. (TUM online identifies semesters by term ids: for example, 199 is winter term 2023/24, 200 is summer term 2024. For reasons unknown to me, term ids 201 and 202 are skipped, and winter term 2024/25 has term id 203.)

```sh
cd src/
sh regenerate-all.sh
```

4. (alternatively:) Regenerate individual curriculum tables manually.

- Fetch the offered courses from TUM online (update the --termid argument accordingly).

```sh
cd src/
python fetch_offered_courses.py --termid 203 --oldtermsfrom 171
```

- Fetch the curriculum tree data (update the --curriculum argument accordingly, see `src/curriculums.py` for the supported options.)

```sh
python fetch_curriculum_tree.py --curriculum master-informatics
```

- Generate the HTML file with the table (update the --curriculum, --termid and --output arguments accordingly)

```sh
python print_html_table.py --termid 203 --curriculum master-informatics --output "../informatics-ws24-25.html"
python print_html_table.py --termid 203 --curriculum master-informatics --oldtermsfrom 171 --output ../informatics-all.html
```
