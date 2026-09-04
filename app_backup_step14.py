import os
import sys

import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="ReviveAI",
    page_icon="💰",
    layout="wide"
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "reviveai.db"
)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    echo=False
)


# ==================================================
# LOAD DATA FROM DATABASE
# ==================================================

@st.cache_data
def load_recovery_data():

    query = """
    SELECT *
    FROM recovery_opportunities
    """

    df = pd.read_sql(
        query,
        engine
    )

    return df


@st.cache_data
def load_invoice_data():

    query = """
    SELECT *
    FROM invoices
    """

    df = pd.read_sql(
        query,
        engine
    )

    return df


recovery_df = load_recovery_data()

invoice_df = load_invoice_data()


# ==================================================
# HEADER
# ==================================================

st.title("💰 ReviveAI")

st.subheader(
    "AI-Powered Revenue Recovery Platform"
)

st.markdown(
    """
    **ReviveAI** identifies overdue revenue, predicts
    recovery probability, prioritizes recovery cases,
    and recommends the most suitable recovery action.
    """
)


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("⚙️ Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "🏠 Executive Dashboard",
        "🚨 Recovery Opportunities",
        "👥 Customer Intelligence",
        "🤖 AI Recovery Assistant"
    ]
)


# ==================================================
# SIDEBAR FILTERS
# ==================================================

st.sidebar.markdown("---")

st.sidebar.subheader("🔎 Filters")

risk_options = sorted(
    recovery_df["risk_level"]
    .dropna()
    .unique()
)

selected_risk = st.sidebar.multiselect(
    "Risk Level",
    risk_options,
    default=risk_options
)


priority_options = sorted(
    recovery_df["priority_category"]
    .dropna()
    .unique()
)

selected_priority = st.sidebar.multiselect(
    "Priority",
    priority_options,
    default=priority_options
)


segment_options = sorted(
    recovery_df["customer_segment"]
    .dropna()
    .unique()
)

selected_segment = st.sidebar.multiselect(
    "Customer Segment",
    segment_options,
    default=segment_options
)


filtered_df = recovery_df[
    recovery_df["risk_level"].isin(
        selected_risk
    )
    &
    recovery_df["priority_category"].isin(
        selected_priority
    )
    &
    recovery_df["customer_segment"].isin(
        selected_segment
    )
].copy()


# ==================================================
# EXECUTIVE DASHBOARD
# ==================================================

if page == "🏠 Executive Dashboard":

    st.header("🏠 Executive Dashboard")

    st.write(
        "Overview of revenue recovery performance "
        "and current recovery opportunities."
    )

    # ------------------------------------------------
    # KPI CALCULATIONS
    # ------------------------------------------------

    total_invoice_value = (
        filtered_df["invoice_amount"]
        .sum()
    )

    overdue_df = filtered_df[
        filtered_df["days_overdue"] > 0
    ]

    overdue_revenue = (
        overdue_df["invoice_amount"]
        .sum()
    )

    expected_recovery = (
        overdue_df["expected_recovery"]
        .sum()
    )

    revenue_at_risk = (
        overdue_df["potential_loss"]
        .sum()
    )

    high_critical = len(
        overdue_df[
            overdue_df[
                "priority_category"
            ].isin(
                ["High", "Critical"]
            )
        ]
    )

    recovery_rate = 0

    if overdue_revenue > 0:

        recovery_rate = (
            expected_recovery
            / overdue_revenue
            * 100
        )

    # ------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Total Invoice Value",
        f"₹{total_invoice_value:,.0f}"
    )

    col2.metric(
        "🚨 Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}"
    )

    col3.metric(
        "💵 Expected Recovery",
        f"₹{expected_recovery:,.0f}"
    )

    col4.metric(
        "🎯 Recovery Rate",
        f"{recovery_rate:.1f}%"
    )

    st.markdown("---")

    # ------------------------------------------------
    # SECONDARY METRICS
    # ------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📄 Total Invoices",
        f"{len(filtered_df):,}"
    )

    col2.metric(
        "⏰ Overdue Invoices",
        f"{len(overdue_df):,}"
    )

    col3.metric(
        "🔴 High/Critical",
        f"{high_critical:,}"
    )

    col4.metric(
        "📊 Average Recovery Probability",
        f"{filtered_df['recovery_probability_percent'].mean():.1f}%"
    )

    st.markdown("---")

    # ------------------------------------------------
    # RISK DISTRIBUTION
    # ------------------------------------------------

    st.subheader("🚨 Revenue Risk Distribution")

    risk_counts = (
        filtered_df["risk_level"]
        .value_counts()
        .reset_index()
    )

    risk_counts.columns = [
        "Risk Level",
        "Invoices"
    ]

    fig_risk = px.bar(
        risk_counts,
        x="Risk Level",
        y="Invoices",
        title="Invoices by Risk Level"
    )

    st.plotly_chart(
        fig_risk,
        use_container_width=True
    )

    # ------------------------------------------------
    # OVERDUE AGING
    # ------------------------------------------------

    st.subheader("⏰ Overdue Aging")

    aging_counts = (
        overdue_df["days_overdue"]
        .apply(
            lambda x:
                "1-30 Days"
                if x <= 30
                else
                "31-60 Days"
                if x <= 60
                else
                "61-90 Days"
                if x <= 90
                else
                "91-180 Days"
                if x <= 180
                else
                "180+ Days"
        )
        .value_counts()
        .reset_index()
    )

    aging_counts.columns = [
        "Overdue Range",
        "Invoices"
    ]

    fig_aging = px.bar(
        aging_counts,
        x="Overdue Range",
        y="Invoices",
        title="Invoice Aging Distribution"
    )

    st.plotly_chart(
        fig_aging,
        use_container_width=True
    )


