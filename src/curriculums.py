from types import SimpleNamespace

curriculums = {
    "master-informatics": SimpleNamespace(
        use_theory_nodes=True,
        tree_file="../data/curriculum_tree_informatics.obj",
        heading="Elective Modules in Master Informatics",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=4731",
    ),
    "master-informatics-fspo2023": SimpleNamespace(
        use_theory_nodes=True,
        tree_file="../data/curriculum_tree_informatics_fspo2023.obj",
        heading="Elective Modules in Master Informatics (FSPO 2023)",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=5217",
    ),
    "master-dea": SimpleNamespace(
        use_theory_nodes=False,
        tree_file="../data/curriculum_tree_dea.obj",
        heading="Elective Modules in Master Data Engineering and Analytics",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStStudiumNr=&pSJNr=1615&pStpStpNr=4733&pStartSemester=",
    ),
    "master-mathematics": SimpleNamespace(
        use_theory_nodes=False,
        tree_file="../data/curriculum_tree_math.obj",
        heading="Elective Modules in Master Mathematics",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=4852&pSjNr=1617",
    )
}
