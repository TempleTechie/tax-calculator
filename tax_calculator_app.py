import streamlit as st

# Function to calculate tax based on the regime
def calculate_tax(income, is_salaried, regime="new"):
    # Standard Deduction
    if is_salaried:
        income = max(0, income - 75000)  

    # New Tax Regime Slabs (Budget 2025)
    new_tax_slabs = [
        (400000, 0.00),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float('inf'), 0.30)
    ]

    # Old Tax Regime Slabs
    old_tax_slabs = [
        (250000, 0.00),
        (500000, 0.05),
        (1000000, 0.20),
        (float('inf'), 0.30)
    ]

    tax_slabs = new_tax_slabs if regime == "new" else old_tax_slabs

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

# Function to generate and download PDF
def generate_pdf(income, is_salaried, new_tax, old_tax, new_breakdown, old_breakdown):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    pdf.cell(200, 10, "India Income Tax Calculation (2025)", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Annual Income: ₹{income:,.2f}", ln=True)
    if is_salaried:
        pdf.cell(200, 10, "Standard Deduction Applied: ₹75,000", ln=True)
    pdf.ln(5)

    # New Regime
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"New Tax Regime: ₹{new_tax:,.2f}", ln=True)
    pdf.set_font("Arial", size=12)
    for line in new_breakdown:
        pdf.cell(200, 7, line, ln=True)
    
    pdf.ln(5)
    
    # Old Regime
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"Old Tax Regime: ₹{old_tax:,.2f}", ln=True)
    pdf.set_font("Arial", size=12)
    for line in old_breakdown:
        pdf.cell(200, 7, line, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Thank you for using the Tax Calculator!", ln=True, align='C')

    pdf.output("Tax_Calculation.pdf")

# Streamlit UI
st.set_page_config(page_title="2025 India Tax Calculator", layout="centered", initial_sidebar_state="collapsed")
st.title("India 2025 Income Tax Calculator")

st.markdown("### 💰 Compare Old vs New Tax Regime")

# Input fields
income = st.number_input("Enter your annual income (in ₹):", min_value=0, step=1000, value=800000)
is_salaried = st.checkbox("Are you a salaried individual? (₹75,000 standard deduction applies)")

# Calculate Tax for Both Regimes
new_tax, new_breakdown = calculate_tax(income, is_salaried, regime="new")
old_tax, old_breakdown = calculate_tax(income, is_salaried, regime="old")

# Display Tax Results
st.subheader("💵 Total Tax Payable:")
st.write(f"🆕 **New Tax Regime:** ₹{new_tax:,.2f}")
st.write(f"🆙 **Old Tax Regime:** ₹{old_tax:,.2f}")

st.markdown("### 📊 Tax Slab Breakdown:")

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🆕 New Regime")
    for item in new_breakdown:
        st.write(f"- {item}")

with col2:
    st.markdown("#### 🆙 Old Regime")
    for item in old_breakdown:
        st.write(f"- {item}")


st.markdown("---")
st.caption("📌 Note: This is a simplified calculation based on the **2025 Budget** tax slabs.")
