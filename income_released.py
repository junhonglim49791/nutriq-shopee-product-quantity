from enum import Enum
from datetime import datetime
import calendar
import re

from print import (
    print_error_message_panel,
    print_income_released_date_range_error,
    print_income_released_format_info,
)


def is_month_split_in_halves(filename):
    dates_list = re.findall(r"\d{8}", filename)
    start_date, end_date = dates_list
    start_date_obj = datetime.strptime(start_date, "%Y%m%d")
    end_date_obj = datetime.strptime(end_date, "%Y%m%d")
    _, days_in_month = calendar.monthrange(start_date_obj.year, start_date_obj.month)
    same_month_year = (start_date_obj.month == end_date_obj.month) and (
        start_date_obj.year == end_date_obj.year
    )

    if not same_month_year:
        return False

    expected_month_halves = {"first_half": (1, 15), "second_half": (16, days_in_month)}
    given_month_halve = (start_date_obj.day, end_date_obj.day)

    for expected_range in expected_month_halves.values():
        if given_month_halve == expected_range:
            return True

    return False


def is_income_released_filename_correct(filename):
    income_released_filename_pattern = r"Income\.released\.my\.\d{8}_\d{8}\.xlsx"
    return re.match(income_released_filename_pattern, filename)


class IncomeReleasedFileErrorMessages(Enum):
    EMPTY_DIRECTORY = 1
    MORE_THAN_1FILE = 2
    WRONG_EXT = 3
    NOT_INCOME_RELEASED = 4
    INCOME_RELEASED_INCORRECT_RANGE = 5
    NOT_EXCEL = 6


def get_income_released_error_message(msg_type, current_file_extension=""):
    match msg_type:
        case IncomeReleasedFileErrorMessages.EMPTY_DIRECTORY:
            main_msg = (
                "Please upload [italic]ONE[/italic] shopee income released excel file."
            )
            subtext = "income_released folder is empty."
            print_error_message_panel(main_msg, subtext)
            print_income_released_format_info()

        case IncomeReleasedFileErrorMessages.WRONG_EXT:
            main_msg = (
                "Please make sure uploaded file is in [italic].xlsx[/italic] format."
            )
            subtext = f"Current file extension: {current_file_extension}"
            print_error_message_panel(main_msg, subtext)
            print_income_released_format_info()

        case IncomeReleasedFileErrorMessages.NOT_EXCEL:
            main_msg = "Please make sure to upload an [italic]uncorrupted or valid[/italic] excel file."
            print_error_message_panel(main_msg)

        case IncomeReleasedFileErrorMessages.MORE_THAN_1FILE:
            main_msg = "Please make sure only [italic]ONE[/italic] file is in the [italic]income_released[/italic] folder."
            subtext = "Multiple files detected"
            print_error_message_panel(main_msg, subtext)

        case IncomeReleasedFileErrorMessages.NOT_INCOME_RELEASED:
            main_msg = (
                "This excel file is [italic]NOT[/italic] the shopee income excel file."
            )
            subtext = "Please upload the correct file."
            print_error_message_panel(main_msg, subtext)
            print_income_released_format_info()

        case IncomeReleasedFileErrorMessages.INCOME_RELEASED_INCORRECT_RANGE:
            main_msg = "Please correct the [italic]range[/italic]."
            subtext = "Make sure the dates is within same year and month."
            print_error_message_panel(main_msg, subtext)
            print_income_released_date_range_error()
