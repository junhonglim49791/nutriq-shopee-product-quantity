import os
from threading import Event

from income_released_process import (
    get_processed_income_released_df,
    get_required_order_completed_filename,
    get_unique_year_month_list,
    get_income_released_order_ids,
)

from order import (
    order_completed_file_check,
)

from order_process_for_product_qty import (
    get_order_completed_df,
    get_product_quantity,
    get_order_completed_format,
    save_product_quantity,
)

from print import (
    print_uploaded_file,
    print_generated_product_qty_file,
    waiting_for_user,
)

from folder_observer import (
    start_income_released_folder_monitoring,
    start_order_completed_folder_monitoring,
    OrderCompletedFolderMonitorHandler,
)


from income_released import income_released_file_checks, get_all_files_in_a_dir


file_valid_event = Event()


def main():

    income_released_dir = "income_released"
    order_completed_dir = "order_completed"
    observer = None
    handler = None
    income_file_dict = {}

    # let git upload the folders to github, so user doesn't have to create themselves to prevent incorrect naming
    if os.path.exists(f"{income_released_dir}/.gitkeep"):
        os.remove(f"{income_released_dir}/.gitkeep")

    if os.path.exists(f"{order_completed_dir}/.gitkeep"):
        os.remove(f"{order_completed_dir}/.gitkeep")

    # initial check
    is_passed = income_released_file_checks(income_released_dir)[0]

    if is_passed:
        file_valid_event.set()
        income_file_dict = income_released_file_checks(income_released_dir)[1]

    if not file_valid_event.is_set():
        observer, handler = start_income_released_folder_monitoring(
            income_released_dir,
            file_valid_event,
        )

    waiting_for_user(file_valid_event)

    if handler:
        income_file_dict = handler.get_income_file_dict()

    if observer:
        observer.stop()
        observer.join()

    file_valid_event.clear()

    all_files_income_released_folder = income_file_dict[
        "all_files_income_released_folder"
    ]
    income_released_filename = income_file_dict["income_released_filename"]
    income_released_file_path = income_file_dict["income_released_file_path"]
    """Income.released file checks passed"""
    print_uploaded_file(all_files_income_released_folder)

    processed_income_released_df = get_processed_income_released_df(
        income_released_file_path
    )

    # Get the required filenames for Order.completed, based on shopee's limitation which allows only maximum 30 days range download
    unique_year_month_list = get_unique_year_month_list(processed_income_released_df)

    required_completed_order_filenames = get_required_order_completed_filename(
        unique_year_month_list
    )

    order_completed_file_handler = OrderCompletedFolderMonitorHandler(
        order_completed_file_check,
        order_completed_dir,
        required_completed_order_filenames,
        file_valid_event,
    )

    if order_completed_file_handler.is_passed:
        file_valid_event.set()

    if not file_valid_event.is_set():
        observer = start_order_completed_folder_monitoring(
            order_completed_file_handler,
            order_completed_dir,
        )

    waiting_for_user(file_valid_event)

    all_files_order_completed_folder = (
        order_completed_file_handler.get_all_files_order_completed_folder()
    )

    if observer:
        observer.stop()
        observer.join()

    """Order.completed pass file check"""
    print_uploaded_file(all_files_order_completed_folder)

    completed_order_filepaths_list = [
        os.path.join(order_completed_dir, file)
        for file in all_files_order_completed_folder
    ]

    income_released_order_ids = get_income_released_order_ids(
        processed_income_released_df
    )

    # Get the orders that are paid by shopee from Order.completed because it has the 'Quantity' column for stock counting
    processed_order_completed_df = get_order_completed_df(
        completed_order_filepaths_list, income_released_order_ids
    )

    product_qty_df = get_product_quantity(processed_order_completed_df)

    # Order.completed has the same format, just choose any one to copy the header and data rows format to generate Procut.quantity excel file later
    any1_order_completed_filepath = completed_order_filepaths_list[0]

    order_completed_format_dict = get_order_completed_format(
        any1_order_completed_filepath
    )

    # Save to current directory
    product_qty_filename = save_product_quantity(
        order_completed_format_dict, product_qty_df, income_released_filename
    )

    print_generated_product_qty_file(product_qty_filename)


if __name__ == "__main__":
    main()
