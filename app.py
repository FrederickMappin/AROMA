import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from src.network_explorer.data_loader import load_similarity_matrix
from src.network_explorer.network import create_protein_network, get_protein_neighbors
from src.network_explorer.visualization import visualize_protein_neighborhood

# Import Response Explorer modules
from src.response_explorer.data_loader import load_response_explorer_data
from src.response_explorer.analysis import compare_receptor_to_chemicals
from src.response_explorer.vis_table_match import format_results_table, display_results_table
from src.response_explorer.vis_linechart import create_line_chart_visualization
from src.response_explorer.vis_feature_images import display_top_features_images
from src.response_explorer.vis_clustering import create_clustering_visualization

st.set_page_config(page_title="AROMA", layout="centered")

st.sidebar.image("images/M_logo.png", use_column_width=True)
st.sidebar.header("Parameters")

# Initialize session state variables if they don't exist yet
if 'similarity_threshold' not in st.session_state:
    st.session_state.similarity_threshold = 85
if 'top_chemicals' not in st.session_state:
    st.session_state.top_chemicals = 10
if 'n_features' not in st.session_state:
    st.session_state.n_features = 10

# This will store the "shared" receptor selection
if 'shared_receptor' not in st.session_state:
    st.session_state.shared_receptor = ""

# Add at top of file after session state initialization:
if 'needs_rerun' not in st.session_state:
    st.session_state.needs_rerun = False
if 'target_receptor' not in st.session_state:
    st.session_state.target_receptor = ""

# Create a function to update all receptor selections
def sync_receptor_selection(receptor):
    # Update the shared receptor
    st.session_state.shared_receptor = receptor
    # Update both tab-specific receptors
    st.session_state.network_receptor = receptor
    st.session_state.response_receptor = receptor

# At the very top of your script, right after imports:
if st.session_state.get('needs_rerun'):
    st.session_state.needs_rerun = False
    st.session_state.shared_receptor = st.session_state.target_receptor
    # No need to call rerun here as it will naturally rerun

# Use a sidebar radio to control the tab
tab = st.sidebar.radio("Select view", ["Structural Network Explorer", "Predicted Response Explorer", "Feature Catalog"])