# ==================================================
# RECOVERY OPPORTUNITIES
# ==================================================

elif page == "🚨 Recovery Opportunities":

    st.header("🚨 Recovery Opportunities")

    st.write(
        "Invoices currently requiring recovery action."
    )

    overdue_df = filtered_df[
        filtered_df["days_overdue"] > 0
    ].copy()

    # ------------------------------------------------
    # PRIORITY FILTER
    # ------------------------------------------------

    st.subheader(
        "🎯 Top Recovery Opportunities"
    )

    display_columns = [
        "invoice_id",
        "customer_id",
        "invoice_amount",
        "days_overdue",
        "recovery_probability_percent",
        "expected_recovery",
        "risk_level",
        "priority_category",
        "recommended_action"
    ]

    top_df = (
        overdue_df
        .sort_values(
            by=[
                "priority_score",
                "expected_recovery"
            ],
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        top_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ------------------------------------------------
    # EXPECTED RECOVERY BY RISK
    # ------------------------------------------------

    st.subheader(
        "💵 Expected Recovery by Risk Level"
    )

    risk_recovery = (
        overdue_df
        .groupby("risk_level")
        ["expected_recovery"]
        .sum()
        .reset_index()
    )

    fig_recovery = px.bar(
        risk_recovery,
        x="risk_level",
        y="expected_recovery",
        title="Expected Recovery by Risk Level"
    )

    st.plotly_chart(
        fig_recovery,
        use_container_width=True
    )

    # ------------------------------------------------
    # RECOMMENDED ACTIONS
    # ------------------------------------------------

    st.subheader(
        "🤖 Recommended Recovery Actions"
    )

    actions = (
        overdue_df[
            "recommended_action"
        ]
        .value_counts()
        .reset_index()
    )

    actions.columns = [
        "Recommended Action",
        "Invoices"
    ]

    fig_actions = px.pie(
        actions,
        names="Recommended Action",
        values="Invoices",
        title="Recovery Actions"
    )

    st.plotly_chart(
        fig_actions,
        use_container_width=True
    )


# ==================================================
# CUSTOMER INTELLIGENCE
# ==================================================

elif page == "👥 Customer Intelligence":

    st.header("👥 Customer Intelligence")

    st.write(
        "Customer-level revenue recovery insights."
    )

    # ------------------------------------------------
    # CUSTOMER AGGREGATION
    # ------------------------------------------------

    customer_df = (
        filtered_df
        .groupby("customer_id")
        .agg(
            total_invoices=(
                "invoice_id",
                "count"
            ),

            total_invoice_value=(
                "invoice_amount",
                "sum"
            ),

            expected_recovery=(
                "expected_recovery",
                "sum"
            ),

            average_days_overdue=(
                "days_overdue",
                "mean"
            ),

            average_recovery_probability=(
                "recovery_probability_percent",
                "mean"
            ),

            customer_lifetime_value=(
                "customer_lifetime_value",
                "max"
            )
        )
        .reset_index()
    )

    # ------------------------------------------------
    # CUSTOMER METRICS
    # ------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "👥 Customers",
        f"{len(customer_df):,}"
    )

    col2.metric(
        "💰 Customer Invoice Value",
        f"₹{customer_df['total_invoice_value'].sum():,.0f}"
    )

    col3.metric(
        "💵 Expected Customer Recovery",
        f"₹{customer_df['expected_recovery'].sum():,.0f}"
    )

    st.markdown("---")

    # ------------------------------------------------
    # TOP CUSTOMERS
    # ------------------------------------------------

    st.subheader(
        "🏆 Highest Revenue Customers"
    )

    top_customers = (
        customer_df
        .sort_values(
            "customer_lifetime_value",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        top_customers,
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------------
    # CUSTOMER RISK SCATTER
    # ------------------------------------------------

    st.subheader(
        "📊 Customer Value vs Overdue Behavior"
    )

    fig_customer = px.scatter(
        customer_df,
        x="customer_lifetime_value",
        y="average_days_overdue",
        size="expected_recovery",
        hover_name="customer_id",
        title="Customer Lifetime Value vs Average Days Overdue"
    )

    st.plotly_chart(
        fig_customer,
        use_container_width=True
    )


# ==================================================
# AI RECOVERY ASSISTANT
# ==================================================

elif page == "🤖 AI Recovery Assistant":

    st.header(
        "🤖 AI Recovery Assistant"
    )

    st.write(
        "Generate a personalized recovery message "
        "for a selected overdue invoice."
    )

    overdue_df = filtered_df[
        filtered_df["days_overdue"] > 0
    ].copy()

    if len(overdue_df) == 0:

        st.warning(
            "No overdue invoices available "
            "with the selected filters."
        )

    else:

        # --------------------------------------------
        # SELECT INVOICE
        # --------------------------------------------

        invoice_options = (
            overdue_df["invoice_id"]
            .tolist()
        )

        selected_invoice = st.selectbox(
            "Select Invoice",
            invoice_options
        )

        selected_row = overdue_df[
            overdue_df["invoice_id"]
            == selected_invoice
        ].iloc[0]

        # --------------------------------------------
        # INVOICE INFORMATION
        # --------------------------------------------

        st.subheader(
            "📄 Invoice Information"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Invoice Amount",
            f"₹{selected_row['invoice_amount']:,.2f}"
        )

        col2.metric(
            "Days Overdue",
            f"{int(selected_row['days_overdue'])}"
        )

        col3.metric(
            "Recovery Probability",
            f"{selected_row['recovery_probability_percent']:.1f}%"
        )

        col4.metric(
            "Expected Recovery",
            f"₹{selected_row['expected_recovery']:,.2f}"
        )

        st.markdown("---")

        # --------------------------------------------
        # RECOVERY STRATEGY
        # --------------------------------------------

        st.subheader(
            "🎯 Recommended Strategy"
        )

        st.info(
            selected_row[
                "recommended_action"
            ]
        )

        # --------------------------------------------
        # MESSAGE GENERATION
        # --------------------------------------------

        days = int(
            selected_row["days_overdue"]
        )

        amount = float(
            selected_row["invoice_amount"]
        )

        invoice_id = selected_row[
            "invoice_id"
        ]

        probability = float(
            selected_row[
                "recovery_probability_percent"
            ]
        )

        customer_segment = selected_row[
            "customer_segment"
        ]

        if days <= 30:

            subject = (
                f"Payment Reminder - "
                f"Invoice {invoice_id}"
            )

            message = f"""
Dear Customer,

This is a friendly reminder regarding
invoice {invoice_id} for ₹{amount:,.2f}.

Our records indicate that the payment is
currently {days} days overdue.

We would appreciate it if you could arrange
the payment at your earliest convenience.

If the payment has already been made,
please disregard this message.

Regards,
ReviveAI Recovery Team
"""

        elif days <= 60:

            subject = (
                f"Payment Follow-Up - "
                f"Invoice {invoice_id}"
            )

            message = f"""
Dear Customer,

We are following up regarding invoice
{invoice_id} for ₹{amount:,.2f}.

The invoice is currently {days} days overdue.

Please arrange the outstanding payment
at the earliest possible opportunity.

If there are any payment difficulties,
please contact us so that we can discuss
available options.

Regards,
ReviveAI Recovery Team
"""

        elif days <= 90:

            subject = (
                f"Urgent Payment Follow-Up - "
                f"Invoice {invoice_id}"
            )

            message = f"""
Dear Customer,

This is an urgent follow-up regarding
invoice {invoice_id} for ₹{amount:,.2f}.

The payment is now {days} days overdue.

We request that you arrange settlement
as soon as possible to avoid further
escalation.

If you are experiencing difficulties
with payment, please contact our team.

Regards,
ReviveAI Recovery Team
"""

        else:

            subject = (
                f"Important Payment Resolution Required - "
                f"Invoice {invoice_id}"
            )

            message = f"""
Dear Customer,

We are writing regarding the outstanding
invoice {invoice_id} for ₹{amount:,.2f}.

The payment is currently {days} days overdue.

Please contact our recovery team as soon
as possible to resolve the outstanding
balance.

If there is a dispute or payment difficulty,
we are available to discuss the situation
and identify an appropriate resolution.

Regards,
ReviveAI Recovery Team
"""

        # --------------------------------------------
        # DISPLAY MESSAGE
        # --------------------------------------------

        st.subheader(
            "✉️ AI Recovery Message"
        )

        st.text_input(
            "Subject",
            value=subject
        )

        st.text_area(
            "Message",
            value=message,
            height=300
        )

        # --------------------------------------------
        # AI EXPLANATION
        # --------------------------------------------

        st.subheader(
            "🧠 Why this strategy?"
        )

        st.write(
            f"""
            **Customer Segment:** {customer_segment}

            **Recovery Probability:** {probability:.2f}%

            **Days Overdue:** {days}

            **Recommended Action:** 
            {selected_row['recommended_action']}

            ReviveAI selected this recovery strategy
            based on the invoice's overdue severity,
            predicted recovery probability and
            customer/payment behavior.
            """
        )


# ==================================================
# FOOTER
# ==================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "ReviveAI | AI Revenue Recovery Platform"
)

st.sidebar.caption(
    "Major Project Prototype"
)