import streamlit as st
from supabase import create_client
from datetime import datetime

# ====================================
# STREAMLIT CONFIG
# ====================================

st.set_page_config(
    page_title="RentalSnapshot",
    layout="centered"
)

# ====================================
# SUPABASE
# ====================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# ====================================
# SESSION
# ====================================

if "user" not in st.session_state:
    st.session_state.user = None

# ====================================
# TITLE
# ====================================

st.title("🏠 RentalSnapshot")

st.write(
    "Quick rental property profitability analysis."
)

# ====================================
# LOGIN
# ====================================

st.header("🔐 Login")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

col1, col2 = st.columns(2)

with col1:

    if st.button("Login"):

        try:

            user = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            st.session_state.user = user.user

            st.success("Successfully logged in")

except Exception as e:
    st.error(f"Login error: {e}")

with col2:

    if st.button("Create account"):

        try:

            supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            st.success("Account created")

except Exception as e:
    st.error(f"Account creation error: {e}")

# ====================================
# APPLICATION
# ====================================

if st.session_state.user:

    st.warning(
        "⚠️ This tool provides estimates for informational purposes only "
        "and does not constitute financial or real estate advice."
    )

    # ====================================
    # DEAL INFORMATION
    # ====================================

    with st.expander(
        "📥 Deal Information",
        expanded=True
    ):

        purchase_price = st.number_input(
            "Purchase Price ($)",
            min_value=0.0,
            value=300000.0
        )

        down_payment = st.number_input(
            "Down Payment ($)",
            min_value=0.0,
            value=60000.0
        )

        monthly_rent = st.number_input(
            "Monthly Rent ($)",
            min_value=0.0,
            value=2000.0
        )

        mortgage_payment = st.number_input(
            "Monthly Mortgage Payment ($)",
            min_value=0.0,
            value=1400.0
        )

    # ====================================
    # EXPENSES
    # ====================================

    with st.expander(
        "💸 Expenses",
        expanded=False
    ):

        monthly_expenses = st.number_input(
            "Monthly Operating Expenses ($)",
            min_value=0.0,
            value=400.0
        )

        property_taxes = st.number_input(
            "Monthly Property Taxes ($)",
            min_value=0.0,
            value=250.0
        )

        home_insurance = st.number_input(
            "Monthly Home Insurance ($)",
            min_value=0.0,
            value=120.0
        )

        life_insurance = st.number_input(
            "Credit / Life Insurance ($)",
            min_value=0.0,
            value=80.0
        )

        vacancy_rate = st.slider(
            "Vacancy Rate (%)",
            0,
            20,
            5
        )

    # ====================================
    # ANALYZE BUTTON
    # ====================================

    st.markdown("---")

    analyze = st.button(
        "🔍 Analyze Deal",
        use_container_width=True
    )

    # ====================================
    # ANALYSIS
    # ====================================

    if analyze:

        net_income = monthly_rent * (
            1 - vacancy_rate / 100
        )

        total_expenses = (
            mortgage_payment
            + monthly_expenses
            + property_taxes
            + home_insurance
            + life_insurance
        )

        cashflow = net_income - total_expenses

        annual_cashflow = cashflow * 12

        if down_payment > 0:

            roi = (
                annual_cashflow
                / down_payment
            ) * 100

        else:
            roi = 0

        # ====================================
        # TRACKING
        # ====================================

        supabase.table(
            "usage_logs"
        ).insert({

            "user_email":
            st.session_state.user.email,

            "analyses_count": 1,

            "created_at":
            datetime.utcnow().isoformat(timespec="seconds")

        }).execute()

        # ====================================
        # RESULTS
        # ====================================

        st.markdown("---")

        st.header("📊 Results")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Monthly Cashflow",
                f"${cashflow:,.0f}"
            )

        with col2:

            st.metric(
                "ROI",
                f"{roi:.2f}%"
            )

        st.metric(
            "Annual Cashflow",
            f"${annual_cashflow:,.0f}"
        )

        # ====================================
        # VERDICT
        # ====================================

        st.header("🚦 Quick Verdict")

        if cashflow > 300:

            st.success(
                "🟢 Strong Deal"
            )

        elif cashflow > 0:

            st.warning(
                "🟡 Average Deal"
            )

        else:

            st.error(
                "🔴 Weak Deal"
            )

        # ====================================
        # STRESS TEST
        # ====================================

        st.header(
            "⚠️ Quick Stress Test"
        )

        stressed_rent = monthly_rent * 0.9

        stressed_income = (
            stressed_rent
            * (1 - vacancy_rate / 100)
        )

        stressed_cashflow = (
            stressed_income
            - total_expenses
        )

        st.write(
            f"If rent drops by 10%, "
            f"cashflow becomes "
            f"${stressed_cashflow:,.0f}"
        )

    # ====================================
    # FEEDBACK
    # ====================================

    st.markdown("---")

    st.header("💬 Feedback")

    feedback = st.text_area(
        "What is missing or frustrating?"
    )

    if st.button("Send Feedback"):

        if feedback.strip() != "":

            supabase.table(
                "feedback"
            ).insert({

                "user_email":
                st.session_state.user.email,

                "feedback":
                feedback,

                "created_at":
                datetime.utcnow().isoformat()

            }).execute()

            st.success(
                "Thanks for your feedback 🙌"
            )

        else:

            st.warning(
                "Please enter feedback before submitting."
            )
