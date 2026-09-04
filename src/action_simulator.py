import pandas as pd


def simulate_actions(row):
    """
    Simulates different revenue recovery strategies
    for a selected invoice.
    """

    invoice_amount = float(row["invoice_amount"])
    current_probability = float(row["recovery_probability"])

    days_overdue = int(row["days_overdue"])
    payment_failures = int(row["payment_failures"])

    results = []

    # ---------------------------------------------------------
    # 1. DO NOTHING
    # ---------------------------------------------------------

    do_nothing_probability = max(
        0.05,
        current_probability - 0.15
    )

    results.append({
        "Action": "Do Nothing",
        "Recovery Probability": do_nothing_probability,
        "Discount": 0,
        "Expected Recovery": invoice_amount * do_nothing_probability
    })

    # ---------------------------------------------------------
    # 2. AUTOMATED REMINDER
    # ---------------------------------------------------------

    automated_probability = min(
        0.95,
        current_probability + 0.05
    )

    results.append({
        "Action": "Automated Payment Reminder",
        "Recovery Probability": automated_probability,
        "Discount": 0,
        "Expected Recovery": invoice_amount * automated_probability
    })

    # ---------------------------------------------------------
    # 3. PERSONALIZED REMINDER
    # ---------------------------------------------------------

    personalized_probability = min(
        0.95,
        current_probability + 0.10
    )

    results.append({
        "Action": "Personalized Payment Reminder",
        "Recovery Probability": personalized_probability,
        "Discount": 0,
        "Expected Recovery": invoice_amount * personalized_probability
    })

    # ---------------------------------------------------------
    # 4. PAYMENT ASSISTANCE
    # ---------------------------------------------------------

    assistance_probability = min(
        0.95,
        current_probability + 0.15
    )

    results.append({
        "Action": "Payment Assistance",
        "Recovery Probability": assistance_probability,
        "Discount": 0,
        "Expected Recovery": invoice_amount * assistance_probability
    })

    # ---------------------------------------------------------
    # 5. 5% DISCOUNT + REMINDER
    # ---------------------------------------------------------

    discount = 0.05

    discount_probability = min(
        0.95,
        current_probability + 0.18
    )

    discounted_amount = invoice_amount * (1 - discount)

    results.append({
        "Action": "5% Discount + Personalized Reminder",
        "Recovery Probability": discount_probability,
        "Discount": discount * 100,
        "Expected Recovery": discounted_amount * discount_probability
    })

    # ---------------------------------------------------------
    # CREATE DATAFRAME
    # ---------------------------------------------------------

    results_df = pd.DataFrame(results)

    # Calculate improvement against doing nothing

    baseline = results_df.loc[
        results_df["Action"] == "Do Nothing",
        "Expected Recovery"
    ].iloc[0]

    results_df["Recovery Improvement"] = (
        results_df["Expected Recovery"] - baseline
    )

    # ---------------------------------------------------------
    # FIND BEST ACTION
    # ---------------------------------------------------------

    best_action = results_df.loc[
        results_df["Expected Recovery"].idxmax()
    ]

    return results_df, best_action


# ---------------------------------------------------------
# TEST THE SIMULATOR
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("REVIVEAI - RECOVERY ACTION SIMULATOR")
    print("=" * 60)

    # Load recovery opportunities
    file_path = "outputs/recovery_opportunities.csv"

    df = pd.read_csv(file_path)

    # Select overdue invoices
    overdue_df = df[df["days_overdue"] > 0].copy()

    if overdue_df.empty:

        print("No overdue invoices found.")

    else:

        # Select highest expected recovery opportunity
        row = overdue_df.loc[
            overdue_df["expected_recovery"].idxmax()
        ]

        print("\nSELECTED INVOICE")
        print("-" * 60)

        print(f"Invoice ID: {row['invoice_id']}")
        print(
            f"Invoice Amount: ₹{row['invoice_amount']:,.2f}"
        )
        print(
            f"Days Overdue: {row['days_overdue']}"
        )
        print(
            f"Current Recovery Probability: "
            f"{row['recovery_probability_percent']:.2f}%"
        )

        results, best_action = simulate_actions(row)

        print("\nACTION SIMULATION")
        print("-" * 60)

        for _, result in results.iterrows():

            print(
                f"{result['Action']} | "
                f"Probability: "
                f"{result['Recovery Probability'] * 100:.2f}% | "
                f"Expected Recovery: "
                f"₹{result['Expected Recovery']:,.2f}"
            )

        print("\nBEST ACTION")
        print("-" * 60)

        print(
            f"Recommended Strategy: "
            f"{best_action['Action']}"
        )

        print(
            f"Expected Recovery: "
            f"₹{best_action['Expected Recovery']:,.2f}"
        )

        print(
            f"Recovery Improvement: "
            f"₹{best_action['Recovery Improvement']:,.2f}"
        )

        print("\nSTEP 19 COMPLETED SUCCESSFULLY")