# src/beiwe_har/preprocessing/dataset.py

import pandas as pd
import numpy as np
from pathlib import Path
import pytz
from geopy.distance import geodesic

# Fixed output filenames
ACC_OUT  = "acc_dataset.csv"
GYRO_OUT = "gyro_dataset.csv"
GPS_OUT  = "gps_dataset.csv"


def create_accelerometer_dataset(study_path: str) -> None:
    """
    Combine all users' accelerometer CSVs under <study_path>/<user>/accelerometer/*.csv
    Save as <study_path>/acc_dataset.csv
    """
    base_path = Path(study_path)
    all_data = []
    est = pytz.timezone("US/Eastern")

    for user_dir in base_path.glob("*"):
        acc_dir = user_dir / "accelerometer"
        if not acc_dir.is_dir():
            continue

        user_id = user_dir.name
        for csv_file in acc_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file, usecols=['UTC time', 'x', 'y', 'z'])
                df['timestamp'] = (
                    pd.to_datetime(df['UTC time'])
                    .dt.tz_localize('UTC')
                    .dt.tz_convert(est)
                )
                df.drop(columns=['UTC time'], inplace=True)
                df['magnitude'] = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
                df['user'] = user_id
                df = df[['user', 'timestamp', 'x', 'y', 'z', 'magnitude']]
                all_data.append(df)
            except Exception as e:
                print(f"Error processing {csv_file}: {e}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True).sort_values(['user', 'timestamp'])
        out_path = base_path / ACC_OUT
        combined.to_csv(out_path, index=False)
        print(f"Preprocessed accelerometer data saved to: {out_path}")
    else:
        print("No valid accelerometer data found for preprocessing.")


def create_gyroscope_dataset(study_path: str) -> None:
    """
    Combine all users' gyro CSVs under <study_path>/<user>/gyro/*.csv
    Save as <study_path>/gyro_dataset.csv
    """
    base_path = Path(study_path)
    all_data = []
    est = pytz.timezone("US/Eastern")

    for user_dir in base_path.glob("*"):
        gyro_dir = user_dir / "gyro"
        if not gyro_dir.is_dir():
            continue

        user_id = user_dir.name
        for csv_file in gyro_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file, usecols=['UTC time', 'x', 'y', 'z'])
                df['timestamp'] = (
                    pd.to_datetime(df['UTC time'])
                    .dt.tz_localize('UTC')
                    .dt.tz_convert(est)
                )
                df.drop(columns=['UTC time'], inplace=True)
                df['magnitude'] = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)
                df['user'] = user_id
                df = df[['user', 'timestamp', 'x', 'y', 'z', 'magnitude']]
                all_data.append(df)
            except Exception as e:
                print(f"Error processing {csv_file}: {e}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True).sort_values(['user', 'timestamp'])
        out_path = base_path / GYRO_OUT
        combined.to_csv(out_path, index=False)
        print(f"Preprocessed gyroscope data saved to: {out_path}")
    else:
        print("No valid gyroscope data found for preprocessing.")


def create_gps_dataset(study_path: str) -> None:
    """
    Combine all users' GPS CSVs under <study_path>/<user>/gps/*.csv
    Save as <study_path>/gps_dataset.csv
    """
    base_path = Path(study_path)
    all_data = []
    est = pytz.timezone("US/Eastern")

    for user_dir in base_path.glob("*"):
        gps_dir = user_dir / "gps"
        if not gps_dir.is_dir():
            continue

        user_id = user_dir.name
        for csv_file in gps_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file, usecols=['UTC time', 'latitude', 'longitude', 'altitude', 'accuracy'])
                df['timestamp'] = (
                    pd.to_datetime(df['UTC time'])
                    .dt.tz_localize('UTC')
                    .dt.tz_convert(est)
                )
                df.drop(columns=['UTC time'], inplace=True)
                df.sort_values('timestamp', inplace=True)

                coords = list(zip(df['latitude'], df['longitude']))
                df['distance'] = [0.0] + [
                    geodesic(coords[i - 1], coords[i]).meters for i in range(1, len(coords))
                ]
                df['time_diff'] = df['timestamp'].diff().dt.total_seconds().fillna(0)
                df['speed'] = df.apply(
                    lambda r: r['distance'] / r['time_diff'] if r['time_diff'] > 0 else 0, axis=1
                )

                df['user'] = user_id
                df = df[['user', 'timestamp', 'latitude', 'longitude', 'altitude', 'accuracy', 'distance', 'speed']]
                all_data.append(df)
            except Exception as e:
                print(f"Error processing {csv_file}: {e}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True).sort_values(['user', 'timestamp'])
        out_path = base_path / GPS_OUT
        combined.to_csv(out_path, index=False)
        print(f"Preprocessed GPS data saved to: {out_path}")
    else:
        print("No valid GPS data found for preprocessing.")


def create_dataset(study_path: str) -> None:
    """
    Run all creators with fixed filenames:
      - acc_dataset.csv
      - gyro_dataset.csv
      - gps_dataset.csv
    """
    base = Path(study_path)

    create_accelerometer_dataset(study_path)
    create_gyroscope_dataset(study_path)
    create_gps_dataset(study_path)