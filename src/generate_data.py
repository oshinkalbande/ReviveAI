
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Make results reproducible
np.random.seed(42)

# Number of invoices
NUM_RECORDS = 10000

# -----------------------------
# 1. Generate customer data
# -----------------------------

customer_ids = [f"CUST{i:04d}" for i in range(1, 2001)]

customer_segment = np.random.choice(
    ["SMB", "Mid-Market", "Enterprise"],
    size=len(customer_ids),
    p=[0.50, 0.35, 0.15]
)

customer_lifetime_value = np.random.randint(
    50000, 5000000, size=len(customer_ids)
)

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "customer_segment": customer_segment,
    "customer_lifetime_value": customer_lifetime_value
})

# -----------------------------
# 2. Generate invoice data
# -----------------------------

invoice_customer = np.random.choice(
    customer_ids,
    size=NUM_RECORDS
)

invoice_ids = [
    f"INV{i:06d}"
    for i in range(1, NUM_RECORDS + 1)
]

start_date = datetime(2025, 1, 1)

invoice_dates = [
    start_date + timedelta(days=int(x))
    for x in np.random.randint(0, 600, NUM_RECORDS)
]

invoice_amounts = np.round(
    np.random.lognormal(mean=10, sigma=1, size=NUM_RECORDS),
    2
)

# Keep amounts within realistic limits
invoice_amounts = np.clip(
    invoice_amounts,
    5000,
    2000000
)

due_days = np.random.choice(
    [15, 30, 45, 60],
    size=NUM_RECORDS,
    p=[0.10, 0.55, 0.20, 0.15]
)

due_dates = [
    invoice_date + timedelta(days=int(days))
    for invoice_date, days in zip(invoice_dates, due_days)
]

# -----------------------------
# 3. Customer payment behaviour
# -----------------------------

previous_payments = np.random.randint(
    1, 30, NUM_RECORDS
)

previous_late_payments = np.random.binomial(
    previous_payments,
    0.25
)

average_payment_delay = np.maximum(
    np.random.normal(12, 10, NUM_RECORDS).round(),
    0
).astype(int)

payment_failures = np.random.poisson(
    0.8,
    NUM_RECORDS
)

communication_count = np.random.randint(
    0, 8,
    NUM_RECORDS
)

last_contact_days = np.random.randint(
    1, 90,
    NUM_RECORDS
)

discount_used = np.random.choice(
    [0, 1],
    size=NUM_RECORDS,
    p=[0.75, 0.25]
)

# -----------------------------
# 4. Determine payment status
# -----------------------------

# Create a payment behaviour score
risk_score = (
    previous_late_payments * 2
    + average_payment_delay * 0.8
    + payment_failures * 5
    + last_contact_days * 0.15
)

# Probability of being paid
payment_probability = 1 / (
    1 + np.exp((risk_score - 25) / 10)
)

random_values = np.random.random(NUM_RECORDS)

payment_status = np.where(
    random_values < payment_probability,
    "Paid",
    "Overdue"
)

# -----------------------------
# 5. Generate payment dates
# -----------------------------

payment_dates = []

for i in range(NUM_RECORDS):

    if payment_status[i] == "Paid":

        delay = max(
            0,
            int(
                np.random.normal(
                    average_payment_delay[i],
                    5
                )
            )
        )

        payment_date = due_dates[i] + timedelta(
            days=delay
        )

        payment_dates.append(payment_date)

    else:
        payment_dates.append(pd.NaT)

# -----------------------------
# 6. Calculate days overdue
# -----------------------------

today = datetime(2026, 9, 3)

days_overdue = []

for i in range(NUM_RECORDS):

    if payment_status[i] == "Paid":

        days_overdue.append(0)

    else:

        overdue = (
            today - due_dates[i]
        ).days

        days_overdue.append(
            max(0, overdue)
        )

# -----------------------------
# 7. Create recovery outcome
# -----------------------------

recovery_probability = (
    0.75
    - (np.array(days_overdue) * 0.003)
    - (previous_late_payments * 0.015)
    - (payment_failures * 0.02)
    + (communication_count * 0.015)
)

recovery_probability = np.clip(
    recovery_probability,
    0.05,
    0.95
)

recovery_random = np.random.random(NUM_RECORDS)

recovered = (
    recovery_random < recovery_probability
).astype(int)

# Paid invoices are considered recovered
recovered = np.where(
    payment_status == "Paid",
    1,
    recovered
)

# -----------------------------
# 8. Create final dataset
# -----------------------------

df = pd.DataFrame({

    "customer_id": invoice_customer,

    "invoice_id": invoice_ids,

    "invoice_amount": invoice_amounts,

    "invoice_date": invoice_dates,

    "due_date": due_dates,

    "payment_date": payment_dates,

    "payment_status": payment_status,

    "days_overdue": days_overdue,

    "previous_payments": previous_payments,

    "previous_late_payments": previous_late_payments,

    "average_payment_delay": average_payment_delay,

    "payment_failures": payment_failures,

    "communication_count": communication_count,

    "last_contact_days": last_contact_days,

    "discount_used": discount_used,

    "recovered": recovered
})

# Add customer information
df = df.merge(
    customers,
    on="customer_id",
    how="left"
)

# -----------------------------
# 9. Save dataset
# -----------------------------

df.to_csv(
    "data/revenue_data.csv",
    index=False
)

print("=" * 60)
print("AI REVENUE RECOVERY DATASET CREATED")
print("=" * 60)

print(f"Total invoices: {len(df)}")

print("\nPayment Status:")
print(df["payment_status"].value_counts())

print("\nTotal Invoice Value:")
print(f"₹{df['invoice_amount'].sum():,.2f}")

print("\nOverdue Revenue:")
overdue_revenue = df.loc[
    df["payment_status"] == "Overdue",
    "invoice_amount"
].sum()

print(f"₹{overdue_revenue:,.2f}")

print("\nRecovered Revenue:")
recovered_revenue = df.loc[
    df["recovered"] == 1,
    "invoice_amount"
].sum()

print(f"₹{recovered_revenue:,.2f}")

print("\nDataset saved to:")
print("data/revenue_data.csv")

print("=" * 60)
