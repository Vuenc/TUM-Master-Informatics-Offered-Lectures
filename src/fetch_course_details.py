from dataclasses import dataclass
from typing import List

import aiohttp

@dataclass
class CourseIdWithSemesterId:
    course_id: int
    semester_id: int

async def fetch_related_course_ids(session: aiohttp.ClientSession, course_id) -> List[int]:
    response = await session.get(f"https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses/same-courses/{course_id}")
    responseJson = await response.json()
    return [int(course["id"]) for course in sorted(responseJson["courses"], key=lambda c: int(c["semesterDto"]["id"]), reverse=True)]
