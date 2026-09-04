import os
import sys

import pandas as pd
import joblib

# ==================================================
# IMPORT DATABASE MODULE
# ==================================================

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

from database import (
    SessionLocal,
    RecoveryOpportunity,
    create_tables
)


# ==================================================
# PROJECT PATHS
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "ml_ready_data.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "recovery_model.pkl"
)

FEATURE_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model_features.pkl"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "outputs",
    "recovery_opportunities.csv"
)


# ==================================================
# HEADER
# ==================================================

print()
print("=" * 55)
print("REVIVEAI - DATABASE RECOVERY ENGINE")
print("=" * 55)


# ==================================================
# LOAD ML DATA
# ==================================================

print()
print("Loading ML-ready data...")

df = pd.read_csv(DATA_PATH)

print(f"Records loaded: {len(df)}")


# ==================================================
# LOAD MODEL
# ==================================================

print()
print("Loading recovery prediction model...")

model = joblib.load(MODEL_PATH)

model_features = joblib.load(FEATURE_PATH)

print("Model loaded successfully.")
print(f"Features used: {len(model_features)}")


# ==================================================
# PREPARE ML FEATURES
# ==================================================

X = df[model_features].copy()

X = X.replace(
    [float("inf"), float("-inf")],
    0
)

X = X.fillna(0)


# ==================================================
# PREDICT RECOVERY PROBABILITY
# ==================================================

print()
print("Predicting recovery probability...")

df["recovery_probability"] = (
    model.predict_proba(X)[:, 1]
)

df["recovery_probability_percent"] = (
    df["recovery_probability"] * 100
).round(2)


# ==================================================
# EXPECTED RECOVERY
# ==================================================

df["expected_recovery"] = (
    df["invoice_amount"]
    * df["recovery_probability"]
)


# ==================================================
# OVERDUE STATUS
# ==================================================

def get_overdue_status(days):

    if days <= 0:
        return "Current"

    elif days <= 30:
        return "1-30 Days"

    elif days <= 60:
        return "31-60 Days"

    elif days <= 90:
        return "61-90 Days"

    elif days <= 180:
        return "91-180 Days"

    else:
        return "180+ Days"


df["overdue_status"] = (
    df["days_overdue"]
    .apply(get_overdue_status)
)


# ==================================================
# OVERDUE FLAG
# ==================================================

df["overdue_invoice"] = (
    df["days_overdue"] > 0
)


# ==================================================
# RISK LEVEL
# ==================================================

def determine_risk(row):

    days = row["days_overdue"]

    probability = row[
        "recovery_probability"
    ]

    payment_failures = row[
        "payment_failures"
    ]

    # ----------------------------------------------
    # CURRENT
    # ----------------------------------------------

    if days <= 0:
        return "Current"

    # ----------------------------------------------
    # CRITICAL
    # ----------------------------------------------

    if days > 180 and probability < 0.45:
        return "Critical"

    if days > 120 and probability < 0.35:
        return "Critical"

    if days > 90 and probability < 0.30:
        return "Critical"

    # ----------------------------------------------
    # HIGH
    # ----------------------------------------------

    if days > 90:
        return "High"

    if days > 60 and probability < 0.60:
        return "High"

    if days > 60 and payment_failures >= 3:
        return "High"

    # ----------------------------------------------
    # MEDIUM
    # ----------------------------------------------

    if days > 30:
        return "Medium"

    if probability < 0.50:
        return "Medium"

    if payment_failures >= 2:
        return "Medium"

    # ----------------------------------------------
    # LOW
    # ----------------------------------------------

    return "Low"


df["risk_level"] = df.apply(
    determine_risk,
    axis=1
)


# ==================================================
# URGENCY SCORE
# ==================================================

def calculate_urgency(days):

    if days <= 0:
        return 0

    elif days <= 30:
        return 20

    elif days <= 60:
        return 40

    elif days <= 90:
        return 60

    elif days <= 180:
        return 80

    else:
        return 100


df["urgency_score"] = (
    df["days_overdue"]
    .apply(calculate_urgency)
)


# ==================================================
# RECOVERY VALUE SCORE
# ==================================================

# Expected recovery is important, but it should
# NOT alone determine whether an invoice is High.
#
# We normalize expected recovery among overdue
# invoices so it can be used as a secondary signal.

overdue_mask = (
    df["days_overdue"] > 0
)

df["recovery_value_score"] = 0.0

