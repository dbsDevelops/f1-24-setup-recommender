import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

# Load the dataset
data = pd.read_csv('./data/processed/packets_2025-01-26 19:51:52.729769.csv', dtype={'m_car_telemetry_data': 'object'})

# Display the first few rows to confirm
print(data.head())

# Filter the relevant columns
relevant_data = data[['m_lapDistance', 'm_lastLapTimeInMS']].dropna()

# Display the first few rows
print(relevant_data.head())

# Pearson correlation
pearson_corr, pearson_p = pearsonr(relevant_data['m_lapDistance'], relevant_data['m_lastLapTimeInMS'])
print(f"Pearson Correlation: {pearson_corr:.4f}, p-value: {pearson_p:.4e}")

# Spearman correlation
spearman_corr, spearman_p = spearmanr(relevant_data['m_lapDistance'], relevant_data['m_lastLapTimeInMS'])
print(f"Spearman Correlation: {spearman_corr:.4f}, p-value: {spearman_p:.4e}")

# Scatter plot with regression line
plt.figure(figsize=(10, 6))
sns.regplot(
    x='m_lapDistance',
    y='m_lastLapTimeInMS',
    data=relevant_data,
    scatter_kws={'alpha': 0.5},
    line_kws={'color': 'red'}
)
plt.title('Correlation between Lap Distance and Last Lap Time')
plt.xlabel('Lap Distance (m)')
plt.ylabel('Last Lap Time (ms)')
plt.show()
