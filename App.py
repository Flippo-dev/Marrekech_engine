import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Marrakech Grand Unified Model", layout="wide")
st.title("🇲🇦 The Grand Unified Model: Full Spectrum Simulation")
st.markdown("### 🔮 Simulating 10,000 Universes (Optimistic, Pessimistic & Realistic)")

# --- 1. SIDEBAR: THE SPECTRUM OF REALITY ---
with st.sidebar:
    st.header("1. The Unknowns (Ranges)")
    
    # Capital
    st.subheader("🏗️ Investment Capital")
    reno_air_min, reno_air_max = st.slider("Airbnb Reno Range", 100000, 200000, (130000, 170000))
    reno_lt_min, reno_lt_max = st.slider("Long-Term Reno Range", 20000, 60000, (35000, 45000))
    
    st.subheader("💶 Market Rates")
    # The single most important slider: The Price Range
    rate_min, rate_max = st.slider("Airbnb Nightly Rate Range", 300, 1500, (450, 950))
    rate_mode = st.slider("Most Likely Nightly Rate", rate_min, rate_max, 700)
    
    rent_min, rent_max = st.slider("Long-Term Rent Range", 3000, 8000, (5000, 6500))
    
    st.subheader("📉 Operational Drag")
    # Fees that eat your profit
    mgr_fee = st.slider("Manager Fee %", 15, 25, 20) / 100
    airbnb_fee = 0.17 # Fixed platform fee
    clean_fee = st.number_input("Cleaning Cost (MAD)", value=250)
    
    st.subheader("🏦 Macroeconomics")
    inflation_volatility = st.slider("Inflation Volatility (Risk)", 0, 10, 5) / 100 

# --- 2. THE SIMULATION ENGINE ---
sims = 10000
years = 10
months = years * 12

npv_airbnb = []
npv_longterm = []

# MARRAKECH SEASONALITY (The Heartbeat)
base_seasonality = np.array([0.80, 0.70, 0.90, 0.85, 0.65, 0.75, 0.35, 0.25, 0.60, 0.95, 0.90, 0.85])

for s in range(sims):
    # A. DETERMINE THE "UNIVERSE TYPE" (Boom or Bust?)
    market_health = np.random.beta(5, 5) 
    
    # B. INITIALIZE CAPITAL
    capex_air = np.random.uniform(reno_air_min, reno_air_max)
    capex_lt = np.random.uniform(reno_lt_min, reno_lt_max)
    
    cf_air_monthly = []
    cf_lt_monthly = []
    
    # C. LONG TERM RENT 
    rent_range = rent_max - rent_min
    this_universe_rent = rent_min + (rent_range * market_health)
    
    # D. RUN TIMELINE
    for m in range(months):
        month_idx = m % 12
        year_idx = m // 12
        
        # Inflation Walk
        annual_inf = np.random.normal(0.03, inflation_volatility)
        inf_factor = (1 + annual_inf) ** year_idx
        
        # --- AIRBNB PHYSICS ---
        health_factor = (market_health - 0.5) * 0.4 
        occ_base = base_seasonality[month_idx] + health_factor
        occ_today = np.clip(np.random.normal(occ_base, 0.1), 0.0, 0.98)
        
        # Rate
        base_rate = np.random.triangular(rate_min, rate_mode, rate_max)
        rate_today = base_rate * (0.8 + (market_health * 0.4)) * inf_factor
        
        # Financials
        gross_rev = (30 * occ_today) * rate_today
        fees = gross_rev * (airbnb_fee + mgr_fee) 
        
        stays = (30 * occ_today) / 3
        ops_cost = (stays * clean_fee) + (1500 * inf_factor) 
        
        # Summer AC Shock
        if month_idx in [6, 7]: ops_cost += 800
        
        net_air = gross_rev - fees - ops_cost - 3500 # Mortgage
        
        # Tax (CPU 15%)
        if net_air > 0: net_air *= 0.85
        
        cf_air_monthly.append(net_air)
        
        # --- LONG TERM PHYSICS ---
        vacancy_prob = 0.05 + ((1 - market_health) * 0.1) 
        
        if np.random.random() < vacancy_prob:
            net_lt = -3500 - 300
        else:
            net_lt = (this_universe_rent * inf_factor) - 3500 - 300
            if net_lt > 0: net_lt *= 0.85
            
        cf_lt_monthly.append(net_lt)

    # E. NPV (Discount Rate 10%)
    npv_a = -capex_air + sum([cf / ((1.10**(1/12))**i) for i, cf in enumerate(cf_air_monthly)])
    npv_l = -capex_lt + sum([cf / ((1.10**(1/12))**i) for i, cf in enumerate(cf_lt_monthly)])
    
    npv_airbnb.append(npv_a)
    npv_longterm.append(npv_l)

# --- 3. THE GRAND DASHBOARD ---
st.subheader("1. The Spectrum of Outcomes")
st.caption("10,000 parallel universes. Wider curve = More Risk.")

df_npv = pd.DataFrame({'Strategy': ['Airbnb']*sims + ['Long-Term']*sims, 'NPV (MAD)': npv_airbnb + npv_longterm})
fig_npv = px.histogram(df_npv, x="NPV (MAD)", color="Strategy", barmode="overlay", nbins=120,
                       color_discrete_map={'Airbnb':'#00CC96', 'Long-Term':'#EF553B'})
st.plotly_chart(fig_npv, use_container_width=True)

# METRICS
c1, c2, c3, c4 = st.columns(4)
wins = sum(np.array(npv_airbnb) > np.array(npv_longterm))
prob_win = (wins / sims) * 100
avg_premium = np.mean(npv_airbnb) - np.mean(npv_longterm)
risk_ruin = (sum(np.array(npv_airbnb) < 0) / sims) * 100

c1.metric("Win Probability", f"{prob_win:.1f}%")
c2.metric("Expected Premium", f"{avg_premium:,.0f} MAD")
c3.metric("Risk of Ruin", f"{risk_ruin:.1f}%")
c4.metric("Sims Run", f"{sims:,}")

st.divider()
st.subheader("2. Detailed Scenario Breakdown")
col1, col2 = st.columns(2)

with col1:
    st.info("##### 🐻 Pessimistic Case (Bottom 20%)")
    pess_air = np.percentile(npv_airbnb, 20)
    pess_lt = np.percentile(npv_longterm, 20)
    st.write(f"Airbnb Value: **{pess_air:,.0f} MAD**")
    st.write(f"Long-Term Value: **{pess_lt:,.0f} MAD**")

with col2:
    st.info("##### 🐂 Optimistic Case (Top 20%)")
    opt_air = np.percentile(npv_airbnb, 80)
    opt_lt = np.percentile(npv_longterm, 80)
    st.write(f"Airbnb Value: **{opt_air:,.0f} MAD**")
    st.write(f"Long-Term Value: **{opt_lt:,.0f} MAD**")
