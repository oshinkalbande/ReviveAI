import pandas as pd

# -----------------------------------
# 1. Load the dataset
# -----------------------------------

df = pd.read_csv("data/revenue_data.csv")

print("=" * 70)
print("AI REVENUE RECOVERY - DATASET EXPLORATION")
print("=" * 70)


# -----------------------------------
# 2. Basic information
# -----------------------------------

print("\n1. DATASET SHAPE")
print("-" * 70)

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


# -----------------------------------
# 3. Display first 5 records
# -----------------------------------

print("\n2. FIRST 5 RECORDS")
print("-" * 70)

print(df.head())


# -----------------------------------
# 4. Display column names
# -----------------------------------

print("\n3. COLUMN NAMES")
print("-" * 70)

for column in df.columns:
    print("-", column)


# -----------------------------------
# 5. Data types
# -----------------------------------

print("\n4. DATA TYPES")
print("-" * 70)

print(df.dtypes)


# -----------------------------------
# 6. Missing values
# -----------------------------------

print("\n5. MISSING VALUES")
print("-" * 70)

missing_values = df.isnull().sum()

print(missing_values)


# -----------------------------------
# 7. Duplicate records
# -----------------------------------

print("\n6. DUPLICATE RECORDS")
print("-" * 70)

duplicates = df.duplicated().sum()

print("Number of duplicate rows:", duplicates)


# -----------------------------------
# 8. Payment status
# -----------------------------------

print("\n7. PAYMENT STATUS")
print("-" * 70)

print(df["payment_status"].value_counts())


# -----------------------------------
# 9. Revenue statistics
# -----------------------------------

print("\n8. INVOICE AMOUNT STATISTICS")
print("-" * 70)

print(df["invoice_amount"].describe())


# -----------------------------------
# 10. Total revenue
# -----------------------------------

print("\n9. TOTAL INVOICE VALUE")
print("-" * 70)

total_revenue = df["invoice_amount"].sum()

print(f"₹{total_revenue:,.2f}")


# -----------------------------------
# 11. Outstanding revenue
# -----------------------------------

print("\n10. OUTSTANDING REVENUE")
print("-" * 70)

outstanding_revenue = df.loc[
    df["payment_status"] == "Overdue",
    "invoice_amount"
].sum()

print(f"₹{outstanding_revenue:,.2f}")


# -----------------------------------
# 12. Recovered revenue
# -----------------------------------

print("\n11. RECOVERED REVENUE")
print("-" * 70)

recovered_revenue = df.loc[
    df["recovered"] == 1,
    "invoice_amount"
].sum()

print(f"₹{recovered_revenue:,.2f}")


# -----------------------------------
# 13. Average days overdue
# -----------------------------------

print("\n12. AVERAGE DAYS OVERDUE")
print("-" * 70)

average_overdue = df.loc[
    df["payment_status"] == "Overdue",
    "days_overdue"
].mean()

print(f"{average_overdue:.2f} days")


# -----------------------------------
# 14. Customer segments
# -----------------------------------

print("\n13. CUSTOMER SEGMENTS")
print("-" * 70)

print(df["customer_segment"].value_counts())


# -----------------------------------
# 15. Recovery distribution
# -----------------------------------

print("\n14. RECOVERY OUTCOME")
print("-" * 70)

print(df["recovered"].value_counts())


print("\n" + "=" * 70)
print("DATASET EXPLORATION COMPLETED")
print("=" * 70)

