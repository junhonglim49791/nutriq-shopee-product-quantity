import pandas as pd

from datetime import datetime, timedelta
import warnings

# Ignore UserWarning: Workbook contains no default style, apply openpyxl's default when the uploaded Income.released is not saved before after downloaded
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# Original columns
# MultiIndex([('Order Info', 'Unnamed: 0_level_1',          'Sequence No.'),
#             ('Order Info', 'Unnamed: 1_level_1',               'View By'),
#             ('Order Info', 'Unnamed: 2_level_1',              'Order ID'),
#             ('Order Info', 'Unnamed: 3_level_1',             'refund id'),
#             ('Order Info', 'Unnamed: 4_level_1',            'Product ID'),
#             ('Order Info', 'Unnamed: 5_level_1',          'Product Name'),
#             ('Order Info', 'Unnamed: 6_level_1',   'Order Creation Date'),
#             ('Order Info', 'Unnamed: 7_level_1', 'Payout Completed Date'),
#             ('Order Info', 'Unnamed: 8_level_1',       'Release Channel'),
#             ('Order Info', 'Unnamed: 9_level_1',            'Order Type')],
#            )


# Get Order Info part for stock count, others are unnecessary
def get_processed_income_released_df(income_released_file_path):
    income_released_df = pd.read_excel(
        income_released_file_path,
        sheet_name="Income",
        header=[0, 1, 2],
        engine="openpyxl",
    )

    order_info_df = income_released_df.loc[
        :, income_released_df.columns.get_level_values(0) == "Order Info"
    ]

    removed_sku_rows_df = order_info_df.loc[
        order_info_df[("Order Info", "Unnamed: 1_level_1", "View By")] != "Sku"
    ]

    # Check empty cells have 'nan' or "" as value
    # print(removed_sku_rows_df[("Order Info", "Unnamed: 3_level_1", "refund id")].unique())

    final_income_df = removed_sku_rows_df.loc[
        :,
        [
            ("Order Info", "Unnamed: 1_level_1", "View By"),
            ("Order Info", "Unnamed: 2_level_1", "Order ID"),
            ("Order Info", "Unnamed: 6_level_1", "Order Creation Date"),
        ],
    ]

    # Shopee sorted by default? Yes, but just in case
    sorted_final_income_df = final_income_df.sort_values(
        by=("Order Info", "Unnamed: 6_level_1", "Order Creation Date")
    )
    return sorted_final_income_df


def get_income_released_order_ids(processed_income_released_df):
    order_ids_header = ("Order Info", "Unnamed: 2_level_1", "Order ID")
    return processed_income_released_df[order_ids_header]


# "Order Creation Date" is str type
# print(
#     final_income_df["Order Info", "Unnamed: 6_level_1", "Order Creation Date"]
#     .map(type)
#     .unique()
# )
"""Get list of tuples. where tuple('YYYY-MM', [list of unique dates]), to determine the filenames of Order.Completed"""


def get_unique_year_month_list(final_income_df):
    order_creation_date_header = (
        "Order Info",
        "Unnamed: 6_level_1",
        "Order Creation Date",
    )
    # The values for 'Order Creation Date' colum is in %Y-%m-%d. Getting YYYY-MM using str.slice(0,7) as key helps with sorting the dates in desc order.
    # Using month only for the key will not sort properly when there is a case of '12' (Dec) in 2024, and the next month is '01' Jan in 2025.
    # Sort in desc because I found that the latest month will always have more orders, trying to make use it as a base dataframe to be expanded with earlier months.
    unique_year_month_list = (
        final_income_df[order_creation_date_header].str.slice(0, 7).unique()
    )
    """
    Example for May's tuple:
        year_month: '2025-05'
        unique_dates: ['2025-05-01', '2025-05-02', '2025-05-03', '2025-05-04'......]
        ('2025-05', ['2025-05-01', '2025-05-02', '2025-05-03', '2025-05-04'......])
    """
    unique_year_month_list = [(year_month, []) for year_month in unique_year_month_list]

    orders_creation_date_series = final_income_df[order_creation_date_header]

    for year_month, unique_dates in unique_year_month_list:
        unique_dates.extend(
            orders_creation_date_series[
                orders_creation_date_series.str.slice(0, 7) == year_month
            ].unique()
        )
    unique_year_month_list = sorted(unique_year_month_list, reverse=True)
    return unique_year_month_list


