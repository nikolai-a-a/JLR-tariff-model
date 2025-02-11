import streamlit as st
import pandas as pd

# Set page layout to wide for better screen utilization
st.set_page_config(layout="wide")

# Base model values
base_values = {
    "US ASP (£)": 70000,
    "US Units Sold": 82645,
    "Global Revenue (£B)": 29.36,
    "Global Units Sold": 431733,
    "Total Fixed Costs (£B)": 9.521,
    "Operating Profit (£B)": 2.58,
    "Operating Margin (%)": 8.8
}

# Function to properly format numbers with two decimals (removing trailing zeros)
def format_number(value):
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return value

# Function to calculate updated tariff scenarios
def calculate_scenario(elasticity, pass_through_rate):
    tariff_percent = 25  # Tariff applied as a percentage
    tariff_per_unit = base_values["US ASP (£)"] * (tariff_percent / 100)
    new_asp = base_values["US ASP (£)"] + (tariff_per_unit * (pass_through_rate / 100))
    
    price_change_percent = ((new_asp - base_values["US ASP (£)"]) / base_values["US ASP (£)"]) * 100
    demand_change_percent = elasticity * price_change_percent
    new_us_units_sold = int(base_values["US Units Sold"] * (1 + (demand_change_percent / 100)))
    new_us_revenue = (new_asp * new_us_units_sold) / 1e9  # Convert to £B
    
    global_units_sold_new = base_values["Global Units Sold"] - (base_values["US Units Sold"] - new_us_units_sold)
    global_revenue_new = (base_values["Global Revenue (£B)"] - base_values["US Revenue (£B)"]) + new_us_revenue
    
    fixed_cost_per_unit_original = (base_values["Total Fixed Costs (£B)"] * 1e9) / base_values["Global Units Sold"]
    fixed_cost_per_unit_new = (base_values["Total Fixed Costs (£B)"] * 1e9) / global_units_sold_new
    
    additional_fixed_cost_burden = ((fixed_cost_per_unit_new - fixed_cost_per_unit_original) * global_units_sold_new) / 1e9  # Convert to £B
    operating_profit_before_tariff = global_revenue_new * (base_values["Operating Margin (%)"] / 100)
    tariff_cost_producer = (tariff_per_unit * new_us_units_sold * (1 - pass_through_rate / 100)) / 1e9  # Convert to £B
    new_operating_profit = operating_profit_before_tariff - tariff_cost_producer - additional_fixed_cost_burden
    new_operating_margin = (new_operating_profit / global_revenue_new) * 100 if global_revenue_new > 0 else 0

    return {
        "Tariff (%)": tariff_percent,
        "US ASP (£)": format_number(new_asp),
        "Price Change (%)": format_number(price_change_percent),
        "Demand Change (%)": format_number(demand_change_percent),
        "US Units Sold": format_number(new_us_units_sold),
        "U.S. Revenue (£B)": format_number(new_us_revenue),
        "Global Revenue (£B)": format_number(global_revenue_new),
        "Global Units Sold": format_number(global_units_sold_new),
        "Operating Profit Before Tariff (£B)": format_number(operating_profit_before_tariff),
        "Additional Fixed Cost Burden (£B)": format_number(additional_fixed_cost_burden),
        "Tariff Attributable to Producer (£B)": format_number(tariff_cost_producer),
        "New Operating Profit (£B)": format_number(new_operating_profit),
        "New Operating Margin (%)": format_number(new_operating_margin),
    }

# Sidebar for user input (with unique keys)
st.sidebar.header("User Inputs for Scenario A")
elasticity_A = st.sidebar.slider("Select Price-Demand Elasticity", -3.0, 0.0, -1.5, step=0.25, key="elasticity_A")
pass_through_rate_A = st.sidebar.slider("Tariff Pass-Through to Consumer (%)", 0, 100, 50, step=25, key="pass_through_A")

st.sidebar.header("User Inputs for Scenario B")
elasticity_B = st.sidebar.slider("Select Price-Demand Elasticity", -3.0, 0.0, -1.0, step=0.25, key="elasticity_B")
pass_through_rate_B = st.sidebar.slider("Tariff Pass-Through to Consumer (%)", 0, 100, 50, step=25, key="pass_through_B")

# Base scenario table
st.markdown("### FY2024 Base Scenario (No Tariffs)")
base_values["US Revenue (£B)"] = (base_values["US ASP (£)"] * base_values["US Units Sold"]) / 1e9
base_values["Fixed Cost per Unit (£)"] = round((base_values["Total Fixed Costs (£B)"] * 1e9) / base_values["Global Units Sold"], 2)
base_df = pd.DataFrame([base_values])

# Apply formatting
base_df = base_df.applymap(format_number)
st.table(base_df[[ 
    "US ASP (£)", "US Units Sold", "US Revenue (£B)", "Global Revenue (£B)", 
    "Global Units Sold", "Fixed Cost per Unit (£)", "Total Fixed Costs (£B)", 
    "Operating Profit (£B)", "Operating Margin (%)"
]])

# Updated tariff scenarios
scenario_A_results = calculate_scenario(elasticity_A, pass_through_rate_A)
scenario_B_results = calculate_scenario(elasticity_B, pass_through_rate_B)

st.markdown(f"### Scenario A: Tariff Pass-Through to Consumer {pass_through_rate_A}%, Price-Demand Elasticity = {elasticity_A} ({'Inelastic' if elasticity_A > -1 else 'Unit Elastic' if elasticity_A == -1 else 'Elastic' if elasticity_A > -2 else 'Highly Elastic'})")
scenario_A_df = pd.DataFrame([scenario_A_results]).applymap(format_number)
st.table(scenario_A_df)

st.markdown(f"### Scenario B: Tariff Pass-Through to Consumer {pass_through_rate_B}%, Price-Demand Elasticity = {elasticity_B} ({'Inelastic' if elasticity_B > -1 else 'Unit Elastic' if elasticity_B == -1 else 'Elastic' if elasticity_B > -2 else 'Highly Elastic'})")
scenario_B_df = pd.DataFrame([scenario_B_results]).applymap(format_number)
st.table(scenario_B_df)
