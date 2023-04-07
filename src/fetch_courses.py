from typing import Dict, List, Tuple
import requests
import re
import argparse
import multiprocessing.pool

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
    print(len(course_dtos), "courses found in total for term", term_id)
    return course_dtos

def fetch_course_dto_batch(skip_filter):
    skip, filter = skip_filter
    url = "https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses?%s$orderBy=title=ascnf&$skip=%d&$top=100"
    response = requests.get(url % (filter, skip), headers={"Accept": "application/json"}).json()
    return [resource_json["content"]["cpCourseDto"] for resource_json in response["resource"]]


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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="fetch_courses.py [-h] --termid TERMID\n\nPlease provide the term id: winter 2022/23 is 197, summer 2023 is 198, winter 2023/24 is 199, etc.")
    parser.add_argument('--termid', required=True, type=int, help="The term id (winter 2022/23 is 197, summer 2023 is 198, etc.)")
    args = parser.parse_args()

    if args.termid % 2 == 0:
        print(f"Term ID {args.termid}: Summer term {int(1924 + args.termid/2)}")
    else:
        print(f"Term ID {args.termid}: Winter term {int(1924 + args.termid/2)}/{int(1924 + args.termid/2)+1}")

    print("Searching for courses associated with Master informatics curriculum...")
    courses = fetch_course_dtos(term_id=args.termid, only_master_informatics=True)
    course_INs_names = extract_course_INs_names(courses)

    course_INs_names = sorted(course_INs_names, key=lambda c: c[1])

    print("VO/VI courses associated with Master informatics curriculum:")
    print()
    for (_, IN) in course_INs_names:
        print(IN)
    for (name, _) in course_INs_names:
        print(name)


    print()
    print("##############################################################################")
    print()
    print("Searching for other courses with IN number...")
    courses_all = fetch_course_dtos(term_id=args.termid, only_master_informatics=False)
    course_INs_names_all = extract_course_INs_names(courses_all)

    course_INs_names_all = set(course_INs_names_all) - set(course_INs_names)

    course_INs_names_all = sorted(course_INs_names_all, key=lambda c: c[1])
    

    print("VO/VI courses with IN number *not* associated with Master informatics curriculum, according to TUM online:")
    for (_, IN) in course_INs_names_all:
        print(IN)
    for (name, _) in course_INs_names_all:
        print(name)