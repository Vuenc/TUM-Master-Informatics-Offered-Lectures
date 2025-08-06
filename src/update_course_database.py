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
    curriculum_filter = f"curriculumVersionId-eq={curriculum_version_id};"
    term_id_filter = f"termId-eq={term_id};"
    filter = f"$filter={curriculum_filter}{term_id_filter}&"

    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*[
            session.get(f"https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses?{filter}$orderBy=title=ascnf&$skip={pagination_skip}&$top=100", headers={"Accept": "application/json"})
            for pagination_skip in range(0, 1500, 100)
        ])
        course_dto_pages = await asyncio.gather(*[
            response.json() for response in responses
        ])
        if len(course_dto_pages[-1]["courses"]) > 0:
            print("Warning! Pagination limit of 1500 not sufficient, last page still contains courses")
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
        fetch_offered_courses.py [-h] --termid TERMID --jsonpath JSONPATH [--oldtermsfrom OLDTERMSFROMID] ]
        
        Please provide the term id: winter 2023/24 is 199, summer 2024 is 200, winter 2024/25 is 203 (!), etc.
        """)

    parser.add_argument("--curriculum", required=True, type=str, help="One of ['master-informatics', 'master-dea']")
    parser.add_argument('--termid', required=True, type=int, help="The term id (winter 2023/24 is 199, summer 2024 is 200, winter 2024/25 is 203 (!), etc)")
    parser.add_argument('--oldtermsfrom', required=False, type=int, help="The first included term when fetching courses for a range of terms (in this case, --termid specifies the last one)")
    args = parser.parse_args()

    curriculum = curriculums.curriculums[args.curriculum]

    existing_courses: List = []
    existing_terms = []
    if os.path.isfile(curriculum.all_offered_courses_path):
        with open(curriculum.all_offered_courses_path) as f:
            existing_data = json.load(f)
            # Remove existing entries for current semester: this should always be fetched (this is likely to have changed)
            existing_courses = [dto for dto in existing_data["courses"] if dto["semesterDto"]["id"] != args.termid]
        existing_terms = list(set(dto["semesterDto"]["id"] for dto in existing_data["courses"]).difference({args.termid}))
        print(f"Found data for old terms in '{curriculum.all_offered_courses_path}'. This data is not downloaded again.")
        print(f"Old terms found: {', '.join(util.term_id_to_name(term_id) for term_id in sorted(existing_terms))}" )

    terms_to_fetch = [term_id
             for term_id in range(args.oldtermsfrom if args.oldtermsfrom is not None else args.termid, args.termid+1)
             if term_id not in [201, 202]
             and term_id not in existing_terms
    ]

    print(f"Fetching offered courses from {util.term_id_to_name(terms_to_fetch[0])} to {util.term_id_to_name(terms_to_fetch[-1])}")
    # Fetch all offered courses in the terms to fetch, from newest to oldest
    available_courses_dtos_per_term = []
    field_selector = {"courseTypeDto": {"key": True}, "termName": True, "semesterDto": {"id": True}, "title": True, "id": True,}
    for term_id in reversed(terms_to_fetch):
        term_name = util.term_id_to_name(term_id)
        seen_course_ids = set()
        all_term_course_dtos = []
        for curriculum_id in curriculum.curriculum_ids:
            term_course_dtos = await fetch_course_dtos(term_id, curriculum_id, allowed_course_types)
            term_course_dtos = [course_dto for course_dto in term_course_dtos if str(course_dto["id"]) not in seen_course_ids]
            for course_dto in term_course_dtos:
                course_dto["termName"] = term_name
                course_dto["title"] = next((t["value"] for t in course_dto["courseTitle"]["translations"]["translation"] if t["lang"] == "en" and "value" in t), course_dto["courseTitle"]["value"])
                # Clean the retrieved DTOs (remove unneeded fields) to save a significant amount of space and json parsing time
            term_course_dtos = [clean_dto(course_dto, field_selector) for course_dto in term_course_dtos]
            seen_course_ids.update(str(course_dto["id"]) for course_dto in term_course_dtos)
            all_term_course_dtos.extend(term_course_dtos)
        print(len(all_term_course_dtos), "courses found in total for", term_name)
        available_courses_dtos_per_term.append(all_term_course_dtos)


    # Map course ids to the id of the ldest related course (which identifies the equivalence class)
    oldest_related_course_id_by_course_id = {}

    async with aiohttp.ClientSession() as session:
        # The available_courses_dtos are already sorted by term from newest to oldest.
        for available_courses_dtos_term, term_id  in zip(available_courses_dtos_per_term, reversed(terms_to_fetch)):
            print("Fetching related courses for", util.term_id_to_name(term_id))
            # Fetch details only for courses where no newer equivalent course was seen yet
            course_dtos_to_fetch_details_for = []
            for course_dto in available_courses_dtos_term:
                if (oldest_related_course_id := oldest_related_course_id_by_course_id.get(int(course_dto["id"]), None)) is not None:
                    course_dto["oldestRelatedCourseId"] = oldest_related_course_id
                else:
                    course_dtos_to_fetch_details_for.append(course_dto)

            # Asynchronously fetch the curriculum path and related courses for each of the courses
            (all_related_course_ids,) = await asyncio.gather(
                asyncio.gather(*[fetch_course_details.fetch_related_course_ids(session, course_dto["id"])
                    for course_dto in course_dtos_to_fetch_details_for]
            ))

            # Identify the oldest related course ID (equivalence class ID)
            for course_dto, related_course_ids in zip(course_dtos_to_fetch_details_for, all_related_course_ids):
                oldest_related_course_id = related_course_ids[-1] if len(related_course_ids) > 0 else int(course_dto["id"])
                course_dto["oldestRelatedCourseId"] = oldest_related_course_id
                for related_course_id in related_course_ids:
                    oldest_related_course_id_by_course_id[int(related_course_id)] = oldest_related_course_id

    with open(curriculum.all_offered_courses_path, "w") as f:
        # Sort data, and save it with indent=0 which will add newlines (more diff-friendly)
        courses_to_save = sorted(existing_courses + sum(reversed(available_courses_dtos_per_term), []), key=lambda dto: (int(dto["semesterDto"]["id"]), int(dto["id"]))) # type: ignore
        saved_data = {"courses": courses_to_save}
        json.dump(saved_data, f, indent=0)

    print(f"Results written to JSON file '{curriculum.all_offered_courses_path}'")


if __name__ == "__main__":
    asyncio.run(main())
