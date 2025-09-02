import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


from lukhed_basic_utils.timeCommon import create_timestamp, get_date_tomorrow, get_date_yesterday

def test_create_time_stamp():
    print(create_timestamp())

def test_get_date_tomorrow():
    print(get_date_tomorrow())

def test_get_date_yesterday():
    print(get_date_yesterday(convert_to_string_format="%Y%m%d"))

if __name__ == '__main__':
    test_get_date_yesterday()