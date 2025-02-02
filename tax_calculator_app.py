import streamlit as st
from fpdf import FPDF
import io

# Function to calculate tax
def calculate_tax(income, is_salaried, regime, use_budget_2025=False, deductions=0):
    # Apply correct standard deduction
    if is_salaried:
        if regime == "new":
            income = max(0, income - 75000)  # New Regime Standard Deduction
        else:
            income = max(0, income - 50000)  # Old Regime Standard Deduction

    # New Regime - Current Slabs (Before Budget 2025)
    current_tax_slabs = [
        (250000, 0.00),
        (500000, 0.05),
        (750000, 0.10),
        (1000000, 0.15),
        (1250000, 0.20),
        (1500000, 0.25),
        (float('inf'), 0.30)
    ]

    # New Regime - Budget 2025 Slabs
    budget_2025_tax_slabs = [
        (400000, 0.00),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float('inf'), 0.30)
    ]

    # Old Regime Slabs
    old_tax_slabs = [
        (250000, 0.00),
        (500000, 0.05),
        (1000000, 0.20),
        (float('inf'), 0.30)
    ]

    # Select correct tax slabs
    if regime == "new":
        tax_slabs = budget_2025_tax_slabs if use_budget_2025 else current_tax_slabs
    else:
        # Apply additional deductions for the old regime (like 80C, 80D, etc.)
        income = max(0, income - deductions)
        tax_slabs = old_tax_slabs

    # Calculate tax
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

# Function to generate PDF
def generate_pdf(income, is_salaried, tax_payable, breakdown, regime, use_budget_2025, deductions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    pdf.cell(200, 10, "India Tax Calculation Report (2025)", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Regime: {regime} Tax Regime", ln=True)
    pdf.cell(200, 10, f"Annual Income: INR {income:,.2f}", ln=True)
    if is_salaried:
        pdf.cell(200, 10, f"Standard Deduction Applied: INR {75000 if regime == 'new' else 50000:,.2f}", ln=True)
    if regime == "Old":
        pdf.cell(200, 10, f"Total Deductions Applied: INR {deductions:,.2f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"Total Tax Payable: INR {tax_payable:,.2f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Tax Slab Breakdown:", ln=True)
    for line in breakdown:
        pdf.cell(200, 7, line.replace("₹", "INR"), ln=True)  # Replace ₹ with INR

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Thank you for using the Tax Calculator!", ln=True, align='C')

    # Save PDF to memory buffer
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)  # Write PDF data

# Streamlit UI
st.set_page_config(page_title="🇮🇳 India Tax Calculator", layout="centered", initial_sidebar_state="collapsed")
st.title("🇮🇳 India Tax Calculator (2025 Budget)")
st.markdown("### 💰 Compare New vs Old Tax Regime & Budget 2025 Changes")

# Select tax regime
regime = st.radio("Select Tax Regime:", ["New", "Old"])

# Dynamically update standard deduction message
sd_amount = 75000 if regime == "New" else 50000
is_salaried = st.checkbox(f"Are you a salaried individual? (₹{sd_amount:,.0f} standard deduction applies)")

# Input income (must be defined before calling functions)
income = st.number_input("Enter your annual income (in ₹):", min_value=0, step=1000, value=800000)

# Additional deductions for Old Regime
deductions = 0
if regime == "Old":
    deductions = st.number_input("Enter total deductions (80C, 80D, HRA, etc.):", min_value=0, step=1000, value=150000)

# New Regime - Option to use Budget 2025 Slabs
use_budget_2025 = False
if regime == "New":
    use_budget_2025 = st.checkbox("Use Budget 2025 New Regime Slabs")

# ✅ FIX: Call calculate_tax() after defining income & regime
tax_payable, tax_breakdown = calculate_tax(income, is_salaried, regime.lower(), use_budget_2025, deductions)

# Display results
st.subheader(f"💵 Total Tax Payable: ₹{tax_payable:,.2f}")

st.markdown("### 📊 Tax Slab Breakdown:")
for item in tax_breakdown:
    st.write(f"- {item}")

# Button to generate and download PDF
if st.button("📄 Download Tax Report (PDF)"):
    pdf_bytes = generate_pdf(income, is_salaried, tax_payable, tax_breakdown, regime, use_budget_2025, deductions)
    
    st.download_button(label="📥 Click to Download PDF", 
                       data=pdf_bytes, 
                       file_name="Tax_Calculation.pdf", 
                       mime="application/pdf")
