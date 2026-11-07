import json

import pytest
from clean import check, clean
from sharding import select_shard

INTENTS = {"alarm_set", "weather_query", "calendar_remove"}


def test_sharding_covers_every_line_once():
    lines = [str(i) for i in range(11)]
    parts = [select_shard(lines, i, 3) for i in range(3)]
    assert sorted(sum(parts, []), key=int) == lines
    assert parts[1] == ["1", "4", "7", "10"]


def test_sharding_bad_index():
    with pytest.raises(ValueError):
        select_shard(["a"], 2, 2)


def _rec(i, text, obj):
    return {"id": i, "text": text, "teacher_raw": obj if isinstance(obj, str) else json.dumps(obj)}


def test_check_reasons():
    ok = {"intent": "weather_query", "date": None, "time": None, "place": "london"}
    assert check(_rec("1", "weather in london", ok), INTENTS) is None
    assert check(_rec("1", "x", "not json"), INTENTS) == "a"
    assert check(_rec("1", "x", {"intent": "alarm_set"}), INTENTS) == "b"
    assert check(_rec("1", "x", {**ok, "intent": "bogus"}), INTENTS) == "c"
    assert check(_rec("1", "weather in paris", ok), INTENTS) == "d"   # 'london' not in command


def test_clean_counts_add_up_and_dedup_keeps_smallest_id():
    ok = {"intent": "weather_query", "date": None, "time": None, "place": None}
    recs = [_rec("C0003", "hello", ok), _rec("C0001", "hello", ok), _rec("C0002", "bye", "oops"),
            _rec("C0004", "other", ok)]
    kept, c = clean(recs, INTENTS)
    assert [r["id"] for r in kept] == ["C0001", "C0004"]
    assert c["duplicates"] == 1 and c["a_invalid_json"] == 1 and c["kept"] == 2
    assert c["input"] == 4
