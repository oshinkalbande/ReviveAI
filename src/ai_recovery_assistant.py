import pandas as pd


# ============================================================
# REVIVEAI - AI RECOVERY ASSISTANT
# ============================================================

print("=" * 70)
print("REVIVEAI - AI RECOVERY ASSISTANT")
print("=" * 70)


# ============================================================
# 1. LOAD RECOVERY DATA
# ============================================================

DATA_PATH = "outputs/recovery_opportunities.csv"

df = pd.read_csv(DATA_PATH)

print("\nRecovery opportunity data loaded.")
print("Total invoices:", len(df))


# ============================================================
# 2. FIND AN ACTUAL OVERDUE INVOICE
# ============================================================

overdue_df = df[
    df["days_overdue"] > 0
].copy()


if len(overdue_df) == 0:

    print("\nNo overdue invoices found.")
    print("AI Recovery Assistant cannot generate a recovery message.")

    raise SystemExit


# Select highest-priority overdue invoice

customer = overdue_df.iloc[0]


# ============================================================
# 3. EXTRACT INFORMATION
# ============================================================

customer_id = customer["customer_id"]

invoice_id = customer["invoice_id"]

invoice_amount = customer["invoice_amount"]

days_overdue = int(
    customer["days_overdue"]
)

recovery_probability = customer[
    "recovery_probability_percent"
]

expected_recovery = customer[
    "expected_recovery"
]

risk_level = customer[
    "risk_level"
]

priority_category = customer[
    "priority_category"
]

recommended_action = customer[
    "recommended_action"
]

customer_segment = customer[
    "customer_segment"
]

customer_lifetime_value = customer[
    "customer_lifetime_value"
]


# ============================================================
# 4. DISPLAY RECOVERY OPPORTUNITY
# ============================================================

print("\n" + "=" * 70)
print("SELECTED RECOVERY OPPORTUNITY")
print("=" * 70)

print(
    f"\nCustomer ID: {customer_id}"
)

print(
    f"Invoice ID: {invoice_id}"
)

print(
    f"Invoice Amount: ₹{invoice_amount:,.2f}"
)

print(
    f"Days Overdue: {days_overdue}"
)

print(
    f"Recovery Probability: "
    f"{recovery_probability}%"
)

print(
    f"Expected Recovery: "
    f"₹{expected_recovery:,.2f}"
)

print(
    f"Risk Level: {risk_level}"
)

print(
    f"Priority: {priority_category}"
)

print(
    f"Customer Segment: {customer_segment}"
)

print(
    f"Customer Lifetime Value: "
    f"₹{customer_lifetime_value:,.2f}"
)

print(
    f"Recommended Action: "
    f"{recommended_action}"
)


# ============================================================
# 5. AI MESSAGE GENERATOR
# ============================================================

