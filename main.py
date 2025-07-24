import os

import pandas as pd
from openpyxl import load_workbook

from income_released import (
    get_income_released_error_message,
    is_month_split_in_halves,
    is_income_released_filename_correct,
    IncomeReleasedFileErrorMessages,
)

from income_released_process import (
    get_processed_income_released_df,
    get_required_order_completed_filename,
    get_unique_year_month_list,
    get_income_released_order_ids,
)

from order import (
    is_order_completed_filename_correct,
    which_filename_is_correct,
    get_order_completed_error_message,
    show_more_than_required_files_number,
)

from order_process_for_product_qty import (
    get_order_completed_df,
    get_product_quantity,
    get_order_completed_format,
    save_product_quantity,
)

from print import print_uploaded_file


def is_dir_empty(path):
    return os.path.isdir(path) and len(os.listdir(path)) == 0


def get_all_files_in_a_dir(dir):
    all_files_order_completed_folder = [
        file for file in os.listdir(dir) if os.path.isfile(os.path.join(dir, file))
    ]
    return all_files_order_completed_folder


def is_excel(path):
    with open(path, "rb") as f:
        first_n_bytes = 4
        excel_bytes = b"PK\x03\x04"
        file_sig = f.read(first_n_bytes)
        return file_sig == excel_bytes


def main():

    income_released_dir = "income_released"

    if is_dir_empty(income_released_dir):
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.EMPTY_DIRECTORY
        )
        return

    all_files_income_released_folder = get_all_files_in_a_dir(income_released_dir)
    income_released_file = all_files_income_released_folder[0]
    income_released_filename, extension = os.path.splitext(income_released_file)
    income_released_file_path = os.path.join(income_released_dir, income_released_file)

    if len(all_files_income_released_folder) > 1:
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.MORE_THAN_1FILE
        )
        return

    if not income_released_file.endswith("xlsx"):
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.WRONG_EXT, extension
        )
        return

    if not is_excel(income_released_file_path):
        get_income_released_error_message(IncomeReleasedFileErrorMessages.NOT_EXCEL)
        return

    if not is_income_released_filename_correct(income_released_file):
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.NOT_INCOME_RELEASED,
            income_released_filename,
        )
        return

    if not is_month_split_in_halves(income_released_filename):
        get_income_released_error_message(
            IncomeReleasedFileErrorMessages.INCOME_RELEASED_INCORRECT_RANGE
        )

    # Correct income_released file is uploaded, start processing
    print_uploaded_file(all_files_income_released_folder)

    processed_income_released_df = get_processed_income_released_df(
        income_released_file_path
    )

    unique_year_month_list = get_unique_year_month_list(processed_income_released_df)

    required_completed_order_filenames = get_required_order_completed_filename(
        unique_year_month_list
    )
    # print(completed_order_filenames)

    order_completed_dir = "order_completed"
    all_files_order_completed_folder = get_all_files_in_a_dir(order_completed_dir)

    if len(all_files_order_completed_folder) > len(required_completed_order_filenames):
        show_more_than_required_files_number(len(required_completed_order_filenames))
        return

    if not is_order_completed_filename_correct(
        all_files_order_completed_folder, required_completed_order_filenames
    ):

        required_file_exists = which_filename_is_correct(
            all_files_order_completed_folder, required_completed_order_filenames
        )
        get_order_completed_error_message(required_file_exists)
        return

    # Correct order_completed file is uploaded, start processing
    print_uploaded_file(all_files_order_completed_folder)

    # Use the required completed order filenames to process, since it is sorted, to use the latest month as the base df
    completed_order_filepaths_list = [
        os.path.join(order_completed_dir, file)
        for file in all_files_order_completed_folder
    ]

    #  get income_released_order_ids
    income_released_order_ids = get_income_released_order_ids(
        processed_income_released_df
    )

    # print(list(income_released_order_ids))
    # print("2505065PU181Y4" in list(income_released_order_ids))

    processed_order_completed_df = get_order_completed_df(
        completed_order_filepaths_list, income_released_order_ids
    )
    # print(
    #     processed_order_completed_df[
    #         (processed_order_completed_df["SKU Reference No."] == "COLD_PACK_STRAP")
    #         & (processed_order_completed_df["Quantity"] == 2)
    #     ]
    # )

    # print(
    #     processed_order_completed_df[
    #         processed_order_completed_df["SKU Reference No."] == "NOVAMULTI_30"
    #     ]
    # )
    product_qty_df = get_product_quantity(processed_order_completed_df)

    any1_order_completed_filepath = completed_order_filepaths_list[0]

    order_completed_format_dict = get_order_completed_format(
        any1_order_completed_filepath
    )

    save_product_quantity(
        order_completed_format_dict, product_qty_df, income_released_filename
    )


if __name__ == "__main__":
    main()
