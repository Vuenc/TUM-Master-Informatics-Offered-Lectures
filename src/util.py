def term_id_to_name(term_id):
    assert(term_id >= 152 and term_id <= 350)
    return f"{'SS' if term_id % 2 == 0 else 'WS'}{str(23 + int((term_id - 198 - (term_id % 2))/2)).zfill(2)}{'/' + str(23 + int((term_id - 198 + 1)/2)).zfill(2) if term_id % 2 == 1 else ''}"
