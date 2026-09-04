import pandas as pd
from datetime import datetime
from sqlalchemy import text

from src.database import engine


# --------------------------------------------------
# ADD RECOVERY ACTION
# --------------------------------------------------

def add_recovery_action(
    invoice_id,
    customer_id,
    recommended_action,
    actual_action,
    recovery_status,
    recovered_amount=0,
    recovery_date=None,
    next_followup_date=None,
    notes=""
):
    """
    Records a recovery action taken for an invoice.
    """

    action_date = datetime.now().strftime("%Y-%m-%d")

    query = text(
        """
        INSERT INTO recovery_tracking
        (
            invoice_id,
            customer_id,
            recommended_action,
            actual_action,
            action_date,
            recovery_status,
            recovered_amount,
            recovery_date,
            next_followup_date,
            notes
        )
        VALUES
        (
            :invoice_id,
            :customer_id,
            :recommended_action,
            :actual_action,
            :action_date,
            :recovery_status,
            :recovered_amount,
            :recovery_date,
            :next_followup_date,
            :notes
        )
        """
    )

    with engine.begin() as connection:

        connection.execute(
            query,
            {
                "invoice_id": invoice_id,
                "customer_id": customer_id,
                "recommended_action": recommended_action,
                "actual_action": actual_action,
                "action_date": action_date,
                "recovery_status": recovery_status,
                "recovered_amount": recovered_amount,
                "recovery_date": recovery_date,
                "next_followup_date": next_followup_date,
                "notes": notes,
            }
        )

    print("Recovery action recorded successfully.")


# --------------------------------------------------
# GET ALL RECOVERY TRACKING RECORDS
# --------------------------------------------------

def get_recovery_tracking():

    query = """
        SELECT *
        FROM recovery_tracking
        ORDER BY id DESC
    """

    return pd.read_sql(
        query,
        engine
    )


# --------------------------------------------------
# GET HISTORY FOR ONE INVOICE
# --------------------------------------------------

def get_invoice_history(invoice_id):

    query = text(
        """
        SELECT *
        FROM recovery_tracking
        WHERE invoice_id = :invoice_id
        ORDER BY id DESC
        """
    )

    return pd.read_sql(
        query,
        engine,
        params={
            "invoice_id": invoice_id
        }
    )


# --------------------------------------------------
# TEST RECOVERY TRACKING
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("REVIVEAI - RECOVERY TRACKING SYSTEM")
    print("=" * 60)

    # --------------------------------------------------
    # LOAD RECOVERY OPPORTUNITIES
    # --------------------------------------------------

    print("\nLoading recovery opportunity data...")

    recovery_data = pd.read_csv(
        "outputs/recovery_opportunities.csv"
    )

    # --------------------------------------------------
    # SELECT OVERDUE INVOICE
    # --------------------------------------------------

    overdue_df = recovery_data[
        recovery_data["days_overdue"] > 0
    ].copy()

    if overdue_df.empty:

        print("No overdue invoices found.")

    else:

        # Select first overdue invoice for testing
        row = overdue_df.iloc[0]

        print("\nSELECTED INVOICE")
        print("-" * 60)

        print(
            f"Invoice ID: {row['invoice_id']}"
        )

        print(
            f"Customer ID: {row['customer_id']}"
        )

        print(
            f"Invoice Amount: "
            f"₹{row['invoice_amount']:,.2f}"
        )

        print(
            f"Days Overdue: "
            f"{row['days_overdue']}"
        )

        print(
            f"Recommended Action: "
            f"{row['recommended_action']}"
        )

        # --------------------------------------------------
        # RECORD TEST ACTION
        # --------------------------------------------------

        add_recovery_action(

            invoice_id=row["invoice_id"],

            customer_id=row["customer_id"],

            recommended_action=row[
                "recommended_action"
            ],

            actual_action=row[
                "recommended_action"
            ],

            recovery_status="Action Taken",

            recovered_amount=0,

            notes=(
                "Initial recovery action "
                "recorded for testing."
            )
        )

        # --------------------------------------------------
        # DISPLAY INVOICE HISTORY
        # --------------------------------------------------

        print("\nRECOVERY HISTORY")
        print("-" * 60)

        history = get_invoice_history(
            row["invoice_id"]
        )

        if history.empty:

            print(
                "No recovery history found."
            )

        else:

            print(
                history.to_string(
                    index=False
                )
            )

        print()
        print(
            "STEP 20 COMPLETED SUCCESSFULLY"
        )