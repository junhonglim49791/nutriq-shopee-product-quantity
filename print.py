import textwrap

from rich.console import Console
from rich.panel import Panel

console = Console()


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


def print_order_completed_file_info(required_file_text):
    console.print(
        Panel(
            required_file_text,
            title="[cyan]Info[/cyan]",
            border_style="cyan",
            expand=True,
        )
    )
