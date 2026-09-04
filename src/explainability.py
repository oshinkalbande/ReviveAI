import pandas as pd


def explain_recovery_case(row):

    reasons = []
    positive_signals = []
    negative_signals = []

    days_overdue = float(row.get("days_overdue", 0))
    payment_failures = int(row.get("payment_failures", 0))
    previous_late_payments = int(row.get("previous_late_payments", 0))
    communication_count = int(row.get("communication_count", 0))
    last_contact_days = float(row.get("last_contact_days", 0))
    recovery_probability = float(row.get("recovery_probability", 0))
    invoice_amount = float(row.get("invoice_amount", 0))
    customer_lifetime_value = float(
        row.get("customer_lifetime_value", 0)
    )

    # -----------------------------
    # RISK SIGNALS
    # -----------------------------

    if days_overdue <= 0:

        reasons.append(
            "Invoice is currently not overdue."
        )

    elif days_overdue <= 30:

        reasons.append(
            f"Invoice is {int(days_overdue)} days overdue."
        )

    elif days_overdue <= 60:

        reasons.append(
            f"Invoice is moderately overdue ({int(days_overdue)} days)."
        )

    elif days_overdue <= 90:

        reasons.append(
            f"Invoice is significantly overdue ({int(days_overdue)} days)."
        )

    else:

        reasons.append(
            f"Invoice is severely overdue ({int(days_overdue)} days)."
        )

        negative_signals.append(
            "Long overdue period increases recovery risk."
        )

    if previous_late_payments >= 3:

        negative_signals.append(
            f"Customer has {previous_late_payments} previous late payments."
        )

    elif previous_late_payments > 0:

        negative_signals.append(
            f"Customer has {previous_late_payments} previous late payment(s)."
        )

    else:

        positive_signals.append(
            "Customer has no recorded previous late payments."
        )

    if payment_failures >= 3:

        negative_signals.append(
            f"Customer has experienced {payment_failures} payment failures."
        )

    elif payment_failures > 0:

        negative_signals.append(
            f"Customer has {payment_failures} previous payment failure(s)."
        )

    else:

        positive_signals.append(
            "No previous payment failures recorded."
        )

    if last_contact_days > 14:

        negative_signals.append(
            f"Customer has not been contacted for {int(last_contact_days)} days."
        )

    elif last_contact_days <= 7:

        positive_signals.append(
            "Customer has been contacted recently."
        )

    if recovery_probability >= 0.70:

        positive_signals.append(
            f"High predicted recovery probability ({recovery_probability:.1%})."
        )

    elif recovery_probability >= 0.50:

        positive_signals.append(
            f"Moderate predicted recovery probability ({recovery_probability:.1%})."
        )

    else:

        negative_signals.append(
            f"Low predicted recovery probability ({recovery_probability:.1%})."
        )

    # -----------------------------
    # VALUE SIGNAL
    # -----------------------------

    if invoice_amount >= 200000:

        reasons.append(
            f"High-value invoice worth ₹{invoice_amount:,.0f}."
        )

    if customer_lifetime_value >= 1000000:

        positive_signals.append(
            "Customer has high lifetime value."
        )

    # -----------------------------
    # ACTION EXPLANATION
    # -----------------------------

    if days_overdue <= 0:

        action_reason = (
            "The invoice is current, so ReviveAI recommends monitoring "
            "it rather than initiating recovery escalation."
        )

    elif days_overdue > 90 and recovery_probability < 0.50:

        action_reason = (
            "The invoice is severely overdue and has relatively low "
            "recovery probability, so human intervention is recommended."
        )

    elif days_overdue > 60:

        action_reason = (
            "The invoice has been overdue for a significant period. "
            "ReviveAI recommends urgent follow-up to prevent further revenue loss."
        )

    elif payment_failures >= 3:

        action_reason = (
            "Repeated payment failures indicate a potential payment "
            "problem. ReviveAI recommends direct customer assistance."
        )

    elif days_overdue > 30:

        action_reason = (
            "The invoice is moderately overdue, so a personalized "
            "payment reminder is recommended."
        )

    else:

        action_reason = (
            "The invoice is recently overdue, so an automated payment "
            "reminder is appropriate."
        )

    return {
        "risk_reasons": reasons,
        "positive_signals": positive_signals,
        "negative_signals": negative_signals,
        "action_reason": action_reason
    }


if __name__ == "__main__":

    print("=" * 60)
    print("REVIVEAI - EXPLAINABILITY ENGINE")
    print("=" * 60)

    try:

        df = pd.read_csv(
            "outputs/recovery_opportunities.csv"
        )

        overdue_df = df[df["days_overdue"] > 0]

        if overdue_df.empty:

            print("No overdue recovery opportunities found.")

        else:

            row = overdue_df.sort_values(
                "priority_score",
                ascending=False
            ).iloc[0]

            explanation = explain_recovery_case(row)

            print("\nSELECTED CASE")
            print("-" * 60)

            print(
                f"Invoice ID: {row['invoice_id']}"
            )

            print(
                f"Invoice Amount: ₹{row['invoice_amount']:,.2f}"
            )

            print(
                f"Days Overdue: {int(row['days_overdue'])}"
            )

            print(
                f"Recovery Probability: "
                f"{row['recovery_probability']:.2%}"
            )

            print("\nWHY IS THIS CASE IMPORTANT?")

            for reason in explanation["risk_reasons"]:
                print(f"• {reason}")

            print("\nPOSITIVE SIGNALS")

            for signal in explanation["positive_signals"]:
                print(f"✓ {signal}")

            print("\nNEGATIVE SIGNALS")

            for signal in explanation["negative_signals"]:
                print(f"⚠ {signal}")

            print("\nWHY THIS ACTION?")

            print(explanation["action_reason"])

            print("\nSTEP 17 COMPLETED SUCCESSFULLY")

    except FileNotFoundError:

        print(
            "Recovery opportunities file not found."
        )

        print(
            "Run database_recovery_engine.py first."
        )