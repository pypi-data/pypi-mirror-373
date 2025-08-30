import json
from pathlib import Path

import pytest

@pytest.mark.parametrize("test", pytest.parsing_tests, ids=lambda test: test.name)
def test_parse(test: Path):
    from libparse import LibertyParser
    ref = Path(str(test) + ".ref")
    print(ref)
    if not ref.is_file():
        with pytest.raises(RuntimeError):
            LibertyParser(open(test))
    else:
        ref_obj = json.load(open(ref, encoding="utf8"))
        parser = LibertyParser(open(test))
        dict = parser.ast.to_dict()
        assert ref_obj == dict, "parse result didn't match"
