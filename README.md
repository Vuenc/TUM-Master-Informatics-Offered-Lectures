# TUM Informatics, DEA: Offered Lectures

This document aims to provide a **list of lectures** that are being offered this semester for the Informatics bachelor and master and DEA master at TUM, grouped by area of specialization:

- **Informatics bachelor**:
  - List of lectures [offered in winter semester 2025/26](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/bachelor-informatics-ws25-26.html)
  - [List of all courses and when last offered](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/bachelor-informatics-all.html)
- **Informatics master**:
  - List of lectures [offered in winter semester 2025/26](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/master-informatics-ws25-26.html)
  - [List of all courses and when last offered](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/master-informatics-all.html)
- **DEA master**:
  - List of lectures [offered in winter semester 2025/26](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/dea-ws25-26.html)
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
python update_course_database.py --termid 204 --oldtermsfrom 171 --curriculum master-informatics
```

- Fetch the curriculum tree data (update the --curriculum argument accordingly, see `src/curriculums.py` for the supported options.)

```sh
python fetch_curriculum_tree.py --parallel_drivers 5 --curriculum master-informatics
```

- Generate the HTML file with the table (update the --curriculum, --termid and --output arguments accordingly)

```sh
python print_html_table.py --termid 204 --curriculum master-informatics --output "../informatics-ss25.html"
python print_html_table.py --termid 204 --curriculum master-informatics --oldtermsfrom 171 --output ../informatics-all.html
```
