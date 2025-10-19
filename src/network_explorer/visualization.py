import networkx as nx
import matplotlib.pyplot as plt

def visualize_protein_neighborhood(ego, central_protein, node_size=50, central_node_size=200):
    """
    Visualize the neighborhood of a protein.
    
    Parameters:
        ego (networkx.Graph): Ego graph representing the neighborhood
        central_protein (str): The central protein
        node_size (int): Size of regular nodes
        central_node_size (int): Size of the central protein node
        
    Returns:
        matplotlib.figure.Figure: The figure containing the visualization
    """
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 9), dpi=100)
    
    # Create layout
    pos = nx.spring_layout(ego, seed=42)
    
    # Draw all nodes
    nx.draw_networkx_nodes(ego, pos, node_color='blue', node_size=node_size, ax=ax)
    
    # Highlight the central protein
    nx.draw_networkx_nodes(ego, pos, nodelist=[central_protein], 
                          node_color='red', node_size=central_node_size, ax=ax)
    
    # Draw edges in light gray
    nx.draw_networkx_edges(ego, pos, width=1, edge_color='lightgray', ax=ax)
    
    # Offset labels for better readability
    label_pos = {k: (v[0], v[1] + 0.03) for k, v in pos.items()}
    
    # Draw labels
    nx.draw_networkx_labels(
        ego, label_pos, font_size=10, 
        font_color='black', font_weight='bold', ax=ax
    )
    
    # Set title and hide axes
    plt.title(f"Neighborhood of {central_protein}", fontsize=16)
    plt.axis('off')
    
    return fig