import pandas as pd

from database import (
    engine,
    SessionLocal,
    Invoice,
    RecoveryOpportunity,
    create_tables
)


# --------------------------------------------------
# LOAD INVOICE DATA
# --------------------------------------------------

def load_invoices():

    print("Loading invoice data...")

    file_path = "data/revenue_data.csv"

    df = pd.read_csv(file_path)

    print(f"Invoice records found: {len(df)}")

    # Create tables
    create_tables()

    # Clear old invoice data
    session = SessionLocal()

    session.query(Invoice).delete()

    session.commit()

    # Insert records
    records = []

    for _, row in df.iterrows():

        invoice = Invoice(

            customer_id=str(row["customer_id"]),

            invoice_id=str(row["invoice_id"]),

            invoice_amount=float(row["invoice_amount"]),

            invoice_date=str(row["invoice_date"]),

            due_date=str(row["due_date"]),

            payment_date=str(row["payment_date"])
                if pd.notna(row["payment_date"])
                else None,

            payment_status=str(row["payment_status"]),

            days_overdue=int(row["days_overdue"]),

            previous_payments=int(row["previous_payments"]),

            previous_late_payments=int(
                row["previous_late_payments"]
            ),

            average_payment_delay=float(
                row["average_payment_delay"]
            ),

            payment_failures=int(
                row["payment_failures"]
            ),

            communication_count=int(
                row["communication_count"]
            ),

            last_contact_days=int(
                row["last_contact_days"]
            ),

            discount_used=int(
                row["discount_used"]
            ),

            recovered=int(
                row["recovered"]
            ),

            customer_segment=str(
                row["customer_segment"]
            ),

            customer_lifetime_value=float(
                row["customer_lifetime_value"]
            )
        )

        records.append(invoice)

    session.add_all(records)

    session.commit()

    session.close()

    print("Invoice data inserted successfully.")

    print(f"Records inserted: {len(records)}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print()
    print("REVIVEAI - DATABASE LOADER")
    print("=" * 40)

    load_invoices()

    print()
    print("STEP 12 DATABASE LOADING COMPLETED")