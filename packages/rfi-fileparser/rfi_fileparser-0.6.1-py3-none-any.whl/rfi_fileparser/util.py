from datetime import datetime, timedelta

def is_valid_date(input_str):
    start_time = datetime.strptime("2022/01/01", "%Y/%m/%d")
    two_days_ago = datetime.now() - timedelta(days=2)
    end_time = two_days_ago.strftime("%Y/%m/%d")
    try:
        parsed_date = datetime.strptime(input_str, "%Y/%m/%d")
        # Check range
        if start_time <= parsed_date <= two_days_ago:
            return True
        else:
            print(f"Date '{input_str}' is outside the allowed range (2022/01/01 to {end_time}).")
            return False
    except ValueError:
        # Raised if format is wrong or date is invalid
        print(f"Invalid input: '{input_str}'. Please ensure the date is in the format yyyy/mm/dd.")
        return False


def is_valid_type(input_options):
    valid_keys = ['dashboard', 'jamming', 'spoofing']
    if input_options not in valid_keys:
        print(f"Invalid input: '{input_options}'. Valid options are: {', '.join(valid_keys)}")
        return False
    return True


def is_vaild_range(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
    end_date = datetime.strptime(end_date_str, "%Y/%m/%d")
    if start_date > end_date:
        print(f"Start date is after end date!")
        return False
    return True


def dates_in_between(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
    end_date = datetime.strptime(end_date_str, "%Y/%m/%d")
    all_dates = []
    while start_date <= end_date:
        all_dates.append(start_date.strftime("%Y/%m/%d"))
        start_date += timedelta(days=1)
    return all_dates