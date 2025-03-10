import argparse
import json
from typing import Dict, List
import fetch_offered_courses
import pickle
import pandas as pd
import regex
import multiprocessing
import numpy as np
from types import SimpleNamespace
from curriculums import curriculums
import util

COURSE_CODE_REGEX = regex.compile("\\[([A-Z]+\\d+)\\]")

THEORY_NODE_NAMES = ["Theorie", "Theory"]

# REGISTRATION_BASE_URL = "https://campus.tum.de/tumonline/ee/rest/pages/slc.tm.cp/course-registration/" 
COURSE_DETAILS_BASE_URL = "https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/#/slc.tm.cp/student/courses/"

STYLE = """
<style>
    .main-container {
        width: 95%;
        display: inline-grid;
        justify-items: center;
        font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol";
    }
    @media (min-width: 1150px) {
        .main-container {
            width: 50%;
        }
    }
    table {
        table-layout: fixed;
        width: 100%;
        word-wrap: break-word;
        border: 0px;
        font-family: "Arial";
        font-size: 0.92rem;
        line-height: 1.3rem;
    }
    td, th {
        border: 0px;
    }
    td {
      padding-top: 0.7rem;
      padding-bottom: 0.7rem;
    }
    th {
        text-align: left;
    }
    .titleheader {
        width: 60%;
    }
    body {
        width: 100%;
        margin: 0px;
        display: inline-grid;
        justify-items: center;
        font-size: 1rem;
    }
    tbody tr:nth-child(odd) {
      background-color: #f6f6f6;
    }
    @media (min-resolution: 150dpi) {
      body {
        font-size: 1.7rem;
      }
      table {
        font-size: calc(1.9*0.92rem);
        line-height: calc(1.9*1.3rem);
      }
      .titleheader {
          width: 40%;
      }
    }
    @media (min-resolution: 300dpi) {
      body {
        font-size: 2rem;
      }
      table {
        font-size: calc(2.1*0.92rem);
        line-height: calc(2.1*1.3rem);
      }
      .titleheader {
          width: 40%;
      }
    }
    .tagIcon {
      cursor: default
    }
</style>
"""

HEADER = """
<div style="text-align: justify;">
<p>
    This is a list of elective modules grouped by area with availability data, which as far as I know is not provided by TUM elsewhere. I hope it will be helpful to you!
</p>
<p>
💎: Rare course (not offered in the last two semesters) <br>
🌟: New course (offered for the first time)
</p>

<p>
    <b>Disclaimer:</b> This site is non-official and automatically generated by fetching the data from the curriculum tree view and the data from the Courses tab in TUM online, and merging
    it based on the course identifiers. It can contain errors, for example if
</p>
<ul>
  <li>a course is missing the course identifier (INxxxx etc.) from its name</li>
  <li>a new course was not yet present in the tree view at the time this list was created</li>
</ul>
</div>
"""

GITHUB_LINK_AND_KOFI_BUTTON = """
<div style="width: 100%; margin-top: 10px; display: flex; align-items: center">
    <div style="display: flex; align-items: center; margin-right: 20px; padding-top: 3px;">
        <img src="github-mark.svg" style="height: 22px; aspect-ratio: 1/1; margin-right: 5px; padding-bottom: 4px">
        <a href="https://github.com/Vuenc/TUM-Master-Informatics-Offered-Lectures">
            This project on Github
        </a>
    </div>
    <script type='text/javascript' src='https://storage.ko-fi.com/cdn/widget/Widget_2.js'></script>
    <script type='text/javascript'>kofiwidget2.init('Buy me a Coffee', '#29abe0', 'K3K6135GAH');kofiwidget2.draw();</script> 
</div>
"""

NEW_COURSE_TAG_HTML_FACTORY = lambda _: """<span title="New course: offered for the first time!" class="tagIcon">🌟</span>"""

RARE_COURSE_TAG_HTML_FACTORY = lambda tag_and_last_offered: f"""<span title="Rare course: last offered in {tag_and_last_offered['last_offered']}" class="tagIcon">💎</span>"""


TAG_FACTORIES = {
    "newCourse": NEW_COURSE_TAG_HTML_FACTORY,
    "rareCourse": RARE_COURSE_TAG_HTML_FACTORY,
}

