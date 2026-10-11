import pandas as pd
import numpy as np

CSV_PATH = "sales.csv"

def load_and_clean(path):
    df = pd.read_csv(path)
    print(f"Raw rows loaded: {len(df)}")

    # Remove duplicate transactions
    before = len(df)
    df = df.drop_duplicates(subset="order_id", keep="first")
    print(f"Duplicate orders removed: {before - len(df)}")

    df["units_sold"] = pd.to_numeric(df["units_sold"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df["unit_price"] = df["unit_price"].fillna(
        df.groupby("product_name")["unit_price"].transform("median")
    )

    df["region"] = df["region"].fillna("Unknown")

    before = len(df)
    df = df.dropna(subset=["units_sold", "unit_price", "date"])
    df = df[df["units_sold"] > 0]
    print(f"Invalid rows dropped: {before - len(df)}")

    df["units_sold"] = df["units_sold"].astype(int)
    return df.reset_index(drop=True)

#NUMPY REVENUE ----------
def add_revenue(df):
    df["revenue"] = np.multiply(df["units_sold"].to_numpy(),
                                df["unit_price"].to_numpy())
    revenue = df["revenue"].to_numpy()
    total_revenue = np.sum(revenue)
    total_orders = df["order_id"].nunique()
    aov = total_revenue / total_orders
    total_units = np.sum(df["units_sold"].to_numpy())
    return df, total_revenue, aov, total_units

def revenue_by(df, column):
    return (df.groupby(column)["revenue"].sum()
              .sort_values(ascending=False))

def filter_by_date(df, start, end):
    mask = (df["date"] >= start) & (df["date"] <= end)
    return df[mask]
# CONSOLE REPORT 
def print_report(df, total_revenue, aov, total_units):
    by_category = revenue_by(df, "category")
    by_product = revenue_by(df, "product_name")
    by_region = revenue_by(df, "region")

    line = "=" * 48
    print(f"\n{line}\n{'RETAIL SALES INTELLIGENCE REPORT':^48}\n{line}")
    print(f"Total Revenue        : ${total_revenue:,.2f}")
    print(f"Average Order Value  : ${aov:,.2f}")
    print(f"Total Units Sold     : {total_units}")
    print(f"Total Orders         : {df['order_id'].nunique()}")

    print(f"\nTop Product : {by_product.index[0]} (${by_product.iloc[0]:,.2f})")
    print(f"Top Category: {by_category.index[0]} (${by_category.iloc[0]:,.2f})")
    print(f"Top Region  : {by_region.index[0]} (${by_region.iloc[0]:,.2f})")

    print("\n--- Revenue by Category ---")
    print(by_category.round(2).to_string())
    print("\n--- Revenue by Product (high to low) ---")
    print(by_product.round(2).to_string())
    print("\n--- Revenue by Region ---")
    print(by_region.round(2).to_string())

    week = filter_by_date(df, "2026-09-01", "2026-09-05")
    print("\n--- Date Range Filter: 2026-09-01 to 2026-09-05 ---")
    print(f"Orders: {len(week)} | Revenue: ${week['revenue'].sum():,.2f}")
    print(line)

if __name__ == "__main__":
    data = load_and_clean(CSV_PATH)
    data, total_rev, aov, units = add_revenue(data)
    print_report(data, total_rev, aov, units)
