import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine

def compare_receptor_to_chemicals(receptor_name, predicted_df, cas_df, label_df, top_n=10):
    """
    For a given receptor (gene), max-scale its full vector from complete predictions,
    and search the chemical list for the best match using cosine similarity.
    
    Parameters:
    -----------
    receptor_name : str
        Name of the receptor to analyze
    predicted_df : pandas.DataFrame
        DataFrame containing the complete propagated predictions
    cas_df : pandas.DataFrame
        DataFrame containing chemical features
    label_df : pandas.DataFrame
        Original label matrix
    top_n : int, default=10
        Number of top chemical matches to return
        
    Returns:
    --------
    dict or None
        Dictionary containing analysis results or None if error
    str or None
        Error message or None if successful
    """
    # Set 'name' as index for cas_df if not already
    cas_df_copy = cas_df.copy()
    if cas_df_copy.index.name != 'name':
        cas_df_copy.set_index('name', inplace=True)

    # Check receptor exists in predictions
    if receptor_name not in predicted_df.index:
        return None, f"Error: Receptor '{receptor_name}' not found in the network."

    # Check if receptor has any non-zero predictions
    if predicted_df.loc[receptor_name].sum() == 0:
        message = f"Warning: Receptor '{receptor_name}' has all zero predictions."
        # Continue with analysis but return the warning
        warning = message
    else:
        warning = None
    
    # Find all columns in common (excluding 'cas', 'smiles')
    exclude_cols = {'cas', 'smiles'}
    common_cols = [col for col in predicted_df.columns 
                   if col in cas_df_copy.columns and col not in exclude_cols]
    
    if not common_cols:
        return None, "No matching columns found between receptor and chemical data."

    # Extract and align vectors
    receptor_vec = predicted_df.loc[receptor_name, common_cols].astype(float).values
    chemical_matrix = cas_df_copy[common_cols].astype(float).fillna(0)

    # Max scaling
    max_value = np.max(receptor_vec)
    if max_value > 0:
        receptor_vec_scaled = receptor_vec / max_value
    else:
        receptor_vec_scaled = receptor_vec

    # Compute cosine similarity for all chemicals
    similarities = []
    for chem_name, chem_row in chemical_matrix.iterrows():
        chem_vec = chem_row.values
        if np.all(receptor_vec_scaled == 0) or np.all(chem_vec == 0):
            sim = 0
        else:
            sim = 1 - cosine(receptor_vec_scaled, chem_vec)
        
        # Get CAS number from DataFrame
        cas_number = cas_df_copy.loc[chem_name, 'cas'] if 'cas' in cas_df_copy.columns else None
        similarities.append((chem_name, cas_number, sim))

    # Sort and prepare results
    similarities.sort(key=lambda x: x[2], reverse=True)
    results_df = pd.DataFrame(similarities, columns=['Chemical_Name', 'CAS_Number', 'Similarity'])
    actual_top_n = min(top_n, len(results_df))
    
    # Note if this is a newly labeled receptor
    is_new = receptor_name not in label_df.index
    status = "NEWLY LABELED" if is_new else "ORIGINALLY LABELED"
    
    # Prepare data for visualization
    top_results = results_df.head(actual_top_n)
    top_chems = top_results['Chemical_Name'].tolist()
    
    # Return analysis results
    return {
        'results': top_results,
        'receptor_name': receptor_name, 
        'status': status,
        'receptor_vec': receptor_vec_scaled,
        'chemical_matrix': chemical_matrix,
        'common_cols': common_cols,
        'top_chems': top_chems,
        'actual_top_n': actual_top_n,
        'warning': warning
    }, None