import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

from recovery_tracking import (
    add_recovery_action,
    get_recovery_tracking,
    get_invoice_history
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ReviveAI Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATABASE
# ============================================================

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


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_recovery_data():

    query = """
    SELECT *
    FROM recovery_opportunities
    """

    return pd.read_sql(
        query,
        engine
    )


@st.cache_data
def load_customer_segments():

    path = os.path.join(
        BASE_DIR,
        "outputs",
        "customer_segments.csv"
    )

    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)

    # --------------------------------------------------------
    # FIX CUSTOMER SEGMENT COLUMN
    # --------------------------------------------------------

    # Your CSV currently appears to use customer_segment.
    # The old dashboard expected customer_segment_label.
    # Create the missing column automatically.

    if (
        "customer_segment_label" not in df.columns
        and "customer_segment" in df.columns
    ):
        df["customer_segment_label"] = (
            df["customer_segment"]
        )

    return df


recovery_df = load_recovery_data()

customer_segments_df = load_customer_segments()


# ============================================================
# BASIC DATA CHECK
# ============================================================

if recovery_df.empty:

    st.error(
        "No recovery opportunity data was found."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("💰 ReviveAI")

st.markdown(
    "### Revenue Recovery Command Center"
)

st.caption(
    "AI-powered detection, prediction and prioritization "
    "of revenue recovery opportunities."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💰 REVIVEAI")

st.sidebar.caption(
    "Revenue Recovery Intelligence"
)

st.sidebar.markdown("---")


page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Command Center",
        "🚨 Recovery Command",
        "👥 Customer Intelligence",
        "🤖 AI Action Center",
        "💬 AI Assistant",
        "📈 Recovery Tracking"
    ]
)


# ============================================================
# FILTERS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader("🔎 Filters")


# -----------------------------
# RISK FILTER
# -----------------------------

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


# -----------------------------
# PRIORITY FILTER
# -----------------------------

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


# -----------------------------
# CUSTOMER SEGMENT FILTER
# -----------------------------

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


# ============================================================
# APPLY FILTERS
# ============================================================

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


# ============================================================
# HELPER FUNCTION
# ============================================================

def format_rupees(value):

    if pd.isna(value):
        return "₹0"

    return f"₹{value:,.0f}"


# ============================================================
# PAGE 1 — COMMAND CENTER
# ============================================================

if page == "🏠 Command Center":

    st.header(
        "🏠 Revenue Recovery Command Center"
    )

    st.write(
        "A real-time overview of revenue exposure, "
        "recovery potential and operational priorities."
    )

    overdue_df = filtered_df[
        filtered_df["days_overdue"] > 0
    ].copy()


    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    total_invoice_value = (
        filtered_df["invoice_amount"].sum()
    )

    overdue_revenue = (
        overdue_df["invoice_amount"].sum()
    )

    expected_recovery = (
        overdue_df["expected_recovery"].sum()
    )

    revenue_at_risk = (
        overdue_df["potential_loss"].sum()
    )

    recovery_rate = 0

    if overdue_revenue > 0:

        recovery_rate = (
            expected_recovery
            / overdue_revenue
            * 100
        )


    high_critical_df = overdue_df[
        overdue_df["risk_level"].isin(
            ["High", "Critical"]
        )
    ]

    high_critical_amount = (
        high_critical_df["invoice_amount"].sum()
    )


    # ========================================================
    # KPI ROW
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Revenue Under Management",
        format_rupees(total_invoice_value)
    )

    col2.metric(
        "🚨 Revenue at Risk",
        format_rupees(revenue_at_risk)
    )

    col3.metric(
        "💵 Expected Recovery",
        format_rupees(expected_recovery)
    )

    col4.metric(
        "🎯 Recovery Rate",
        f"{recovery_rate:.1f}%"
    )


    st.markdown("---")


    # ========================================================
    # SECOND KPI ROW
    # ========================================================

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
        "🔴 High/Critical Cases",
        f"{len(high_critical_df):,}"
    )

    col4.metric(
        "💎 High/Critical Value",
        format_rupees(high_critical_amount)
    )


    st.markdown("---")


    # ========================================================
    # RECOVERY FUNNEL
    # ========================================================

    st.subheader(
        "📈 Revenue Recovery Funnel"
    )

    funnel_labels = [
        "Total Invoice Value",
        "Overdue Revenue",
        "Revenue at Risk",
        "Expected Recovery"
    ]

    funnel_values = [
        total_invoice_value,
        overdue_revenue,
        revenue_at_risk,
        expected_recovery
    ]

    fig_funnel = go.Figure(
        go.Funnel(
            y=funnel_labels,
            x=funnel_values,
            textinfo="value+percent initial"
        )
    )

    fig_funnel.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_funnel,
        width="stretch"
    )


    # ========================================================
    # TWO CHARTS
    # ========================================================

    col1, col2 = st.columns(2)


    # -----------------------------
    # RISK DISTRIBUTION
    # -----------------------------

    with col1:

        st.subheader(
            "🚨 Risk Distribution"
        )

        risk_counts = (
            overdue_df["risk_level"]
            .value_counts()
            .reset_index()
        )

        risk_counts.columns = [
            "Risk Level",
            "Invoices"
        ]

        fig_risk = px.pie(
            risk_counts,
            names="Risk Level",
            values="Invoices",
            hole=0.45
        )

        st.plotly_chart(
            fig_risk,
            width="stretch"
        )


    # -----------------------------
    # OVERDUE AGING
    # -----------------------------

    with col2:

        st.subheader(
            "⏰ Overdue Aging"
        )

        def aging_bucket(days):

            if days <= 30:
                return "1-30 Days"

            if days <= 60:
                return "31-60 Days"

            if days <= 90:
                return "61-90 Days"

            if days <= 180:
                return "91-180 Days"

            return "180+ Days"


        aging = overdue_df[
            "days_overdue"
        ].apply(
            aging_bucket
        )

        aging_counts = (
            aging
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
            y="Invoices"
        )

        st.plotly_chart(
            fig_aging,
            width="stretch"
        )


    # ========================================================
    # TOP OPPORTUNITIES
    # ========================================================

    st.markdown("---")

    st.subheader(
        "🔥 Highest-Value Recovery Opportunities"
    )

    top_opportunities = (
        overdue_df
        .sort_values(
            "expected_recovery",
            ascending=False
        )
        .head(10)
    )

    display_columns = [
        "invoice_id",
        "customer_id",
        "invoice_amount",
        "days_overdue",
        "recovery_probability_percent",
        "expected_recovery",
        "risk_level",
        "priority_category"
    ]

    st.dataframe(
        top_opportunities[
            display_columns
        ],
        width="stretch",
        hide_index=True
    )


