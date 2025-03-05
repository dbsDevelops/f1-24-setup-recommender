#!/usr/bin/env python3
"""
pca_tsne_visualization.py

This script loads the master_sanitized_dataset.csv, performs Principal Component Analysis (PCA)
to reduce the dimensionality of the data (helping to filter noise and reduce correlated features),
and then applies t-SNE to further reduce the data to 2 dimensions for visualization.
The resulting scatter plot is displayed and saved as "pca_tsne_plot.png".
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

# --- Configuration ---
INPUT_CSV = "./data/processed/master_sanitized_dataset.csv"  # Adjust path if needed
OUTPUT_PLOT = "./analysis/pca_tsne_plot.png"
N_PCA_COMPONENTS = 5  # We can adjust this number based on the explained variance ratio
TSNE_PERPLEXITY = 30
TSNE_RANDOM_STATE = 42

def load_data(input_csv):
    """
    Load the CSV file into a DataFrame.
    :param input_csv: Path to the input CSV file
    """
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} records from {input_csv}")
    return df

def prepare_features(df):
    """
    Prepare the features for dimensionality reduction.
    :param df: The DataFrame containing the data with features to be prepared for PCA and t-SNE analysis.
    """
    # lapNumber is the only identifier and non-feature column, so we drop it here.
    columns_to_drop = ["lapNumber"]
    features = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors="ignore")
    
    # Ensure all features are numeric.
    features = features.apply(pd.to_numeric, errors="coerce").fillna(0)

    # Option A: Scale ALL features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # Option B: Scale ONLY lapData_lastLapTimeInMS (and keep others as-is)
    # We'll do this by combining the scaled lap times with the rest
    # if "lapData_lastLapTimeInMS" in features.columns:
    #     lap_times = features[["lapData_lastLapTimeInMS"]].values
    #     lap_times_scaled = StandardScaler().fit_transform(lap_times)
    #     features["lapData_lastLapTimeInMS"] = lap_times_scaled
    
    # Convert DataFrame to NumPy array for PCA
    # features_array = features.values
    return features_scaled, features

def perform_pca(features):
    """
    Perform Principal Component Analysis (PCA) on the given features.
    :param features: The features to apply PCA on.
    """
    pca = PCA(n_components=N_PCA_COMPONENTS, random_state=TSNE_RANDOM_STATE)
    pca_result = pca.fit_transform(features)
    print("Explained variance ratio (PCA):")
    print(pca.explained_variance_ratio_)
    return pca_result, pca

def perform_tsne(pca_result):
    """
    Perform t-SNE on the given PCA result.
    :param pca_result: The result of PCA to apply t-SNE on.
    :param random_state: Random state for t-SNE.
    :param perplexity: Perplexity parameter for t-SNE.
    """
    tsne = TSNE(n_components=2, random_state=TSNE_RANDOM_STATE, perplexity=TSNE_PERPLEXITY)
    tsne_result = tsne.fit_transform(pca_result)
    return tsne_result

def plot_results(tsne_result, df, output_file, color_col="lapData_lastLapTimeInMS"):
    """
    Plot the t-SNE results.
    :param tsne_result: The result of t-SNE to plot.
    :param df: The original DataFrame for optional coloring by lap number.
    :param output_file: The output file path to save the plot.
    """
    plt.figure(figsize=(10,8))
    # Optionally, color the points by lapNumber if available.
    if color_col in df.columns:
        # Create a colormap based on lap number.
        scatter = plt.scatter(tsne_result[:,0], tsne_result[:,1], c=df[color_col], cmap='viridis', s=50)
        plt.colorbar(scatter, label=color_col)
    else:
        plt.scatter(tsne_result[:,0], tsne_result[:,1], s=50)
    plt.title("t-SNE Visualization (with normalization)")
    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.show()
    print(f"Plot saved to {output_file}")

def main():
    """
    Main function for the PCA-tSNE visualization script.
    """
    df = load_data(INPUT_CSV)
    features_array, features_df = prepare_features(df)
    pca_result, pca_model = perform_pca(features_array)

    # Create a DataFrame of loadings for each component
    loadings = pd.DataFrame(
        pca_model.components_,
        columns=features_df.columns,
        index=[f"PC{i+1}" for i in range(N_PCA_COMPONENTS)]
    )

    # Show top contributors for the first principal component
    pc1_loadings = loadings.loc["PC1"].abs().sort_values(ascending=False)
    print("Top contributors to PC1:")
    print(pc1_loadings.head(10))

    # Showt top contributors for the second principal component
    pc2_loadings = loadings.loc["PC2"].abs().sort_values(ascending=False)
    print("Top contributors to PC2:")
    print(pc2_loadings.head(10))

    # Show top contributors for the third principal component
    pc3_loadings = loadings.loc["PC3"].abs().sort_values(ascending=False)
    print("Top contributors to PC3:")
    print(pc3_loadings.head(10))

    tsne_result = perform_tsne(pca_result)
    plot_results(tsne_result, features_df, OUTPUT_PLOT)

if __name__ == "__main__":
    main()