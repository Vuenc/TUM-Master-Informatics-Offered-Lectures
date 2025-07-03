from dataclasses import dataclass
from typing import Dict

@dataclass
class Curriculum:
    use_theory_nodes: bool
    heading: str
    curriculum_id: int
    tree_url: str
    tree_file_path: str

curriculums: Dict[str, Curriculum] = {
    "master-informatics": Curriculum(
        use_theory_nodes=True,
        heading="Elective Modules in Master Informatics",
        curriculum_id=5217,
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=5217",
        tree_file_path="../data/curriculum_tree_informatics.json",
    ),
    "master-dea": Curriculum(
        use_theory_nodes=False,
        heading="Elective Modules in Master Data Engineering and Analytics",
        curriculum_id=4733,
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStStudiumNr=&pSJNr=1615&pStpStpNr=4733&pStartSemester=",
        tree_file_path="../data/curriculum_tree_dea.json",
    ),
    "master-mathematics": Curriculum(
        use_theory_nodes=False,
        heading="Elective Modules in Master Mathematics",
        curriculum_id=4852,
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=4852&pSjNr=1617",
        tree_file_path="../data/curriculum_tree_mathematics.json",
    )
}
