from enum import Enum
from datetime import datetime
import calendar
import re
import os

from print import (
    print_error_message_panel,
    print_income_released_date_range_error,
    print_income_released_format_info,
)


def get_all_files_in_a_dir(dir):
    all_files_order_completed_folder = [
        file for file in os.listdir(dir) if os.path.isfile(os.path.join(dir, file))
    ]
    return all_files_order_completed_folder


def is_dir_empty(path):
    return os.path.isdir(path) and len(os.listdir(path)) == 0


# Use excel's binary to check whether a file is in .xlsx format
def is_excel(path):
    with open(path, "rb") as f:
        first_n_bytes = 4
        excel_bytes = b"PK\x03\x04"
        file_sig = f.read(first_n_bytes)
        return file_sig == excel_bytes


# Expected the Income.released file should be within 15 days range of a month
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
    # the date range should be something like: 20250101_20250115 or 20250116_20250131
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
    NOT_EXCEL = 3
    NOT_INCOME_RELEASED = 4
    INCOME_RELEASED_INCORRECT_RANGE = 5


def get_income_released_error_message(msg_type, current_file_extension=""):
    match msg_type:
        case IncomeReleasedFileErrorMessages.EMPTY_DIRECTORY:
            main_msg = (
                "Please upload [italic]ONE[/italic] shopee income released excel file."
            )
            subtext = "income_released folder is empty."
            print_error_message_panel(main_msg, subtext)
            print_income_released_format_info()

        case IncomeReleasedFileErrorMessages.NOT_EXCEL:
            main_msg = "Please make sure to upload an uncorrupted or valid excel file in [italic].xlsx[/italic] format."
            subtext = f"Current file extension: {current_file_extension}"
            print_error_message_panel(main_msg, subtext)
            print_income_released_format_info()

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


def income_released_file_checks(income_released_dir):
    if is_dir_empty(income_released_dir):
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.EMPTY_DIRECTORY
        )
        return (False,)

    all_files_income_released_folder = get_all_files_in_a_dir(income_released_dir)
    income_released_file = all_files_income_released_folder[0]
    income_released_filename, extension = os.path.splitext(income_released_file)
    income_released_file_path = os.path.join(income_released_dir, income_released_file)

    if len(all_files_income_released_folder) > 1:
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.MORE_THAN_1FILE
        )
        return (False,)

    if not is_excel(income_released_file_path):
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.NOT_EXCEL, extension
        )
        return (False,)

    if not is_income_released_filename_correct(income_released_file):
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.NOT_INCOME_RELEASED,
            # income_released_filename,
        )
        return (False,)

    # Evoice is done for every 2 weeks, so expecting the Income.released excel file also in the correct date range
    if not is_month_split_in_halves(income_released_filename):
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.INCOME_RELEASED_INCORRECT_RANGE
        )
        return (False,)

    return (
        True,
        {
            "all_files_income_released_folder": all_files_income_released_folder,
            "income_released_filename": income_released_filename,
            "income_released_file_path": income_released_file_path,
        },
    )
