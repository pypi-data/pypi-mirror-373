from src.usdm4 import USDM4
from simple_error_log.errors import Errors
from tests.helpers.files import write_json_file, read_json_file

SAVE = False


def dump_validation_result(result):
    print(
        f"RESULT: {[v for k, v in result._items.items() if v['status'] not in ['Not Implemented', 'Success']]}"
    )


def test_validate(tmp_path):
    result = USDM4().validate("tests/test_files/test_validate.json")
    dump_validation_result(result)
    assert result.passed_or_not_implemented()


def test_validate_error():
    result = USDM4().validate("tests/test_files/test_validate_error.json")
    dump_validation_result(result)
    assert not result.passed_or_not_implemented()


def test_example_1():
    test_file = "tests/test_files/package/example_1.json"
    result = USDM4().validate(test_file)
    assert not result.passed_or_not_implemented()


def test_example_2():
    test_file = "tests/test_files/package/example_2.json"
    result = USDM4().validate(test_file)
    dump_validation_result(result)
    assert result.passed_or_not_implemented()


def test_minimum():
    errors = Errors()
    result = USDM4().minimum("Test Study", "SPONSOR-1234", "1", errors)
    result.study.id = "FAKE-UUID"
    if SAVE:
        write_json_file(None, "test_minimum_expected.json", result.to_json())
    expected = read_json_file(None, "test_minimum_expected.json")
    assert result.to_json() == expected
