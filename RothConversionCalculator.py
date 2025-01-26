# Roth Conversion Calculator
# This code uses Streamlit for the user interface and Plotly for visualization.
# Run with: streamlit run RothConversionCalculator.py
# Make sure to install needed libraries:
# pip install streamlit plotly

import streamlit as st
import plotly.graph_objects as go

# Helper function for modeling Roth conversion outcomes
# For demonstration, we will use a simplified model:
# - We estimate future tax rates based on current tax bracket.
# - We allow user to input expected retirement age, annual spending, pension, Social Security, etc.
# - We do a naive calculation to see how different partial conversions now vs. later might look.
# This can be expanded to more advanced Monte Carlo or tax bracket modeling.


def calculate_roth_conversion(
    current_age: int,
    retirement_age: int,
    current_401k_balance: float,
    annual_contributions: float,
    expected_growth_rate: float,
    annual_spending_in_retirement: float,
    pension_amount: float,
    social_security_age: int,
    social_security_amount: float,
    desired_conversion_amount: float,
    conversion_start_age: int,
    conversion_end_age: int,
    future_tax_rate: float,
    current_tax_rate: float
):
    # Basic compounding function until retirement
    years_to_retirement = retirement_age - current_age
    future_401k_balance = current_401k_balance
    for _ in range(years_to_retirement):
        future_401k_balance += annual_contributions
        future_401k_balance *= (1 + expected_growth_rate)

    # Calculate how much is converted
    # For simplicity, assume a linear conversion from conversion_start_age to conversion_end_age.

    # Effective tax on conversion:
    # This is naive. We are not factoring in the bracket system. We just apply current_tax_rate for conversions before retirement, future_tax_rate after.

    # We'll store a timeline of ages and 401(k) balances.
    # We'll assume that from retirement_age onward, the user only invests passively (no new contributions).

    # build a range from current_age to, say, 90, to track balances across time.
    timeline_ages = list(range(current_age, 91))
    timeline_401k_balances = []
    timeline_roth_balances = []

    roth_balance = 0.0
    current_401k = current_401k_balance

    # Grow the 401(k) from current_age up to retirement_age
    for age in range(current_age, retirement_age):
        current_401k += annual_contributions
        current_401k *= (1 + expected_growth_rate)
        timeline_401k_balances.append(current_401k)
        timeline_roth_balances.append(roth_balance)

    # from retirement_age to 90
    for age in range(retirement_age, 91):
        # check if we are in the range to do conversions
        if conversion_start_age <= age <= conversion_end_age:
            # we do a partial conversion from 401k to Roth
            # for simplicity, assume we do the same partial conversion each year in that range
            annual_conversion = desired_conversion_amount / (conversion_end_age - conversion_start_age + 1)
            if annual_conversion > current_401k:
                annual_conversion = current_401k  # can't convert more than we have

            # tax rate depends on if we are before or after retirement
            # for demonstration, assume that once we hit retirement age, we use future_tax_rate
            if age < retirement_age:
                tax_on_conversion = annual_conversion * current_tax_rate
            else:
                tax_on_conversion = annual_conversion * future_tax_rate

            # reduce the 401k by conversion + taxes (this is simplistic, real approach is more complex)
            current_401k -= annual_conversion

            # add net conversion to Roth
            net_converted = annual_conversion - tax_on_conversion
            if net_converted < 0:
                net_converted = 0
            roth_balance += net_converted

        # 401k growth
        current_401k *= (1 + expected_growth_rate)
        # Roth growth
        roth_balance *= (1 + expected_growth_rate)

        timeline_401k_balances.append(current_401k)
        timeline_roth_balances.append(roth_balance)

    return timeline_ages, timeline_401k_balances, timeline_roth_balances


def main():
    st.title("Roth Conversion Calculator")
    st.write("Use this calculator to explore a simplified model of when to convert 401(k) assets to Roth.")

    # Sidebar inputs
    st.sidebar.header("User Inputs")
    current_age = st.sidebar.number_input("Current Age", min_value=18, max_value=70, value=40)
    retirement_age = st.sidebar.number_input("Planned Retirement Age", min_value=current_age, max_value=70, value=65)
    current_401k_balance = st.sidebar.number_input("Current 401(k) Balance ($)", min_value=0.0, value=200000.0, step=1000.0)
    annual_contributions = st.sidebar.number_input("Annual 401(k) Contributions ($)", min_value=0.0, value=19000.0, step=1000.0)
    expected_growth_rate = st.sidebar.number_input("Expected Annual Growth Rate (%)", min_value=0.0, value=6.0, step=0.1) / 100.0
    annual_spending_in_retirement = st.sidebar.number_input("Annual Spending in Retirement ($)", min_value=0.0, value=60000.0, step=1000.0)
    pension_amount = st.sidebar.number_input("Annual Pension Income in Retirement ($)", min_value=0.0, value=0.0, step=1000.0)
    social_security_age = st.sidebar.number_input("Social Security Start Age", min_value=62, max_value=70, value=67)
    social_security_amount = st.sidebar.number_input("Estimated Social Security Annual ($)", min_value=0.0, value=25000.0, step=1000.0)
    desired_conversion_amount = st.sidebar.number_input("Total Desired Roth Conversion Amount ($)", min_value=0.0, value=100000.0, step=1000.0)
    conversion_start_age = st.sidebar.number_input("Conversion Start Age", min_value=current_age, max_value=90, value=60)
    conversion_end_age = st.sidebar.number_input("Conversion End Age", min_value=conversion_start_age, max_value=90, value=70)
    future_tax_rate = st.sidebar.number_input("Estimated Tax Rate in Retirement (%)", min_value=0.0, value=25.0, step=1.0) / 100.0
    current_tax_rate = st.sidebar.number_input("Current Marginal Tax Rate (%)", min_value=0.0, value=22.0, step=1.0) / 100.0

    # Calculate
    if st.sidebar.button("Calculate"):
        timeline_ages, timeline_401k, timeline_roth = calculate_roth_conversion(
            current_age=current_age,
            retirement_age=retirement_age,
            current_401k_balance=current_401k_balance,
            annual_contributions=annual_contributions,
            expected_growth_rate=expected_growth_rate,
            annual_spending_in_retirement=annual_spending_in_retirement,
            pension_amount=pension_amount,
            social_security_age=social_security_age,
            social_security_amount=social_security_amount,
            desired_conversion_amount=desired_conversion_amount,
            conversion_start_age=conversion_start_age,
            conversion_end_age=conversion_end_age,
            future_tax_rate=future_tax_rate,
            current_tax_rate=current_tax_rate
        )
        # Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timeline_ages, y=timeline_401k, mode='lines', name='401(k) Balance'))
        fig.add_trace(go.Scatter(x=timeline_ages, y=timeline_roth, mode='lines', name='Roth Balance'))
        fig.update_layout(
            title="401(k) and Roth Balances Over Time",
            xaxis_title="Age",
            yaxis_title="Balance ($)",
            legend=dict(x=0, y=1, bgcolor='rgba(255,255,255,0)'),
            hovermode='x'
        )
        st.plotly_chart(fig)
        st.write("This chart shows the modeled balances in your 401(k) vs. Roth account over time, given your inputs.")

        st.write("## Next Steps")
        st.write("- Consider tax brackets and future legislative changes.")
        st.write("- Factor in required minimum distributions (RMDs).")
        st.write("- Consult a professional for personalized advice.")
    else:
        st.write("Use the sidebar to input your data, then click Calculate.")

if __name__ == "__main__":
    main()
