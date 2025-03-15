#!/usr/bin/env python3
"""
df_sanetizer.py

This script loads a general CSV file (joined from multiple packet types) and creates a sanitized CSV with one record per lap.
Each record contains:
  - The header’s session time and frame identifier (renamed as m_header_sessionTime and m_header_frameIdentifier)
  - Lap data: sector1TimeMS, sector2TimeMS, and sector3TimeMS (renamed as lapData_sector1TimeInMS, etc.)
  - Car setup parameters for the player’s car (from columns beginning with m_carSetups_0_, renamed with prefix carSetups_)

It determines lap candidates by filtering motion packets based on the distance (using only X and Y) to a known start/finish point.
"""

import os
import math
import glob
import pandas as pd
import numpy as np

# --- Configuration ---

# Circuit name
CIRCUIT = "bahrein"

# Known start/finish coordinates (X, Y only)
SF_X = -394.5699768066406   # in metres
SF_Y = 91.22926330566406  # in metres

# Distance threshold to decide if the car is at the start/finish line (in metres)
THRESHOLD = 10.0  
# Minimum time gap (in seconds) between lap candidates
TIME_GAP = 86.0
# Maximum allowed difference (in seconds) to consider a lap or setup record as corresponding
MERGE_TOLERANCE = 0.5

# --- Helper Functions ---

def distance_to_sf(row):
    """
    Computes the Euclidean distance (using only X and Y) from the player's car (from a motion packet)
    to the start/finish location.
    Expects the flattened CSV to include:
       m_carMotionData_0_m_worldPositionX and m_carMotionData_0_m_worldPositionY
    """
    try:
        x = row["m_carMotionData_0_m_worldPositionX"]
        y = row["m_carMotionData_0_m_worldPositionY"]
    except KeyError:
        return np.inf
    return math.sqrt((x - SF_X)**2 + (y - SF_Y)**2)

def detect_lap_candidates(df_motion):
    """
    From the motion DataFrame, compute distance_to_sf for each row and select rows where the distance is below THRESHOLD.
    Then, sort by session time and keep only one candidate per lap (enforcing a TIME_GAP).
    """
    df_motion = df_motion.copy()
    df_motion["distance_sf"] = df_motion.apply(distance_to_sf, axis=1)
    # Only consider rows where the car is near the start/finish
    df_candidates = df_motion[df_motion["distance_sf"] < THRESHOLD].copy()
    if "m_header_m_sessionTime" not in df_candidates.columns:
        print("Error: 'm_header_m_sessionTime' column not found in motion data.")
        return pd.DataFrame()
    df_candidates.sort_values("m_header_m_sessionTime", inplace=True)
    df_candidates["time_diff"] = df_candidates["m_header_m_sessionTime"].diff()
    df_lap_candidates = df_candidates[(df_candidates["time_diff"].isna()) | (df_candidates["time_diff"] > TIME_GAP)].copy()
    return df_lap_candidates

def find_nearest_record(candidate_time, df, time_col="m_header_m_sessionTime", tol=MERGE_TOLERANCE):
    """
    Given a candidate time and a DataFrame (which is sorted by time_col),
    finds the row whose time is nearest to candidate_time.
    If the difference exceeds tol, returns None.
    """
    diffs = (df[time_col] - candidate_time).abs()
    if diffs.empty:
        return None
    idx = diffs.idxmin()
    if diffs.loc[idx] > tol:
        return None
    return df.loc[idx]

