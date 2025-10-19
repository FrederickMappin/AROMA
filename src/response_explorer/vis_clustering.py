import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import pdist
import streamlit as st



def create_clustering_visualization(results_data):
    """
    Create a hierarchical clustering visualization of the top chemical matches.
    
    Parameters:
    -----------
    results_data : dict
        Dictionary containing analysis results
        
    Returns:
    --------
    matplotlib.figure.Figure
        The clustering figure
    """
    if not results_data or results_data.get('actual_top_n', 0) <= 0:
        return None
    
    receptor_name = results_data['receptor_name']
    chemical_matrix = results_data['chemical_matrix']
    common_cols = results_data['common_cols']
    top_chems = results_data['top_chems']
    actual_top_n = results_data['actual_top_n']
    
    # Extract feature values for top chemicals
    top_chem_matrix = pd.DataFrame(
        [chemical_matrix.loc[name].values for name in top_chems],
        index=top_chems,
        columns=common_cols
    )
    
    # Create figure with appropriate size for just the dendrogram
    # Adjust width based on number of chemicals
    fig_width = max(12, actual_top_n * 0.5)
    fig_height = 8
    fig = plt.figure(figsize=(fig_width, fig_height))
    
    # Get current axes
    ax = plt.gca()
    
    # Compute distance matrix and linkage for hierarchical clustering
    distances = pdist(top_chem_matrix, metric='cosine')
    linkage_matrix = sch.linkage(distances, method='ward')
    
    # Plot vertical dendrogram WITH labels at the top
    dendrogram = sch.dendrogram(
        linkage_matrix,
        orientation='top',
        labels=top_chem_matrix.index,
        leaf_font_size=10,
        ax=ax
    )
    
    # Remove the box/frame around the plot
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Remove axes ticks (but keep the labels)
    ax.tick_params(axis='both', which='both', length=0)
    
    # Set labels and title
    plt.title(f'Chemical Clustering for {receptor_name}')
    plt.xlabel('')  # Remove x-label as it's now redundant
    plt.ylabel('')  # Remove y-label for cleaner look
    
    # Make labels diagonal for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Adjust the position of the dendrogram to connect with labels
    plt.subplots_adjust(bottom=0.2)
    
    return fig