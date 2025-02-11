import streamlit as st
import pandas as pd

# Function to determine elasticity type
def elasticity_label(elasticity):
    if elasticity > -1:
        return "Inelastic"
    elif elasticity == -1:
        return "Unit Elastic"
    elif elasticity > -2:
        return "Elastic"
    else:
        return "Highly Elastic"

# Function to style the DataFrame for display
def style_dataframe(df):
    return df.style.format(precision=2).hide(axis="index")  # Hides the index

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
        "Tariff (%)": tariff_percent,
        "US ASP (£)": int(new_asp),
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
st.sidebar.header("User Inputs for Scenario A")
elasticity_A = st.sidebar.slider("Select Price-Demand Elasticity", -3.0, 0.0, -1.5, step=0.25, key="elasticity_A")
pass_through_rate_A = st.sidebar.slider("Tariff Pass-Through to Consumer (%)", 0, 100, 50, step=25, key="pass_through_A")

st.sidebar.header("User Inputs for Scenario B")
elasticity_B = st.sidebar.slider("Select Price-Demand Elasticity", -3.0, 0.0, -1.0, step=0.25, key="elasticity_B")
pass_through_rate_B = st.sidebar.slider("Tariff Pass-Through to Consumer (%)", 0, 100, 50, step=25, key="pass_through_B")

# Base scenario table
st.markdown("#### FY2024 Base Scenario (No Tariffs)")  # Smaller title
base_values["US Revenue (£B)"] = (base_values["US ASP (£)"] * base_values["US Units Sold"]) / 1e9
base_values["Fixed Cost per Unit (£)"] = round((base_values["Total Fixed Costs (£B)"] * 1e9) / base_values["Global Units Sold"], 2)
base_df = pd.DataFrame([base_values])

# **Remove Zero Index Column**
base_df.index = [""]  # Hides the default index

st.table(
    style_dataframe(base_df[[
        "US ASP (£)", "US Units Sold", "US Revenue (£B)", "Global Revenue (£B)", 
        "Global Units Sold", "Fixed Cost per Unit (£)", "Total Fixed Costs (£B)", 
        "Operating Profit (£B)", "Operating Margin (%)"
    ]])
)

# Calculate scenarios
scenario_A_results = calculate_scenario(elasticity_A, pass_through_rate_A)
scenario_B_results = calculate_scenario(elasticity_B, pass_through_rate_B)

# **Remove Zero Index Column from Scenario Tables**
scenario_A_df = pd.DataFrame([scenario_A_results])
scenario_B_df = pd.DataFrame([scenario_B_results])
scenario_A_df.index = [""]
scenario_B_df.index = [""]

# Updated tariff scenarios with defined elasticity types
st.markdown(f"#### Scenario A: Tariff Pass-Through to Consumer {pass_through_rate_A}%, Price-Demand Elasticity = {elasticity_A} ({elasticity_label(elasticity_A)})")
st.table(style_dataframe(scenario_A_df))

st.markdown(f"#### Scenario B: Tariff Pass-Through to Consumer {pass_through_rate_B}%, Price-Demand Elasticity = {elasticity_B} ({elasticity_label(elasticity_B)})")
st.table(style_dataframe(scenario_B_df))