def get_required_order_completed_filename(unique_year_month_list):
    # unique_year_month_list is expectd to be sorted in desc order. Which means current month should always be later then previous month.
    # Check every 2 months, and change the current month's and previous month's date list when conditions are met
    for i in range(len(unique_year_month_list) - 1):
        current_year_month_str = unique_year_month_list[i][0]
        current_year_month_dates_list = unique_year_month_list[i][1]
        current_year_month_end_date_str = current_year_month_dates_list[-1]
        current_year_month_end_date_obj = datetime.strptime(
            current_year_month_end_date_str, "%Y-%m-%d"
        )

        # Shopee only allow 30 days download for a Order.completed file. If we find before 30 days from the current month's end date, and is in the previous
        # month, we should modify the current month's start date, so that user knows what is the corret date range to print.
        """Example
            if in '2025-05' , ['2025-05-01', .... '2025-05-27'] <--- last date in May, user should download from '2025-04-27, instead of '2025-05-01'
        """
        date_before30days_from_current_year_month_end_date = (
            current_year_month_end_date_obj - timedelta(days=30)
        )

        date_before30days_from_current_year_month_end_date_str = (
            date_before30days_from_current_year_month_end_date.strftime("%Y-%m-%d")
        )

        date_before30days_from_current_year_month = (
            date_before30days_from_current_year_month_end_date.strftime("%Y-%m")
        )

        # if is within the current month, no need to find new start date from previous month because there is already 30 days orders data in this month
        if date_before30days_from_current_year_month == current_year_month_str:
            continue

        # If is not within this month, we have to get a new start date for current month, new end date for previous month
        # and update their according list of unique dates
        prev_month_dates_list = unique_year_month_list[i + 1][1]
        new_index_current_month_start_date = None

        # Sometimes, date_before30days_from_current_year_month_end_date_str is not in the previous date list because there are no released income on that day.
        # If is in the list, get that index so that we know how to slice the previous month's and current month's list of unique dates

        if (
            date_before30days_from_current_year_month_end_date_str
            in prev_month_dates_list
        ):
            new_index_current_month_start_date = prev_month_dates_list.index(
                date_before30days_from_current_year_month_end_date_str
            )
        else:
            # Check whether there is a date from previous month which is later than the date_before30days_from_current_year_month_end_date_str.
            # This means that I can take that date as a new start date for current month
            """Example
            if in '2025-05' , ['2025-05-01', ... '2025-05-27'] <--- last date in May,
            '2025-04-27' is the date_before30days_from_current_year_month_end_date_str,
            and in '2025-04', ['2025-04-25', '2025-04-26', '2025-04-27'(imagine is here for explanation),'2025-04-28'],
            Since '2025-04-28' is in the 30 days range, '2025-04-26' is out of 30 days range. So user should download from '2025-04-28, instead of '2025-05-01'
            """
            for i, date in enumerate(prev_month_dates_list):
                if date > date_before30days_from_current_year_month_end_date_str:
                    new_index_current_month_start_date = i
                    # Stop the loop, only the next date is needed, if not index every date that is later than date_before30days will be set to new_index
                    break

        # Just skip if there is no date within the range of date_before30days_from_current_year_month_end_date_str to current month's end date,
        if new_index_current_month_start_date is None:
            continue

        """Example
        if in '2025-05' , ['2025-05-01', ... '2025-05-27'] <--- last date in May,
        '2025-04-27' is date_before30days_from_current_year_month_end_date_str,
        and in '2025-04', ['2025-04-25', '2025-04-26', '2025-04-27'(IMAGINE is here for explanation),'2025-04-28'],
        Since '2025-04-28' is in the 30 days range, '2025-04-26' is out of 30 days range. So user should download from '2025-04-28, instead of '2025-05-01',
        previous month's date list become:
        ['2025-04-25', '2025-04-26']
        current month's date list become:
        ['2025-04-28', ... '2025-05-27']
        """
        # At the front of current month's list of dates, add dates starting from date_before30days_from_current_year_month_end_date_str to
        # the last date from previous month
        current_year_month_dates_list[:0] = prev_month_dates_list[
            new_index_current_month_start_date:
        ]
        # The last date of previous month should be the date before date_before30days_from_current_year_month_end_date_str
        prev_month_dates_list[:] = prev_month_dates_list[
            :new_index_current_month_start_date
        ]

    completed_order_filenames = []
    for year_month, datelist in unique_year_month_list:
        if len(datelist) != 0:
            start_date = datelist[0].replace("-", "")
            end_date = datelist[-1].replace("-", "")
            completed_order_filenames.append(
                f"Order.completed.{start_date}_{end_date}.xlsx"
            )
    return completed_order_filenames
