import textwrap
from time import sleep
from itertools import cycle

from rich.console import Console, Group
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align
from rich.columns import Columns
from rich.measure import Measurement

console = Console()


# Generate the Spinners dynamically on the left and right side of center text when user resizes the terminal
def generate_loading_panel():
    center_text = (
        " [italic]Waiting for user to upload[/] ———— [underline]Ctrl+C[/] to quit"
    )
    center_text_measurement = Measurement.get(console, console.options, center_text)
    remaining_space_for_spinners = console.size.width - center_text_measurement.maximum

    NUMBER_OF_SIDES = 2
    each_side_space_for_spinners = remaining_space_for_spinners // NUMBER_OF_SIDES

    # 1 space for the icon 1 space for left+right in Columns
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


# to get the list[Panel] from the IncomeFolderHandler after calling the income_released_file_checks()
class IncomeReleasedErrorsPanel:
    def __init__(self):
        self.renderables = []

    def set_income_released_error_panel(self, panel_list):
        self.renderables = panel_list


income_released_error_panel = IncomeReleasedErrorsPanel()


# Take control of the terminal and print all the renderables together, to solve the issues of bad looking outputs when terminal is resized
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
# def waiting_for_user_Live(event):
#     with Live(
#         loading_panel,
#         console=console,
#         refresh_per_second=10,
#         screen=True,
#     ) as live:
#         event.wait()


"""
this is still not as good as Live.display, but still better than just using even.wait(). If not more Status lines would be printed when
terminal sizes is smaller than console.status(). Also the printed Panels will misaligned. The solution below at least hide the misalignment
and significantly lower the amount of Status lines printed"""

"""Problems when terminal size shrinks when running the script:
1. When terminal size shrinks, the Panels will be misaligned.
2. console.status would be printed every line whenever the terminal is shorter than the status's message (in fast succession or terminal's width
is very close to the status message's length)
"""
# def waiting_for_user_status(event):
#     with console.status(
#         "[italic]Waiting for user to upload correct Order.completed......[underline]Press Ctrl+C[/underline] to exit[/italic]",
#         spinner="shark",
#         spinner_style="red",
#     ):
#         event.wait()


# Another way of keeping the output consistent is to alert user when terminal is resizing
"""2 ways to solve the status message eating previous output:
1. status.stop() and status.start() in show_terminal_shrinking_warning(). 
2. call status only when condition is met, like the 2nd function waiting_for_user_status(event) given below 

To explain 1.:

    Whenever status or screen use Live.display, after the context, it will removed itself
    Normal output:
        ---------------------Original terminal size---------------------
    1   ╭──────────────────────────── Info ────────────────────────────╮
    2   │ Order.completed.20250426_20250426.xlsx..........❌           │
    3   │ Order.completed.20250501_20250530.xlsx..........✅           │
    4   ╰──────────────────────────────────────────────────────────────╯
    5   ▐________/|____▌ Waiting for user to upload correct Order.completed......Press Ctrl+C to exit

    Say after status (5) is resolved, then it becomes 4 lines left, the next output can continue on line 5:
        ---------------------Original terminal size---------------------
    1   ╭──────────────────────────── Info ────────────────────────────╮
    2   │ Order.completed.20250426_20250426.xlsx..........❌           │
    3   │ Order.completed.20250501_20250530.xlsx..........✅           │
    4   ╰──────────────────────────────────────────────────────────────╯
    5 <----- continues here

    If i do,
        status.stop()
        if console.size.width < previous_width:
            show_terminal_shrinking_warning(previous_width)
        status.start()
        console.screen() should knows to continues on line 5, but that console.status continues on line 4

        ---------------------Original terminal size---------------------
    1   ╭──────────────────────────── Info ────────────────────────────╮
    2   │ Order.completed.20250426_20250426.xlsx..........❌           │
    3   │ Order.completed.20250501_20250530.xlsx..........✅           │
    4   ▐________/|____▌ Waiting for user to upload correct Order.comple
        ted......Press Ctrl+C to exit

    everytime i shrink the terminal when the status message is already wrapping (terminal shorter), then pull back to original or bigger size, 
    1 line would be eaten. i have no idea why.

    compensate this by getting the console.screen() first then status.stop(), hypothesis:
        If 1 line will be eaten then use console.screen to get to line 6, and status.stop() at line 5, after 6 is done, status.start() go back to 5
        ---------------------Original terminal size---------------------
    1   ╭──────────────────────────── Info ────────────────────────────╮
    2   │ Order.completed.20250426_20250426.xlsx..........❌           │
    3   │ Order.completed.20250501_20250530.xlsx..........✅           │
    4   ╰──────────────────────────────────────────────────────────────╯
    5   ▐________/|____▌ Waiting for user to upload correct Order.completed......Press Ctrl+C to exit
    6   ╭────────────────────────────────────────────────────────────────────────────── WARNING ─────────────────────────────────╮
        │ ⚠️  Terminal is shrinking!!! This will affect the visuals, please use the original or bigger size                      |
        ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    If the panel ended up in line 5, then status.start() goes to line 4

            ---------------------Original terminal size---------------------
    1   ╭──────────────────────────── Info ────────────────────────────╮
    2   │ Order.completed.20250426_20250426.xlsx..........❌           │
    3   │ Order.completed.20250501_20250530.xlsx..........✅           │
    4   ╰──────────────────────────────────────────────────────────────╯
    5   ╭────────────────────────────────────────────────────────────────────────────── WARNING ─────────────────────────────────╮
        │ ⚠️  Terminal is shrinking!!! This will affect the visuals, please use the original or bigger size                      |
        ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
"""


