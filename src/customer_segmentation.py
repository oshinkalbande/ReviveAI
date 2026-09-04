import pandas as pd
import numpy as np
import joblib

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# ============================================================
# REVIVEAI - CUSTOMER INTELLIGENCE & SEGMENTATION
# ============================================================

print("=" * 70)
print("REVIVEAI - CUSTOMER INTELLIGENCE & SEGMENTATION")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "data/ml_ready_data.csv"

df = pd.read_csv(DATA_PATH)

print("\nDataset loaded successfully.")
print("Invoice records:", len(df))


# ============================================================
# 2. CUSTOMER-LEVEL AGGREGATION
# ============================================================

customer_df = df.groupby("customer_id").agg(

    total_invoices=("invoice_id", "count"),

    total_invoice_value=("invoice_amount", "sum"),

    average_invoice_value=("invoice_amount", "mean"),

    average_days_overdue=("days_overdue", "mean"),

    maximum_days_overdue=("days_overdue", "max"),

    total_previous_payments=("previous_payments", "sum"),

    total_previous_late_payments=(
        "previous_late_payments",
        "sum"
    ),

    average_payment_delay=(
        "average_payment_delay",
        "mean"
    ),

    total_payment_failures=(
        "payment_failures",
        "sum"
    ),

    total_communications=(
        "communication_count",
        "sum"
    ),

    average_last_contact_days=(
        "last_contact_days",
        "mean"
    ),

    payment_reliability_score=(
        "payment_reliability_score",
        "mean"
    ),

    payment_behavior_score=(
        "payment_behavior_score",
        "mean"
    ),

    customer_value_score=(
        "customer_value_score",
        "mean"
    ),

    customer_lifetime_value=(
        "customer_lifetime_value",
        "mean"
    ),

    recovery_rate=(
        "recovered",
        "mean"
    )

).reset_index()


print("\nUnique customers:", len(customer_df))


# ============================================================
# 3. CREATE CUSTOMER FEATURES
# ============================================================

customer_df["late_payment_rate"] = np.where(
    customer_df["total_previous_payments"] > 0,

    customer_df["total_previous_late_payments"] /
    customer_df["total_previous_payments"],

    0
)

customer_df["payment_failure_rate"] = np.where(
    customer_df["total_invoices"] > 0,

    customer_df["total_payment_failures"] /
    customer_df["total_invoices"],

    0
)

customer_df["communication_per_invoice"] = (
    customer_df["total_communications"] /
    customer_df["total_invoices"]
)


# Avoid infinite values
customer_df = customer_df.replace(
    [np.inf, -np.inf],
    np.nan
)


# Fill missing values
numeric_columns = customer_df.select_dtypes(
    include=np.number
).columns

customer_df[numeric_columns] = (
    customer_df[numeric_columns]
    .fillna(customer_df[numeric_columns].median())
)


# ============================================================
# 4. SELECT CLUSTERING FEATURES
# ============================================================

segmentation_features = [

    "total_invoices",

    "total_invoice_value",

    "average_invoice_value",

    "average_days_overdue",

    "maximum_days_overdue",

    "late_payment_rate",

    "payment_failure_rate",

    "average_payment_delay",

    "payment_reliability_score",

    "payment_behavior_score",

    "customer_value_score",

    "customer_lifetime_value",

    "recovery_rate"

]


print(
    "\nSegmentation features:",
    len(segmentation_features)
)


# ============================================================
# 5. PREPARE DATA FOR K-MEANS
# ============================================================

X = customer_df[
    segmentation_features
].copy()

X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

X = X.fillna(
    X.median(numeric_only=True)
)


# ============================================================
# 6. STANDARDIZE FEATURES
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ============================================================
# 7. TRAIN K-MEANS
# ============================================================

print("\n" + "=" * 70)
print("TRAINING K-MEANS CUSTOMER SEGMENTATION")
print("=" * 70)


kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

customer_df["cluster"] = kmeans.fit_predict(
    X_scaled
)


# ============================================================
# 8. ANALYZE CLUSTERS
# ============================================================

cluster_summary = customer_df.groupby(
    "cluster"
).agg(

    customers=("customer_id", "count"),

    average_invoice_value=(
        "average_invoice_value",
        "mean"
    ),

    average_days_overdue=(
        "average_days_overdue",
        "mean"
    ),

    late_payment_rate=(
        "late_payment_rate",
        "mean"
    ),

    payment_failure_rate=(
        "payment_failure_rate",
        "mean"
    ),

    payment_reliability=(
        "payment_reliability_score",
        "mean"
    ),

    customer_lifetime_value=(
        "customer_lifetime_value",
        "mean"
    ),

    recovery_rate=(
        "recovery_rate",
        "mean"
    )

).reset_index()


print("\nCluster Summary:")
print(
    cluster_summary.round(3).to_string(index=False)
)


# ============================================================
# 9. AUTOMATICALLY NAME CUSTOMER SEGMENTS
# ============================================================

