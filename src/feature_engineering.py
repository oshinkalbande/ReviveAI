
import pandas as pd
import numpy as np

print("=" * 70)
print("AI REVENUE RECOVERY - FEATURE ENGINEERING")
print("=" * 70)


# --------------------------------------------------
# 1. Load processed dataset
# --------------------------------------------------

df = pd.read_csv(
    "data/processed_revenue_data.csv"
)

print("\n1. PROCESSED DATA LOADED")
print("-" * 70)
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


# --------------------------------------------------
# 2. Late Payment Ratio
# --------------------------------------------------

df["late_payment_ratio"] = (
    df["previous_late_payments"] /
    df["previous_payments"].replace(0, 1)
)

df["late_payment_ratio"] = df[
    "late_payment_ratio"
].clip(0, 1)

print("\n2. LATE PAYMENT RATIO CREATED")


# --------------------------------------------------
# 3. Payment Reliability Score
# --------------------------------------------------

df["payment_reliability_score"] = (
    1 - df["late_payment_ratio"]
) * 100

df["payment_reliability_score"] = (
    df["payment_reliability_score"].round(2)
)

print("\n3. PAYMENT RELIABILITY SCORE CREATED")


# --------------------------------------------------
# 4. Overdue Severity
# --------------------------------------------------

def classify_overdue(days):

    if days == 0:
        return "Current"

    elif days <= 30:
        return "Mild"

    elif days <= 60:
        return "Moderate"

    elif days <= 90:
        return "Severe"

    else:
        return "Critical"


df["overdue_severity"] = (
    df["days_overdue"]
    .apply(classify_overdue)
)

print("\n4. OVERDUE SEVERITY CREATED")


# --------------------------------------------------
# 5. Invoice Value Category
# --------------------------------------------------

def classify_invoice_value(amount):

    if amount < 50000:
        return "Small"

    elif amount < 200000:
        return "Medium"

    elif amount < 1000000:
        return "Large"

    else:
        return "Very Large"


df["invoice_value_category"] = (
    df["invoice_amount"]
    .apply(classify_invoice_value)
)

print("\n5. INVOICE VALUE CATEGORY CREATED")


# --------------------------------------------------
# 6. Customer Payment Behaviour Score
# --------------------------------------------------

df["payment_behavior_score"] = (
    df["payment_reliability_score"] * 0.5
    +
    (100 - np.minimum(
        df["average_payment_delay"] * 2,
        100
    )) * 0.3
    +
    (100 - np.minimum(
        df["payment_failures"] * 10,
        100
    )) * 0.2
)

df["payment_behavior_score"] = (
    df["payment_behavior_score"]
    .clip(0, 100)
    .round(2)
)

print("\n6. PAYMENT BEHAVIOUR SCORE CREATED")


# --------------------------------------------------
# 7. Communication Effectiveness
# --------------------------------------------------

df["communication_effectiveness"] = (
    df["communication_count"] /
    (
        df["communication_count"]
        +
        df["last_contact_days"]
        +
        1
    )
)

df["communication_effectiveness"] = (
    df["communication_effectiveness"]
    .clip(0, 1)
    .round(3)
)

print("\n7. COMMUNICATION EFFECTIVENESS CREATED")


# --------------------------------------------------
# 8. Customer Value Score
# --------------------------------------------------

max_ltv = df[
    "customer_lifetime_value"
].max()

df["customer_value_score"] = (
    df["customer_lifetime_value"] /
    max_ltv
) * 100

df["customer_value_score"] = (
    df["customer_value_score"]
    .clip(0, 100)
    .round(2)
)

print("\n8. CUSTOMER VALUE SCORE CREATED")


# --------------------------------------------------
# 9. Overdue Risk Score
# --------------------------------------------------

overdue_component = np.minimum(
    df["days_overdue"] / 120,
    1
) * 100

late_component = (
    df["late_payment_ratio"] * 100
)

failure_component = np.minimum(
    df["payment_failures"] / 5,
    1
) * 100

df["overdue_risk_score"] = (
    overdue_component * 0.50
    +
    late_component * 0.30
    +
    failure_component * 0.20
)

