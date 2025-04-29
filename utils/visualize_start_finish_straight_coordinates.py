import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV that you collected for start/finish detection
df = pd.read_csv("data/raw/monaco/2025-03-29_17-16-58/motion_data_2025-03-29_17-17-01.csv")

# Plot X vs Y for motion data
plt.figure(figsize=(8,6))
plt.scatter(df["m_carMotionData_0_m_worldPositionX"], df["m_carMotionData_0_m_worldPositionY"], s=1, alpha=0.5)
plt.title("Motion Data Coordinates")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()