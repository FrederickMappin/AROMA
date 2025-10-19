import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import streamlit as st

def create_line_chart_visualization(results_data, raw_data=None):
    """
    Create a line chart showing the receptor's feature profile with both raw and normalized values.
    
    Parameters:
    -----------
    results_data : dict
        Dictionary containing analysis results with normalized values
    raw_data : pandas.Series, optional
        Raw predicted values for the receptor
        
    Returns:
    --------
    matplotlib.figure.Figure
        The line chart figure
    """
    if not results_data:
        return None
    
    receptor_name = results_data['receptor_name']
    status = results_data['status']
    receptor_vec = results_data['receptor_vec']
    common_cols = results_data['common_cols']
    
    # Create line chart
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot normalized receptor profile
    plt.plot(common_cols, receptor_vec, 'o-', color='#1f77b4', 
             label=f"{receptor_name} (Normalized)", linewidth=2.5)
    
    # Plot raw values if available
    if raw_data is not None:
        # Ensure we're using the same features in both datasets
        raw_features = [col for col in common_cols if col in raw_data.index]
        if raw_features:
            raw_values = [raw_data[feature] for feature in raw_features]
            plt.plot(raw_features, raw_values, 's--', color='#ff7f0e',
                    label=f"{receptor_name} (Raw values)", linewidth=1.5, alpha=0.8)
    
    # Format the plot
    plt.xticks(rotation=90)
    plt.title(f"Feature Profile: {receptor_name} ({status})")
    plt.xlabel("Chemical Features")
    plt.ylabel("Feature Value")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add a horizontal line at y=0 for reference
    plt.axhline(y=0, color='r', linestyle='-', alpha=0.2)
    
    # Improve layout for readability
    plt.tight_layout()
    
    return fig