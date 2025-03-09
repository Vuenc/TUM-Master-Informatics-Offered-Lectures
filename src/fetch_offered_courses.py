import json
from typing import Dict, List, Tuple
import requests
import re
import argparse
import multiprocessing.pool
import os

import tqdm.contrib.concurrent
import util

def fetch_course_dtos(term_id, only_master_informatics=False) -> List[Dict]:
    # termId = "196" # SS 2022
    only_master_informatics_filter = "curriculumVersionId-eq=4731;" if only_master_informatics else ""
    term_id_filter = f"termId-eq={term_id};"
    filter = f"$filter={only_master_informatics_filter}{term_id_filter}&"
    url = "https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses?%s$orderBy=title=ascnf&$skip=%d&$top=100"
    total_count = None
    course_dtos = []
    pbar = None
    pool = multiprocessing.pool.ThreadPool()
    batch_range = range(0, 10000, 100)
    course_dtos = sum(pool.map(fetch_course_dto_batch, zip(batch_range, [filter] * len(batch_range))), [])
    # while total_count is None or len(course_dtos) < total_count:
    #     response = requests.get(url % (filter, len(course_dtos)), headers={"Accept": "application/json"}).json()
    #     old_total_count, total_count = total_count, response["totalCount"]
    #     if old_total_count is None:
    #         pbar = tqdm.tqdm(total=total_count, leave=False)
    #     course_dtos += [resource_json["content"]["cpCourseDto"] for resource_json in response["resource"]]
    #     if pbar is not None:
    #         pbar.update(len(course_dtos) - pbar.n)
    # if pbar is not None:
    #     pbar.close()
    print(len(course_dtos), "courses found in total for", util.term_id_to_name(term_id))
    return course_dtos

def fetch_course_dto_batch(skip_and_filter):
    skip, filter = skip_and_filter
    url = "https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses?%s$orderBy=title=ascnf&$skip=%d&$top=100"
    response = requests.get(url % (filter, skip), headers={"Accept": "application/json"}).json()
    return response["courses"]


allowed_course_types = ["VI", "VO"]

def extract_course_INs_names(courses_dtos: List[Dict], enforce_IN=True) -> List[Tuple[str, str]]:
    in_regex = re.compile(r"IN\d\d\d\d")
    useless_characters_regex = re.compile(r"(\s*\(,?\s*|\s*\)\s*|^\s+|\s+$)")
    courses = []
    for course_dto in courses_dtos:
        if course_dto["courseTypeDto"]["key"] not in allowed_course_types:
            continue
        title = next((t["value"] for t in course_dto["courseTitle"]["translations"]["translation"] if t["lang"] == "en" and "value" in t), course_dto["courseTitle"]["value"])
        
        IN_numbers = in_regex.findall(title)
        if len(IN_numbers) > 0 or not enforce_IN:
            course_name = useless_characters_regex.sub("", in_regex.sub("", title))
            for IN_number in IN_numbers:
                courses.append((course_name, IN_number))
    return courses

def fetch_courses_for_term(term_id_and_name):
    term_id, term_name = term_id_and_name
    term_course_dtos = fetch_course_dtos(term_id=term_id, only_master_informatics=False)
    for course_dto in term_course_dtos:
        course_dto["termName"] = term_name
        course_dto["title"] = next((t["value"] for t in course_dto["courseTitle"]["translations"]["translation"] if t["lang"] == "en" and "value" in t), course_dto["courseTitle"]["value"])
    return term_course_dtos

def clean_dto(dto, fields):
    out = {}
    for field, field_selector in fields.items():
        if isinstance(field_selector, dict):
            out[field] = clean_dto(dto[field], field_selector)
        else:
            out[field] = dto[field]
    return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="""
        fetch_offered_courses.py [-h] --termid TERMID [--oldtermsfrom OLDTERMSFROMID] [--jsonpath JSONPATH]
        
        Please provide the term id: winter 2023/24 is 199, summer 2024 is 200, winter 2024/25 is 203 (!), etc.
        """)
    parser.add_argument('--termid', required=True, type=int, help="The term id (winter 2023/24 is 199, summer 2024 is 200, winter 2024/25 is 203 (!), etc)")
    parser.add_argument('--oldtermsfrom', required=False, type=int, help="The first included term when fetching courses for a range of terms (in this case, --termid specifies the last one)")
    parser.add_argument('--jsonpath', required=False, type=str, default="../data/all_offered_courses.json", help="Path where the json file with all courses is stored. If it exists, courses for old terms are fetched from there instead of being downloaded. Default: '../data/all_offered_courses.json'")
    args = parser.parse_args()

    existing_data = []
    existing_terms = []
    if os.path.isfile(args.jsonpath):
        with open(args.jsonpath) as f:
            existing_data = json.load(f)
            # Remove existing entries for current semester: this should always be fetched (this is likely to have changed)
            existing_data = [dto for dto in existing_data if dto["semesterDto"]["id"] != args.termid]
        existing_terms = list(set(dto["semesterDto"]["id"] for dto in existing_data).difference({args.termid}))
        print(f"Found data for old terms in '{args.jsonpath}'. This data is not downloaded again.")
        print(f"Old terms found: {', '.join(util.term_id_to_name(term_id) for term_id in sorted(existing_terms))}" )

    terms = [(term_id, util.term_id_to_name(term_id))
             for term_id in range(args.oldtermsfrom if args.oldtermsfrom is not None else args.termid, args.termid+1)
             if term_id not in [201, 202]
             and term_id not in existing_terms
    ]

    print(f"Fetching offered courses from {terms[0][1]} to {terms[-1][1]}")
    # all offered courses are stored from newest to oldest
    available_courses_dtos = sum(
        tqdm.contrib.concurrent.thread_map(
            # Enable parallelism by setting max_workers > 1 (e.g. `len(terms)`). Warning: might be too many HTTP requests to handle.
            fetch_courses_for_term, reversed(terms), max_workers=1 # len(terms)
        ),
        []
    )

    # Clean the retrieved DTOs (removed unneeded fields) to save some space and json parsing time
    field_selector = {"courseTypeDto": {"key": True}, "termName": True, "semesterDto": {"id": True}, "title": True, "id": True,}
    available_courses_dtos = list(map(lambda d: clean_dto(d, field_selector), available_courses_dtos))

    with open(args.jsonpath, "w") as f:
        # Sort data, and save it with indent=0 which will add newlines (more diff-friendly)
        saved_data = sorted(existing_data + available_courses_dtos, key=lambda dto: (dto["semesterDto"]["id"], "id"))
        json.dump(saved_data, f, indent=0)

    print(f"Results written to JSON file '{args.jsonpath}'")
