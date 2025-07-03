import json
from typing import Dict, List, Tuple
import curriculums
import argparse
import os

import util

import aiohttp
import asyncio
import fetch_course_details

allowed_course_types = ["VI", "VO"]

async def fetch_course_dtos(term_id, curriculum_version_id, allowed_course_types) -> List[Dict]:
    # term_id = "196" # SS 2022
    only_master_informatics_filter = f"curriculumVersionId-eq={curriculum_version_id};"
    term_id_filter = f"termId-eq={term_id};"
    filter = f"$filter={only_master_informatics_filter}{term_id_filter}&"

    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*[
            session.get(f"https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses?{filter}$orderBy=title=ascnf&$skip={pagination_skip}&$top=100", headers={"Accept": "application/json"})
            for pagination_skip in range(0, 10000, 100)
        ])
        course_dto_pages = await asyncio.gather(*[
            response.json() for response in responses
        ])
        course_dtos = [course_dto for page in course_dto_pages for course_dto in page["courses"] if course_dto["courseTypeDto"]["key"] in allowed_course_types]

    return course_dtos

def clean_dto(dto, fields):
    out = {}
    for field, field_selector in fields.items():
        if isinstance(field_selector, dict):
            out[field] = clean_dto(dto[field], field_selector)
        else:
            out[field] = dto[field]
    return out


# What this file should do (after refactor):
# - read in course "database" (i.e. all_offered_courses JSON file; or maybe we want an actual database?)
#   - the "database" should contain: an entry for each course offered since 200x; its ID; the "equivalence class ID", let's define it as the ID of the oldest equivalent course
# - download all offered courses for the selected curriculum in the current semester (and the old semesters, if they don't exist yet)
# - for each new course, download the curriculum position data (-> fetch_course_details)
# - for each new course, compute its association ID
#   - if fetching non-current semester courses, be smart about that: fetch course details of the newest course, associate all returned courses to the association ID;
#     go through semesters backwards and only fetch details for non-associated courses. Store curriculum information per association ID.
# (should there be an extra DB per curriculum?)


async def main():
    parser = argparse.ArgumentParser(
        usage="""
        fetch_offered_courses.py [-h] --termid TERMID [--oldtermsfrom OLDTERMSFROMID] [--jsonpath JSONPATH]
        
        Please provide the term id: winter 2023/24 is 199, summer 2024 is 200, winter 2024/25 is 203 (!), etc.
        """)

    parser.add_argument("--curriculum", required=True, type=str, help="One of ['master-informatics', 'master-dea']")
    parser.add_argument('--termid', required=True, type=int, help="The term id (winter 2023/24 is 199, summer 2024 is 200, winter 2024/25 is 203 (!), etc)")
    parser.add_argument('--oldtermsfrom', required=False, type=int, help="The first included term when fetching courses for a range of terms (in this case, --termid specifies the last one)")
    parser.add_argument('--jsonpath', required=False, type=str, default="../data/all_offered_courses.json", help="Path where the json file with all courses is stored. If it exists, courses for old terms are fetched from there instead of being downloaded. Default: '../data/all_offered_courses.json'")
    args = parser.parse_args()

    curriculum = curriculums.curriculums[args.curriculum]

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

    terms_to_fetch = [term_id
             for term_id in range(args.oldtermsfrom if args.oldtermsfrom is not None else args.termid, args.termid+1)
             if term_id not in [201, 202]
             and term_id not in existing_terms
    ]

    print(f"Fetching offered courses from {util.term_id_to_name(terms_to_fetch[0])} to {util.term_id_to_name(terms_to_fetch[-1])}")
    # Fetch all offered courses in the terms to fetch, from newest to oldest
    available_courses_dtos = []
    field_selector = {"courseTypeDto": {"key": True}, "termName": True, "semesterDto": {"id": True}, "title": True, "id": True,}
    for term_id in reversed(terms_to_fetch):
        term_course_dtos = await fetch_course_dtos(term_id, curriculum.curriculum_id, allowed_course_types)
        term_name = util.term_id_to_name(term_id)
        print(len(term_course_dtos), "courses found in total for", term_name)
        for course_dto in term_course_dtos:
            course_dto["termName"] = term_name
            course_dto["title"] = next((t["value"] for t in course_dto["courseTitle"]["translations"]["translation"] if t["lang"] == "en" and "value" in t), course_dto["courseTitle"]["value"])
            # Clean the retrieved DTOs (remove unneeded fields) to save a significant amount of space and json parsing time
        term_course_dtos = [clean_dto(course_dto, field_selector) for course_dto in term_course_dtos]
        available_courses_dtos.extend(term_course_dtos)


    async with aiohttp.ClientSession() as session:
        curriculum_paths = await asyncio.gather(
            *[fetch_course_details.fetch_curriculum_paths(session, course_dto["id"], curriculum.curriculum_id)
              for course_dto in available_courses_dtos])
        for course_dto, curriculum_paths in zip(available_courses_dtos, curriculum_paths):
            course_dto["curriculumPaths"] = curriculum_paths
            
        

    with open(args.jsonpath, "w") as f:
        # Sort data, and save it with indent=0 which will add newlines (more diff-friendly)
        saved_data = sorted(existing_data + available_courses_dtos, key=lambda dto: (dto["semesterDto"]["id"], "id"))
        json.dump(saved_data, f, indent=0)

    print(f"Results written to JSON file '{args.jsonpath}'")


if __name__ == "__main__":
    asyncio.run(main())