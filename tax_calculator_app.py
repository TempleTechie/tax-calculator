import streamlit as st

# Function to calculate tax based on regime and slabs
def calculate_tax(income, is_salaried, regime, use_budget_2025):
    # Apply Standard Deduction
    standard_deduction = 75000 if regime == "New" else 50000
    if is_salaried:
        income = max(0, income - standard_deduction)
    
    # Define tax slabs
    if regime == "New":
        if use_budget_2025:
            tax_slabs = [
                (400000, 0.00), (800000, 0.05), (1200000, 0.10),
                (1600000, 0.15), (2000000, 0.20), (2400000, 0.25),
                (float('inf'), 0.30)
            ]
            tax_free_limit = 1275000 if is_salaried else 1200000
        else:
            tax_slabs = [
                (300000, 0.00), (700000, 0.05), (1000000, 0.10),
                (1200000, 0.15), (1500000, 0.20), (float('inf'), 0.30)
            ]
            tax_free_limit = 775000 if is_salaried else 700000
    else:
        tax_slabs = [
            (250000, 0.00), (500000, 0.05), (1000000, 0.20),
            (float('inf'), 0.30)
        ]
        tax_free_limit = 500000  # Rebate under Section 87A for Old Regime

    # If income is within tax-free limit, no tax
    if income <= tax_free_limit:
        return 0.0, ["No tax applicable within the limit"]

    # Calculate Tax
    tax = 0.0
    previous_limit = 0
    breakdown = []

    for limit, rate in tax_slabs:
        if income > limit:
            tax_amount = (limit - previous_limit) * rate
            tax += tax_amount
            breakdown.append(f"₹{previous_limit+1} - ₹{limit} @ {rate*100}% = ₹{tax_amount:,.2f}")
            previous_limit = limit
        else:
            tax_amount = (income - previous_limit) * rate
            tax += tax_amount
            breakdown.append(f"₹{previous_limit+1} - ₹{income} @ {rate*100}% = ₹{tax_amount:,.2f}")
            break

    return tax, breakdown

# Streamlit UI
st.markdown("<h2 style='text-align: center;'>🇮🇳 <b>India Tax Calculator (2025 Budget)</b></h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>💰 Calculate your income tax under Old & New Regime</h4>", unsafe_allow_html=True)

# User Inputs
income = st.number_input("Enter your annual income (in ₹):", min_value=0, step=1000, value=800000)

# Tax Regime Selection
regime = st.radio("Select Tax Regime:", ["New", "Old"], index=0)

# Standard Deduction Info
standard_deduction = 75000 if regime == "New" else 50000
is_salaried = st.checkbox(f"Are you a salaried individual? (Standard Deduction: ₹{standard_deduction:,})")

# Budget 2025 Slab Toggle (Only for New Regime)
use_budget_2025 = st.checkbox("Use Budget 2025 New Tax Slabs? (New Regime Only)") if regime == "New" else False

# Calculate Tax
tax_payable, tax_breakdown = calculate_tax(income, is_salaried, regime, use_budget_2025)

# Display Results
st.markdown(f"<h3>💵 <b>Total Tax Payable: ₹{tax_payable:,.2f}</b></h3>", unsafe_allow_html=True)
st.markdown("### 📊 Tax Slab Breakdown:")
for item in tax_breakdown:
    st.write(f"- {item}")

# Mobile-Friendly Styling
st.markdown("""
    <style>
        input[type=number] {
            font-size: 20px !important;
        }
        label {
            font-size: 18px !important;
        }
        h3 {
            color: #d9534f;
        }
        .stCheckbox label {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)