def show_terminal_shrinking_warning(status, previous_width):
    status.stop()
    with console.screen():

        print_order_completed_error_message_panel(
            main_msg="Terminal is shrinking!!!",
            subtext="This will affect the visuals, please use the original or bigger size",
        )
        while console.size.width < previous_width:
            sleep(0.5)

    status.start()


def waiting_for_user_status(event):
    previous_width = console.size.width
    with console.status(
        "[italic]Waiting for user to upload correct Order.completed......[underline]Press Ctrl+C[/underline] to exit[/italic]",
        spinner="shark",
        spinner_style="red",
    ) as status:
        while not event.is_set():

            if console.size.width < previous_width:
                show_terminal_shrinking_warning(status, previous_width)
            sleep(0.5)


"""Previosly when using status.stop() and status.start(), the previous terminal output will be "eaten" by status, cant replicate that 
situation consistenly, keeping another function below just in case. I found that when the "eating" problem occus, do a clear in command
line and it works normally again with above function.
"""


# def waiting_for_user_status(event):
#     previous_width = console.size.width

#     while not event.is_set():
#         current_width = console.size.width

#         if current_width < previous_width:
#             show_terminal_shrinking_warning(previous_width)
#         else:
#             with console.status(
#                 "[italic]Waiting for user to upload correct Order.completed......[underline]Press Ctrl+C[/underline] to exit[/italic]",
#                 spinner="shark",
#                 spinner_style="red",
#             ):
#                 # if not event.is_set() is not here, cant exit console.status() when the event is set in the file handler
#                 while not event.is_set() and console.size.width >= previous_width:
#                     sleep(0.5)


# print_order_completed_error_message_panel print Panels but this one returns a Panel, for Live.display
def get_income_released_error_message_panel(main_msg, subtext=""):
    panel = Panel(
        f"[bold yellow]⚠️  {main_msg}[/bold yellow] {subtext}",
        title="[yellow]WARNING[/yellow]",
        border_style="yellow",
        expand=True,
    )
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


# Previously order_completed and income_released share this function, but income_released changes to return Panel
def print_order_completed_error_message_panel(main_msg, subtext=""):
    panel = Panel(
        f"[bold yellow]⚠️  {main_msg}[/bold yellow] {subtext}",
        title="[yellow]WARNING[/yellow]",
        border_style="yellow",
        expand=True,
    )
    console.print(panel)