# ============================================================
# PAGE 2 — RECOVERY COMMAND
# ============================================================

elif page == "🚨 Recovery Command":

    st.header(
        "🚨 Recovery Command Center"
    )

    st.write(
        "Prioritize invoices based on recovery potential "
        "and urgency."
    )

    overdue_df = filtered_df[
        filtered_df["days_overdue"] > 0
    ].copy()


    # ========================================================
    # PRIORITY SUMMARY
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    critical = len(
        overdue_df[
            overdue_df["priority_category"]
            == "Critical"
        ]
    )

    high = len(
        overdue_df[
            overdue_df["priority_category"]
            == "High"
        ]
    )

    medium = len(
        overdue_df[
            overdue_df["priority_category"]
            == "Medium"
        ]
    )

    low = len(
        overdue_df[
            overdue_df["priority_category"]
            == "Low"
        ]
    )


    col1.metric(
        "🔴 Critical",
        critical
    )

    col2.metric(
        "🟠 High",
        high
    )

    col3.metric(
        "🟡 Medium",
        medium
    )

    col4.metric(
        "🟢 Low",
        low
    )


    st.markdown("---")


    # ========================================================
    # OPPORTUNITY TABLE
    # ========================================================

    st.subheader(
        "🎯 Recovery Opportunity Queue"
    )

    top_df = (
        overdue_df
        .sort_values(
            [
                "priority_score",
                "expected_recovery"
            ],
            ascending=False
        )
    )

    columns = [
        "invoice_id",
        "customer_id",
        "invoice_amount",
        "days_overdue",
        "recovery_probability_percent",
        "expected_recovery",
        "potential_loss",
        "risk_level",
        "priority_category",
        "recommended_action"
    ]

    st.dataframe(
        top_df[
            columns
        ].head(100),
        width="stretch",
        hide_index=True
    )


    st.markdown("---")


    # ========================================================
    # ACTION ANALYSIS
    # ========================================================

    st.subheader(
        "🤖 Recommended Recovery Actions"
    )

    action_counts = (
        overdue_df[
            "recommended_action"
        ]
        .value_counts()
        .reset_index()
    )

    action_counts.columns = [
        "Recommended Action",
        "Invoices"
    ]

    fig_action = px.bar(
        action_counts,
        x="Invoices",
        y="Recommended Action",
        orientation="h"
    )

    st.plotly_chart(
        fig_action,
        width="stretch"
    )


# ============================================================
# PAGE 3 — CUSTOMER INTELLIGENCE
# ============================================================

