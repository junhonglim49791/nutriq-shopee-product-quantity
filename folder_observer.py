from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from income_released import income_released_file_checks, get_all_files_in_a_dir
from order import order_completed_file_check, which_filename_is_correct


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

    def on_any_event(self, event):
        if not event.is_directory and event.event_type in (
            "created",
            "deleted",
            "moved",
        ):
            is_passed = self.file_check_callback(self.income_released_dir)[0]
            if is_passed:
                self.income_file_dict = self.file_check_callback(
                    self.income_released_dir
                )[1]
                self.income_released_file_valid_event.set()

    def get_income_file_dict(self):
        return self.income_file_dict


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
        self.all_files_order_completed_folder = []
        self.required_file_exists = []

    def on_any_event(self, event):
        if not event.is_directory and event.event_type in (
            "created",
            "deleted",
            "moved",
        ):
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
            if is_passed:
                self.order_completed_file_valid_event.set()

    def get_all_files_order_completed_folder(self):
        return self.all_files_order_completed_folder


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


def start_order_completed_folder_monitoring(
    order_completed_dir,
    required_completed_order_filenames,
    order_completed_file_valid_event,
):
    observer = Observer()
    handler = OrderCompletedFolderMonitorHandler(
        order_completed_file_check,
        order_completed_dir,
        required_completed_order_filenames,
        order_completed_file_valid_event,
    )
    observer.schedule(handler, order_completed_dir, recursive=False)
    observer.start()
    return observer, handler