if overdue_mask.any():

    max_expected_recovery = (
        df.loc[
            overdue_mask,
            "expected_recovery"
        ].max()
    )

    if max_expected_recovery > 0:

        df.loc[
            overdue_mask,
            "recovery_value_score"
        ] = (
            df.loc[
                overdue_mask,
                "expected_recovery"
            ]
            / max_expected_recovery
            * 100
        )


# ==================================================
# PRIORITY SCORE
# ==================================================

# Priority is primarily driven by:
#
# 1. Expected recovery
# 2. Urgency
#
# But current invoices are always excluded.

df["priority_score"] = 0.0

df.loc[
    overdue_mask,
    "priority_score"
] = (
    df.loc[
        overdue_mask,
        "expected_recovery"
    ]
    * (
        1
        + df.loc[
            overdue_mask,
            "urgency_score"
        ] / 100
    )
)


# ==================================================
# NORMALIZED PRIORITY
# ==================================================

df["normalized_priority"] = 0.0

if overdue_mask.any():

    max_priority = (
        df.loc[
            overdue_mask,
            "priority_score"
        ].max()
    )

    if max_priority > 0:

        df.loc[
            overdue_mask,
            "normalized_priority"
        ] = (
            df.loc[
                overdue_mask,
                "priority_score"
            ]
            / max_priority
            * 100
        )


# ==================================================
# BUSINESS PRIORITY CATEGORY
# ==================================================

def determine_priority(row):

    days = row["days_overdue"]

    probability = row[
        "recovery_probability"
    ]

    payment_failures = row[
        "payment_failures"
    ]

    risk = row["risk_level"]

    # ----------------------------------------------
    # CURRENT
    # ----------------------------------------------

    if days <= 0:
        return "Monitor"

    # ----------------------------------------------
    # CRITICAL
    # ----------------------------------------------

    if risk == "Critical":
        return "Critical"

    # ----------------------------------------------
    # HIGH
    # ----------------------------------------------

    if days > 90:
        return "High"

    if days > 60 and (
        probability < 0.60
        or payment_failures >= 3
    ):
        return "High"

    # ----------------------------------------------
    # MEDIUM
    # ----------------------------------------------

    if days > 30:
        return "Medium"

    if payment_failures >= 2:
        return "Medium"

    # ----------------------------------------------
    # LOW
    # ----------------------------------------------

    return "Low"


df["priority_category"] = df.apply(
    determine_priority,
    axis=1
)


# ==================================================
# RECOMMENDED ACTION
# ==================================================

def recommend_action(row):

    days = row["days_overdue"]

    probability = row[
        "recovery_probability"
    ]

    failures = row[
        "payment_failures"
    ]

    amount = row[
        "invoice_amount"
    ]

    risk = row["risk_level"]

    # ----------------------------------------------
    # CURRENT
    # ----------------------------------------------

    if days <= 0:

        return (
            "Monitor and schedule follow-up"
        )

    # ----------------------------------------------
    # CRITICAL
    # ----------------------------------------------

    if risk == "Critical":

        return (
            "Escalate to human recovery team"
        )

    # ----------------------------------------------
    # PAYMENT FAILURES
    # ----------------------------------------------

    if failures >= 3:

        return (
            "Contact customer and offer payment assistance"
        )

    # ----------------------------------------------
    # VERY OLD INVOICE
    # ----------------------------------------------

    if days > 180:

        return (
            "Priority human follow-up"
        )

    if days > 90:

        return (
            "Priority human follow-up"
        )

    # ----------------------------------------------
    # LARGE 60+ DAY OVERDUE
    # ----------------------------------------------

    if days > 60:

        return (
            "Send urgent payment reminder"
        )

    # ----------------------------------------------
    # 30+ DAYS
    # ----------------------------------------------

    if days > 30:

        return (
            "Send personalized payment reminder"
        )

    # ----------------------------------------------
    # 1-30 DAYS
    # ----------------------------------------------

    if probability >= 0.70:

        return (
            "Send automated payment reminder"
        )

    return (
        "Send payment reminder"
    )


df["recommended_action"] = df.apply(
    recommend_action,
    axis=1
)


# ==================================================
# POTENTIAL LOSS
# ==================================================

df["potential_loss"] = (
    df["invoice_amount"]
    - df["expected_recovery"]
)

df["potential_loss"] = (
    df["potential_loss"]
    .clip(lower=0)
)


# ==================================================
# RECOVERY OPPORTUNITY
# ==================================================

