from typing import Literal, Tuple


def term_id_to_semester(term_id) -> Tuple[int, Literal["WS"] | Literal["SS"]]:
    if term_id in [201, 202]:
        raise Exception(f"Invalid term ID {term_id}: for unknown reasons, TUM online marks summer 2024 as term 200, winter 2024/25 as term 203, and skips 201 and 202.")
    if term_id > 202:
        # Account for TUM online skipping 201, 202
        term_id -= 2

    assert(term_id >= 152 and term_id <= 350)
    year = 2023 + int((term_id - 198 - (term_id % 2))/2) # the year the semester starts in
    summer_or_winter = 'SS' if term_id % 2 == 0 else 'WS'
    return year, summer_or_winter


def term_id_to_name(term_id):
    year, summer_or_winter = term_id_to_semester(term_id)
    assert year >= 2000 and year < 2099
    return f"{summer_or_winter}{str(year - 2000).zfill(2)}{'/' + str(year+1 - 2000).zfill(2) if summer_or_winter == "SS" else ''}"


def term_id_distance(term_id_1, term_id_2):
    if term_id_1 in [201, 202] or term_id_2 in [201, 202]: raise ValueError("Term IDs 201 and 202 are not used")
    distance = abs(term_id_1 - term_id_2) - (2 if max(term_id_1, term_id_2) > 202 and min(term_id_1, term_id_2) < 201 else 0)
    return distance


def term_id_to_curriculum_academic_year(term_id):
    """Convert term ID (TUM online JSON interface) -> academic year in curriculum tree view: the pSjNr (probably "Studienjahr-Nummer") parameter in the curriculum view URL"""
    # 1593 is Academic Year 2011/12, which contains winter 2011/12 and summer 2012
    # Each year adds +2 to the academic year counter
    year, semester = term_id_to_semester(term_id)
    year = year - 1 if semester == "SS" else year
    return 1593 + (year - 2011) * 2
