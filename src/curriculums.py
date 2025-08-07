from dataclasses import dataclass
from typing import Any, Callable, Dict, List

@dataclass
class Curriculum:
    use_theory_nodes: bool
    heading: str
    curriculum_ids: List[str]
    tree_file_path: str
    all_offered_courses_path: str
    extract_area: Callable[[List[str]], str | None]
    extra_columns: Dict[str, Callable[[Any], str]]

def extract_area_informatics(curriculum_path: List[str]) -> str | None:
    if len(curriculum_path) >= 2 and curriculum_path[0] == "Elective Modules Informatics":
        return curriculum_path[1]
    return None

def extract_area_dea(curriculum_path: List[str]) -> str | None:
    if len(curriculum_path) >= 1 and curriculum_path[0] == "Required Modules Data Engineering and Analytics":
        return curriculum_path[0]
    if len(curriculum_path) >= 2 and curriculum_path[0] == "Elective Modules":
        return curriculum_path[1]
    return None

def extract_informatics_theo_column(course) -> str:
    return "THEO" if ("Theory" in course.curriculum_path or "Theorie" in course.curriculum_path) else ""

EXTRA_COLUMNS_INFORMATICS = {
    "THEO": extract_informatics_theo_column
}

curriculums: Dict[str, Curriculum] = {
    "master-informatics": Curriculum(
        use_theory_nodes=True,
        heading="Elective Modules in Master Informatics",
        all_offered_courses_path="../data/all_offered_courses_informatics.json",
        tree_file_path="../data/curriculum_tree_informatics.json",
        curriculum_ids = ["5217", "4731", "4594", "4271", "2612"],
        extract_area=extract_area_informatics,
        extra_columns=EXTRA_COLUMNS_INFORMATICS,
    ),
    "master-dea": Curriculum(
        use_theory_nodes=False,
        heading="Elective Modules in Master Data Engineering and Analytics",
        all_offered_courses_path="../data/all_offered_courses_dea.json",
        tree_file_path="../data/curriculum_tree_dea.json",
        curriculum_ids=["4733", "4567"],
        extract_area=extract_area_dea,
        extra_columns={},
    ),
    "master-mathematics": Curriculum(
        use_theory_nodes=False,
        heading="Elective Modules in Master Mathematics",
        all_offered_courses_path="../data/all_offered_courses_mathematics.json",
        tree_file_path="../data/curriculum_tree_mathematics.json",
        curriculum_ids=["5244", "4852", "4407"],
        extract_area=None,
        extra_columns={},
    )
}