def main():
    parser = argparse.ArgumentParser(usage=
    """
    print_html_table.py [-h] --termid TERMID --curriculum CURRICULUM --output PATH [--oldtermsfrom OLDTERMID]
    Please provide the term id: winter 2022/23 is 197, summer 2023 is 198, winter 2023/24 is 199, etc.
    Curriculum: valid options are `master-informatics', 'master-dea', 'master-informatics-fspo2023'
    """)
    parser.add_argument('--termid', required=True, type=int, help="The term id (winter 2022/23 is 197, summer 2023 is 198, etc.)")
    parser.add_argument("--curriculum", required=True, type=str, help="One of ['master-informatics', 'master-dea']")
    parser.add_argument("--output", required=True, type=str, help="Path where to write the output html")
    parser.add_argument("--oldtermsfrom", required=False, type=int, help="The term id starting at which old course availability data (last offered) should be fetched")
    args = parser.parse_args()

    curriculum = curriculums[args.curriculum]
    terms = [(term_id, util.term_id_to_name(term_id)) for term_id in range(args.oldtermsfrom if args.oldtermsfrom is not None else args.termid, args.termid+1) if term_id not in [201, 202]]
    terms_dict = {term_name: term_id for term_id, term_name in terms}
    terms_dict["?"] = 0 # sort "unknown" last
    include_last_offered = args.oldtermsfrom is not None

    title = f"{curriculum.heading} - offered in {terms[-1][1]}{(' and since ' + terms[0][1]) if include_last_offered else ''}"
    print(f"""Creating table "{title}"...""")

    with open("../data/all_offered_courses.json") as f:
        available_courses_dtos = json.load(f)

    with open(args.output, "w") as file:
        file.write("<!DOCTYPE html><html lang='en'><body>")
        file.write("<div class=\"main-container\">")
        file.write(f"<h1>{title}</h1>")
        file.write(HEADER)
        file.write(GITHUB_LINK_AND_KOFI_BUTTON)
        with open(curriculum.tree_file, "r") as f:
            tree = json.load(f)
        for electives_area_node in tree["children"]:
            file.write(f"<h3>{electives_area_node['name']}</h3>")
            course_row_dicts = compute_course_row_dicts_recursively(electives_area_node, available_courses_dtos, include_non_offered=include_last_offered,
                                                                    current_term_id=args.termid, current_term_only=not include_last_offered)
            df = pd.DataFrame(data=course_row_dicts, columns=["ID", "Title", "Credits"]
                              + (["THEO"] if curriculum.use_theory_nodes else [])+ (["Last offered"] if include_last_offered else []))
            if include_last_offered:
                df = df.loc[np.argsort(-np.vectorize(lambda x: terms_dict[x])(df["Last offered"].to_numpy())), :]
            df["ID"] = df["ID"].apply(lambda course_code_and_tags: course_code_and_tags["course_code"] + "   "
                                      + " ".join(TAG_FACTORIES[tag["tag"]](tag) for tag in course_code_and_tags["tags"]))
            df["Title"] = df["Title"].apply(lambda title_and_url:f"<a href=\"{ title_and_url['url'] }\">{ title_and_url['title'] }</a>"
                                            if title_and_url['url'] is not None else title_and_url['title'])
            table_html = df.to_html(index=False, escape=False)
            table_html = table_html.replace("<th>Title</th>", "<th class='titleheader'>Title</th>")
            file.write(table_html)
        file.write("</div>")
        file.write("</body>")
        file.write(STYLE)
        file.write("</html>")
    print("Wrote table to file", args.output)

def compute_course_row_dicts_recursively(subtree: Dict, available_courses_dtos: List[Dict], include_non_offered: bool, current_term_id: int,
                                         current_term_only: bool, is_theory_node=False) -> List[Dict]:
    course_row_dicts = []
    course_code_match = COURSE_CODE_REGEX.match(subtree["name"])
    if course_code_match is not None:
        course_code = course_code_match.groups()[0]
        matching_dtos = sorted([dto for dto in available_courses_dtos if course_code in dto["title"]],
                key=lambda dto: (int(dto["semesterDto"]["id"]), 1 if dto["courseTypeDto"]["key"] in ["VO", "VI"] else 0),
                reverse=True)
        most_recent_offered_course_dto = next(iter(matching_dtos), None)
        semesters_offered = set(dto["semesterDto"]["id"] for dto in matching_dtos)
        if (most_recent_offered_course_dto is not None or include_non_offered) and (current_term_id in semesters_offered or not current_term_only):
            if most_recent_offered_course_dto is not None:
                base_title = most_recent_offered_course_dto["title"]
                register_url = f"{COURSE_DETAILS_BASE_URL}{most_recent_offered_course_dto['id']}"
                last_offered = most_recent_offered_course_dto["termName"]
            else:
                base_title = subtree["name"]
                register_url = None
                last_offered = "?"

            tags = []
            if len(semesters_offered) == 1 and current_term_id in semesters_offered:
                tags.append(dict(tag="newCourse"))
            if (len(semesters_offered) > 1 and current_term_id in semesters_offered
                and ((t:=current_term_id-1)-(2 if t in [201, 202] else 0)) not in semesters_offered and ((t:=current_term_id-2)-(2 if t in [201, 202] else 0)) not in semesters_offered):
                tags.append(dict(tag="rareCourse", last_offered=util.term_id_to_name(max(term_id for term_id in semesters_offered if term_id != current_term_id))))

            title = regex.sub(f"[\\(\\[]{regex.escape(course_code)}[\\)\\]]", "", base_title).strip()
            course_row_dicts.append({
                "Title": dict(title=title, url=register_url),
                "ID": dict(course_code=course_code, tags=tags),
                "Credits": subtree["credits"],
                "Last offered": last_offered,
                "THEO": "THEO" if is_theory_node else "",
            })
    else:
        for child in subtree["children"]:
            course_row_dicts.extend(compute_course_row_dicts_recursively(child, available_courses_dtos, include_non_offered, current_term_id, current_term_only,
                                                                         is_theory_node or subtree["name"] in THEORY_NODE_NAMES))
    return course_row_dicts

if __name__ == "__main__":
    main()
