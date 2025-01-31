import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# =================================================================
# 1. Load Data from .pickle (Better for preserving data types!)
# =================================================================
# Pickle files keep data EXACTLY as saved (no CSV corruption)
raw_data = pd.read_pickle('./data/raw/data_2025-01-26 19:51:52.729769.pickle') 
# Check the type of raw_data
print(type(raw_data))  # Likely a dictionary or list
data = pd.DataFrame(raw_data)  # Convert to DataFrame for analysis
print(data.head())

# =================================================================
# 2. Clean & Prepare Data
# =================================================================
# Select numerical features (PCA needs numbers!)
numerical_data = data.select_dtypes(include=[np.number])

# Handle missing values (use median for robustness to outliers)
numerical_data = numerical_data.fillna(numerical_data.median())  # Better than mean

# =================================================================
# 3. Improved PCA Workflow
# =================================================================
# Standardize data (critical for PCA!)
scaler = StandardScaler()
scaled_data = scaler.fit_transform(numerical_data)

# Let PCA decide components to keep 95% variance (better than forcing 2!)
pca = PCA(n_components=0.95)  # Adjust this threshold as needed
pca_data = pca.fit_transform(scaled_data)

# Check how many components PCA kept
print(f"PCA kept {pca.n_components_} components to explain 95% variance")

# =================================================================
# 4. Better Clustering with K-Means
# =================================================================
# Use the Elbow Method to find optimal clusters (replace 3 with your choice)
# Uncomment to test:
# inertias = []
# for k in range(1, 10):
#     kmeans = KMeans(n_clusters=k, random_state=42).fit(pca_data)
#     inertias.append(kmeans.inertia_)
# plt.plot(range(1, 10), inertias); plt.title("Elbow Method"); plt.show()

kmeans = KMeans(n_clusters=3, random_state=42)  # Use optimal k from elbow method
data['Cluster'] = kmeans.fit_predict(pca_data)

# =================================================================
# 5. Visualization (Now in 2D/3D based on PCA components)
# =================================================================
# Plot first 2 PCA components
plt.figure(figsize=(10, 7))
sns.scatterplot(
    x=pca_data[:, 0], y=pca_data[:, 1],
    hue=data['Cluster'], palette='viridis', s=100
)
plt.title('F124 Setup Clusters (PCA Reduced)')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.show()

# =================================================================
# 6. Save Results
# =================================================================
# Save clustered data (use pickle to avoid CSV issues!)
data.to_pickle('./data/output/clustered_data.pickle')
data.to_csv('./data/output/clustered_data.csv', index=False)  # Optional CSV backup