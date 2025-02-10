import streamlit as st
import pandas as pd

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

# Helper function for formatting numbers (round to 2 decimals, no trailing zeros)
def format_number(value):
    if isinstance(value, (int, float)):
        return f"{value:.2f}".rstrip('0').rstrip('.')  # Two decimals, remove trailing zeros
    return value

# Function to calculate updated values
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
        "Scenario": f"{pass_through_rate}% Pass-Through",
        "Tariff (%)": tariff_percent,
        "US ASP (£)": round(new_asp, 2),
        "Price Change (%)": round(price_change_percent, 2),
        "Demand Change (%)": round(demand_change_percent, 2),
        "US Units Sold": new_us_units_sold,
        "U.S. Revenue (£B)": round(new_us_revenue, 2),
        "Global Revenue (£B)": round(global_revenue_new, 2),
        "Global Units Sold": global_units_sold_new,
        "Operating Profit Before Tariff (£B)": round(operating_profit_before_tariff, 2),
        "Additional Fixed Cost Burden (£B)": round(additional_fixed_cost_burden, 2),
        "Tariff Attributable to Producer (£B)": round(tariff_cost_producer, 2),
        "New Operating Profit (£B)": round(new_operating_profit, 2),
        "New Operating Margin (%)": round(new_operating_margin, 2)
    }

# Streamlit app
st.sidebar.header("User Inputs for Scenario 1")
elasticity_1 = st.sidebar.slider("Select Price-Demand Elasticity (Scenario 1)", -3.0, 0.0, -1.5, step=0.1)
pass_through_rate_1 = st.sidebar.slider("Select Pass-Through Rate (%) (Scenario 1)", 0, 100, 50, step=5)

st.sidebar.header("User Inputs for Scenario 2")
elasticity_2 = st.sidebar.slider("Select Price-Demand Elasticity (Scenario 2)", -3.0, 0.0, -1.0, step=0.1)
pass_through_rate_2 = st.sidebar.slider("Select Pass-Through Rate (%) (Scenario 2)", 0, 100, 50, step=5)

# Base scenario table
st.title("Base Scenario Reference Table (No Tariffs)")
base_values["US Revenue (£B)"] = (base_values["US ASP (£)"] * base_values["US Units Sold"]) / 1e9
base_values["Fixed Cost per Unit (£)"] = round((base_values["Total Fixed Costs (£B)"] * 1e9) / base_values["Global Units Sold"], 2)
base_df = pd.DataFrame([base_values])
base_df = base_df.applymap(format_number)  # Apply formatting
st.table(base_df[[ 
    "US ASP (£)", "US Units Sold", "US Revenue (£B)", "Global Revenue (£B)", 
    "Global Units Sold", "Fixed Cost per Unit (£)", "Total Fixed Costs (£B)", 
    "Operating Profit (£B)", "Operating Margin (%)"
]])

# Updated scenarios for Scenario 1
st.title(f"Updated Tariff Scenarios (Scenario 1: Elasticity = {elasticity_1})")
scenario_results_1 = calculate_scenario(elasticity_1, pass_through_rate_1)
scenario_df_1 = pd.DataFrame([scenario_results_1])
scenario_df_1 = scenario_df_1.applymap(format_number)  # Apply formatting
st.table(scenario_df_1)

# Updated scenarios for Scenario 2
st.title(f"Updated Tariff Scenarios (Scenario 2: Elasticity = {elasticity_2})")
scenario_results_2 = calculate_scenario(elasticity_2, pass_through_rate_2)
scenario_df_2 = pd.DataFrame([scenario_results_2])
scenario_df_2 = scenario_df_2.applymap(format_number)  # Apply formatting
st.table(scenario_df_2)
