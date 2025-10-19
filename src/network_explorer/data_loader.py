import pandas as pd
import os

def load_similarity_matrix(file_path):
    """
    Load the similarity matrix from a CSV file.
    
    Parameters:
        file_path (str): Path to the CSV file containing the similarity matrix
        
    Returns:
        pandas.DataFrame: The loaded similarity matrix
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    # Load the similarity matrix
    similarity_df = pd.read_csv(file_path, index_col=0)
    
    return similarity_df