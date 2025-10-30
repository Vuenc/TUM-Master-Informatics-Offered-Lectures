
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import List

import jinja2

import util
from curriculums import curriculums

COURSE_CODE_REGEX = re.compile(r"\[([A-Z0-9_]+)\]")
COURSE_CODE_PARENTHESIS_REGEX = re.compile(r"\s*\((?:[A-Z]+[0-9]+(?:_[A-Z0-9])*|English)(?:, (?:[A-Z]+[0-9]+(?:_[A-Z0-9])*|English))*\)|\[(?:[A-Z]+[0-9]+(?:_[A-Z0-9])*|English)(?:, (?:[A-Z]+[0-9]+(?:_[A-Z0-9])*|English))*\]")

THEORY_NODE_NAMES = ["Theorie", "Theory"]

# REGISTRATION_BASE_URL = "https://campus.tum.de/tumonline/ee/rest/pages/slc.tm.cp/course-registration/" 
COURSE_DETAILS_BASE_URL = "https://campus.tum.de/tumonline/ee/ui/ca2/app/desktop/#/slc.tm.cp/student/courses/"

@dataclass
class Course:
    title: str
    url: str
    course_code: str
    term_id: int
    term_name: str
    credits: str
    equivalent_courses: List[Course]
    curriculum_path: List[str]

def main():
    parser = argparse.ArgumentParser(usage=
    """
    print_html_table.py [-h] --termid TERMID --curriculum CURRICULUM --output PATH [--oldtermsfrom OLDTERMID]
    Please provide the term id: winter 2022/23 is 197, summer 2023 is 198, winter 2023/24 is 199, etc.
    Curriculum: valid options are `master-informatics', 'master-dea'
    """)
    parser.add_argument('--termid', required=True, type=int, help="The term id (winter 2022/23 is 197, summer 2023 is 198, etc.)")
    parser.add_argument("--curriculum", required=True, type=str, help="One of ['master-informatics', 'master-dea']")
    parser.add_argument("--output", required=True, type=str, help="Path where to write the output html")
    parser.add_argument("--oldtermsfrom", required=False, type=int, help="The term id starting at which old course availability data (last offered) should be fetched")
    args = parser.parse_args()

    curriculum = curriculums[args.curriculum]

    with open(curriculum.all_offered_courses_path) as f:
        available_data = json.load(f)
        available_courses_dtos = available_data["courses"]
    with open(curriculum.tree_file_path) as f:
        curriculum_course_infos = json.load(f)
    curriculum_courses_by_url = {url[url.rfind("/"):]: course_info for course_info in curriculum_course_infos for url in course_info["urls"]}

    available_courses_dtos = sorted(available_courses_dtos, key=lambda course_dto: int(course_dto["semesterDto"]["id"]), reverse=True)
    courses_by_area = defaultdict(lambda: [])
    equivalent_courses_by_oldest_related_course_id = {}
    for course_dto in available_courses_dtos:
        is_in_term_range = int(course_dto["semesterDto"]["id"]) >= (args.oldtermsfrom or args.termid)
        url = f"{COURSE_DETAILS_BASE_URL}{course_dto["id"]}"
        equivalent_courses = equivalent_courses_by_oldest_related_course_id.get(int(course_dto["oldestRelatedCourseId"]), None)
        if equivalent_courses == []:
            continue
        
        area = None
        course_code = None
        credits = None
        curriculum_path = None
        if equivalent_courses is None:
            # This is the youngest of its equivalence class, and we should extract the area
            curriculum_course_info = curriculum_courses_by_url.get(url[url.rfind("/"):])
            if curriculum_course_info is None:
                print(f"Course {course_dto["title"]} ({util.term_id_to_name(course_dto["semesterDto"]["id"])}) belonging to URL {url} not found in curriculum!")
                equivalent_courses_by_oldest_related_course_id[int(course_dto["oldestRelatedCourseId"])] = []
                continue
            assert curriculum_course_info is not None
            curriculum_path = list(curriculum_course_info["rule_node_names_by_levels"].values())
            area = curriculum.extract_area(curriculum_path)
            if area is None:
                equivalent_courses_by_oldest_related_course_id[int(course_dto["oldestRelatedCourseId"])] = []
                continue
            course_code_match = COURSE_CODE_REGEX.match(curriculum_course_info["module_name"]) if curriculum_course_info is not None else None
            course_code = course_code_match.groups()[0] if course_code_match is not None else "?"
            credits = str(curriculum_course_info["num_credits"]) if curriculum_course_info is not None else "?"
        else:
            course_code = equivalent_courses[0].course_code
            credits = equivalent_courses[0].credits
            curriculum_path = equivalent_courses[0].curriculum_path
        course = Course(
            title=COURSE_CODE_PARENTHESIS_REGEX.sub("", course_dto["title"]),
            url=url,
            course_code=course_code,
            credits=credits,
            term_id = course_dto["semesterDto"]["id"],
            term_name=util.term_id_to_name(course_dto["semesterDto"]["id"]),
            equivalent_courses=[], # will be set later
            curriculum_path=curriculum_path,
        )
        if equivalent_courses is None:
            equivalent_courses = [course]
            equivalent_courses_by_oldest_related_course_id[int(course_dto["oldestRelatedCourseId"])] = equivalent_courses
            if is_in_term_range:
                courses_by_area[area].append(course)
        else:
            equivalent_courses.append(course)

        course.equivalent_courses = equivalent_courses

    terms = [(term_id, util.term_id_to_name(term_id)) for term_id in range(args.oldtermsfrom if args.oldtermsfrom is not None else args.termid, args.termid+1) if term_id not in [201, 202]]
    terms_dict = {term_name: term_id for term_id, term_name in terms}
    terms_dict["?"] = 0 # sort "unknown" last
    include_last_offered = args.oldtermsfrom is not None
    title = f"{curriculum.heading} - offered in {terms[-1][1]}{(' and in previous semesters') if include_last_offered else ''}"

    print(f"""\nCreating table "{title}"...""")


    curriculum_entry_paths = [list(curriculum_course_info["rule_node_names_by_levels"].values()) for curriculum_course_info in curriculum_course_infos]
    areas_according_to_curriculum_tree = list({area: 0 for path in curriculum_entry_paths if (area := curriculum.extract_area(path)) is not None})
    print("Areas:", areas_according_to_curriculum_tree)

    def is_rare_course(course: Course) -> bool:
        equivalent_courses = course.equivalent_courses
        return (
            len(equivalent_courses) > 1
            and equivalent_courses[0].term_id == args.termid
            and util.term_id_distance(equivalent_courses[0].term_id, equivalent_courses[1].term_id) > 2
        )
    
    def course_last_offered_in(course: Course) -> str:
        return util.term_id_to_name(course.equivalent_courses[1].term_id)

    jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader("../templates/"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    jinja_environment.filters = {
        **jinja_environment.filters,
        "is_rare_course": is_rare_course,
        "course_last_offered_in": course_last_offered_in
    }
    jinja_context = {
        "title": title,
        "with_rare_and_new_courses": args.oldtermsfrom is None,
        "courses_by_area": sorted(courses_by_area.items(), key=lambda area_and_val: areas_according_to_curriculum_tree.index(area_and_val[0])),
        "extra_column_keys": curriculum.extra_columns.keys(),
        "extra_column_extractors": curriculum.extra_columns.values(),
        "include_last_offered": include_last_offered,
    }
    template = jinja_environment.get_template("base.html")
    rendered = template.render(**jinja_context)
    
    with open(args.output, "w") as file:
        file.write(rendered)
    print("Wrote table to file", args.output)

if __name__ == "__main__":
    main()
