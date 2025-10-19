import os
import streamlit as st
import pandas as pd
from PIL import Image
import base64

def display_top_features_images(receptor_name, predicted_df, n_features=10):
    """
    Display the top n feature images for a selected receptor.
    
    Parameters:
    -----------
    receptor_name : str
        The receptor ID to analyze
    predicted_df : pandas.DataFrame
        DataFrame containing the feature values for all receptors
    n_features : int
        Number of top features to display
    """
    # Check if receptor exists in the dataframe
    if receptor_name not in predicted_df.index:
        st.error(f"Receptor {receptor_name} not found in dataset")
        return
        
    # Get the feature values for this receptor
    receptor_features = predicted_df.loc[receptor_name]
    
    # Sort features by value (highest first)
    sorted_features = receptor_features.sort_values(ascending=False)
    
    # Get the top n features
    top_features = sorted_features.head(n_features)
    
    # Paths to image directories
    fragments_dir = "images/fragments_highdef"
    groups_dir = "images/groups_highdef"
    
    # Title for the section
    st.subheader(f"Top {n_features} Chemical Features for {receptor_name}")
    
    # Track which feature types we've found
    found_groups = False
    found_fragments = False
    
    # Create tabs for Groups and Fragments
    group_tab, fragment_tab = st.tabs(["Functional Groups", "MCS Fragments"])
    
    # Helper function to get image as base64
    def get_image_as_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    
    # Process groups first
    with group_tab:
        group_features = [f for f in top_features.index if f.startswith("Group")]
        if group_features:
            found_groups = True
            st.write(f"**Top {len(group_features)} functional groups:**")
            
            # Create rows with 3 images each
            for i in range(0, len(group_features), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i+j < len(group_features):
                        feature = group_features[i+j]
                        value = top_features[feature]
                        group_num = feature.replace("Group", "")
                        
                        # Look for image file containing the group name, not just starting with it
                        img_path = None
                        for img_file in os.listdir(groups_dir):
                            if f"Group{group_num}_" in img_file or f"Group{group_num}." in img_file:
                                img_path = os.path.join(groups_dir, img_file)
                                break
                        
                        if img_path and os.path.exists(img_path):
                            with cols[j]:
                                # Use HTML for better image quality
                                st.markdown(f"**{feature}**")
                                st.markdown(f"Value: **{value:.5f}**")
                                st.markdown(f"""
                                <div style="text-align: center;">
                                    <img src="data:image/png;base64,{get_image_as_base64(img_path)}" 
                                         width="200" style="image-rendering: high-quality;">
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            with cols[j]:
                                st.markdown(f"**{feature}**")
                                st.markdown(f"Value: **{value:.5f}**")
                                st.write("*(Image not found)*")
    
    # Process fragments next
    with fragment_tab:
        fragment_features = [f for f in top_features.index if f.startswith("Fragment")]
        if fragment_features:
            found_fragments = True
            st.write(f"**Top {len(fragment_features)} fragment features:**")
            
            # Create rows with 3 images each
            for i in range(0, len(fragment_features), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i+j < len(fragment_features):
                        feature = fragment_features[i+j]
                        value = top_features[feature]
                        frag_num = feature.replace("Fragment", "")
                        
                        # Look for image file containing the fragment name, not just starting with it
                        img_path = None
                        for img_file in os.listdir(fragments_dir):
                            if f"Fragment{frag_num}" in img_file:
                                img_path = os.path.join(fragments_dir, img_file)
                                break
                        
                        if img_path and os.path.exists(img_path):
                            with cols[j]:
                                # Use HTML for better image quality
                                st.markdown(f"**{feature}**")
                                st.markdown(f"Value: **{value:.5f}**")
                                st.markdown(f"""
                                <div style="text-align: center;">
                                    <img src="data:image/png;base64,{get_image_as_base64(img_path)}" 
                                         width="200" style="image-rendering: high-quality;">
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            with cols[j]:
                                st.markdown(f"**{feature}**")
                                st.markdown(f"Value: **{value:.5f}**")
                                st.write("*(Image not found)*")
    
    # Display a message if no features of a certain type were found
    if not found_groups:
        with group_tab:
            st.info("No group features among top results")
    
    if not found_fragments:
        with fragment_tab:
            st.info("No fragment features among top results")