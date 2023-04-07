from types import SimpleNamespace

curriculums = {
    "master-informatics": SimpleNamespace(
        use_theory_nodes=True,
        tree_file="../data/tumonline_tree_informatics.obj",
        heading="Electives Modules in Master Informatics",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=4731",
    ),
    "master-dea": SimpleNamespace(
        use_theory_nodes=False,
        tree_file="../data/tumonline_tree_dea.obj",
        heading="Electives Modules in Master Data Engineering and Analytics",
        tree_url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStStudiumNr=&pSJNr=1615&pStpStpNr=4733&pStartSemester=",
    )
}