df["overdue_risk_score"] = (
    df["overdue_risk_score"]
    .clip(0, 100)
    .round(2)
)

print("\n9. OVERDUE RISK SCORE CREATED")


# --------------------------------------------------
# 10. Recovery Potential Score
# --------------------------------------------------

reliability_factor = (
    df["payment_reliability_score"] / 100
)

communication_factor = (
    df["communication_effectiveness"]
)

risk_factor = (
    1 - df["overdue_risk_score"] / 100
)

df["recovery_potential_score"] = (
    (
        reliability_factor * 0.45
        +
        communication_factor * 0.20
        +
        risk_factor * 0.35
    ) * 100
)

df["recovery_potential_score"] = (
    df["recovery_potential_score"]
    .clip(0, 100)
    .round(2)
)

print("\n10. RECOVERY POTENTIAL SCORE CREATED")


# --------------------------------------------------
# 11. Expected Recovery Baseline
# --------------------------------------------------

df["expected_recovery_baseline"] = (
    df["invoice_amount"]
    *
    df["recovery_potential_score"]
    / 100
)

df["expected_recovery_baseline"] = (
    df["expected_recovery_baseline"]
    .round(2)
)

print("\n11. EXPECTED RECOVERY BASELINE CREATED")


# --------------------------------------------------
# 12. Recovery Priority Score
# --------------------------------------------------

df["recovery_priority_score"] = (
    df["expected_recovery_baseline"]
    *
    (
        1
        +
        df["days_overdue"] / 100
    )
)

df["recovery_priority_score"] = (
    df["recovery_priority_score"]
    .round(2)
)

print("\n12. RECOVERY PRIORITY SCORE CREATED")


# --------------------------------------------------
# 13. Select ML-ready features
# --------------------------------------------------

ml_features = [
    "invoice_amount",
    "days_overdue",
    "previous_payments",
    "previous_late_payments",
    "average_payment_delay",
    "payment_failures",
    "communication_count",
    "last_contact_days",
    "discount_used",
    "customer_lifetime_value",
    "payment_delay",
    "invoice_age",
    "late_payment_ratio",
    "payment_reliability_score",
    "payment_behavior_score",
    "communication_effectiveness",
    "customer_value_score",
    "overdue_risk_score",
    "recovery_potential_score",
    "expected_recovery_baseline",
    "recovery_priority_score"
]

print("\n13. ML FEATURES")
print("-" * 70)

for feature in ml_features:
    print("-", feature)


# --------------------------------------------------
# 14. Check missing values
# --------------------------------------------------

print("\n14. MISSING VALUES IN ML FEATURES")
print("-" * 70)

missing = df[ml_features].isnull().sum()

print(
    missing[missing > 0]
)


# --------------------------------------------------
# 15. Save feature-engineered dataset
# --------------------------------------------------

output_file = (
    "data/ml_ready_data.csv"
)

df.to_csv(
    output_file,
    index=False
)

print("\n15. ML-READY DATASET SAVED")
print("-" * 70)

print(output_file)


# --------------------------------------------------
# 16. Display important statistics
# --------------------------------------------------

print("\n16. FEATURE STATISTICS")
print("-" * 70)

print(
    df[
        [
            "payment_reliability_score",
            "payment_behavior_score",
            "overdue_risk_score",
            "recovery_potential_score",
            "expected_recovery_baseline",
            "recovery_priority_score"
        ]
    ].describe()
)


# --------------------------------------------------
# 17. Top recovery opportunities
# --------------------------------------------------

print("\n17. TOP 10 RECOVERY OPPORTUNITIES")
print("-" * 70)

top_opportunities = df[
    [
        "invoice_id",
        "customer_id",
        "invoice_amount",
        "days_overdue",
        "overdue_risk_score",
        "recovery_potential_score",
        "expected_recovery_baseline",
        "recovery_priority_score"
    ]
].sort_values(
    "recovery_priority_score",
    ascending=False
).head(10)

print(top_opportunities.to_string(index=False))


print("\n" + "=" * 70)
print("FEATURE ENGINEERING COMPLETED SUCCESSFULLY")
print("=" * 70)

