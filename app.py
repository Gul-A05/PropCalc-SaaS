import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration to modern wide layout
st.set_page_config(page_title="PropCalc Engine", page_icon="🏢", layout="wide")

st.title("🏢 PropCalc Engine — Real Estate Deal Evaluation Pipeline")
st.markdown("An automated pipeline computing deal performance metrics, investment formulas, and geospatial property distributions.")

# --- SIDEBAR CONTROL UNIT ---
st.sidebar.header("🎯 Investment Benchmarks")
target_cap_rate = st.sidebar.slider("Minimum Target Cap Rate (%)", 4.0, 12.0, 7.5, step=0.1) / 100
target_coc = st.sidebar.slider("Minimum Cash-on-Cash Return (%)", 5.0, 20.0, 10.0, step=0.1) / 100
down_payment_pct = st.sidebar.slider("Standard Down Payment (%)", 10, 30, 20, step=5) / 100

# --- INGESTION STAGE ---
st.subheader("📥 1. Ingestion & Preprocessing")
uploaded_file = st.file_uploader("Upload Property Registry Ledger (CSV)", type="csv")

if uploaded_file is not None:
    # Read raw dataset
    raw_df = pd.read_csv(uploaded_file)
    
    with st.expander("🔍 View Raw Uploaded Ledger"):
        st.dataframe(raw_df)
        
    # Defensive Data Cleaning Pipeline (Cleans currency signs and whitespace safely)
    clean_df = raw_df.copy()
    for col in ['Purchase_Price', 'Gross_Monthly_Rent', 'Annual_Expenses']:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(
                clean_df[col].astype(str).str.replace('$', '').str.replace(',', '').str.strip(), 
                errors='coerce'
            )
    
    # Drop records missing critical calculation coordinates
    clean_df = clean_df.dropna(subset=['Purchase_Price', 'Gross_Monthly_Rent', 'Annual_Expenses'])
    
    # --- CORE CALCULATION ENGINE ---
    # Formula 1: Annual Gross Revenue
    clean_df['Annual_Gross_Rent'] = clean_df['Gross_Monthly_Rent'] * 12
    
    # Formula 2: Net Operating Income (NOI = Revenue - Operating Expenses)
    clean_df['Net_Operating_Income'] = clean_df['Annual_Gross_Rent'] - clean_df['Annual_Expenses']
    
    # Formula 3: Capitalization Rate (Cap Rate = NOI / Purchase Price)
    clean_df['Cap_Rate'] = clean_df['Net_Operating_Income'] / clean_df['Purchase_Price']
    
    # Formula 4: Cash-on-Cash Return (CoC = NOI / Initial Out-of-Pocket Equity)
    # Assumes upfront investment is down payment + basic closing costs calculated at 3% of asset price
    clean_df['Initial_Equity'] = (clean_df['Purchase_Price'] * down_payment_pct) + (clean_df['Purchase_Price'] * 0.03)
    clean_df['Cash_on_Cash'] = clean_df['Net_Operating_Income'] / clean_df['Initial_Equity']
    
    # --- EVALUATION FILTERING STAGE ---
    st.subheader("🔥 2. Verified High-Yield Investment Targets")
    st.markdown(f"Properties passing targets: **Cap Rate $\ge$ {target_cap_rate*100:.1f}%** and **Cash-on-Cash $\ge$ {target_coc*100:.1f}%**")
    
    # Isolate targets matching threshold bounds
    deals_df = clean_df[
        (clean_df['Cap_Rate'] >= target_cap_rate) & 
        (clean_df['Cash_on_Cash'] >= target_coc)
    ].copy()
    
    if not deals_df.empty:
        # Display readable metrics table for real estate analysts
        display_df = deals_df.copy()
        display_df['Cap Rate (%)'] = (display_df['Cap_Rate'] * 100).round(2).astype(str) + '%'
        display_df['Cash-on-Cash (%)'] = (display_df['Cash_on_Cash'] * 100).round(2).astype(str) + '%'
        display_df['Purchase Price'] = '$' + display_df['Purchase_Price'].map('{:,.2f}'.format)
        display_df['Net Income (NOI)'] = '$' + display_df['Net_Operating_Income'].map('{:,.2f}'.format)
        
        st.dataframe(
            display_df[['Property_Address', 'Purchase Price', 'Net Income (NOI)', 'Cap Rate (%)', 'Cash-on-Cash (%)']], 
            use_container_width=True
        )
        
            
        # Export Capabilities (Generates calculated ledger sheet output)
        st.subheader("📊 4. Analytical Export Engine")
        csv_buffer = deals_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Computed Investment Analysis (.CSV)",
            data=csv_buffer,
            file_name="computed_property_analysis.csv",
            mime="text/csv"
        )
    else:
        st.warning("No properties in the uploaded registry file match your current financial target thresholds. Try adjusted inputs.")

else:
    st.info("💡 Awaiting property data ingestion. Please upload a standard real estate spreadsheet asset (.CSV) to run calculations.")