df["recovery_opportunity"] = (
    df["days_overdue"] > 0
)


# ==================================================
# SAVE CSV
# ==================================================

print()
print("Saving recovery analysis...")

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print(
    f"CSV saved: {OUTPUT_PATH}"
)


# ==================================================
# CONNECT DATABASE
# ==================================================

print()
print("Connecting to SQLite database...")

create_tables()

session = SessionLocal()


# ==================================================
# REMOVE OLD RECOVERY RESULTS
# ==================================================

session.query(
    RecoveryOpportunity
).delete()

session.commit()


# ==================================================
# INSERT RECOVERY RESULTS
# ==================================================

records = []

for _, row in df.iterrows():

    opportunity = RecoveryOpportunity(

        customer_id=str(
            row["customer_id"]
        ),

        invoice_id=str(
            row["invoice_id"]
        ),

        invoice_amount=float(
            row["invoice_amount"]
        ),

        days_overdue=int(
            row["days_overdue"]
        ),

        recovery_probability=float(
            row["recovery_probability"]
        ),

        recovery_probability_percent=float(
            row["recovery_probability_percent"]
        ),

        expected_recovery=float(
            row["expected_recovery"]
        ),

        potential_loss=float(
            row["potential_loss"]
        ),

        risk_level=str(
            row["risk_level"]
        ),

        priority_score=float(
            row["priority_score"]
        ),

        priority_category=str(
            row["priority_category"]
        ),

        recommended_action=str(
            row["recommended_action"]
        ),

        customer_segment=str(
            row["customer_segment"]
        ),

        customer_lifetime_value=float(
            row["customer_lifetime_value"]
        )
    )

    records.append(opportunity)


session.add_all(records)

session.commit()


# ==================================================
# BUSINESS SUMMARY
# ==================================================

overdue_df = df[
    df["days_overdue"] > 0
].copy()

current_df = df[
    df["days_overdue"] <= 0
].copy()


high_critical_df = overdue_df[
    overdue_df[
        "priority_category"
    ].isin(
        ["High", "Critical"]
    )
]


print()
print("=" * 55)
print("REVIVEAI BUSINESS SUMMARY")
print("=" * 55)

print()

print(
    f"Total invoices: {len(df)}"
)

print(
    f"Current invoices: {len(current_df)}"
)

print(
    f"Overdue invoices: {len(overdue_df)}"
)

print(
    f"Total invoice value: "
    f"₹{df['invoice_amount'].sum():,.2f}"
)

print(
    f"Expected recovery from overdue invoices: "
    f"₹{overdue_df['expected_recovery'].sum():,.2f}"
)

print(
    f"Potential revenue at risk: "
    f"₹{overdue_df['potential_loss'].sum():,.2f}"
)

print(
    f"High/Critical overdue invoices: "
    f"{len(high_critical_df)}"
)

print(
    f"Database records created: "
    f"{len(records)}"
)


# ==================================================
# RISK DISTRIBUTION
# ==================================================

print()
print("RISK DISTRIBUTION")
print("-" * 30)

print(
    df["risk_level"]
    .value_counts()
)


# ==================================================
# PRIORITY DISTRIBUTION
# ==================================================

print()
print("PRIORITY DISTRIBUTION")
print("-" * 30)

print(
    df["priority_category"]
    .value_counts()
)


# ==================================================
# TOP RECOVERY OPPORTUNITIES
# ==================================================

print()
print("TOP 10 RECOVERY OPPORTUNITIES")
print("-" * 55)

top_opportunities = (
    overdue_df
    .sort_values(
        by=[
            "priority_score",
            "expected_recovery"
        ],
        ascending=False
    )
    .head(10)
)


for _, row in top_opportunities.iterrows():

    print(
        f"{row['invoice_id']} | "
        f"₹{row['invoice_amount']:,.2f} | "
        f"{int(row['days_overdue'])} days overdue | "
        f"{row['recovery_probability_percent']:.2f}% recovery | "
        f"{row['risk_level']} | "
        f"{row['priority_category']} | "
        f"{row['recommended_action']}"
    )


# ==================================================
# DATABASE COUNT
# ==================================================

database_count = session.query(
    RecoveryOpportunity
).count()

session.close()


print()
print(
    f"Recovery records in database: "
    f"{database_count}"
)

print()
print("=" * 55)
print("STEP 13.1 COMPLETED SUCCESSFULLY")
print("=" * 55)