if tab == "Structural Network Explorer":
    st.title("AROMA")
    st.markdown("""
    **AROMA (Analysis of Receptor Organization for Molecular Activity)** is an application intended to provide guidance for deorphanization experimentation planning, ligand predictions, and rational repellent design. 
    AROMA is based on a Semi-supervised label propagation (diffusion) model of currently deorphanized Dipteran Odorant Receptors.
  """)
    st.subheader("Structural Network Explorer")
    
    # Create an expander for the explorer description (keep AROMA description unchanged)
    with st.expander("About Structural Network Explorer", expanded=False):
        st.markdown("""
        **Structural Network Explorer** allows for the visualization of a protein structure similarity networks by selected OR neighborhood. 
        The nodes are olfactory receptors and edges are structural similarity scores of Alphafold2 proteins evaluated using Local-Global Alignment (LGA) method.
        """)

    similarity_path = "data/AllvsAll.csv"
    if os.path.exists(similarity_path):
        similarity_df = load_similarity_matrix(similarity_path)
        G = create_protein_network(similarity_df, 85)
        proteins = sorted(list(G.nodes()))

        # Sidebar widgets ONLY for this tab
        receptor_options = [""] + proteins
        
        # Get saved receptor from session state
        selected_receptor = st.sidebar.selectbox(
            "Select Receptor", 
            options=receptor_options,
            index=receptor_options.index(st.session_state.shared_receptor) if st.session_state.shared_receptor in receptor_options else 0,
            format_func=lambda x: "Select a receptor..." if x == "" else x,
            key="receptor_select"
        )
        st.session_state.shared_receptor = selected_receptor
        
        # Update ALL receptor states when selection changes
        if selected_receptor != st.session_state.shared_receptor:
            sync_receptor_selection(selected_receptor)
        
        # Use saved threshold
        similarity_threshold = st.sidebar.slider(
            "Similarity Threshold", 
            min_value=75, 
            max_value=95,
            value=st.session_state.similarity_threshold,
            step=5,
            key="network_threshold_slider"
        )
        
        # Save threshold to session state
        st.session_state.similarity_threshold = similarity_threshold
        
        G = create_protein_network(similarity_df, similarity_threshold)
        st.sidebar.info(f"Network has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        proteins = sorted(list(G.nodes()))

        if selected_receptor == "":
            st.info("Please type or select a receptor from the sidebar to build and view the network.")
        else:
            radius = 1
            ego_graph, neighbors = get_protein_neighbors(G, selected_receptor)
            node_size = 100
            central_node_size = 200
            fig = visualize_protein_neighborhood(
                ego_graph, 
                selected_receptor, 
                node_size=node_size, 
                central_node_size=central_node_size
            )
            st.pyplot(fig)
            
            # DYNAMIC NEIGHBORHOOD BUTTONS - REPLACE THE EXPANDER
            st.subheader("Neighborhood Navigation")
            st.write("Click any receptor to navigate to its neighborhood:")
            
            # Create a DataFrame with protein names and similarity scores
            neighbor_data = []
            for protein, _ in neighbors:
                if selected_receptor in G and protein in G[selected_receptor]:
                    similarity_score = G[selected_receptor][protein]['weight']
                    neighbor_data.append({"Protein": protein, "Similarity Score": similarity_score})
                else:
                    neighbor_data.append({"Protein": protein, "Similarity Score": 0})
            
            # Create DataFrame with both columns and sort by similarity
            neighbors_df = pd.DataFrame(neighbor_data)
            neighbors_df = neighbors_df.sort_values("Similarity Score", ascending=False)
            
            # Create dynamic buttons using columns (3 buttons per row)
            MAX_BUTTONS_PER_ROW = 3
            
            for i in range(0, len(neighbors_df), MAX_BUTTONS_PER_ROW):
                # Create columns for this row
                cols = st.columns(MAX_BUTTONS_PER_ROW)
                
                # Add buttons to columns
                for j in range(MAX_BUTTONS_PER_ROW):
                    idx = i + j
                    if idx < len(neighbors_df):
                        protein = neighbors_df.iloc[idx]["Protein"]
                        similarity = neighbors_df.iloc[idx]["Similarity Score"]
                        
                        # Create button with similarity info
                        if cols[j].button(f"{protein} ({similarity:.2f})", key=f"btn_{protein}"):
                            # When button is clicked, set flags for next rerun
                            st.session_state.needs_rerun = True
                            st.session_state.target_receptor = protein
            
            # Optionally keep the table view inside an expander
            with st.expander("Neighborhood Details", expanded=False):
                # Convert to HTML with full width styling
                neighbors_df["Similarity Score"] = neighbors_df["Similarity Score"].apply(lambda x: f"{x:.2f}")
                html = neighbors_df.to_html(index=False, classes="table table-striped")
                st.markdown(f"""
                <div style="height: 300px; overflow-y: auto; overflow-x: auto; border: 1px solid #e1e4e8; border-radius: 6px; padding: 0;">
                    {html}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error(f"File not found: {similarity_path}")
        st.info("Please provide a valid path to the similarity matrix.")

elif tab == "Predicted Response Explorer":
    st.title("Predicted Response Explorer")

    try:
        # Load response data
        data_dict = load_response_explorer_data(data_dir="data")
        label_df = data_dict['label_df']
        cas_df = data_dict['cas_df']
        predicted_df = data_dict['predicted_df']
        
        # Get list of receptors for the dropdown
        receptor_options = [""] + sorted(predicted_df.index.tolist())
        
        # Use the session state value as default
        selected_receptor = st.sidebar.selectbox(
            "Select Receptor", 
            options=receptor_options,
            index=receptor_options.index(st.session_state.shared_receptor) if st.session_state.shared_receptor in receptor_options else 0,
            format_func=lambda x: "Select a receptor..." if x == "" else x,
            key="receptor_select"  # Same key for both tabs
        )
        st.session_state.shared_receptor = selected_receptor

        # Update ALL receptor states when selection changes
        if selected_receptor != st.session_state.shared_receptor:
            sync_receptor_selection(selected_receptor)

        # MOVED UP: Features to display slider
        n_features = st.sidebar.slider(
            "Features to display", 
            min_value=0,
            max_value=30,
            value=st.session_state.n_features,  # Use saved value
            step=5,
            key="n_features_slider"
        )
        
        # Save the value to session state
        st.session_state.n_features = n_features
        
        # MOVED DOWN: Number of top chemicals slider
        top_n = st.sidebar.slider(
            "Number of top chemicals to display", 
            min_value=0, 
            max_value=30,
            value=st.session_state.top_chemicals,  # Use saved value as default
            step=5,
            key="top_chemicals_slider"  # Add a unique key
        )
        
        # Save slider value to session state
        st.session_state.top_chemicals = top_n
        
        # Check if a receptor is selected before running analysis
        if selected_receptor == "":
            st.info("Please select a receptor from the sidebar to view chemical predictions.")
        else:
            # Only run analysis if a receptor is selected
            results, error_message = compare_receptor_to_chemicals(
                receptor_name=selected_receptor,
                predicted_df=predicted_df,
                cas_df=cas_df,
                label_df=label_df,
                top_n=top_n
            )
            
            # Reorder the visualizations and table in the Response Explorer section
            if error_message:
                st.error(error_message)
            else:
                # Move this line inside the expander when results are available
                with st.expander("About Response Explorer", expanded=False):
                    st.markdown("""
                    **Response Explorer** lets you analyze the predicted responses of olfactory receptors to various chemicals, identifying the best chemical matches for any receptor based on cosine similarity of propagated features. 
                    Current visualization include **Profile Comparison** and **Clustering Analysis** of chemicals, along with **Top Matching Chemicals** by overall cosine similairity.
                    
                    Data is divided into:
                    - **NEWLY LABELED**: Receptors that received labels through propagation
                    - **ORIGINALLY LABELED**: Receptors that provided the seed labels
                    """)
                    
                    # Add receptor status if results are available
                    if selected_receptor != "" and 'results' in locals() and not error_message and 'status' in results:
                        st.write(f"**Receptor Status:** {results['status']}")
                
                # Only show visualizations if there are non-zero predictions
                if results.get('warning') and "all zero predictions" in results['warning']:
                    # Show one warning that applies to all visualizations
                    st.warning("Visualizations not displayed for receptors with all zero predictions.")
                else:
                    # MOVED LINE CHART TO TOP: Feature Profile first
                    st.subheader(f"Feature Profile for {selected_receptor}")
                    # Pass both normalized and raw data
                    line_chart_fig = create_line_chart_visualization(
                        results,
                        raw_data=predicted_df.loc[selected_receptor] if selected_receptor in predicted_df.index else None
                    )   
                    if line_chart_fig:
                        st.pyplot(line_chart_fig)
                    else:
                        st.info("Could not generate feature profile visualization for this receptor.")
                    
                    # FEATURE IMAGES SECOND
                    display_top_features_images(selected_receptor, predicted_df, n_features)
                    
                    # CLUSTERING VISUALIZATION THIRD
                    st.subheader("Chemical Clustering Analysis")
                    st.write("Hierarchical clustering of top chemical matches based on feature similarity.")
                    clustering_fig = create_clustering_visualization(results)
                    if clustering_fig:
                        st.pyplot(clustering_fig)
                    else:
                        st.info("Could not generate clustering visualization for this receptor.")
                        
                    # MOVED INSIDE: Table now only shows for non-zero predictions
                    st.subheader("Top Chemical Matches")
                    formatted_results, table_info = format_results_table(results)
                    display_results_table(formatted_results, table_info)
                
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure all required data files are in the correct location.")

elif tab == "Feature Catalog":
    st.title("Feature Catalog")
    
    # Create an expander for the Feature Catalog description
    with st.expander("About Feature Catalog", expanded=False):
        st.markdown("""
        Features used for label propagation are divided into two groups; Functional Groups and Maximum common substructure (MCS) fragments. 
        Functional groups labels that were unused in chemical dataset were removed before propagation. Maximum common substructures were 
        computed through multiple iteration of clustering and from sparse to densely packed clusters looking for the MCS at each clustering level. 
        """)
    
    # Helper function to convert image to base64 (MOVED HERE)
    def get_image_as_base64(image_path):
        import base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    
    # Add sliders to control image width
    col1, col2 = st.columns(2)
    with col1:
        groups_width = 800
    with col2:
        fragments_width = 800
    
    # Display the images with controlled size
    st.subheader("Functional Groups")
    st.markdown(f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{get_image_as_base64('images/groups.png')}" 
             width="{groups_width}" style="max-width: 100%; image-rendering: high-quality;">
    </div>
    """, unsafe_allow_html=True)

    st.subheader("MCS Fragments")
    st.markdown(f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{get_image_as_base64('images/fragments.png')}" 
             width="{fragments_width}" style="max-width: 100%; image-rendering: high-quality;">
    </div>
    """, unsafe_allow_html=True)

