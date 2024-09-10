# TUM Master Informatics, DEA: Offered Lectures

This document aims to provide a **list of elective lectures** that are being offered this semester for the Informatics and DEA masters at TUM, grouped by area of specialization:

- **Informatics master**:
  - List of courses [offered in winter semester 2024/25](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/informatics-ws24-25.html)
  - [List of all courses and when last offered](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/informatics-all.html)
- **DEA master**:
  - List of **elective** courses [offered in summer winter semester 2024/25](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/dea-ws24-25.html)
  - [List of all courses and when last offered](https://vuenc.github.io/TUM-Master-Informatics-Offered-Lectures/dea-all.html)

_This list is not official, might be incomplete or have errors. Use with care!_

I created the list by scraping data from the TUM online curriculum tree view (all lectures sorted by area) and merging it with the data from the TUM online courses tabs, which gives me the currently offered lectures.

<style>img.kofiimg{display: initial!important;vertical-align:middle;height:13px!important;width:20px!important;padding-top:0!important;padding-bottom:0!important;border:none;margin-top:0;margin-right:5px!important;margin-left:0!important;margin-bottom:3px!important;content:url('https://storage.ko-fi.com/cdn/cup-border.png')}.kofiimg:after{vertical-align:middle;height:25px;padding-top:0;padding-bottom:0;border:none;margin-top:0;margin-right:6px;margin-left:0;margin-bottom:4px!important;content:url('https://storage.ko-fi.com/cdn/whitelogo.svg')}.btn-container{display:inline-block!important;white-space:nowrap;min-width:160px}span.kofitext{color:#fff !important;letter-spacing: -0.15px!important;text-wrap:none;vertical-align:middle;line-height:33px !important;padding:0;text-align:center;text-decoration:none!important; text-shadow: 0 1px 1px rgba(34, 34, 34, 0.05);}.kofitext a{color:#fff !important;text-decoration:none:important;}.kofitext a:hover{color:#fff !important;text-decoration:none}a.kofi-button{box-shadow: 1px 1px 0px rgba(0, 0, 0, 0.2);line-height:36px!important;min-width:150px;display:inline-block!important;background-color:#29abe0;padding:2px 12px !important;text-align:center !important;border-radius:7px;color:#fff;cursor:pointer;overflow-wrap:break-word;vertical-align:middle;border:0 none #fff !important;font-family:'Quicksand',Helvetica,Century Gothic,sans-serif !important;text-decoration:none;text-shadow:none;font-weight:700!important;font-size:14px !important}a.kofi-button:visited{color:#fff !important;text-decoration:none !important}a.kofi-button:hover{opacity:.85;color:#f5f5f5 !important;text-decoration:none !important}a.kofi-button:active{color:#f5f5f5 !important;text-decoration:none !important}.kofitext img.kofiimg {height:15px!important;width:22px!important;display: initial;animation: kofi-wiggle 3s infinite;}@keyframes kofi-wiggle{0%{transform:rotate(0) scale(1)}60%{transform:rotate(0) scale(1)}75%{transform:rotate(0) scale(1.12)}80%{transform:rotate(0) scale(1.1)}84%{transform:rotate(-10deg) scale(1.1)}88%{transform:rotate(10deg) scale(1.1)}92%{transform:rotate(-10deg) scale(1.1)}96%{transform:rotate(10deg) scale(1.1)}100%{transform:rotate(0) scale(1)}}</style>
<link href="https://fonts.googleapis.com/css?family=Quicksand:400,700" rel="stylesheet" type="text/css">
<div class="btn-container"><a title="Support me on ko-fi.com" class="kofi-button" style="background-color:#29abe0;" href="https://ko-fi.com/K3K6135GAH" target="_blank"> <span class="kofitext"><img src="https://storage.ko-fi.com/cdn/cup-border.png" alt="Ko-fi donations" class="kofiimg">Buy me a Coffee</span></a></div>

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
   1. Fetch the offered courses from TUM online (update the --termid argument accordingly).

```sh
cd src/
python fetch_offered_courses.py --termid 203 --oldtermsfrom 171
```

    2. Fetch the curriculum tree data (update the --curriculum argument accordingly, see `src/curriculums.py` for the supported options.)

```sh
python fetch_curriculum_tree.py --curriculum master-informatics
```

    3. Generate the HTML file with the table (update the --curriculum, --termid and --output arguments accordingly)

```sh
python print_html_table.py --termid 203 --curriculum master-informatics --output "../informatics-ws24-25.html"
python print_html_table.py --termid 203 --curriculum master-informatics --oldtermsfrom 171 --output ../informatics-all.html
```

If you want a similar list for other study programs, I'm happy to collaborate! Just open an issue and we can have a look. The scripts should be easy to generalize to other study programs.