def assign_segment(row, summary):

    overdue = row["average_days_overdue"]
    late_rate = row["late_payment_rate"]
    failure_rate = row["payment_failure_rate"]
    clv = row["customer_lifetime_value"]
    reliability = row["payment_reliability_score"]

    avg_clv = summary[
        "customer_lifetime_value"
    ].mean()

    # High-value + risky
    if (
        clv >= avg_clv
        and (
            overdue > 45
            or late_rate > 0.35
            or failure_rate > 0.20
        )
    ):
        return "Valuable but Risky"

    # High payment problems
    elif (
        overdue > 60
        or late_rate > 0.45
        or failure_rate > 0.30
    ):
        return "High-Risk Customer"

    # Mostly reliable
    elif (
        overdue <= 20
        and reliability >= 0.70
        and late_rate <= 0.25
    ):
        return "Reliable Customer"

    # Everything in between
    else:
        return "Occasional Late Payer"


customer_df["customer_segment"] = customer_df.apply(
    lambda row: assign_segment(
        row,
        customer_df
    ),
    axis=1
)


# ============================================================
# 10. RECOMMEND CUSTOMER STRATEGY
# ============================================================

def recommend_strategy(segment):

    if segment == "Reliable Customer":
        return "Automated reminder and self-service payment"

    elif segment == "Occasional Late Payer":
        return "Personalized payment reminder"

    elif segment == "High-Risk Customer":
        return "Frequent follow-up and payment assistance"

    elif segment == "Valuable but Risky":
        return "Priority human intervention"

    else:
        return "Monitor customer"


customer_df["recommended_strategy"] = (
    customer_df["customer_segment"]
    .apply(recommend_strategy)
)


# ============================================================
# 11. CUSTOMER PRIORITY SCORE
# ============================================================

customer_df["customer_priority_score"] = (

    customer_df["customer_lifetime_value"] *
    (
        1
        + customer_df["average_days_overdue"]
        / 100
    ) *
    (
        1
        + customer_df["late_payment_rate"]
    )

)

customer_df["customer_priority_score"] = (
    customer_df["customer_priority_score"]
    .round(2)
)


# ============================================================
# 12. SORT CUSTOMERS BY PRIORITY
# ============================================================

customer_df = customer_df.sort_values(
    by="customer_priority_score",
    ascending=False
)


# ============================================================
# 13. SAVE CUSTOMER SEGMENTS
# ============================================================

OUTPUT_PATH = (
    "outputs/customer_segments.csv"
)

customer_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nCustomer segmentation saved:")
print(OUTPUT_PATH)


# ============================================================
# 14. SAVE CLUSTER MODEL
# ============================================================

joblib.dump(
    kmeans,
    "models/customer_segmentation_model.pkl"
)

joblib.dump(
    scaler,
    "models/customer_scaler.pkl"
)

joblib.dump(
    segmentation_features,
    "models/customer_segmentation_features.pkl"
)


print("\nSegmentation models saved:")
print("models/customer_segmentation_model.pkl")
print("models/customer_scaler.pkl")
print(
    "models/customer_segmentation_features.pkl"
)


# ============================================================
# 15. SEGMENT DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("CUSTOMER SEGMENT DISTRIBUTION")
print("=" * 70)

print(
    customer_df[
        "customer_segment"
    ].value_counts()
)


# ============================================================
# 16. SEGMENT SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CUSTOMER SEGMENT SUMMARY")
print("=" * 70)

segment_summary = customer_df.groupby(
    "customer_segment"
).agg(

    customers=("customer_id", "count"),

    average_invoice_value=(
        "average_invoice_value",
        "mean"
    ),

    average_days_overdue=(
        "average_days_overdue",
        "mean"
    ),

    late_payment_rate=(
        "late_payment_rate",
        "mean"
    ),

    customer_lifetime_value=(
        "customer_lifetime_value",
        "mean"
    ),

    recovery_rate=(
        "recovery_rate",
        "mean"
    )

).reset_index()


print(
    segment_summary.round(2)
    .to_string(index=False)
)


# ============================================================
# 17. TOP 20 PRIORITY CUSTOMERS
# ============================================================

print("\n" + "=" * 70)
print("TOP 20 PRIORITY CUSTOMERS")
print("=" * 70)

top_customers = customer_df.head(20)[
    [
        "customer_id",
        "customer_segment",
        "total_invoice_value",
        "average_days_overdue",
        "late_payment_rate",
        "customer_lifetime_value",
        "recovery_rate",
        "customer_priority_score",
        "recommended_strategy"
    ]
]


print(
    top_customers.round(2)
    .to_string(index=False)
)


# ============================================================
# 18. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("STEP 10 COMPLETED SUCCESSFULLY!")
print("=" * 70)

print("\nReviveAI can now:")
print("✓ Analyze customers")
print("✓ Group customers using K-Means")
print("✓ Identify risky customer behavior")
print("✓ Identify valuable customers")
print("✓ Calculate customer priority")
print("✓ Recommend customer-specific strategies")