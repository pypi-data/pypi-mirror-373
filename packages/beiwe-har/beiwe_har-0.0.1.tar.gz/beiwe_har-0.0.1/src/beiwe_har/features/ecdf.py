# ECDF feature extraction
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

def extract_ECDF_features(input_file,
                          frequency=50,
                          duration_in_seconds=2,
                          num_components=25):
    """
    Extract ECDF features from a segmented accelerometer CSV file.

    Parameters:
    - input_file: str, path to a single segmented CSV file
    - frequency: int, sampling frequency in Hz (default: 50)
    - duration_in_seconds: int or float, window size in seconds (default: 2)
    - num_components: int, number of ECDF components per axis (default: 25)
    """

    window_size = int(frequency * duration_in_seconds)

    def ecdfRep(data, components):
        m = np.mean(data, axis=0)
        data = np.sort(data, axis=0)
        data = data[np.int32(np.around(np.linspace(0, data.shape[0] - 1, num=components))), :]
        data = data.flatten()
        return np.hstack((data, m))

    # Load and process file
    df = pd.read_csv(input_file)

    # Preserve metadata columns (keep session_id if present)
    meta_names = [c for c in ["user", "window_start_time", "session_id"] if c in df.columns]
    if not {"user", "window_start_time"}.issubset(meta_names):
        # fallback to original behavior if names are unexpected
        meta_cols = df.iloc[:, :2].copy()
        df_signals = df.iloc[:, 2:].copy()
    else:
        meta_cols = df[meta_names].copy()
        df_signals = df.drop(columns=meta_names).copy()

    # Reshape data into windows
    try:
        X = df_signals.values.reshape(-1, window_size, 3)
    except Exception as e:
        raise ValueError(f"Error reshaping data in file {input_file}: {e}")

    ecdf_features = np.zeros((X.shape[0], (num_components + 1) * 3))
    for i in tqdm(range(X.shape[0]), desc=os.path.basename(input_file)):
        ecdf_features[i] = ecdfRep(X[i], num_components)

    df_out = pd.DataFrame(ecdf_features)

    # Combine metadata + features
    df_out = pd.concat([meta_cols.reset_index(drop=True), df_out], axis=1)

    # Save output
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(os.path.dirname(input_file), f"{base_name.replace('_segmented','')}_ECDF_features.csv")
    df_out.to_csv(output_file, index=False)
    print(f"Saved ECDF features to: {output_file}")
    return df_out
