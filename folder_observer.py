from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from income_released import income_released_file_checks, get_all_files_in_a_dir
from order import order_completed_file_check, which_filename_is_correct
from print import income_released_error_panel, console


class IncomeReleasedFolderMonitorHandler(FileSystemEventHandler):
    def __init__(
        self,
        file_check_callback,
        income_released_dir,
        income_released_file_valid_event,
    ):
        self.file_check_callback = file_check_callback
        self.income_released_dir = income_released_dir
        self.income_released_file_valid_event = income_released_file_valid_event
        self.income_file_dict = {}
        self.error_panel = None
        self.info_panel = None

    def on_any_event(self, event):
        if not event.is_directory and event.event_type in (
            "created",
            "deleted",
            "moved",
        ):
            is_passed, success_fail_dict = self.file_check_callback(
                self.income_released_dir
            )
            if is_passed:
                self.income_file_dict = success_fail_dict["success"]
                self.income_released_file_valid_event.set()
            else:
                income_released_error_panel.set_income_released_error_panel(
                    success_fail_dict["fail"]
                )

    def get_income_file_dict(self):
        return self.income_file_dict


def start_income_released_folder_monitoring(
    income_released_dir,
    income_released_file_valid_event,
):
    observer = Observer()
    handler = IncomeReleasedFolderMonitorHandler(
        income_released_file_checks,
        income_released_dir,
        income_released_file_valid_event,
    )
    observer.schedule(handler, income_released_dir, recursive=False)
    observer.start()
    return observer, handler


class OrderCompletedFolderMonitorHandler(FileSystemEventHandler):
    def __init__(
        self,
        file_check_callback,
        order_completed_dir,
        required_completed_order_filenames,
        order_completed_file_valid_event,
    ):
        self.file_check_callback = file_check_callback
        self.required_completed_order_filenames = required_completed_order_filenames
        self.order_completed_dir = order_completed_dir
        self.order_completed_file_valid_event = order_completed_file_valid_event
        self.is_passed = self.is_filecheck_passed()

    def is_filecheck_passed(self):
        self.all_files_order_completed_folder = get_all_files_in_a_dir(
            self.order_completed_dir
        )
        self.required_file_exists = which_filename_is_correct(
            self.all_files_order_completed_folder,
            self.required_completed_order_filenames,
        )

        is_passed = self.file_check_callback(
            self.all_files_order_completed_folder,
            self.required_completed_order_filenames,
            self.required_file_exists,
        )

        return is_passed

    def on_any_event(self, event):
        if not event.is_directory and event.event_type in (
            "created",
            "deleted",
            "moved",
        ):
            self.is_passed = self.is_filecheck_passed()
            if self.is_passed:
                self.order_completed_file_valid_event.set()

    def get_all_files_order_completed_folder(self):
        return self.all_files_order_completed_folder


def start_order_completed_folder_monitoring(
    handler,
    order_completed_dir,
):
    observer = Observer()
    observer.schedule(handler, order_completed_dir, recursive=False)
    observer.start()
    return observer