elif page == "👥 Customer Intelligence":

    st.header(
        "👥 Customer Intelligence"
    )

    st.write(
        "Understand customer value and payment behavior "
        "to improve recovery decisions."
    )


    # ========================================================
    # CHECK CUSTOMER DATA
    # ========================================================

    if customer_segments_df.empty:

        st.warning(
            "Customer segmentation file not found."
        )

        st.stop()


    # ========================================================
    # MAKE SURE SEGMENT COLUMN EXISTS
    # ========================================================

    if (
        "customer_segment_label"
        not in customer_segments_df.columns
    ):

        if (
            "customer_segment"
            in customer_segments_df.columns
        ):

            customer_segments_df[
                "customer_segment_label"
            ] = customer_segments_df[
                "customer_segment"
            ]

        else:

            customer_segments_df[
                "customer_segment_label"
            ] = "Unknown"


    # ========================================================
    # CUSTOMER SEGMENT DISTRIBUTION
    # ========================================================

    segment_counts = (
        customer_segments_df[
            "customer_segment_label"
        ]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    segment_counts.columns = [
        "Customer Segment",
        "Customers"
    ]


    col1, col2 = st.columns(2)


    # -----------------------------
    # SEGMENT PIE CHART
    # -----------------------------

    with col1:

        st.subheader(
            "👥 Customer Segment Distribution"
        )

        fig_segment = px.pie(
            segment_counts,
            names="Customer Segment",
            values="Customers",
            hole=0.45
        )

        st.plotly_chart(
            fig_segment,
            width="stretch"
        )


    # -----------------------------
    # CUSTOMER VALUE VS RISK
    # -----------------------------

    with col2:

        st.subheader(
            "💎 Customer Value vs Risk"
        )

        scatter_df = customer_segments_df.copy()

        required_scatter_columns = [
            "customer_lifetime_value",
            "average_days_overdue",
            "total_invoice_value",
            "customer_id",
            "customer_segment_label"
        ]

        if all(
            column in scatter_df.columns
            for column in required_scatter_columns
        ):

            fig_customer = px.scatter(
                scatter_df,
                x="customer_lifetime_value",
                y="average_days_overdue",
                size="total_invoice_value",
                color="customer_segment_label",
                hover_name="customer_id"
            )

            st.plotly_chart(
                fig_customer,
                width="stretch"
            )

        else:

            st.info(
                "Some customer analysis columns "
                "are not available."
            )


    st.markdown("---")


    # ========================================================
    # STEP 26 — CUSTOMER SELECTOR
    # ========================================================

    st.subheader(
        "🔎 Select Customer"
    )

    customer_ids = sorted(
        customer_segments_df[
            "customer_id"
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


    if not customer_ids:

        st.warning(
            "No customers are available."
        )

        st.stop()


    selected_customer = st.selectbox(
        "Choose a customer to view their intelligence profile:",
        customer_ids,
        key="customer_intelligence_selector"
    )


    # ========================================================
    # SELECT CUSTOMER DATA
    # ========================================================

    customer_row_df = customer_segments_df[
        customer_segments_df[
            "customer_id"
        ].astype(str)
        == str(selected_customer)
    ].copy()


    if customer_row_df.empty:

        st.warning(
            "Customer information not found."
        )

        st.stop()


    customer_row = (
        customer_row_df.iloc[0]
    )


    # ========================================================
    # CUSTOMER RECOVERY DATA
    # ========================================================

    customer_invoice_df = recovery_df[
        recovery_df[
            "customer_id"
        ].astype(str)
        == str(selected_customer)
    ].copy()


    customer_overdue_df = customer_invoice_df[
        customer_invoice_df[
            "days_overdue"
        ] > 0
    ].copy()


    # ========================================================
    # CALCULATE CUSTOMER VALUES
    # ========================================================

    total_invoices = len(
        customer_invoice_df
    )


    total_invoice_value = (
        customer_invoice_df[
            "invoice_amount"
        ].sum()
    )


    outstanding_amount = (
        customer_overdue_df[
            "invoice_amount"
        ].sum()
    )


    expected_customer_recovery = (
        customer_overdue_df[
            "expected_recovery"
        ].sum()
    )


    average_days_overdue = 0

    if not customer_invoice_df.empty:

        average_days_overdue = (
            customer_invoice_df[
                "days_overdue"
            ]
            .clip(lower=0)
            .mean()
        )


    late_payment_rate = 0

    if total_invoices > 0:

        late_payment_rate = (
            len(customer_overdue_df)
            / total_invoices
            * 100
        )


    # ========================================================
    # RECOVERY PROBABILITY
    # ========================================================

    recovery_probability = 0

    if (
        "recovery_probability_percent"
        in customer_overdue_df.columns
    ):

        if not customer_overdue_df.empty:

            recovery_probability = (
                customer_overdue_df[
                    "recovery_probability_percent"
                ].mean()
            )


    # ========================================================
    # CUSTOMER SEGMENT
    # ========================================================

    customer_segment = (
        customer_row.get(
            "customer_segment_label",
            "Unknown"
        )
    )


    # ========================================================
    # CUSTOMER LIFETIME VALUE
    # ========================================================

    customer_lifetime_value = (
        customer_row.get(
            "customer_lifetime_value",
            total_invoice_value
        )
    )


    # ========================================================
    # RISK LEVEL
    # ========================================================

    if not customer_invoice_df.empty:

        risk_counts = (
            customer_invoice_df[
                "risk_level"
            ]
            .value_counts()
        )

        customer_risk = (
            risk_counts.index[0]
        )

    else:

        customer_risk = "Low"


    # ========================================================
    # RECOMMENDED STRATEGY
    # ========================================================

    if not customer_invoice_df.empty:

        action_counts = (
            customer_invoice_df[
                "recommended_action"
            ]
            .value_counts()
        )

        recommended_strategy = (
            action_counts.index[0]
        )

    else:

        recommended_strategy = (
            "No recovery action required"
        )


    # ========================================================
    # CUSTOMER PROFILE
    # ========================================================

    st.markdown("---")

    st.subheader(
        f"👤 Customer Profile — {selected_customer}"
    )


    # ========================================================
    # CUSTOMER KPI ROW 1
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "💎 Customer Lifetime Value",
        format_rupees(
            customer_lifetime_value
        )
    )


    col2.metric(
        "📄 Total Invoices",
        f"{total_invoices:,}"
    )


    col3.metric(
        "💰 Total Invoice Value",
        format_rupees(
            total_invoice_value
        )
    )


    col4.metric(
        "⏰ Outstanding Amount",
        format_rupees(
            outstanding_amount
        )
    )


    # ========================================================
    # CUSTOMER KPI ROW 2
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "📅 Avg. Payment Delay",
        f"{average_days_overdue:.1f} days"
    )


    col2.metric(
        "⚠️ Late Payment Rate",
        f"{late_payment_rate:.1f}%"
    )


    col3.metric(
        "🎯 Recovery Probability",
        f"{recovery_probability:.1f}%"
    )


    col4.metric(
        "💵 Expected Recovery",
        format_rupees(
            expected_customer_recovery
        )
    )


    st.markdown("---")


    # ========================================================
    # CUSTOMER RISK AND STRATEGY
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.subheader(
            "🚨 Risk Level"
        )

        if customer_risk == "Critical":

            st.error(
                f"🔴 {customer_risk}"
            )

        elif customer_risk == "High":

            st.warning(
                f"🟠 {customer_risk}"
            )

        elif customer_risk == "Medium":

            st.info(
                f"🟡 {customer_risk}"
            )

        else:

            st.success(
                f"🟢 {customer_risk}"
            )


    with col2:

        st.subheader(
            "👥 Customer Segment"
        )

        st.info(
            str(customer_segment)
        )


    with col3:

        st.subheader(
            "🤖 Recommended Strategy"
        )

        st.info(
            str(recommended_strategy)
        )


    # ========================================================
    # CUSTOMER INVOICE HISTORY
    # ========================================================

    st.markdown("---")

    st.subheader(
        "📋 Customer Invoice History"
    )


    if customer_invoice_df.empty:

        st.info(
            "No invoice information is available "
            "for this customer."
        )

    else:

        customer_display_columns = [
            "invoice_id",
            "invoice_amount",
            "days_overdue",
            "recovery_probability_percent",
            "expected_recovery",
            "risk_level",
            "priority_category",
            "recommended_action"
        ]


        available_customer_columns = [
            column
            for column in customer_display_columns
            if column in customer_invoice_df.columns
        ]


        st.dataframe(
            customer_invoice_df[
                available_customer_columns
            ].sort_values(
                "expected_recovery",
                ascending=False
            ),
            width="stretch",
            hide_index=True
        )


    # ========================================================
    # CUSTOMER INSIGHT SUMMARY
    # ========================================================

    st.markdown("---")

    st.subheader(
        "🧠 ReviveAI Customer Insight"
    )


    if outstanding_amount > 0:

        st.write(
            f"""
**Customer:** {selected_customer}

**Segment:** {customer_segment}

**Risk Level:** {customer_risk}

**Total Invoice Value:** {format_rupees(total_invoice_value)}

**Outstanding Amount:** {format_rupees(outstanding_amount)}

**Average Payment Delay:** {average_days_overdue:.1f} days

**Late Payment Rate:** {late_payment_rate:.1f}%

**Recovery Probability:** {recovery_probability:.1f}%

**Expected Recovery:** {format_rupees(expected_customer_recovery)}

**Recommended Strategy:** {recommended_strategy}
"""
        )

    else:

        st.success(
            f"Customer {selected_customer} currently has "
            "no outstanding overdue amount."
        )


# ============================================================
# PAGE 4 — AI ACTION CENTER
# ============================================================

elif page == "🤖 AI Action Center":

    st.header(
        "🤖 AI Recovery Action Center"
    )

    st.write(
        "Select an overdue invoice and let ReviveAI "
        "generate the recommended recovery strategy."
    )


    overdue_df = filtered_df[
        filtered_df["days_overdue"] > 0
    ].copy()


    if len(overdue_df) == 0:

        st.warning(
            "No overdue invoices available."
        )

    else:

        # ====================================================
        # INVOICE SELECTOR
        # ====================================================

        selected_invoice = st.selectbox(
            "Select Invoice",
            overdue_df[
                "invoice_id"
            ].tolist(),
            key="ai_invoice_selector"
        )


        row = overdue_df[
            overdue_df["invoice_id"]
            == selected_invoice
        ].iloc[0]


        st.markdown("---")


        # ====================================================
        # INVOICE PROFILE
        # ====================================================

        st.subheader(
            "📄 Invoice Profile"
        )


        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "Invoice Amount",
            format_rupees(
                row["invoice_amount"]
            )
        )


        col2.metric(
            "Days Overdue",
            int(row["days_overdue"])
        )


        col3.metric(
            "Recovery Probability",
            f"{row['recovery_probability_percent']:.1f}%"
        )


        col4.metric(
            "Expected Recovery",
            format_rupees(
                row["expected_recovery"]
            )
        )


        # ====================================================
        # CUSTOMER INFORMATION
        # ====================================================

        st.markdown("---")


        col1, col2, col3 = st.columns(3)


        col1.metric(
            "Customer",
            row["customer_id"]
        )


        col2.metric(
            "Customer Segment",
            row["customer_segment"]
        )


        col3.metric(
            "Customer Lifetime Value",
            format_rupees(
                row["customer_lifetime_value"]
            )
        )


        # ====================================================
        # DECISION ENGINE
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🧠 ReviveAI Decision"
        )

        st.info(
            row["recommended_action"]
        )


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Risk Level",
                row["risk_level"]
            )


        with col2:

            st.metric(
                "Priority",
                row["priority_category"]
            )


        # ====================================================
        # MESSAGE GENERATION
        # ====================================================

        st.markdown("---")

        st.subheader(
            "✉️ Personalized Recovery Message"
        )


        days = int(
            row["days_overdue"]
        )


        amount = float(
            row["invoice_amount"]
        )


        invoice_id = row[
            "invoice_id"
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

We would appreciate it if you could
arrange the payment at your earliest
convenience.

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

If you are experiencing payment
difficulties, please contact our team.

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
as soon as possible.

If you are experiencing difficulties,
please contact our recovery team.

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

We are writing regarding outstanding
invoice {invoice_id} for ₹{amount:,.2f}.

The payment is currently {days} days overdue.

Please contact our recovery team as soon
as possible to resolve the outstanding
balance.

If there is a dispute or payment difficulty,
we are available to discuss an appropriate
resolution.

Regards,
ReviveAI Recovery Team
"""


        st.text_input(
            "Subject",
            value=subject
        )


        st.text_area(
            "Recovery Message",
            value=message,
            height=300
        )


        # ====================================================
        # DECISION EXPLANATION
        # ====================================================

        st.markdown("---")

        st.subheader(
            "🔍 Why ReviveAI Chose This Action"
        )


        st.write(
            f"""
**Invoice:** {invoice_id}

**Days Overdue:** {days}

**Predicted Recovery Probability:**  
{row['recovery_probability_percent']:.2f}%

**Expected Recovery:**  
{format_rupees(row['expected_recovery'])}

**Risk Level:** {row['risk_level']}

**Priority:** {row['priority_category']}

**Recommended Action:**  
{row['recommended_action']}
"""
        )


        # ====================================================
        # AI ACTION → RECOVERY TRACKING
        # ====================================================

        st.markdown("---")

        st.subheader(
            "⚡ Execute AI Recommended Action"
        )

        st.write(
            "Record the action recommended by ReviveAI "
            "and track its real-world recovery outcome."
        )


        with st.form(
            "ai_action_tracking_form"
        ):

            ai_action_status = st.selectbox(
                "Action Status",
                [
                    "Action Taken",
                    "Follow-up Required",
                    "Partially Recovered",
                    "Recovered",
                    "Failed"
                ],
                key="ai_action_status"
            )


            ai_recovered_amount = st.number_input(
                "Recovered Amount (₹)",
                min_value=0.0,
                max_value=float(
                    row["invoice_amount"]
                ),
                value=0.0,
                step=100.0,
                key="ai_recovered_amount"
            )


            ai_recovery_date = st.date_input(
                "Recovery Date",
                value=None,
                key="ai_recovery_date"
            )


            ai_next_followup = st.date_input(
                "Next Follow-up Date",
                value=None,
                key="ai_next_followup"
            )


            ai_notes = st.text_area(
                "Notes",
                placeholder=(
                    "Add notes about the action taken..."
                ),
                key="ai_notes"
            )


            record_ai_action = st.form_submit_button(
                "⚡ Record AI Recommended Action",
                width="stretch"
            )


            if record_ai_action:

                add_recovery_action(
                    invoice_id=row["invoice_id"],
                    customer_id=row["customer_id"],
                    recommended_action=row[
                        "recommended_action"
                    ],
                    actual_action=row[
                        "recommended_action"
                    ],
                    recovery_status=ai_action_status,
                    recovered_amount=ai_recovered_amount,
                    recovery_date=(
                        str(ai_recovery_date)
                        if ai_recovery_date
                        else None
                    ),
                    next_followup_date=(
                        str(ai_next_followup)
                        if ai_next_followup
                        else None
                    ),
                    notes=ai_notes
                )


                st.success(
                    f"AI recommended action for "
                    f"{row['invoice_id']} "
                    f"has been recorded!"
                )


                st.rerun()


# ============================================================
# PAGE 5 — RECOVERY TRACKING
# ============================================================

elif page == "📈 Recovery Tracking":

    st.header(
        "📈 Recovery Tracking"
    )

    st.caption(
        "Track recovery actions, outcomes, recovered revenue, "
        "and follow-ups."
    )


    # ========================================================
    # LOAD TRACKING DATA
    # ========================================================

    tracking_df = get_recovery_tracking()


    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    if tracking_df.empty:

        total_actions = 0

        successful_recoveries = 0

        revenue_recovered = 0

        followups_required = 0

    else:

        total_actions = len(
            tracking_df
        )


        successful_recoveries = len(
            tracking_df[
                tracking_df[
                    "recovery_status"
                ]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "recovered",
                        "successful",
                        "partially recovered"
                    ]
                )
            ]
        )


        revenue_recovered = (
            tracking_df[
                "recovered_amount"
            ]
            .fillna(0)
            .sum()
        )


        followups_required = tracking_df[
            tracking_df[
                "next_followup_date"
            ].notna()
            &
            (
                tracking_df[
                    "next_followup_date"
                ].astype(str)
                != ""
            )
        ].shape[0]


    # ========================================================
    # KPI CARDS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Actions Taken",
            f"{total_actions:,}"
        )


    with col2:

        st.metric(
            "Successful Recoveries",
            f"{successful_recoveries:,}"
        )


    with col3:

        st.metric(
            "Revenue Recovered",
            f"₹{revenue_recovered:,.2f}"
        )


    with col4:

        st.metric(
            "Follow-ups Scheduled",
            f"{followups_required:,}"
        )


    st.divider()


    # ========================================================
    # RECORD NEW RECOVERY ACTION
    # ========================================================

    st.subheader(
        "📝 Record Recovery Action"
    )


    opportunities_path = os.path.join(
        BASE_DIR,
        "outputs",
        "recovery_opportunities.csv"
    )


    if os.path.exists(
        opportunities_path
    ):

        opportunities_df = pd.read_csv(
            opportunities_path
        )

    else:

        opportunities_df = recovery_df.copy()


    overdue_invoices = opportunities_df[
        opportunities_df[
            "days_overdue"
        ] > 0
    ].copy()


    if not overdue_invoices.empty:

        selected_invoice = st.selectbox(
            "Select Invoice",
            overdue_invoices[
                "invoice_id"
            ].tolist(),
            key="tracking_invoice"
        )


        selected_row = overdue_invoices[
            overdue_invoices[
                "invoice_id"
            ]
            == selected_invoice
        ].iloc[0]


        # ====================================================
        # DISPLAY SELECTED INVOICE
        # ====================================================

        info1, info2, info3, info4 = st.columns(4)


        with info1:

            st.write(
                "**Invoice Amount**"
            )

            st.write(
                f"₹{selected_row['invoice_amount']:,.2f}"
            )


        with info2:

            st.write(
                "**Days Overdue**"
            )

            st.write(
                f"{int(selected_row['days_overdue'])} days"
            )


        with info3:

            st.write(
                "**Recovery Probability**"
            )

            st.write(
                f"{selected_row['recovery_probability_percent']:.2f}%"
            )


        with info4:

            st.write(
                "**Recommended Action**"
            )

            st.write(
                selected_row[
                    "recommended_action"
                ]
            )


        st.divider()


        # ====================================================
        # ACTION FORM
        # ====================================================

        with st.form(
            "recovery_action_form"
        ):

            actual_action = st.selectbox(
                "Actual Action Taken",
                [
                    "Automated reminder",
                    "Personalized reminder",
                    "Payment assistance",
                    "5% discount + personalized reminder",
                    "Escalate to human recovery team",
                    "Phone call",
                    "Email",
                    "Other"
                ]
            )


            recovery_status = st.selectbox(
                "Recovery Status",
                [
                    "Action Taken",
                    "Follow-up Required",
                    "Partially Recovered",
                    "Recovered",
                    "Failed"
                ]
            )


            recovered_amount = st.number_input(
                "Recovered Amount (₹)",
                min_value=0.0,
                max_value=float(
                    selected_row[
                        "invoice_amount"
                    ]
                ),
                value=0.0,
                step=100.0
            )


            recovery_date = st.date_input(
                "Recovery Date",
                value=None
            )


            next_followup_date = st.date_input(
                "Next Follow-up Date",
                value=None
            )


            notes = st.text_area(
                "Notes",
                placeholder=(
                    "Enter notes about the recovery action..."
                )
            )


            submitted = st.form_submit_button(
                "💾 Save Recovery Action",
                width="stretch"
            )


            if submitted:

                add_recovery_action(
                    invoice_id=selected_row[
                        "invoice_id"
                    ],
                    customer_id=selected_row[
                        "customer_id"
                    ],
                    recommended_action=selected_row[
                        "recommended_action"
                    ],
                    actual_action=actual_action,
                    recovery_status=recovery_status,
                    recovered_amount=recovered_amount,
                    recovery_date=(
                        str(recovery_date)
                        if recovery_date
                        else None
                    ),
                    next_followup_date=(
                        str(next_followup_date)
                        if next_followup_date
                        else None
                    ),
                    notes=notes
                )


                st.success(
                    f"Recovery action for "
                    f"{selected_row['invoice_id']} "
                    f"recorded successfully!"
                )


                st.rerun()


    else:

        st.info(
            "No overdue invoices available "
            "for recovery tracking."
        )


    st.divider()


    # ========================================================
    # RECOVERY HISTORY
    # ========================================================

    st.subheader(
        "📋 Recovery Action History"
    )


    tracking_df = get_recovery_tracking()


    if tracking_df.empty:

        st.info(
            "No recovery actions have been "
            "recorded yet."
        )

    else:

        display_columns = [
            "invoice_id",
            "customer_id",
            "recommended_action",
            "actual_action",
            "action_date",
            "recovery_status",
            "recovered_amount",
            "recovery_date",
            "next_followup_date",
            "notes"
        ]


        available_columns = [
            column
            for column in display_columns
            if column in tracking_df.columns
        ]


        st.dataframe(
            tracking_df[
                available_columns
            ],
            width="stretch",
            hide_index=True
        )


    st.divider()


    # ========================================================
    # INDIVIDUAL INVOICE HISTORY
    # ========================================================

    st.subheader(
        "🔎 Invoice Recovery History"
    )


    if not overdue_invoices.empty:

        history_invoice = st.selectbox(
            "Select Invoice to View History",
            overdue_invoices[
                "invoice_id"
            ].tolist(),
            key="history_invoice"
        )


        history_df = get_invoice_history(
            history_invoice
        )


        if history_df.empty:

            st.info(
                f"No recovery actions recorded "
                f"for {history_invoice}."
            )

        else:

            st.dataframe(
                history_df,
                width="stretch",
                hide_index=True
            )

# ============================================================
# PAGE 6 — AI ASSISTANT
# ============================================================

elif page == "💬 AI Assistant":

    st.title("💬 AI Revenue Assistant")

    st.write(
        "Ask questions about your revenue, customers, "
        "invoices, risk, and recovery opportunities."
    )

    st.info(
        "💡 This assistant works locally using your ReviveAI "
        "data. No OpenAI API or internet connection is required."
    )

    st.markdown("---")

    # ========================================================
    # QUESTION INPUT
    # ========================================================

    user_question = st.text_input(
        "Ask your question:",
        placeholder=(
            "Example: Which customers have the highest "
            "recovery potential?"
        ),
        key="local_ai_question"
    )

    # ========================================================
    # EXAMPLE QUESTIONS
    # ========================================================

    st.subheader("💡 Example Questions")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "• Which customers have the highest "
            "recovery potential?"
        )

        st.write(
            "• Which invoices should we recover first?"
        )

        st.write(
            "• How much overdue revenue do we have?"
        )

    with col2:

        st.write(
            "• How much revenue is at risk?"
        )

        st.write(
            "• What recovery actions should we take?"
        )

        st.write(
            "• What is our total revenue?"
        )

    st.markdown("---")

    # ========================================================
    # ASK ASSISTANT
    # ========================================================

    if st.button(
        "🤖 Ask ReviveAI",
        width="stretch",
        key="local_ai_button"
    ):

        if not user_question.strip():

            st.warning(
                "Please enter a question first."
            )

        else:

            question = user_question.lower().strip()

            # =================================================
            # LOAD DATA
            # =================================================

            df = load_recovery_data()

            if df.empty:

                st.error(
                    "No recovery data is available."
                )

            else:

                # =============================================
                # BASIC CALCULATIONS
                # =============================================

                total_revenue = (
                    df["invoice_amount"]
                    .fillna(0)
                    .sum()
                )

                overdue_df = df[
                    df["days_overdue"] > 0
                ].copy()

                overdue_revenue = (
                    overdue_df["invoice_amount"]
                    .fillna(0)
                    .sum()
                )

                expected_recovery = (
                    overdue_df["expected_recovery"]
                    .fillna(0)
                    .sum()
                )

                high_risk_df = overdue_df[
                    overdue_df["risk_level"].isin(
                        ["High", "Critical"]
                    )
                ].copy()

                high_risk_revenue = (
                    high_risk_df["invoice_amount"]
                    .fillna(0)
                    .sum()
                )

                # =============================================
                # RESPONSE HEADER
                # =============================================

                st.markdown("---")

                st.subheader(
                    "🤖 ReviveAI Response"
                )

                # =================================================
                # 1. HIGHEST RECOVERY CUSTOMERS
                # =================================================

                if (
                    "customer" in question
                    and (
                        "highest" in question
                        or "potential" in question
                        or "recover" in question
                    )
                ):

                    customer_data = (
                        df.groupby("customer_id")
                        .agg(
                            Invoices=(
                                "invoice_id",
                                "count"
                            ),
                            Invoice_Value=(
                                "invoice_amount",
                                "sum"
                            ),
                            Expected_Recovery=(
                                "expected_recovery",
                                "sum"
                            )
                        )
                        .sort_values(
                            "Expected_Recovery",
                            ascending=False
                        )
                        .head(10)
                        .reset_index()
                    )

                    st.success(
                        "🔥 Customers with the highest "
                        "recovery potential:"
                    )

                    st.dataframe(
                        customer_data,
                        use_container_width=True,
                        hide_index=True
                    )

                    if not customer_data.empty:

                        top_customer = (
                            customer_data.iloc[0]
                        )

                        st.write(
                            f"**Top customer:** "
                            f"{top_customer['customer_id']} "
                            f"with expected recovery of "
                            f"₹{top_customer['Expected_Recovery']:,.2f}."
                        )

                # =================================================
                # 2. TOP INVOICES TO RECOVER
                # =================================================

                elif (
                    "invoice" in question
                    and (
                        "first" in question
                        or "priority" in question
                        or "recover" in question
                        or "highest" in question
                    )
                ):

                    top_invoices = (
                        overdue_df
                        .sort_values(
                            "expected_recovery",
                            ascending=False
                        )
                        .head(10)
                        .copy()
                    )

                    st.success(
                        "🎯 These invoices should be "
                        "considered first for recovery:"
                    )

                    invoice_columns = [
                        "invoice_id",
                        "customer_id",
                        "invoice_amount",
                        "days_overdue",
                        "recovery_probability_percent",
                        "expected_recovery",
                        "risk_level",
                        "priority_category"
                    ]

                    available_columns = [
                        column
                        for column in invoice_columns
                        if column in top_invoices.columns
                    ]

                    st.dataframe(
                        top_invoices[
                            available_columns
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                # =================================================
                # 3. REVENUE AT RISK
                # =================================================

                elif (
                    "risk" in question
                    or "at risk" in question
                ):

                    st.info(
                        f"💰 Total invoice revenue: "
                        f"₹{total_revenue:,.2f}"
                    )

                    st.warning(
                        f"⏰ Overdue revenue: "
                        f"₹{overdue_revenue:,.2f}"
                    )

                    st.error(
                        f"🚨 High/Critical risk revenue: "
                        f"₹{high_risk_revenue:,.2f}"
                    )

                    st.success(
                        f"🎯 Expected recoverable revenue: "
                        f"₹{expected_recovery:,.2f}"
                    )

                    if overdue_revenue > 0:

                        risk_percentage = (
                            high_risk_revenue
                            / overdue_revenue
                            * 100
                        )

                        st.write(
                            f"High/Critical cases represent "
                            f"approximately "
                            f"**{risk_percentage:.1f}%** "
                            f"of overdue revenue."
                        )

                # =================================================
                # 4. RECOVERY ACTIONS
                # =================================================

                elif (
                    "action" in question
                    or "recommend" in question
                    or "what should we do" in question
                ):

                    if (
                        "recommended_action"
                        in df.columns
                    ):

                        actions = (
                            overdue_df
                            .groupby(
                                "recommended_action"
                            )
                            .agg(
                                Invoices=(
                                    "invoice_id",
                                    "count"
                                ),
                                Expected_Recovery=(
                                    "expected_recovery",
                                    "sum"
                                )
                            )
                            .sort_values(
                                "Expected_Recovery",
                                ascending=False
                            )
                            .reset_index()
                        )

                        st.success(
                            "🤖 Recommended recovery actions:"
                        )

                        st.dataframe(
                            actions,
                            use_container_width=True,
                            hide_index=True
                        )

                        if not actions.empty:

                            best_action = (
                                actions.iloc[0]
                            )

                            st.write(
                                f"**Highest recovery opportunity:** "
                                f"{best_action['recommended_action']}"
                            )

                    else:

                        st.warning(
                            "Recommended action data "
                            "is not available."
                        )

                # =================================================
                # 5. OVERDUE INFORMATION
                # =================================================

                elif (
                    "overdue" in question
                    or "late" in question
                ):

                    st.info(
                        f"⏰ Number of overdue invoices: "
                        f"**{len(overdue_df):,}**"
                    )

                    st.warning(
                        f"💰 Total overdue revenue: "
                        f"**₹{overdue_revenue:,.2f}**"
                    )

                    if not overdue_df.empty:

                        top_overdue = (
                            overdue_df
                            .sort_values(
                                "days_overdue",
                                ascending=False
                            )
                            .head(10)
                        )

                        st.subheader(
                            "📋 Most Overdue Invoices"
                        )

                        overdue_columns = [
                            "invoice_id",
                            "customer_id",
                            "invoice_amount",
                            "days_overdue",
                            "risk_level",
                            "expected_recovery"
                        ]

                        available_columns = [
                            column
                            for column in overdue_columns
                            if column in top_overdue.columns
                        ]

                        st.dataframe(
                            top_overdue[
                                available_columns
                            ],
                            use_container_width=True,
                            hide_index=True
                        )

                # =================================================
                # 6. TOTAL REVENUE
                # =================================================

                elif (
                    "total revenue" in question
                    or (
                        "revenue" in question
                        and "risk" not in question
                    )
                ):

                    st.success(
                        f"💰 Total invoice revenue: "
                        f"₹{total_revenue:,.2f}"
                    )

                    st.info(
                        f"⏰ Overdue revenue: "
                        f"₹{overdue_revenue:,.2f}"
                    )

                    st.success(
                        f"🎯 Expected recovery: "
                        f"₹{expected_recovery:,.2f}"
                    )

                # =================================================
                # 7. DEFAULT RESPONSE
                # =================================================

                else:

                    st.info(
                        "I can analyze your ReviveAI "
                        "revenue recovery data."
                    )

                    st.write(
                        "Try one of these questions:"
                    )

                    st.write(
                        "🔹 Which customers have the "
                        "highest recovery potential?"
                    )

                    st.write(
                        "🔹 Which invoices should we "
                        "recover first?"
                    )

                    st.write(
                        "🔹 How much revenue is at risk?"
                    )

                    st.write(
                        "🔹 What recovery actions "
                        "should we take?"
                    )

                    st.write(
                        "🔹 How much overdue revenue "
                        "do we have?"
                    )

                    st.write(
                        "🔹 What is our total revenue?"
                    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.success(
    "System Status: Operational"
)

st.sidebar.caption(
    "ReviveAI v1.0 | Major Project Prototype"
)
