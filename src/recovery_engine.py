import pandas as pd
import numpy as np
import joblib


# ============================================================
# REVIVEAI - AI REVENUE RECOVERY DECISION ENGINE
# ============================================================

print("=" * 70)
print("REVIVEAI - AI REVENUE RECOVERY DECISION ENGINE")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "data/ml_ready_data.csv"
MODEL_PATH = "models/recovery_model.pkl"
FEATURE_PATH = "models/model_features.pkl"

df = pd.read_csv(DATA_PATH)

model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURE_PATH)

print("\nData loaded successfully.")
print("Total invoices:", len(df))


# ============================================================
# 2. PREPARE FEATURES
# ============================================================

X = df[model_features].copy()

# Handle infinite values
X = X.replace([np.inf, -np.inf], np.nan)

# Fill missing values
X = X.fillna(X.median(numeric_only=True))

print("Features prepared:", len(model_features))


# ============================================================
# 3. PREDICT RECOVERY PROBABILITY
# ============================================================

recovery_probability = model.predict_proba(X)[:, 1]

df["recovery_probability"] = recovery_probability

df["recovery_probability_percent"] = (
    recovery_probability * 100
).round(2)


# ============================================================
# 4. CALCULATE EXPECTED RECOVERY
# ============================================================

df["expected_recovery"] = (
    df["invoice_amount"] *
    df["recovery_probability"]
)

df["expected_recovery"] = df["expected_recovery"].round(2)


# ============================================================
# 5. CALCULATE POTENTIAL LOSS
# ============================================================

df["potential_loss"] = (
    df["invoice_amount"] -
    df["expected_recovery"]
)

df["potential_loss"] = df["potential_loss"].clip(lower=0).round(2)


# ============================================================
# 6. CREATE RISK LEVEL
# ============================================================

def calculate_risk(probability, days_overdue):

    if days_overdue > 90 and probability < 0.40:
        return "Critical"

    elif days_overdue > 60 and probability < 0.55:
        return "High"

    elif days_overdue > 30 or probability < 0.65:
        return "Medium"

    else:
        return "Low"


df["risk_level"] = df.apply(
    lambda row: calculate_risk(
        row["recovery_probability"],
        row["days_overdue"]
    ),
    axis=1
)


# ============================================================
# 7. CALCULATE URGENCY SCORE
# ============================================================

df["urgency_score"] = (
    df["days_overdue"].clip(upper=180) / 180
) * 100

df["urgency_score"] = df["urgency_score"].round(2)


# ============================================================
# 8. CALCULATE REVENUE PRIORITY SCORE
# ============================================================

# Higher expected recovery + higher urgency
# = higher business priority

df["priority_score"] = (
    df["expected_recovery"] *
    (1 + df["urgency_score"] / 100)
)

df["priority_score"] = df["priority_score"].round(2)


# ============================================================
# 9. NORMALIZED PRIORITY SCORE
# ============================================================

max_priority = df["priority_score"].max()

if max_priority > 0:
    df["priority_score_normalized"] = (
        df["priority_score"] / max_priority
    ) * 100
else:
    df["priority_score_normalized"] = 0

df["priority_score_normalized"] = (
    df["priority_score_normalized"].round(2)
)


# ============================================================
# 10. RECOMMEND RECOVERY ACTION
# ============================================================

def recommend_action(row):

    probability = row["recovery_probability"]
    days_overdue = row["days_overdue"]
    amount = row["invoice_amount"]
    failures = row["payment_failures"]

    # Very old + low recovery probability
    if days_overdue > 90 and probability < 0.40:
        return "Escalate to human recovery team"

    # High-value invoice
    elif amount >= 500000 and probability >= 0.60:
        return "Priority human follow-up"

    # Payment failures
    elif failures >= 3:
        return "Contact customer and offer payment assistance"

    # Very overdue
    elif days_overdue > 60:
        return "Send urgent payment reminder"

    # Moderately overdue
    elif days_overdue > 30:
        return "Send personalized payment reminder"

    # Good probability
    elif probability >= 0.75:
        return "Send automated payment reminder"

    else:
        return "Monitor and schedule follow-up"


