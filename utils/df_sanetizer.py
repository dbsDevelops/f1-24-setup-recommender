#!/usr/bin/env python3
"""
df_sanetizer.py

This script sanitizes a general CSV file (joined from six streams) by keeping only one record per lap.
It detects lap start events using the player's world position (m_carMotionData_0_m_worldPositionX/Y/Z)
relative to a given start/finish location, then selects only desired columns:
  - From header: m_header_m_sessionTime and m_header_m_frameIdentifier
  - Lap times: any columns that contain sector1Time, sector2Time, or sector3Time
  - Car setup parameters: any columns starting with "m_carSetupData"

Finally, the script writes the sanitized CSV and (optionally) joins multiple sanitized CSV files
into one master dataset.
"""

import os
import math
import glob
import pandas as pd
import numpy as np

# --- Configuration ---

# Set the known start/finish coordinates for Circuit de Barcelona (adjust these as needed)
SF_X = 306.8407897949219   # Example value in metres
SF_Y = -76.51145935058594     # Example value in metres

# Distance threshold (in metres) to decide if the car is at the start/finish line
THRESHOLD = 10.0  
# Minimum time gap (in seconds) between lap start candidates (to avoid multiple detections per lap)
TIME_GAP = 5.0

# --- Helper Functions ---

def distance_to_sf(row):
    """
    Computes the Euclidean distance from the player's car world position to the start/finish line.
    Assumes the flattened CSV includes:
       m_carMotionData_0_m_worldPositionX
       m_carMotionData_0_m_worldPositionY
    """
    try:
        x = row["m_carMotionData_0_m_worldPositionX"]
        y = row["m_carMotionData_0_m_worldPositionY"]
    except KeyError:
        # If not found, return infinity so the row is not considered a lap start candidate
        return np.inf
    # Compute Euclidean distance
    return math.sqrt((x - SF_X)**2 + (y - SF_Y)**2)

def filter_lap_starts(df):
    """
    Filters the DataFrame to keep only one record per lap.
    It uses only rows coming from motion packets (i.e. where packet_type=="motion")
    and then selects those rows where the distance to the start/finish is below THRESHOLD.
    A further time filter (using m_header_m_sessionTime) is applied so that only one lap start
    is kept if multiple candidates occur within TIME_GAP seconds.
    """
    if "packet_type" not in df.columns:
        print("Error: 'packet_type' column not found. Cannot filter lap starts.")
        return pd.DataFrame()

    # Filter only motion packets (which contain the world position)
    df_motion = df[df["packet_type"] == "motion"].copy()
    # Compute the distance to the start/finish for each row
    df_motion["distance_sf"] = df_motion.apply(distance_to_sf, axis=1)
    # Select candidate rows where the distance is less than the threshold
    df_candidates = df_motion[df_motion["distance_sf"] < THRESHOLD].copy()

    if "m_header_m_sessionTime" not in df_candidates.columns:
        print("Error: 'm_header_m_sessionTime' column not found. Cannot sort by session time.")
        return pd.DataFrame()
    
    # Sort candidates by session time
    df_candidates.sort_values("m_header_m_sessionTime", inplace=True)
    # Compute time differences between consecutive candidates
    df_candidates["time_diff"] = df_candidates["m_header_m_sessionTime"].diff()
    # Keep the first candidate or those where the gap is greater than TIME_GAP
    df_lap_starts = df_candidates[(df_candidates["time_diff"].isna()) | (df_candidates["time_diff"] > TIME_GAP)].copy()
    return df_lap_starts

def select_desired_columns(df):
    """
    From the filtered lap-start rows, select only the columns needed for PCA analysis:
      - m_header_m_sessionTime and m_header_m_frameIdentifier
      - Lap times: any column that contains "sector1Time", "sector2Time", or "sector3Time"
      - Car setup parameters: any column that starts with "m_carSetupData"
    Adjust the column filters if your flattened CSV uses different naming.
    """
    keep_columns = []
    for col in df.columns:
        # Skip the data related to our rival 
        if "rival" in col:
            continue
        # Always keep these header columns
        if col in ["m_header_m_sessionTime", "m_header_m_frameIdentifier"]:
            keep_columns.append(col)
        # Keep lap sector times (adjust the substrings as necessary)
        elif ("sector1Time" in col) or ("sector2Time" in col) or ("sector3Time" in col):
            keep_columns.append(col)
        # Keep car setup data columns (adjust prefix if needed)
        elif col.startswith("m_carSetups"):
            keep_columns.append(col)
    # You can add additional columns as needed
    return df[keep_columns]

# def sanitize_csv(input_csv, output_csv):
#     """
#     Loads the general CSV file, filters it to one record per lap (using motion packet data),
#     selects only the desired columns, and writes out the sanitized CSV.
#     """
#     print(f"Loading input CSV: {input_csv}")
#     df = pd.read_csv(input_csv)
#     print(f"Total records in general CSV: {len(df)}")
#     df_lap = filter_lap_starts(df)
#     print(f"Lap start candidates found: {len(df_lap)}")
#     if df_lap.empty:
#         print("No lap start records found in the input CSV.")
#         return
#     df_sanitized = select_desired_columns(df_lap)
#     df_sanitized.to_csv(output_csv, index=False)
#     print(f"Sanitized dataset saved to: {output_csv}")

