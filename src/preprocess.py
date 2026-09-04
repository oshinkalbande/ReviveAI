
import pandas as pd
import numpy as np

print("=" * 70)
print("AI REVENUE RECOVERY - DATA PREPROCESSING")
print("=" * 70)

# --------------------------------------------------
# 1. Load raw dataset
# --------------------------------------------------

df = pd.read_csv("data/revenue_data.csv")

print("\n1. RAW DATA")
print("-" * 70)
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


# --------------------------------------------------
# 2. Convert date columns
# --------------------------------------------------

date_columns = [
    "invoice_date",
    "due_date",
    "payment_date"
]

for column in date_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce"
    )

print("\n2. DATE COLUMNS CONVERTED")


# --------------------------------------------------
# 3. Check duplicate invoices
# --------------------------------------------------

duplicates = df["invoice_id"].duplicated().sum()

print("\n3. DUPLICATE INVOICES")
print("-" * 70)
print("Duplicate invoice IDs:", duplicates)

if duplicates > 0:
    df = df.drop_duplicates(
        subset="invoice_id",
        keep="first"
    )

    print("Duplicate invoices removed.")


# --------------------------------------------------
# 4. Handle missing payment dates
# --------------------------------------------------

missing_payment_dates = df["payment_date"].isna().sum()

print("\n4. MISSING PAYMENT DATES")
print("-" * 70)
print(
    "Missing payment dates:",
    missing_payment_dates
)

# We DO NOT fill these values.
# An overdue invoice naturally has no payment date.


# --------------------------------------------------
# 5. Handle numeric missing values
# --------------------------------------------------

numeric_columns = [
    "invoice_amount",
    "days_overdue",
    "previous_payments",
    "previous_late_payments",
    "average_payment_delay",
    "payment_failures",
    "communication_count",
    "last_contact_days",
    "discount_used",
    "recovered",
    "customer_lifetime_value"
]

for column in numeric_columns:

    if df[column].isna().sum() > 0:

        df[column] = df[column].fillna(
            df[column].median()
        )

print("\n5. NUMERIC MISSING VALUES HANDLED")


# --------------------------------------------------
# 6. Handle categorical missing values
# --------------------------------------------------

categorical_columns = [
    "payment_status",
    "customer_segment"
]

for column in categorical_columns:

    if df[column].isna().sum() > 0:

        df[column] = df[column].fillna(
            df[column].mode()[0]
        )

print("\n6. CATEGORICAL MISSING VALUES HANDLED")


# --------------------------------------------------
# 7. Make sure invoice amounts are positive
# --------------------------------------------------

invalid_amounts = (
    df["invoice_amount"] <= 0
).sum()

print("\n7. INVALID INVOICE AMOUNTS")
print("-" * 70)
print("Invalid amounts:", invalid_amounts)

if invalid_amounts > 0:

    df = df[
        df["invoice_amount"] > 0
    ]


# --------------------------------------------------
# 8. Make sure days overdue are valid
# --------------------------------------------------

df["days_overdue"] = df["days_overdue"].clip(
    lower=0
)

print("\n8. DAYS OVERDUE VALIDATED")


# --------------------------------------------------
# 9. Create payment delay feature
# --------------------------------------------------

df["payment_delay"] = np.where(
    df["payment_status"] == "Paid",
    (
        df["payment_date"] -
        df["due_date"]
    ).dt.days,
    df["days_overdue"]
)

df["payment_delay"] = df[
    "payment_delay"
].clip(lower=0)

print("\n9. PAYMENT DELAY FEATURE CREATED")


# --------------------------------------------------
# 10. Create invoice age
# --------------------------------------------------

today = pd.Timestamp("2026-09-03")

df["invoice_age"] = (
    today - df["invoice_date"]
).dt.days

df["invoice_age"] = df[
    "invoice_age"
].clip(lower=0)

print("\n10. INVOICE AGE FEATURE CREATED")


# --------------------------------------------------
# 11. Create late payment ratio
# --------------------------------------------------

df["late_payment_ratio"] = (
    df["previous_late_payments"] /
    df["previous_payments"].replace(0, 1)
)

df["late_payment_ratio"] = df[
    "late_payment_ratio"
].clip(0, 1)

print("\n11. LATE PAYMENT RATIO CREATED")


# --------------------------------------------------
# 12. Create customer payment reliability score
# --------------------------------------------------

df["payment_reliability_score"] = (
    1
    - df["late_payment_ratio"]
)

df["payment_reliability_score"] = (
    df["payment_reliability_score"] * 100
)

print("\n12. PAYMENT RELIABILITY SCORE CREATED")


# --------------------------------------------------
# 13. Create overdue revenue
# --------------------------------------------------

df["overdue_revenue"] = np.where(
    df["payment_status"] == "Overdue",
    df["invoice_amount"],
    0
)

print("\n13. OVERDUE REVENUE CREATED")


# --------------------------------------------------
# 14. Create recovery opportunity
# --------------------------------------------------

df["recovery_opportunity"] = np.where(
    (
        (df["payment_status"] == "Overdue")
        &
        (df["days_overdue"] > 0)
    ),
    df["invoice_amount"],
    0
)

print("\n14. RECOVERY OPPORTUNITY CREATED")


# --------------------------------------------------
# 15. Final missing-value check
# --------------------------------------------------

print("\n15. FINAL MISSING VALUE CHECK")
print("-" * 70)

missing = df.isnull().sum()

print(
    missing[missing > 0]
)


# --------------------------------------------------
# 16. Save cleaned dataset
# --------------------------------------------------

output_file = "data/processed_revenue_data.csv"

df.to_csv(
    output_file,
    index=False
)

print("\n16. CLEANED DATASET SAVED")
print("-" * 70)
print(output_file)


# --------------------------------------------------
# 17. Final summary
# --------------------------------------------------

print("\nFINAL DATASET")
print("-" * 70)

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print(
    "\nTotal Invoice Value:",
    f"₹{df['invoice_amount'].sum():,.2f}"
)

print(
    "Outstanding Revenue:",
    f"₹{df['overdue_revenue'].sum():,.2f}"
)

print(
    "Average Days Overdue:",
    f"{df.loc[df['payment_status'] == 'Overdue', 'days_overdue'].mean():.2f}"
)

print("\n" + "=" * 70)
print("DATA PREPROCESSING COMPLETED SUCCESSFULLY")
print("=" * 70)

