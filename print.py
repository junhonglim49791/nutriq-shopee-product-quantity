import textwrap
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner

console = Console()


def waiting_for_user(event):
    with console.status(
        "[italic]Waiting for user to upload correct file......[underline]Press Ctrl+C[/underline] to exit[/italic]",
        spinner="shark",
        spinner_style="red",
    ):
        while not event.is_set():
            time.sleep(1)


# def waiting_for_user(event):
#     console.file.flush()

#     # Step 1: Panels already printed by get_income_released_error_message(...)
#     # Do NOT print anything else here outside Live
#     time.sleep(0.5)
#     # Step 2: Create the spinner
#     spinner = Spinner(
#         "shark",
#         text="[italic red]Waiting for user to upload correct file... Press Ctrl+C to exit[/italic red]",
#     )

#     # Step 3: Use Live for the spinner only, below the previously printed panels
#     with Live(spinner, refresh_per_second=10, transient=False) as live:
#         while not event.is_set():
#             time.sleep(1)


def print_error_message_panel(main_msg, subtext=""):
    console.print(
        Panel(
            f"[bold yellow]⚠️  {main_msg}[/bold yellow] {subtext}",
            title="[yellow]WARNING[/yellow]",
            border_style="yellow",
            expand=True,
        )
    )


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


def print_income_released_format_info():
    console.print(
        Panel(
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
    )


def print_income_released_date_range_error():
    console.print(
        Panel(
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
    )


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