df["recommended_action"] = df.apply(
    recommend_action,
    axis=1
)


# ============================================================
# 11. CREATE PRIORITY CATEGORY
# ============================================================

def priority_category(score):

    if score >= 70:
        return "Critical Priority"

    elif score >= 45:
        return "High Priority"

    elif score >= 20:
        return "Medium Priority"

    else:
        return "Low Priority"


df["priority_category"] = df[
    "priority_score_normalized"
].apply(priority_category)


# ============================================================
# 12. CREATE RECOVERY OPPORTUNITY FLAG
# ============================================================

df["recovery_opportunity"] = np.where(
    (
        (df["expected_recovery"] > 10000) &
        (df["days_overdue"] > 0)
    ),
    "Yes",
    "No"
)


# ============================================================
# 13. SORT BY PRIORITY
# ============================================================

df = df.sort_values(
    by="priority_score",
    ascending=False
)


# ============================================================
# 14. SELECT IMPORTANT COLUMNS
# ============================================================

output_columns = [
    "customer_id",
    "invoice_id",
    "invoice_amount",
    "days_overdue",
    "payment_status",
    "recovery_probability",
    "recovery_probability_percent",
    "expected_recovery",
    "potential_loss",
    "risk_level",
    "urgency_score",
    "priority_score",
    "priority_score_normalized",
    "priority_category",
    "recommended_action",
    "recovery_opportunity",
    "customer_segment",
    "customer_lifetime_value"
]

output_df = df[output_columns].copy()


# ============================================================
# 15. SAVE OUTPUT
# ============================================================

OUTPUT_PATH = "outputs/recovery_opportunities.csv"

output_df.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nRecovery opportunity file created:")
print(OUTPUT_PATH)


# ============================================================
# 16. BUSINESS SUMMARY
# ============================================================

total_invoice_value = df["invoice_amount"].sum()

total_expected_recovery = df[
    "expected_recovery"
].sum()

total_potential_loss = df[
    "potential_loss"
].sum()

high_priority = (
    df["priority_category"]
    .isin(["Critical Priority", "High Priority"])
    .sum()
)

critical_count = (
    df["priority_category"] ==
    "Critical Priority"
).sum()


print("\n" + "=" * 70)
print("REVIVEAI BUSINESS SUMMARY")
print("=" * 70)

print(
    f"\nTotal Invoice Value: "
    f"₹{total_invoice_value:,.2f}"
)

print(
    f"Expected Recoverable Revenue: "
    f"₹{total_expected_recovery:,.2f}"
)

print(
    f"Potential Revenue at Risk: "
    f"₹{total_potential_loss:,.2f}"
)

print(
    f"High/Critical Priority Invoices: "
    f"{high_priority}"
)

print(
    f"Critical Priority Invoices: "
    f"{critical_count}"
)


# ============================================================
# 17. TOP 20 RECOVERY OPPORTUNITIES
# ============================================================

print("\n" + "=" * 70)
print("TOP 20 RECOVERY OPPORTUNITIES")
print("=" * 70)

top_20 = output_df.head(20)[[
    "invoice_id",
    "invoice_amount",
    "days_overdue",
    "recovery_probability_percent",
    "expected_recovery",
    "risk_level",
    "priority_category",
    "recommended_action"
]]

print(
    top_20.to_string(index=False)
)


# ============================================================
# 18. RISK DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("RISK DISTRIBUTION")
print("=" * 70)

print(
    output_df["risk_level"]
    .value_counts()
)


# ============================================================
# 19. ACTION DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("RECOMMENDED ACTION DISTRIBUTION")
print("=" * 70)

print(
    output_df["recommended_action"]
    .value_counts()
)


# ============================================================
# 20. FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("STEP 9 COMPLETED SUCCESSFULLY!")
print("=" * 70)

print("\nReviveAI can now:")
print("✓ Predict recovery probability")
print("✓ Estimate recoverable revenue")
print("✓ Identify revenue at risk")
print("✓ Calculate urgency")
print("✓ Rank recovery opportunities")
print("✓ Assign risk levels")
print("✓ Recommend recovery actions")