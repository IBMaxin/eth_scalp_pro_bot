import streamlit as st
import subprocess
import sys
import pandas as pd
import re

def parse_output(output):
    """
    A simple function to parse the text output from the script
    and extract key performance metrics.
    """
    metrics = {}
    # Use regular expressions to find the metrics in the text block
    patterns = {
        'TotalTrades': r"TotalTrades\s+([\d\.]+)",
        'WinRate': r"WinRate\s+([\d\.]+)",
        'TotalPnL': r"TotalPnL\s+([-\d\.]+)",
        'Sharpe': r"Sharpe\s+([-\d\.]+)"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            metrics[key] = float(match.group(1))
    return metrics

# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Quantitative Strategy Dashboard")

# Create a button to run the backtest
if st.button("Run New Backtest"):
    
    # Show a message while the script is running
    with st.spinner("Running backtest... This may take a few minutes."):
        
        # This command runs your optimize.py script
        process = subprocess.Popen([sys.executable, "scripts/optimize.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for the process to finish and capture the output
        stdout, stderr = process.communicate()
    
    # Check if the script ran successfully
    if process.returncode == 0:
        st.success("Backtest finished successfully!")
        
        # --- Display Results ---
        st.subheader("Final Validation Performance")
        
        # Parse the output to get the metrics
        final_stats_text = stdout.split("--- FINAL VALIDATION PERFORMANCE ---")[-1]
        metrics = parse_output(final_stats_text)
        
        if metrics:
            # Display metrics in columns for a clean look
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total PnL", f"${metrics.get('TotalPnL', 0):.2f}")
            col2.metric("Win Rate", f"{metrics.get('WinRate', 0):.2f}%")
            col3.metric("Total Trades", f"{int(metrics.get('TotalTrades', 0))}")
            col4.metric("Sharpe Ratio", f"{metrics.get('Sharpe', 0):.2f}")
        else:
            st.warning("Could not parse performance metrics from the output.")

        # Display the equity curve chart
        st.subheader("Equity Curve")
        try:
            st.image("logs/final_validation_equity_curve.png")
        except FileNotFoundError:
            st.warning("Equity curve plot not found.")
            
    else:
        st.error("Backtest failed!")
        # Display the full error output for debugging
        st.subheader("Error Log")
        st.code(stderr)