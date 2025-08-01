import textwrap
from rich.console import Console, Group
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from time import sleep
from rich.measure import Measurement
from itertools import cycle

console = Console()


def generate_loading_panel():
    center_text = (
        " [italic]Waiting for user to upload[/] ———— [underline]Ctrl+C[/] to quit"
    )
    center_text_measurement = Measurement.get(console, console.options, center_text)
    remaining_space_for_spinners = console.size.width - center_text_measurement.maximum

    NUMBER_OF_SIDES = 2
    each_side_space_for_spinners = remaining_space_for_spinners // NUMBER_OF_SIDES

    # 1 for the icon 1 for left+right spacing in Columns
    EACH_SPINNER_OCCUPIES_SPACE = 2
    how_many_spinners_each_side = (
        each_side_space_for_spinners // EACH_SPINNER_OCCUPIES_SPACE
    )

    wanted_dots_name_list = ["dots5", "dots6", "dots7", "dots8"]

    left_spinner_cycle = cycle(wanted_dots_name_list)
    right_spinner_cycle = cycle(reversed(wanted_dots_name_list))

    left_spinner_list = [
        Spinner(next(left_spinner_cycle), style="green")
        for _ in range(how_many_spinners_each_side - 1)
    ]
    right_spinner_list = [
        Spinner(next(right_spinner_cycle), style="green")
        for _ in range(how_many_spinners_each_side - 1)
    ]

    columns_group = Align.center(
        Columns(*[left_spinner_list + [center_text] + right_spinner_list])
    )

    wait_user_upload_panel = Panel(
        columns_group,
        title="Status",
    )
    return wait_user_upload_panel


class IncomeReleasedErrorsPanel:
    def __init__(self):
        self.renderables = []

    def set_income_released_error_panel(self, panel_list):
        self.renderables = panel_list


income_released_error_panel = IncomeReleasedErrorsPanel()


def waiting_for_user_Live(event):
    with Live(
        Group(*income_released_error_panel.renderables, generate_loading_panel()),
        console=console,
        refresh_per_second=10,
        screen=True,
    ) as live:
        while not event.is_set():
            live.update(
                Group(
                    *income_released_error_panel.renderables, generate_loading_panel()
                )
            )


# # easier but doesnt handle resizes, when the terminal is smaller than current Panel, leftover Panels will appear
# def easier_waiting_for_user_Live(event):
#     with Live(
#         loading_panel,
#         console=console,
#         refresh_per_second=10,
#         screen=True,
#     ) as live:
#         event.wait()


def show_terminal_shrinking_warning(previous_width):
    with console.screen():
        print_order_completed_error_message_panel(
            main_msg="Terminal is shrinking!!!",
            subtext="This will affect the visuals, please use the original or bigger size",
        )
        while console.size.width < previous_width:
            sleep(0.5)


# console.status inside the while loop to avoid using status.start() after .stop(), console.status will move up and "eat" the previous output, if the shrinking speed of terminal
# is fast (small to big size)
# def waiting_for_user_status(event):
#     previous_width = console.size.width
#     with console.status(
#         "[italic]Waiting for user to upload correct Order.completed......[underline]Press Ctrl+C[/underline] to exit[/italic]",
#         spinner="shark",
#         spinner_style="red",
#     ) as status:
#         while not event.is_set():

#             if console.size.width < previous_width:
#                 status.stop()
#                 show_terminal_shrinking_warning(previous_width)
#                 status.start()


# this is still not as good as Live.display, but still better than just using even.wait(). If not the more Status lines would be printed when terminal sizes changes from small to big.
# Also the printed Panel will misaligned. The solution below at least hide the misalignment and significantly lower the amount of Status lines printed.
"""def waiting_for_user_status(event):
    with console.status(
        "[italic]Waiting for user to upload correct Order.completed......[underline]Press Ctrl+C[/underline] to exit[/italic]",
        spinner="shark",
        spinner_style="red",
    ):
        event.wait()
"""


def waiting_for_user_status(event):
    previous_width = console.size.width

    while not event.is_set():
        current_width = console.size.width

        if current_width < previous_width:
            show_terminal_shrinking_warning(previous_width)
        else:
            with console.status(
                "[italic]Waiting for user to upload correct Order.completed......[underline]Press Ctrl+C[/underline] to exit[/italic]",
                spinner="shark",
                spinner_style="red",
            ):
                while console.size.width >= previous_width:
                    sleep(0.5)


# print_order_completed_error_message_panel print Panels but this one returns a Panel, testing purposes
def get_income_released_error_message_panel(main_msg, subtext=""):
    panel = Panel(
        f"[bold yellow]⚠️  {main_msg}[/bold yellow] {subtext}",
        title="[yellow]WARNING[/yellow]",
        border_style="yellow",
        expand=True,
    )
    # console.print(panel)
    return panel


def get_income_released_format_info():
    panel = Panel(
        textwrap.dedent(
            f"""\
        Format: [bold cyan]Income.released.my.<start_date>_<end_date>.xlsx[/bold cyan]
        Date format: [bold cyan]YYYYMMDD[/bold cyan]
        Example: [dim]Income.released.my.20240701_20240715.xlsx[/dim]"""
        ),
        title="[cyan]Info[/cyan]",
        border_style="cyan",
        expand=True,
    )
    # console.print(panel)
    return panel


def get_income_released_date_range_error():
    panel = Panel(
        textwrap.dedent(
            f"""\
        Only 2 ranges (YYMM[bold cyan]DD[/bold cyan]) are accepted: [bold cyan](01, 15) and (16, days in a month)[/bold cyan]
        Example of first half of May: [dim]20250501_20250515[/dim]
        Example of second half of May: [dim]20250516_20250531[/dim]"""
        ),
        title="[cyan]Info[/cyan]",
        border_style="cyan",
        expand=True,
    )
    return panel


def print_success_message_pannel(main_msg):
    console.print(
        Panel(
            f"[bold green]{main_msg}[/bold green]",
            title="[green]SUCCESS[/green]",
            border_style="Green",
            expand=True,
        )
    )


def print_uploaded_file(file_list):
    uploaded_file = "\n".join([f"⬆️  {file}" for file in file_list])
    print_success_message_pannel(uploaded_file)


def print_generated_product_qty_file(filename):
    main_msg = "⬇️  " + filename + "is generated"
    print_success_message_pannel(main_msg)


# Show which required Order.completed file is uploaded
def print_order_completed_file_info(required_file_text):
    console.print(
        Panel(
            required_file_text,
            title="[cyan]Info[/cyan]",
            border_style="cyan",
            expand=True,
        )
    )


def print_order_completed_error_message_panel(main_msg, subtext=""):
    panel = Panel(
        f"[bold yellow]⚠️  {main_msg}[/bold yellow] {subtext}",
        title="[yellow]WARNING[/yellow]",
        border_style="yellow",
        expand=True,
    )
    console.print(panel)
