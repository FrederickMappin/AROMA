import pandas as pd
import numpy as np
import streamlit as st

def format_results_table(results_data):
    """
    Format the results dataframe for display as a table.
    
    Parameters:
    -----------
    results_data : dict
        Dictionary containing analysis results
        
    Returns:
    --------
    pandas.DataFrame
        Formatted dataframe ready for display
    dict
        Additional information for table display
    """
    if not results_data or 'results' not in results_data:
        return None, {'error': 'No results data available'}
    
    # Get the results dataframe
    results_df = results_data['results'].copy()
    
    if results_df.empty:
        return pd.DataFrame(), {'message': 'No matching chemicals found'}
    
    # Format the similarity scores as raw decimal values (not percentages)
    results_df['Similarity'] = results_df['Similarity'].apply(lambda x: f"{x:.4f}")
    
    # Rename columns for better display
    results_df = results_df.rename(columns={
        "Chemical_Name": "Chemical Name",
        "CAS_Number": "CAS Number",
        "Similarity": "Similarity Score"
    })
    
    # Additional info for the table display
    table_info = {
        'receptor_name': results_data['receptor_name'],
        'status': results_data['status'],
        'count': results_data['actual_top_n'],
        'warning': results_data.get('warning', None)
    }
    
    return results_df, table_info

def display_results_table(results_df, table_info):
    """
    Display the results table in Streamlit.
    
    Parameters:
    -----------
    results_df : pandas.DataFrame
        Formatted dataframe to display
    table_info : dict
        Additional information for table display
        
    Returns:
    --------
    None
    """
    # Display warnings if present
    if table_info.get('warning'):
        st.warning(table_info['warning'])
        
    # Get the count of chemicals being displayed
    count = table_info.get('count', 0)
    receptor = table_info.get('receptor_name', '')
    
    # Convert DataFrame to HTML with styling classes
    html = results_df.to_html(index=False, classes="table table-striped")
    
    # Display the table in a scrollable container
    st.markdown(f"""
    <div style="height: 400px; overflow-y: auto; overflow-x: auto; border: 1px solid #e1e4e8; border-radius: 6px; padding: 0;">
        {html}
    </div>
    """, unsafe_allow_html=True)
    
    # Display caption about the number of chemicals shown
    if count > 0:
        st.caption(f"Showing top {count} chemical matches for {receptor}.")
    else:
        st.caption(f"No chemical matches found for {receptor}.")