def generate_recovery_message(row):

    invoice_id = row["invoice_id"]

    amount = row["invoice_amount"]

    days = int(row["days_overdue"])

    risk = row["risk_level"]

    priority = row["priority_category"]

    action = row["recommended_action"]

    segment = row["customer_segment"]


    # ========================================================
    # RECENTLY OVERDUE
    # ========================================================

    if days <= 30:

        subject = (
            f"Friendly Payment Reminder - "
            f"Invoice {invoice_id}"
        )

        message = f"""
Dear Customer,

We hope you are doing well.

This is a friendly reminder regarding invoice
{invoice_id} for ₹{amount:,.2f}, which is currently
{days} days overdue.

We kindly request you to arrange the payment at
your earliest convenience.

If the payment has already been processed, please
disregard this message or share the payment details
with our accounts team.

If you are experiencing any difficulty with the
payment, please feel free to contact our team.

Thank you for your cooperation.

Best regards,
ReviveAI Revenue Recovery Team
"""

        strategy = (
            "The invoice is recently overdue, so ReviveAI "
            "recommends a friendly automated reminder."
        )


    # ========================================================
    # MODERATELY OVERDUE
    # ========================================================

    elif days <= 60:

        subject = (
            f"Payment Follow-Up Required - "
            f"Invoice {invoice_id}"
        )

        message = f"""
Dear Customer,

We are following up regarding invoice
{invoice_id} for ₹{amount:,.2f},
which is currently {days} days overdue.

We would appreciate it if you could arrange the
payment at your earliest convenience.

If there is an issue preventing payment, please
contact our accounts team so that we can assist
you with the next steps.

We value our relationship with you and appreciate
your prompt attention to this matter.

Best regards,
ReviveAI Revenue Recovery Team
"""

        strategy = (
            "The invoice is moderately overdue. ReviveAI "
            "therefore recommends a personalized follow-up."
        )


    # ========================================================
    # HIGHLY OVERDUE
    # ========================================================

    elif days <= 90:

        subject = (
            f"Urgent Payment Follow-Up - "
            f"Invoice {invoice_id}"
        )

        message = f"""
Dear Customer,

We are writing regarding invoice
{invoice_id} for ₹{amount:,.2f},
which is currently {days} days overdue.

We kindly request that you arrange the payment
as soon as possible.

If there is a payment issue, dispute, or temporary
difficulty affecting the payment, please contact
our accounts team so that we can discuss the
appropriate next steps.

We appreciate your prompt attention.

Best regards,
ReviveAI Revenue Recovery Team
"""

        strategy = (
            "The invoice is significantly overdue. "
            "ReviveAI recommends an urgent but professional "
            "payment follow-up."
        )


    # ========================================================
    # CRITICAL / VERY OLD
    # ========================================================

    else:

        subject = (
            f"Important Payment Resolution Required - "
            f"Invoice {invoice_id}"
        )

        message = f"""
Dear Customer,

We are contacting you regarding invoice
{invoice_id} for ₹{amount:,.2f},
which is currently {days} days overdue.

We would appreciate your immediate attention
to this outstanding payment.

If there is a dispute, payment difficulty, or
another issue preventing settlement, please
contact our accounts team so that we can work
with you toward a resolution.

Please contact us at your earliest convenience.

Best regards,
ReviveAI Revenue Recovery Team
"""

        strategy = (
            "The invoice is significantly overdue. "
            "ReviveAI recommends stronger human-oriented "
            "recovery communication."
        )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return subject, message, strategy


# ============================================================
# 6. GENERATE MESSAGE
# ============================================================

print("\nGenerating personalized recovery message...")

subject, message, strategy = (
    generate_recovery_message(customer)
)


# ============================================================
# 7. DISPLAY RESULT
# ============================================================

print("\n" + "=" * 70)
print("AI-GENERATED RECOVERY MESSAGE")
print("=" * 70)

print("\nSUBJECT:")
print(subject)

print("\nMESSAGE:")
print(message)

print("\nAI STRATEGY:")
print(strategy)


# ============================================================
# 8. SAVE MESSAGE
# ============================================================

OUTPUT_PATH = (
    "outputs/ai_recovery_message.txt"
)


with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "REVIVEAI - AI RECOVERY ASSISTANT\n"
    )

    file.write("=" * 70 + "\n\n")

    file.write(
        f"Customer ID: {customer_id}\n"
    )

    file.write(
        f"Invoice ID: {invoice_id}\n"
    )

    file.write(
        f"Invoice Amount: ₹{invoice_amount:,.2f}\n"
    )

    file.write(
        f"Days Overdue: {days_overdue}\n"
    )

    file.write(
        f"Recovery Probability: "
        f"{recovery_probability}%\n"
    )

    file.write(
        f"Expected Recovery: "
        f"₹{expected_recovery:,.2f}\n"
    )

    file.write(
        f"Risk Level: {risk_level}\n"
    )

    file.write(
        f"Priority: {priority_category}\n"
    )

    file.write(
        f"Customer Segment: "
        f"{customer_segment}\n"
    )

    file.write(
        f"Recommended Action: "
        f"{recommended_action}\n\n"
    )

    file.write("=" * 70 + "\n\n")

    file.write(
        "SUBJECT:\n"
    )

    file.write(subject)

    file.write(
        "\n\nMESSAGE:\n"
    )

    file.write(message)

    file.write(
        "\nAI STRATEGY:\n"
    )

    file.write(strategy)


# ============================================================
# 9. FINAL STATUS
# ============================================================

print("\nMessage saved successfully.")

print(
    f"Output file: {OUTPUT_PATH}"
)

print("\n" + "=" * 70)
print("STEP 11 COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nReviveAI can now:")

print("✓ Find overdue invoices")

print("✓ Analyze invoice information")

print("✓ Use ML recovery probability")

print("✓ Use risk level")

print("✓ Use recovery priority")

print("✓ Generate personalized recovery communication")

print("✓ Adjust message according to overdue severity")

print("✓ Save the recovery message")