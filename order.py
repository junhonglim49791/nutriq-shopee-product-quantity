from print import (
    print_order_completed_error_message_panel,
    print_order_completed_file_info,
)


# all_files_order_completed_folder -> list of filenames in order_completed/
# required_order_completed_files -> list of filenames that are required, after processing the uploaded Income.released file
def is_order_completed_filename_correct(
    all_files_order_completed_folder, required_order_completed_files
):
    return sorted(all_files_order_completed_folder) == sorted(
        required_order_completed_files
    )


def which_filename_is_correct(
    all_files_order_completed_folder, required_order_completed_files
):

    required_file_exists = {file: False for file in required_order_completed_files}

    for uploaded in all_files_order_completed_folder:
        if uploaded in required_order_completed_files:
            required_file_exists[uploaded] = True

    return sorted(list(required_file_exists.items()))


# required_file_exists example: [("Order.completed.20241212_20241212.xlsx", True), ("Order.completed.20241216_20250114.xlsx", False)]
def get_order_completed_error_message(required_file_exists, uploaded_files_number):
    # if any False is found in required_file_exists, then print missing_file error message.
    # in is_file_exist, True means there is a False in required_file_exists:
    # required_file_exists -> (True, False)
    # is_file_exist        -> (False, True) -> print error msg
    is_file_exist = [not t[1] for t in required_file_exists]
    missing_file = any(is_file_exist)

    missing_file_msg = ""
    too_many_files_msg = ""
    subtext = ""

    if missing_file:
        missing_file_msg = (
            "Please upload the correct file(s) to order_completed folder. "
        )

    if uploaded_files_number > len(required_file_exists):
        too_many_files_msg = "Too many files are uploaded."
        subtext = f"Please upload only [bold italic yellow]{len(required_file_exists)}[/bold italic yellow] file(s)"

    main_msg = missing_file_msg + too_many_files_msg
    print_order_completed_error_message_panel(main_msg, subtext)

    required_file_text = ""
    for index, (file, is_file_exist) in enumerate(required_file_exists):
        endline = "\n" if index != len(required_file_exists) - 1 else ""

        required_file_text += (
            "[cyan]" + file + "[/cyan]" + ".........." + "✅" + endline
            if is_file_exist
            else "[cyan]" + file + "[/cyan]" + ".........." + "❌" + endline
        )

    print_order_completed_file_info(required_file_text)


def order_completed_file_check(
    all_files_order_completed_folder,
    required_completed_order_filenames,
    required_file_exists,
):
    if not is_order_completed_filename_correct(
        all_files_order_completed_folder, required_completed_order_filenames
    ):
        get_order_completed_error_message(
            required_file_exists, len(all_files_order_completed_folder)
        )
        return False

    return True
