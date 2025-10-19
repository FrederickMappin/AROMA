import networkx as nx
import pandas as pd

def create_protein_network(similarity_df, threshold=85):
    """
    Create a protein similarity network where edges represent similarities above threshold.
    
    Parameters:
        similarity_df (pandas.DataFrame): Similarity matrix
        threshold (float): Similarity threshold for edge creation
        
    Returns:
        networkx.Graph: The protein similarity network
    """
    # Initialize an undirected graph
    G = nx.Graph()
    
    # Add nodes
    for protein in similarity_df.index:
        G.add_node(protein)
    
    # Add edges for pairs above the threshold, using the max of both directions
    for i, protein1 in enumerate(similarity_df.index):
        for j, protein2 in enumerate(similarity_df.columns):
            if i < j:  # Only process each pair once
                try:
                    # Get similarity scores in both directions
                    score1 = float(similarity_df.loc[protein1, protein2])
                    score2 = float(similarity_df.loc[protein2, protein1])
                    max_score = max(score1, score2)
                    
                    # Add edge if similarity is above threshold
                    if max_score >= threshold:
                        G.add_edge(protein1, protein2, weight=max_score)
                except Exception:
                    continue  # Handle missing or non-numeric entries
    
    return G

def get_protein_neighbors(G, central_protein, radius=1):
    """
    Extract the neighborhood of a protein within a specified radius.
    
    Parameters:
        G (networkx.Graph): The protein similarity network
        central_protein (str): The protein of interest
        radius (int): Radius of neighborhood
        
    Returns:
        tuple: (ego graph, list of (node, distance) tuples)
    """
    # Check if protein exists in the graph
    if central_protein not in G:
        raise ValueError(f"Protein {central_protein} not found in the network")
    
    # Extract ego graph (neighborhood)
    ego = nx.ego_graph(G, central_protein, radius=radius)
    
    # Get shortest path lengths from the central protein to all nodes in the ego graph
    lengths = nx.single_source_shortest_path_length(G, central_protein, cutoff=radius)
    
    # Sort nodes by distance
    sorted_neighbors = sorted(lengths.items(), key=lambda x: x[1])
    
    return ego, sorted_neighbors