def extract_desired_fields(candidate, lap_record, setup_record):
    """
    For a given lap candidate (from motion), and its associated lap and setup records,
    extract and rename only the desired fields:
      - From candidate: m_header_m_sessionTime -> m_header_sessionTime, 
        m_header_m_frameIdentifier -> m_header_frameIdentifier.
      - From lap_record: extract m_lapData_0_m_sector1TimeMSPart, m_lapData_0_m_sector2TimeMSPart, m_lapData_0_m_sector3TimeMSPart,
        and rename them as lapData_sector1TimeInMS, lapData_sector2TimeInMS, lapData_sector3TimeInMS.
      - From setup_record: extract all columns that start with "m_carSetups_0_" and rename them with prefix "carSetups_".
    """
    merged = {}
    # Header fields (from candidate)
    merged["m_header_sessionTime"] = candidate.get("m_header_m_sessionTime", np.nan)
    merged["m_header_frameIdentifier"] = candidate.get("m_header_m_frameIdentifier", np.nan)
    
    # Lap data: assume the player's lap data is in index 0, with these column names:
    lap_cols = {
        "m_lapData_0_m_lastLapTimeInMS": "lapData_lastLapTimeInMS"
    }
    for orig, new in lap_cols.items():
        merged[new] = lap_record.get(orig, np.nan) if lap_record is not None else np.nan

    # Car setup data: assume the player's car setup is in index 0, and columns start with "m_carSetups_0_"
    if setup_record is not None:
        for col, value in setup_record.items():
            if isinstance(col, str) and col.startswith("m_carSetups_0_"):
                new_col = "carSetups_" + col[len("m_carSetups_0_"):]
                merged[new_col] = value
    else:
        # If no record, set all expected setup columns to NaN (optional: you can list them)
        expected = ["frontWing", "rearWing", "onThrottle", "offThrottle",
                    "frontCamber", "rearCamber", "frontToe", "rearToe",
                    "frontSuspension", "rearSuspension", "frontAntiRollBar",
                    "rearAntiRollBar", "frontSuspensionHeight", "rearSuspensionHeight",
                    "brakePressure", "brakeBias", "engineBraking",
                    "rearLeftTyrePressure", "rearRightTyrePressure",
                    "frontLeftTyrePressure", "frontRightTyrePressure",
                    "ballast", "fuelLoad"]
        for exp in expected:
            merged["carSetups_" + exp] = np.nan
    return merged

def sanitize_and_merge(input_csv, output_csv):
    """
    Loads the general CSV, splits it into motion, lap, and car setup packets, detects lap candidates from motion,
    and for each candidate finds the nearest lap and car setup records.
    Then, extracts only the desired fields and writes out one record per lap candidate.
    """
    df = pd.read_csv(input_csv)
    print(f"Total records in general CSV: {len(df)}")
    
    # Split the DataFrame by packet type.
    df_motion = df[df["packet_type"] == "motion"].copy()
    df_lap = df[df["packet_type"] == "lap"].copy()
    df_setup = df[df["packet_type"] == "car_setup"].copy()
    
    # Ensure the session time column is numeric and sort.
    for d in [df_motion, df_lap, df_setup]:
        d["m_header_m_sessionTime"] = pd.to_numeric(d["m_header_m_sessionTime"], errors="coerce")
        d.sort_values("m_header_m_sessionTime", inplace=True)
    
    # Detect lap candidates from motion packets.
    df_candidates = detect_lap_candidates(df_motion)
    print(f"Lap candidates detected: {len(df_candidates)}")
    
    merged_records = []
    for _, candidate in df_candidates.iterrows():
        cand_time = candidate["m_header_m_sessionTime"]
        lap_record = find_nearest_record(cand_time, df_lap, "m_header_m_sessionTime", MERGE_TOLERANCE)
        setup_record = find_nearest_record(cand_time, df_setup, "m_header_m_sessionTime", MERGE_TOLERANCE)
        merged = extract_desired_fields(candidate, lap_record, setup_record)
        merged_records.append(merged)
    
    if not merged_records:
        print("No merged records found.")
        return
    df_final = pd.DataFrame(merged_records)
    # Optional: sort the final DataFrame by session time.
    df_final.sort_values("m_header_sessionTime", inplace=True)
    df_final.to_csv(output_csv, index=False)
    print(f"Sanitized merged dataset saved to: {output_csv}")

def join_sanitized_csvs(folder, output_master):
    """
    Scans the given folder for sanitized CSV files (with names matching a given pattern),
    concatenates them, and writes a master dataset CSV.
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
    master_df = master_df.reset_index(drop=True)
    master_df['lapNumber'] = master_df.index + 1
    master_df = master_df.drop(columns=["m_header_sessionTime", "m_header_frameIdentifier"])
    master_df.to_csv(output_master, index=False)
    print(f"Master sanitized dataset saved to: {output_master}")

# --- Main Execution ---

def main():
    # Adjust input_csv to point to your general CSV file from a session.
    timestamp = "2025-03-15_16-26-47"
    input_csv = f"./data/raw/{CIRCUIT}/{timestamp}/general_data_{timestamp}.csv"  # Update as needed
    output_csv = f"./data/processed/{CIRCUIT}/sanitized_dataset_{timestamp}.csv"
    
    # Ensure the output directory exists.
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    sanitize_and_merge(input_csv, output_csv)
    join_sanitized_csvs(f"./data/processed/{CIRCUIT}", f"./data/processed/{CIRCUIT}/{CIRCUIT}_master_sanitized_dataset.csv")

if __name__ == "__main__":
    main()