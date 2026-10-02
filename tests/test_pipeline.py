from backend.pipeline import Pipeline,PART_NAMES

def test_pipeline_has_32_parts_and_advanced_gate():
    assert len(PART_NAMES)==32
    r=Pipeline(advanced=False).run({'data_quality':'OK'})
    assert len(r)==32
    assert r[14]['skipped'] is True

def test_data_gap_is_visible_through_pipeline():
    r=Pipeline().run({'data_quality':'DATA_GAP'})
    assert any(x['data_gap'] for x in r[1:])
