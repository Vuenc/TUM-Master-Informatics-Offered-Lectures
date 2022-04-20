from typing import Dict, List, Tuple
import requests
import re
import tqdm

def fetch_course_dtos(only_master_informatics=False) -> List[Dict]:
    # termId = "196" # SS 2022
    filter = "$filter=curriculumVersionId-eq=4731;&" if only_master_informatics else ""
    url = "https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses?%s$orderBy=title=ascnf&$skip=%d&$top=100"
    total_count = None
    course_dtos = []
    pbar = None
    while total_count is None or len(course_dtos) < total_count:
        response = requests.get(url % (filter, len(course_dtos)), headers={"Accept": "application/json"}).json()
        old_total_count, total_count = total_count, response["totalCount"]
        if old_total_count is None:
            pbar = tqdm.tqdm(total=total_count)
        course_dtos += [resource_json["content"]["cpCourseDto"] for resource_json in response["resource"]]
        if pbar is not None:
            pbar.update(len(course_dtos) - pbar.n)
    if pbar is not None:
        pbar.close()
    return course_dtos

allowed_course_types = ["VI", "VO"]

def extract_course_INs_names(courses_dtos: List[Dict], enforce_IN=True) -> List[Tuple[str, str]]:
    # course_regex = re.compile(r"(.*?)\s?.?(IN\d+)\s?(.*?)")
    in_regex = re.compile(r"IN\d\d\d\d")
    useless_characters_regex = re.compile(r"(\s*\(,?\s*|\s*\)\s*|^\s+|\s+$)")
    courses = []
    for course_dto in courses_dtos:
        if course_dto["courseTypeDto"]["key"] not in allowed_course_types:
            continue
        title = next((t["value"] for t in course_dto["courseTitle"]["translations"]["translation"] if t["lang"] == "en" and "value" in t), course_dto["courseTitle"]["value"])
        # print(title)
        IN_numbers = in_regex.findall(title)
        if len(IN_numbers) > 0 or not enforce_IN:
            course_name = useless_characters_regex.sub("", in_regex.sub("", title))
            courses.append((course_name, ", ".join(IN_numbers)))
    return courses

if __name__ == "__main__":
    courses = fetch_course_dtos(True)
    course_INs_names = extract_course_INs_names(courses)

    course_INs_names = sorted(course_INs_names, key=lambda c: c[1])

    print("VO/VI courses associated with Master informatics curriculum:")
    print()
    for (_, IN) in course_INs_names:
        print(IN)
    for (name, _) in course_INs_names:
        print(name)


    courses_all = fetch_course_dtos(False)
    course_INs_names_all = extract_course_INs_names(courses_all)

    course_INs_names_all = set(course_INs_names_all) - set(course_INs_names)

    course_INs_names_all = sorted(course_INs_names_all, key=lambda c: c[1])
    
    print()
    print("##############################################################################")
    print()

    print("VO/VI courses with IN number *not* associated with Master informatics curriculum, according to TUM online:")
    for (_, IN) in course_INs_names_all:
        print(IN)
    for (name, _) in course_INs_names_all:
        print(name)