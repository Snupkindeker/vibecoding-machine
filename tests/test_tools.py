import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:
    sys.path.append(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)


from ai.tools import get_datetime, run_code, current_dir


def test_get_datetime_1():
    assert isinstance(result := get_datetime("UTC"), dict) and result.get("datetime") and result.get("day_of_week") and result.get("day_of_year") and result.get("timezone") and result.get("utc_datetime")

def test_get_datetime_2():
    assert isinstance(result := get_datetime("EST"), dict) and result.get("datetime") and result.get("day_of_week") and result.get("day_of_year")and result.get("timezone") and result.get("utc_datetime")

def test_get_datetime_3():
    assert isinstance(result := get_datetime("US/Eastern"), dict) and result.get("datetime") and result.get("day_of_week") and result.get("day_of_year")and result.get("timezone") and result.get("utc_datetime")

def test_get_datetime_4():
    assert isinstance(result := get_datetime("Asia/Tokyo"), dict) and result.get("datetime") and result.get("day_of_week") and result.get("day_of_year")and result.get("timezone") and result.get("utc_datetime")

def test_get_datetime_5():
    assert isinstance(result := get_datetime("ezz"), str) and result == "An HTTP error occurred while trying to handle the datetime get request."


def test_run_code_1():
    assert isinstance(result := run_code("python", "print(input() * 5)", "hi "), dict) and result.get('status') == 200 and result.get('stdout') == "hi hi hi hi hi \n" and result.get('stderr') is None

def test_run_code_2():
    assert isinstance(result := run_code("python", "print(i)"), dict) and result.get('status') == 200 and result.get('stdout') is None and "NameError" in result.get('stderr')

def test_run_code_3():
    assert isinstance(result := run_code("python", "print(input())"), dict) and result.get('status') == 200 and result.get('stdout') is None and "EOFError" in result.get('stderr')

def test_run_code_4():
    assert isinstance(result := run_code("cpp", "#include <iostream>\nusing namespace std;\nint main() {\n  cout << 10;\n  return 0;\n}"), dict) and result.get('status') == 200 and result.get('stdout') == "10" and result.get('stderr') is None

def test_run_code_5():
    try:
        run_code("1", "#include <error>")
        assert False
    except ValueError:
        assert True


if __name__ == "__main__":
    print(current_dir)
