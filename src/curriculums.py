from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Curriculum:
    use_theory_nodes: bool
    heading: str
    curriculum_ids: List[str]
    tree_url: str
    tree_file_path: str
    all_offered_courses_path: str

curriculums: Dict[str, Curriculum] = {
    "master-informatics": Curriculum(
        use_theory_nodes=True,
        heading="Elective Modules in Master Informatics",
        all_offered_courses_path="../data/all_offered_courses_informatics.json",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=5217",
        tree_file_path="../data/curriculum_tree_informatics.json",
        curriculum_ids = ["5217", "4731", "4594", "4271", "2612"]
    ),
    "master-dea": Curriculum(
        use_theory_nodes=False,
        heading="Elective Modules in Master Data Engineering and Analytics",
        all_offered_courses_path="../data/all_offered_courses_dea.json",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStStudiumNr=&pSJNr=1615&pStpStpNr=4733&pStartSemester=",
        tree_file_path="../data/curriculum_tree_dea.json",
        curriculum_ids=["4733", "4567"],
    ),
    "master-mathematics": Curriculum(
        use_theory_nodes=False,
        heading="Elective Modules in Master Mathematics",
        all_offered_courses_path="../data/all_offered_courses_mathematics.json",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=4852&pSjNr=1617",
        tree_file_path="../data/curriculum_tree_mathematics.json",
        curriculum_ids=["5244", "4852", "4407"],
    )
}
