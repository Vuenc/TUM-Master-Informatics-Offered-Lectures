def term_id_to_name(term_id):
    if term_id in [201, 202]:
        raise Exception(f"Invalid term ID {term_id}: for unknown reasons, TUM online marks summer 2024 as term 200, winter 2024/25 as term 203, and skips 201 and 202.")
    if term_id > 202:
        # Account for TUM online skipping 201, 202
        term_id -= 2

    assert(term_id >= 152 and term_id <= 350)
    return f"{'SS' if term_id % 2 == 0 else 'WS'}{str(23 + int((term_id - 198 - (term_id % 2))/2)).zfill(2)}{'/' + str(23 + int((term_id - 198 + 1)/2)).zfill(2) if term_id % 2 == 1 else ''}"
