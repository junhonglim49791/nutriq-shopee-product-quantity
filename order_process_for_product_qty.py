import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
import re


def get_order_completed_df(order_completed_filepath_list, income_released_order_ids):

    df_to_merge = []
    for order_completed in order_completed_filepath_list:
        order_completed_df = pd.read_excel(
            order_completed, sheet_name="orders", header=0
        )
        remove_refunded_orders_df = order_completed_df.loc[
            order_completed_df["Return / Refund Status"].isna()
        ]

        released_order_completed_df = remove_refunded_orders_df[
            remove_refunded_orders_df["Order ID"].isin(income_released_order_ids)
        ]

        final_order_completed_df = released_order_completed_df[
            [
                "Product Name",
                "SKU Reference No.",
                "Variation Name",
                "Quantity",
            ]
        ].copy()

        final_order_completed_df["From"] = "_".join(
            re.findall(r"\d{8}", order_completed)
        )
        final_order_completed_df["Variation Name"] = final_order_completed_df[
            "Variation Name"
        ].fillna("No Variant")
        final_order_completed_df["Quantity"] = pd.to_numeric(
            final_order_completed_df["Quantity"]
        )

        df_to_merge.append(final_order_completed_df)

    merged_order_completed = pd.concat(df_to_merge, ignore_index=True)

    return merged_order_completed


def get_product_quantity(merged_order_completed):
    # print(merged_order_completed)
    # print(
    #     merged_order_completed[
    #         merged_order_completed["SKU Reference No."] == "NEPRO220MX_24"
    #     ]
    # )
    product_qty_df = (
        merged_order_completed.groupby(
            [
                "Product Name",
                "SKU Reference No.",
                "Variation Name",
            ]
        )["Quantity"]
        .sum()
        .reset_index()
        .sort_values(
            [
                "Product Name",
                "SKU Reference No.",
                "Variation Name",
            ]
        )
    )
    print(product_qty_df["Quantity"].sum())
    # return product_qty_df


# def get_order_completed_format(any_order_completed_file):
