import os
import pandas as pd
from hashlib import md5
from pathlib import Path
from typing import List

def sanitize_all_circuits(base_raw_path: str, base_processed_path: str):
    """
    Recorre todos los subdirectorios por circuito en la ruta base de datos en crudo,
    sanetiza los tiempos de vuelta y los reglajes, y genera:
    - Un archivo CSV por circuito con los datos limpios.
    - Un archivo CSV global combinando todos los circuitos.

    :param str base_raw_path: Ruta base donde se encuentran los datos en crudo.
    :param str base_processed_path: Ruta base donde se guardarán los datos procesados.
    """
    os.makedirs(base_processed_path, exist_ok=True)
    circuit_laps: List[pd.DataFrame] = []

    for circuit_dir in Path(base_raw_path).iterdir():
        if not circuit_dir.is_dir():
            continue

        circuit_name = circuit_dir.name
        print(f"Procesando circuito: {circuit_name}")
        circuit_df = sanitize_sessions_for_circuit(circuit_dir, circuit_name)

        if circuit_df is not None:
            circuit_df.to_csv(os.path.join(base_processed_path, f"{circuit_name}_sanitized.csv"), index=False)
            circuit_laps.append(circuit_df)

    if circuit_laps:
        all_df = pd.concat(circuit_laps, ignore_index=True)
        all_df.to_csv(os.path.join(base_processed_path, "all_circuits_sanitized.csv"), index=False)

def sanitize_sessions_for_circuit(circuit_dir: Path, circuit_name: str) -> pd.DataFrame:
    """
    Procesa todos los subdirectorios de una carpeta de circuito específica,
    uniendo todos los datasets sanetizados de sus sesiones.
    Devuelve un DataFrame con los datos limpios de todas las sesiones del circuito.
    Si no hay datos válidos, devuelve None.

    :param Path circuit_dir: Ruta del directorio del circuito.
    :param str circuit_name: Nombre del circuito.
    """
    all_session_dfs = []

    for session_dir in circuit_dir.iterdir():
        if not session_dir.is_dir():
            continue

        lap_file = next(session_dir.glob("lap_data_*.csv"), None)
        setup_file = next(session_dir.glob("car_setup_data_*.csv"), None)

        if not lap_file or not setup_file:
            continue

        session_df = sanitize_single_session(lap_file, setup_file, circuit_name)
        if session_df is not None:
            all_session_dfs.append(session_df)

    if all_session_dfs:
        return pd.concat(all_session_dfs, ignore_index=True)
    return None

def sanitize_single_session(lap_file: Path, setup_file: Path, circuit_name: str) -> pd.DataFrame:
    """
    Sanetiza los datos de una sola sesión: vincula los tiempos de vuelta con el 
    reglaje más reciente anterior. Devuelve un DataFrame limpio.
    
    :param Path lap_file: Ruta al archivo CSV de tiempos de vuelta.
    :param Path setup_file: Ruta al archivo CSV de reglajes del coche.
    :param str circuit_name: Nombre del circuito.
    """
    lap_data = pd.read_csv(lap_file)
    setup_data = pd.read_csv(setup_file)

    lap_data = lap_data[lap_data["m_lapData_0_m_lastLapTimeInMS"] > 0]
    lap_times = lap_data[["m_header_m_sessionTime", "m_lapData_0_m_lastLapTimeInMS"]].drop_duplicates()
    lap_times = lap_times.sort_values("m_header_m_sessionTime").drop_duplicates(
        subset=["m_lapData_0_m_lastLapTimeInMS"], keep="last"
    )

    setup_cols = [col for col in setup_data.columns if col.startswith("m_carSetups_0_")]
    setup_data["setup_hash"] = setup_data[setup_cols].apply(
        lambda row: md5(str(tuple(row)).encode()).hexdigest(), axis=1
    )
    unique_setups = setup_data.sort_values("m_header_m_sessionTime").drop_duplicates(subset=["setup_hash"])

    merged = pd.merge_asof(
        lap_times.sort_values("m_header_m_sessionTime"),
        unique_setups.sort_values("m_header_m_sessionTime")[
            ["m_header_m_sessionTime", "setup_hash"] + setup_cols
        ],
        on="m_header_m_sessionTime",
        direction="backward"
    )

    if merged.empty:
        return None

    merged = merged.drop(columns=["m_header_m_sessionTime", "setup_hash"])
    merged = merged.rename(columns={"m_lapData_0_m_lastLapTimeInMS": "lapTimeInMS"})
    merged.columns = [
        "lapTimeInMS" if col == "lapTimeInMS" else col.replace("m_carSetups_0_", "")
        for col in merged.columns
    ]
    merged["circuit"] = circuit_name
    return merged