def sanitize_and_merge(input_csv, output_csv, tolerance=0.5):
    """
    Loads the general CSV, detects lap start events using motion packets,
    then for each lap start event, finds the nearest lap and car setup records
    (using m_header_m_sessionTime) and merges them into one record.
    
    'tolerance' is the maximum allowed difference in session time (in seconds)
    to consider two records as corresponding.
    """
    df = pd.read_csv(input_csv)
    print(f"Total records: {len(df)}")
    
    # Split the DataFrame by packet type.
    df_motion = df[df["packet_type"] == "motion"].copy()
    df_lap = df[df["packet_type"] == "lap"].copy()
    df_setup = df[df["packet_type"] == "car_setup"].copy()
    
    # Detect lap start events from motion packets using your distance function.
    df_motion["distance_sf"] = df_motion.apply(distance_to_sf, axis=1)
    df_candidates = df_motion[df_motion["distance_sf"] < THRESHOLD].copy()
    df_candidates.sort_values("m_header_m_sessionTime", inplace=True)
    df_candidates["time_diff"] = df_candidates["m_header_m_sessionTime"].diff()
    # Keep only candidates with a gap > TIME_GAP (or the first candidate)
    df_lap_starts = df_candidates[(df_candidates["time_diff"].isna()) | (df_candidates["time_diff"] > TIME_GAP)].copy()
    print(f"Lap start candidates: {len(df_lap_starts)}")
    
    # Ensure the DataFrames for lap and setup data are sorted by session time.
    df_lap.sort_values("m_header_m_sessionTime", inplace=True)
    df_setup.sort_values("m_header_m_sessionTime", inplace=True)
    
    # Merge lap start events with lap data (nearest match by session time)
    df_merged = pd.merge_asof(df_lap_starts, df_lap,
                              on="m_header_m_sessionTime",
                              direction="nearest",
                              tolerance=tolerance,
                              suffixes=("", "_lap"))
    
    # Merge the result with car setup data.
    df_merged = pd.merge_asof(df_merged, df_setup,
                              on="m_header_m_sessionTime",
                              direction="nearest",
                              tolerance=tolerance,
                              suffixes=("", "_setup"))
    
    # Now, select only desired columns. Adjust these filters as needed.
    keep_columns = []
    for col in df_merged.columns:
        # Always keep the header session time and frame identifier.
        if col in ["m_header_m_sessionTime", "m_header_m_frameIdentifier"]:
            keep_columns.append(col)
        # Keep lap times (assuming the lap data columns have "sector1Time", etc.)
        elif "sector1Time" in col or "sector2Time" in col or "sector3Time" in col:
            keep_columns.append(col)
        # Keep car setup parameters (assuming they start with "m_carSetupData" or "m_carSetups")
        elif col.startswith("m_carSetupData") or col.startswith("m_carSetups"):
            keep_columns.append(col)
    df_final = df_merged[keep_columns]
    
    df_final.to_csv(output_csv, index=False)
    print(f"Sanitized merged dataset saved to: {output_csv}")

def join_sanitized_csvs(folder, output_master):
    """
    Scans the given folder for sanitized CSV files (matching pattern 'sanitized_dataset_*.csv'),
    concatenates them, and writes out a master dataset CSV.
    """
    pattern = os.path.join(folder, "sanitized_dataset_*.csv")
    files = glob.glob(pattern)
    if not files:
        print(f"No sanitized CSV files found in folder: {folder}")
        return
    df_list = []
    for f in files:
        print(f"Loading sanitized file: {f}")
        df = pd.read_csv(f)
        df_list.append(df)
    master_df = pd.concat(df_list, ignore_index=True, sort=False)
    master_df.to_csv(output_master, index=False)
    print(f"Master sanitized dataset saved to: {output_master}")

# --- Main Execution ---

def main():
    # Adjust input_csv to point to your general CSV file recorded from a session.
    input_csv = "./data/raw/2025-02-23_20-56-22/general_data_2025-02-23_20-56-22.csv"  # Change this path as needed

    # Create an output CSV name for the sanitized dataset.
    base_name = os.path.splitext(os.path.basename(input_csv))[0]
    output_csv = f"./data/processed/sanitized_dataset_{base_name}.csv"

    # Run the sanitization process on the input CSV.
    # sanitize_csv(input_csv, output_csv)
    sanitize_and_merge(input_csv, output_csv)

    # (Optional) If you want to join multiple sanitized CSV files from a folder into one master CSV:
    sanitized_folder = "./data/processed"
    master_output = os.path.join(sanitized_folder, "master_sanitized_dataset.csv")
    join_sanitized_csvs(sanitized_folder, master_output)

if __name__ == "__main__":
    main()