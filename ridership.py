import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page config - FIXED VERSION
st.set_page_config(
    page_title="Metro Ridership Calculator",
    page_icon="🚇",
    layout="wide"
)

# REPLACE st.subtitle() with st.markdown()
st.title("🚇 Metro Ridership Impact Calculator")
st.markdown("### Predict ridership increase from last-mile connectivity improvements")

# Elasticity values from literature
ELASTICITIES = {
    "feeder_frequency": 0.5,      # TCRP Report 95
    "last_mile_wait_time": -0.8,  # WRI India study  
    "service_availability": 0.3,  # VTPI
    "feeder_cost": -0.4,          # Standard transit fare elasticity
    "integration_quality": 0.6    # Multimodal integration
}

# Sidebar inputs
st.sidebar.header("Input Parameters")

# Current baseline
st.sidebar.subheader("Current Baseline")
current_ridership = st.sidebar.number_input(
    "Current daily ridership", 
    value=100000, 
    step=10000,
    help="Enter current daily metro ridership"
)

baseline_frequency = st.sidebar.slider(
    "Current feeder frequency (buses/hour)", 
    1, 20, 4,
    help="Average buses per hour on feeder routes"
)

baseline_wait = st.sidebar.slider(
    "Current average wait time (minutes)", 
    2, 30, 12,
    help="Average wait time for last-mile transport"
)

# Improvement scenarios
st.sidebar.subheader("Improvement Scenarios")

freq_improvement = st.sidebar.slider(
    "% Increase in feeder frequency", 
    0, 200, 50,
    help="Percentage increase in bus/feeder frequency"
)

wait_reduction = st.sidebar.slider(
    "% Reduction in wait time", 
    0, 80, 30,
    help="Percentage reduction in average wait time"
)

coverage_improvement = st.sidebar.slider(
    "% Increase in service coverage", 
    0, 100, 25,
    help="Percentage increase in area coverage"
)

cost_reduction = st.sidebar.slider(
    "% Reduction in last-mile cost", 
    0, 50, 15,
    help="Percentage reduction in feeder service cost"
)

integration_improvement = st.sidebar.slider(
    "% Improvement in integration quality", 
    0, 100, 40,
    help="Better schedules, payment integration, wayfinding"
)

# Calculate impacts
def calculate_ridership_impact():
    # Individual elasticity calculations
    freq_impact = (freq_improvement / 100) * ELASTICITIES["feeder_frequency"]
    wait_impact = (wait_reduction / 100) * abs(ELASTICITIES["last_mile_wait_time"])
    coverage_impact = (coverage_improvement / 100) * ELASTICITIES["service_availability"]
    cost_impact = (cost_reduction / 100) * abs(ELASTICITIES["feeder_cost"])
    integration_impact = (integration_improvement / 100) * ELASTICITIES["integration_quality"]
    
    # Total compound effect (multiplicative)
    total_impact = freq_impact + wait_impact + coverage_impact + cost_impact + integration_impact
    
    # Apply diminishing returns for large improvements
    if total_impact > 0.5:
        total_impact = 0.5 + (total_impact - 0.5) * 0.7
    
    new_ridership = current_ridership * (1 + total_impact)
    absolute_increase = new_ridership - current_ridership
    percentage_increase = total_impact * 100
    
    return {
        "freq_impact": freq_impact * 100,
        "wait_impact": wait_impact * 100,
        "coverage_impact": coverage_impact * 100,
        "cost_impact": cost_impact * 100,
        "integration_impact": integration_impact * 100,
        "total_percentage": percentage_increase,
        "new_ridership": int(new_ridership),
        "absolute_increase": int(absolute_increase)
    }

# Main dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Ridership Impact Analysis")
    
    results = calculate_ridership_impact()
    
    # Key metrics
    st.metric(
        "Predicted Ridership Increase", 
        f"{results['total_percentage']:.1f}%",
        delta=f"+{results['absolute_increase']:,} passengers/day"
    )
    
    # Impact breakdown
    st.subheader("Impact Breakdown by Factor")
    
    impact_data = pd.DataFrame({
        'Factor': [
            'Frequency Improvement',
            'Wait Time Reduction', 
            'Coverage Expansion',
            'Cost Reduction',
            'Integration Quality'
        ],
        'Impact (%)': [
            results['freq_impact'],
            results['wait_impact'],
            results['coverage_impact'],
            results['cost_impact'],
            results['integration_impact']
        ]
    })
    
    fig = px.bar(
        impact_data, 
        x='Impact (%)', 
        y='Factor',
        orientation='h',
        title="Ridership Impact by Improvement Factor",
        color='Impact (%)',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("Key Outputs")
    
    # Summary box
    st.info(f"""
    **Current Ridership:** {current_ridership:,}/day
    
    **Predicted New Ridership:** {results['new_ridership']:,}/day
    
    **Total Increase:** +{results['absolute_increase']:,} passengers
    
    **Percentage Gain:** +{results['total_percentage']:.1f}%
    """)
    
    # Elasticity reference
    st.subheader("Elasticity Values Used")
    st.text(f"""
    Frequency: {ELASTICITIES['feeder_frequency']}
    Wait Time: {ELASTICITIES['last_mile_wait_time']}
    Coverage: {ELASTICITIES['service_availability']}
    Cost: {ELASTICITIES['feeder_cost']}
    Integration: {ELASTICITIES['integration_quality']}
    """)
    
    st.caption("Values from TCRP Report 95, WRI India, VTPI studies")

# Scenario comparison
st.header("Scenario Comparison")

scenarios = {
    "Current": 0,
    "Basic Improvement": 15,
    "Moderate Improvement": 35,
    "Comprehensive Improvement": 60
}

scenario_results = []
for scenario, improvement in scenarios.items():
    # Apply uniform improvement across all factors
    temp_results = calculate_ridership_impact() if scenario == "Current" else {
        "total_percentage": improvement * 0.4,  # Conservative multiplier
        "new_ridership": int(current_ridership * (1 + improvement * 0.004))
    }
    scenario_results.append({
        "Scenario": scenario,
        "Ridership": temp_results["new_ridership"] if scenario != "Current" else current_ridership,
        "% Increase": temp_results["total_percentage"] if scenario != "Current" else 0
    })

scenario_df = pd.DataFrame(scenario_results)
fig2 = px.bar(
    scenario_df, 
    x='Scenario', 
    y='Ridership',
    title="Ridership Projections by Improvement Scenario",
    text='% Increase'
)
fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
st.plotly_chart(fig2, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Built using elasticity values from transit research literature | Data sources: TCRP, WRI India, VTPI")

