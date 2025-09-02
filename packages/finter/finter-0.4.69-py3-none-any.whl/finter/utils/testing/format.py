from datetime import datetime


def is_valid_date_string(date_string, date_format='%Y%m%d%H%M%S'):
    try:
        datetime.strptime(date_string, date_format)
        return True  # 변환 성공, 포맷에 맞음
    except ValueError:
        return False  # 변환 실패, 포맷에 맞지 않음

