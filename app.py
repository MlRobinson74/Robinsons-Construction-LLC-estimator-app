import streamlit as st
from datetime import date
from pathlib import Path
import base64

st.set_page_config(page_title="Robinson's Construction Estimator", layout="wide")

st.title("Robinson's Construction LLC — Photo Estimate App")
st.caption("Preliminary construction estimating tool for field-to-office use")

# ---------- Pricing Defaults ----------
DEFAULTS = {
    "Deck": {
        "labor_unit": "sq ft",
        "labor_rate": 28.0,
        "material_rate": 38.0,
        "description": "Deck framing/decking estimate based on square footage. Add railings, stairs, sonotubes, trim, and disposal as needed."
    },
    "Framing": {
        "labor_unit": "sq ft",
        "labor_rate": 18.0,
        "material_rate": 35.0,
        "description": "Rough framing estimate based on building square footage. Includes wall/roof framing allowance."
    },
    "Siding": {
        "labor_unit": "square",
        "labor_rate": 650.0,
        "material_rate": 450.0,
        "description": "Siding estimate based on siding squares. One square equals 100 sq ft."
    },
    "Roofing": {
        "labor_unit": "square",
        "labor_rate": 550.0,
        "material_rate": 650.0,
        "description": "Roofing estimate based on roof squares. Adjust for pitch, height, chimneys, dormers, and tear-off."
    },
    "Trim / Interior Carpentry": {
        "labor_unit": "hour",
        "labor_rate": 75.0,
        "material_rate": 25.0,
        "description": "Interior carpentry estimate based on hours plus material allowance."
    },
    "Repair / Punch List": {
        "labor_unit": "hour",
        "labor_rate": 100.0,
        "material_rate": 35.0,
        "description": "Repair/punch-list estimate based on hours plus material allowance."
    },
}

