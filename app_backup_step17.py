import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine


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

    if os.path.exists(path):
        return pd.read_csv(path)

    return pd.DataFrame()


recovery_df = load_recovery_data()

customer_segments_df = load_customer_segments()


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
        "🤖 AI Action Center"
    ]
)


# ============================================================
# FILTERS
# ============================================================

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

    st.header("🏠 Revenue Recovery Command Center")

    st.write(
        "A real-time overview of revenue exposure, "
        "recovery potential and operational priorities."
    )

    overdue_df = filtered_df[
        filtered_df["days_overdue"] > 0
    ].copy()

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

    st.subheader("📈 Revenue Recovery Funnel")

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
        use_container_width=True
    )

    # ========================================================
    # TWO CHARTS
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "🚨 Risk Distribution"
        )

        risk_counts = (
            filtered_df[
                filtered_df["days_overdue"] > 0
            ]["risk_level"]
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
            use_container_width=True
        )

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
            use_container_width=True
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
        use_container_width=True,
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
        top_df[columns].head(100),
        use_container_width=True,
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
        use_container_width=True
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

    if not customer_segments_df.empty:

        # ====================================================
        # CUSTOMER SEGMENT DISTRIBUTION
        # ====================================================

        segment_counts = (
            customer_segments_df[
                "customer_segment_label"
            ]
            .value_counts()
            .reset_index()
        )

        segment_counts.columns = [
            "Customer Segment",
            "Customers"
        ]

        col1, col2 = st.columns(2)

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
                use_container_width=True
            )

        with col2:

            st.subheader(
                "💎 Customer Value vs Risk"
            )

            fig_customer = px.scatter(
                customer_segments_df,
                x="customer_lifetime_value",
                y="average_days_overdue",
                size="total_invoice_value",
                color="customer_segment_label",
                hover_name="customer_id"
            )

            st.plotly_chart(
                fig_customer,
                use_container_width=True
            )

        st.markdown("---")

        # ====================================================
        # CUSTOMER TABLE
        # ====================================================

        st.subheader(
            "🏆 Customer Portfolio"
        )

        customer_columns = [
            "customer_id",
            "customer_segment_label",
            "total_invoices",
            "total_invoice_value",
            "average_days_overdue",
            "late_payment_rate",
            "recovery_rate",
            "customer_lifetime_value"
        ]

        available_columns = [
            col for col in customer_columns
            if col in customer_segments_df.columns
        ]

        st.dataframe(
            customer_segments_df[
                available_columns
            ].sort_values(
                "customer_lifetime_value",
                ascending=False
            ).head(100),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "Customer segmentation file not found."
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
            overdue_df["invoice_id"].tolist()
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