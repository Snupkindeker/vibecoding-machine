import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

from ai.tools import get_datetime, run_code


def test_get_datetime_1():
    result = get_datetime("UTC")
    assert isinstance(result, dict)
    assert "datetime" in result
    assert "day_of_week" in result
    assert "day_of_year" in result
    assert "timezone" in result
    assert "utc_datetime" in result

def test_get_datetime_2():
    result = get_datetime("EST")
    assert isinstance(result, dict)
    assert result.get("timezone") == "EST"

def test_get_datetime_3():
    result = get_datetime("US/Eastern")
    assert isinstance(result, dict)
    assert result.get("timezone") == "US/Eastern"

def test_get_datetime_4():
    result = get_datetime("Asia/Tokyo")
    assert isinstance(result, dict)
    assert result.get("timezone") == "Asia/Tokyo"

def test_get_datetime_5():
    result = get_datetime("ezz")
    assert isinstance(result, str)
    assert "HTTP error" in result

def test_run_code_1():
    result = run_code("python", "print(input() * 5)", "hi ")
    assert result.get('status') == 200
    assert result.get('stdout') == "hi hi hi hi hi \n"
    assert result.get('stderr') is None

def test_run_code_2():
    result = run_code("python", "print(i)")
    assert result.get('status') == 200
    assert result.get('stdout') is None
    assert "NameError" in result.get('stderr', '')

def test_run_code_3():
    result = run_code("python", "print(input())")
    assert result.get('status') == 200
    assert result.get('stdout') is None
    assert "EOFError" in result.get('stderr', '')

def test_run_code_4():
    result = run_code("cpp", "#include <iostream>\nusing namespace std;\nint main() {\n  cout << 10;\n  return 0;\n}")
    assert result.get('status') == 200
    assert result.get('stdout') == "10"
    assert result.get('stderr') is None

def test_run_code_5():
    import pytest
    with pytest.raises(ValueError):
        run_code("1", "")