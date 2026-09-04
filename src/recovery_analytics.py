import pandas as pd
from sqlalchemy import text
from src.database import engine


def get_recovery_analytics():
    """
    Calculate overall recovery analytics.
    """

    query = """
        SELECT
            rt.id,
            rt.invoice_id,
            rt.customer_id,
            rt.recommended_action,
            rt.actual_action,
            rt.action_date,
            rt.recovery_status,
            rt.recovered_amount,
            rt.recovery_date,
            rt.next_followup_date,
            ro.invoice_amount,
            ro.expected_recovery,
            ro.recovery_probability,
            ro.risk_level,
            ro.priority_category
        FROM recovery_tracking rt
        LEFT JOIN recovery_opportunities ro
        ON rt.invoice_id = ro.invoice_id
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return {
            "total_actions": 0,
            "successful_recoveries": 0,
            "revenue_recovered": 0,
            "expected_recovery": 0,
            "recovery_gap": 0,
            "recovery_rate": 0,
            "data": df
        }

    df["recovered_amount"] = (
        pd.to_numeric(
            df["recovered_amount"],
            errors="coerce"
        ).fillna(0)
    )

    df["invoice_amount"] = (
        pd.to_numeric(
            df["invoice_amount"],
            errors="coerce"
        ).fillna(0)
    )

    df["expected_recovery"] = (
        pd.to_numeric(
            df["expected_recovery"],
            errors="coerce"
        ).fillna(0)
    )

    total_actions = len(df)

    successful_recoveries = len(
        df[
            df["recovery_status"].isin(
                [
                    "Recovered",
                    "Partially Recovered"
                ]
            )
            & (df["recovered_amount"] > 0)
        ]
    )

    revenue_recovered = df["recovered_amount"].sum()

    expected_recovery = df["expected_recovery"].sum()

    recovery_gap = expected_recovery - revenue_recovered

    tracked_invoice_value = df["invoice_amount"].sum()

    if tracked_invoice_value > 0:
        recovery_rate = (
            revenue_recovered
            / tracked_invoice_value
            * 100
        )
    else:
        recovery_rate = 0

    return {
        "total_actions": total_actions,
        "successful_recoveries": successful_recoveries,
        "revenue_recovered": revenue_recovered,
        "expected_recovery": expected_recovery,
        "recovery_gap": recovery_gap,
        "recovery_rate": recovery_rate,
        "data": df
    }


def get_action_performance():
    """
    Analyze recovery performance by actual action.
    """

    query = """
        SELECT
            rt.actual_action,
            COUNT(*) AS total_actions,
            SUM(
                CASE
                    WHEN rt.recovered_amount > 0
                    THEN 1
                    ELSE 0
                END
            ) AS successful_recoveries,
            SUM(rt.recovered_amount) AS revenue_recovered,
            AVG(rt.recovered_amount) AS average_recovered_amount
        FROM recovery_tracking rt
        GROUP BY rt.actual_action
        ORDER BY revenue_recovered DESC
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return df

    df["success_rate"] = (
        df["successful_recoveries"]
        / df["total_actions"]
        * 100
    )

    return df


def get_status_distribution():
    """
    Return distribution of recovery statuses.
    """

    query = """
        SELECT
            recovery_status,
            COUNT(*) AS count
        FROM recovery_tracking
        GROUP BY recovery_status
        ORDER BY count DESC
    """

    return pd.read_sql(query, engine)


def get_recovery_trend():
    """
    Return recovery revenue trend by date.
    """

    query = """
        SELECT
            recovery_date,
            SUM(recovered_amount) AS recovered_amount
        FROM recovery_tracking
        WHERE recovery_date IS NOT NULL
        GROUP BY recovery_date
        ORDER BY recovery_date
    """

    return pd.read_sql(query, engine)


if __name__ == "__main__":

    print("=" * 60)
    print("REVIVEAI - RECOVERY ANALYTICS")
    print("=" * 60)

    analytics = get_recovery_analytics()

    print("\nOVERALL RECOVERY PERFORMANCE")
    print("-" * 60)

    print(
        f"Total Actions: "
        f"{analytics['total_actions']}"
    )

    print(
        f"Successful Recoveries: "
        f"{analytics['successful_recoveries']}"
    )

    print(
        f"Revenue Recovered: "
        f"₹{analytics['revenue_recovered']:,.2f}"
    )

    print(
        f"Expected Recovery: "
        f"₹{analytics['expected_recovery']:,.2f}"
    )

    print(
        f"Recovery Gap: "
        f"₹{analytics['recovery_gap']:,.2f}"
    )

    print(
        f"Actual Recovery Rate: "
        f"{analytics['recovery_rate']:.2f}%"
    )

    print("\nACTION PERFORMANCE")
    print("-" * 60)

    action_data = get_action_performance()

    if action_data.empty:
        print("No action performance data available.")
    else:
        print(action_data.to_string(index=False))

    print("\nSTATUS DISTRIBUTION")
    print("-" * 60)

    status_data = get_status_distribution()

    if status_data.empty:
        print("No recovery status data available.")
    else:
        print(status_data.to_string(index=False))

    print("\nSTEP 23.1 COMPLETED SUCCESSFULLY")