# ---------- Sidebar Defaults ----------
st.sidebar.header("Company Pricing Defaults")
carpenter_rate = st.sidebar.number_input("Carpenter hourly rate", value=75.0, step=5.0)
master_rate = st.sidebar.number_input("Master builder hourly rate", value=100.0, step=5.0)
helper_rate = st.sidebar.number_input("Helper hourly rate", value=75.0, step=5.0)
profit_overhead_percent = st.sidebar.number_input("Overhead / profit %", value=10.0, step=1.0)
contingency_percent = st.sidebar.number_input("Contingency %", value=5.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.caption("Edit the rates in app.py later to match your real pricing.")

# ---------- Input Form ----------
with st.form("estimate_form"):
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer name")
        job_address = st.text_input("Job address")
        estimate_date = st.date_input("Estimate date", value=date.today())
        job_type = st.selectbox("Job type", list(DEFAULTS.keys()))
        project_title = st.text_input("Project title", value=f"{job_type} Estimate")
    with col2:
        uploaded_files = st.file_uploader(
            "Upload job photos",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
        )
        scope_notes = st.text_area("Field notes / scope description", height=150)

    st.subheader("Measurements")
    info = DEFAULTS[job_type]
    st.info(info["description"])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        length = st.number_input("Length (ft)", value=0.0, step=1.0)
    with m2:
        width = st.number_input("Width (ft)", value=0.0, step=1.0)
    with m3:
        height = st.number_input("Height (ft)", value=0.0, step=1.0)
    with m4:
        manual_quantity = st.number_input("Manual quantity override", value=0.0, step=1.0)

    st.caption("For siding, enter wall length and height. For roofing, enter roof squares manually if known. For hourly work, enter estimated hours in manual quantity.")

    st.subheader("Labor")
    l1, l2, l3, l4 = st.columns(4)
    with l1:
        crew_carpenters = st.number_input("Carpenters", value=1, min_value=0, step=1)
    with l2:
        crew_helpers = st.number_input("Helpers", value=0, min_value=0, step=1)
    with l3:
        master_builder = st.checkbox("Master builder on site")
    with l4:
        labor_days = st.number_input("Labor days", value=1.0, step=0.5)

    l5, l6, l7 = st.columns(3)
    with l5:
        hours_per_day = st.number_input("Hours per day", value=8.0, step=0.5)
    with l6:
        travel_hours_per_day = st.number_input("Travel hours per day", value=0.0, step=0.5)
    with l7:
        custom_labor_hours = st.number_input("Custom total labor hours override", value=0.0, step=1.0)

    st.subheader("Line Item Add-ons")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        stairs_allowance = st.number_input("Stairs allowance", value=0.0, step=100.0)
    with a2:
        railing_allowance = st.number_input("Railing allowance", value=0.0, step=100.0)
    with a3:
        equipment_rental = st.number_input("Equipment rental / lift", value=0.0, step=100.0)
    with a4:
        dumpster_disposal = st.number_input("Dumpster / disposal", value=0.0, step=100.0)

    a5, a6, a7, a8 = st.columns(4)
    with a5:
        permit_allowance = st.number_input("Permit allowance", value=0.0, step=50.0)
    with a6:
        delivery_fee = st.number_input("Material delivery", value=0.0, step=50.0)
    with a7:
        extra_material_allowance = st.number_input("Extra material allowance", value=0.0, step=100.0)
    with a8:
        other_allowance = st.number_input("Other allowance", value=0.0, step=100.0)

    st.subheader("Pricing Overrides")
    p1, p2 = st.columns(2)
    with p1:
        labor_unit_rate = st.number_input(f"Labor rate per {info['labor_unit']}", value=float(info["labor_rate"]), step=25.0)
    with p2:
        material_unit_rate = st.number_input(f"Material rate per {info['labor_unit']}", value=float(info["material_rate"]), step=25.0)

    submitted = st.form_submit_button("Calculate Estimate")

# ---------- Calculation ----------
if submitted:
    if manual_quantity > 0:
        quantity = manual_quantity
    elif job_type == "Siding":
        quantity = (length * height) / 100 if length and height else 0
    elif job_type == "Roofing":
        quantity = manual_quantity
    elif job_type in ["Trim / Interior Carpentry", "Repair / Punch List"]:
        quantity = custom_labor_hours if custom_labor_hours > 0 else labor_days * hours_per_day
    else:
        quantity = length * width if length and width else 0

    unit_labor_total = quantity * labor_unit_rate
    material_total = quantity * material_unit_rate + extra_material_allowance

    if custom_labor_hours > 0:
        labor_hours = custom_labor_hours
    else:
        field_hours = labor_days * (hours_per_day + travel_hours_per_day)
        labor_hours = (crew_carpenters + crew_helpers + (1 if master_builder else 0)) * field_hours

    crew_labor_total = 0
    crew_labor_total += crew_carpenters * labor_days * (hours_per_day + travel_hours_per_day) * carpenter_rate
    crew_labor_total += crew_helpers * labor_days * (hours_per_day + travel_hours_per_day) * helper_rate
    if master_builder:
        crew_labor_total += labor_days * (hours_per_day + travel_hours_per_day) * master_rate

    # Use higher of unit labor or crew labor so it does not underprice simple entries.
    labor_total = max(unit_labor_total, crew_labor_total)

    add_ons_total = sum([
        stairs_allowance, railing_allowance, equipment_rental, dumpster_disposal,
        permit_allowance, delivery_fee, other_allowance
    ])

    subtotal = labor_total + material_total + add_ons_total
    contingency = subtotal * (contingency_percent / 100)
    overhead_profit = (subtotal + contingency) * (profit_overhead_percent / 100)
    total = subtotal + contingency + overhead_profit

    st.success("Estimate calculated")

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Labor", f"${labor_total:,.2f}")
    r2.metric("Materials", f"${material_total:,.2f}")
    r3.metric("Add-ons", f"${add_ons_total:,.2f}")
    r4.metric("Total Estimate", f"${total:,.2f}")

    st.subheader("Office Estimate Summary")
    estimate_text = f"""
ROBINSON'S CONSTRUCTION LLC
Preliminary Construction Estimate

Date: {estimate_date}
Customer: {customer_name}
Job Address: {job_address}
Project: {project_title}
Job Type: {job_type}

Scope of Work:
{scope_notes}

Measurements / Quantity:
Length: {length} ft
Width: {width} ft
Height: {height} ft
Estimated Quantity: {quantity:.2f} {info['labor_unit']}

Labor:
Carpenters: {crew_carpenters}
Helpers: {crew_helpers}
Master Builder On Site: {'Yes' if master_builder else 'No'}
Labor Days: {labor_days}
Hours Per Day: {hours_per_day}
Travel Hours Per Day: {travel_hours_per_day}
Estimated Labor Hours: {labor_hours:.2f}
Labor Total: ${labor_total:,.2f}

Materials:
Material Allowance: ${material_total:,.2f}

Add-ons:
Stairs Allowance: ${stairs_allowance:,.2f}
Railing Allowance: ${railing_allowance:,.2f}
Equipment Rental / Lift: ${equipment_rental:,.2f}
Dumpster / Disposal: ${dumpster_disposal:,.2f}
Permit Allowance: ${permit_allowance:,.2f}
Material Delivery: ${delivery_fee:,.2f}
Other Allowance: ${other_allowance:,.2f}

Subtotal: ${subtotal:,.2f}
Contingency: ${contingency:,.2f}
Overhead / Profit: ${overhead_profit:,.2f}

TOTAL PRELIMINARY ESTIMATE: ${total:,.2f}

Notes:
This is a preliminary estimate based on submitted photos, field notes, and measurements. Final pricing is subject to site inspection, confirmed material selections, hidden conditions, permit requirements, engineering requirements, and final approved scope of work.
"""
    st.text_area("Copy/paste estimate text", estimate_text, height=500)

    b64 = base64.b64encode(estimate_text.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64}" download="robinsons_estimate.txt">Download estimate text file</a>'
    st.markdown(href, unsafe_allow_html=True)

    if uploaded_files:
        st.subheader("Uploaded Photos")
        cols = st.columns(3)
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(file, caption=file.name, use_container_width=True)
else:
    st.warning("Enter job information and click Calculate Estimate.")

st.markdown("---")
st.caption("Built as a starter prototype. Photo upload stores photos only during the app session unless connected to a database later.")
