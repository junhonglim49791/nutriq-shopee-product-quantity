from print import print_error_message_panel, print_order_completed_file_match_error


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

    return list(required_file_exists.items())


def get_order_completed_error_message(required_file_exists):
    is_file_exist = [not t[1] for t in required_file_exists]
    show_warning = any(is_file_exist)
    if show_warning:
        main_msg = "Please upload the correct file(s) to order_completed folder"
        print_error_message_panel(main_msg)

    required_file_text = ""
    for index, (file, is_file_exist) in enumerate(required_file_exists):
        endline = "\n" if index != len(required_file_exists) - 1 else ""

        required_file_text += (
            file + ".........." + "✅" + endline
            if is_file_exist
            else file + ".........." + "❌" + endline
        )

    print_order_completed_file_match_error(required_file_text)


def show_more_than_required_files_number(required_file_number):
    main_msg = "Too many files are uploaded."
    subtext = f"Please upload only [bold italic yellow]{required_file_number}[/bold italic yellow] file(s)"
    print_error_message_panel(main_msg, subtext)
