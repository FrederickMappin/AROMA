import os
import pandas as pd
import streamlit as st


def load_response_explorer_data(data_dir="data"):
    """
    Load all required data files for the Response Explorer component.
    
    Parameters:
    -----------
    data_dir : str
        Path to the directory containing the data files
        
    Returns:
    --------
    dict
        Dictionary containing the three loaded dataframes:
        - 'label_df': Original label matrix
        - 'cas_df': Chemical features matrix
        - 'predicted_df': Complete propagated predictions
        
    Raises:
    -------
    FileNotFoundError
        If any required data file is not found
    """
    try:
        # Paths to required files
        label_path = os.path.join(data_dir, "receptor_fragment_ligand_matrix_filtered.csv")
        cas_path = os.path.join(data_dir, "cas_features_filtered.csv")
        predicted_path = os.path.join(data_dir, "propagated_labels_complete.csv")
        
        # Check if all files exist
        for filepath in [label_path, cas_path, predicted_path]:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Required file not found: {filepath}")
        
        # Load the original label matrix
        label_df = pd.read_csv(label_path, index_col=0)
        
        # Load the binary matrix of chemical features
        cas_df = pd.read_csv(cas_path)
        
        # Load the complete propagated predictions
        predicted_df = pd.read_csv(predicted_path, index_col=0)
        
        return {
            'label_df': label_df,
            'cas_df': cas_df, 
            'predicted_df': predicted_df
        }
        
    except Exception as e:
        # Re-raise with more context
        raise type(e)(f"Error loading Response Explorer data: {str(e)}")

def get_available_receptors(predicted_df):
    """
    Get sorted list of all available receptors from the predictions dataframe.
    
    Parameters:
    -----------
    predicted_df : pandas.DataFrame
        The dataframe containing all receptor predictions
        
    Returns:
    --------
    list
        Sorted list of receptor names
    """
    return sorted(predicted_df.index.tolist())

def get_receptor_status(receptor_name, label_df, predicted_df):
    """
    Determine if a receptor is newly labeled (only in predictions)
    or originally labeled (was in the original training data).
    
    Parameters:
    -----------
    receptor_name : str
        Name of the receptor to check
    label_df : pandas.DataFrame
        Original label matrix
    predicted_df : pandas.DataFrame
        Complete propagated predictions
        
    Returns:
    --------
    str
        "NEWLY LABELED" or "ORIGINALLY LABELED"
    
    Raises:
    -------
    ValueError
        If receptor is not found in predictions
    """
    if receptor_name not in predicted_df.index:
        raise ValueError(f"Receptor '{receptor_name}' not found in predictions")
        
    is_new = receptor_name not in label_df.index
    return "NEWLY LABELED" if is_new else "ORIGINALLY LABELED"