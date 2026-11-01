from cemetery.epitaph import verify
def test_unknown_citation():
    out=verify("A claim [E1] and a fake [E99]",[{"id":"E1"}])
    assert out["unknown_citation_ids"]==["E99"]
