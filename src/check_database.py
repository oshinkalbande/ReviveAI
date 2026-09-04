from database import SessionLocal, Invoice, RecoveryOpportunity


session = SessionLocal()


invoice_count = session.query(Invoice).count()

recovery_count = session.query(
    RecoveryOpportunity
).count()


print()
print("REVIVEAI DATABASE CHECK")
print("=" * 40)

print(f"Invoice records: {invoice_count}")

print(
    f"Recovery opportunity records: {recovery_count}"
)


print()
print("Sample invoices:")

invoices = session.query(Invoice).limit(5).all()

for invoice in invoices:

    print(
        invoice.invoice_id,
        "|",
        invoice.customer_id,
        "| ₹",
        round(invoice.invoice_amount, 2),
        "|",
        invoice.days_overdue,
        "days overdue"
    )


session.close()