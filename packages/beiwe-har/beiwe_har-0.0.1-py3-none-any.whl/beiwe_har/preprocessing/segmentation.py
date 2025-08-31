# Segmentation / windowing
import pandas as pd
from pathlib import Path

def generate_windowed_data(
    file_path: str | Path,
    *,
    frequency: int = 50,
    window_size_in_seconds: float = 2.0,
    time_gap_threshold: float = 10.0,     # seconds; start new session after larger gap
    overlap_ratio: float = 0.5,           # 0.0.. <1.0
    axis_cols: tuple[str, str, str] = ("x", "y", "z"),
    output_path: str | Path | None = None
) -> pd.DataFrame:
    """
    Segment uniformly-sampled tri-axial data (e.g., accelerometer or gyroscope) into fixed windows.

    Expects a CSV with at least: ['user','timestamp', axis_cols...].
    Creates columns like x_0..x_{N-1}, y_*, z_* per window.

    Returns the segmented DataFrame and writes a CSV next to `file_path`
    (or to `output_path` if provided).
    """
    file_path = Path(file_path)
    df = pd.read_csv(file_path)

    # --- basic validation ---
    req = {"user", "timestamp", *axis_cols}
    missing = req.difference(df.columns)
    if missing:
        raise ValueError(f"{file_path} is missing required columns: {sorted(missing)}")

    # Parse timestamps (handles tz-aware strings too)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # Sort and compute per-user time gaps to define sessions
    df = df.sort_values(["user", "timestamp"], kind="mergesort").reset_index(drop=True)
    df["time_diff"] = df.groupby("user", sort=False)["timestamp"].diff().dt.total_seconds()
    df["new_session"] = (df["time_diff"].isna()) | (df["time_diff"] > float(time_gap_threshold))
    df["session_id"] = df["new_session"].cumsum()

    # Window and step sizes (guard against zero or invalid)
    window_size = max(1, int(round(window_size_in_seconds * int(frequency))))
    step_size = max(1, int(round(window_size * (1.0 - float(overlap_ratio)))))
    if step_size > window_size:
        step_size = window_size

    ax_x, ax_y, ax_z = axis_cols
    segmented_rows: list[dict] = []

    # Segmentation per (user, session)
    for (user, session_id), session_df in df.groupby(["user", "session_id"], sort=False):
        session_df = session_df.reset_index(drop=True)
        # Drop windows that would include NaNs
        session_df = session_df.dropna(subset=[ax_x, ax_y, ax_z])

        n = len(session_df)
        if n < window_size:
            continue

        # Create windows by index stride
        for start in range(0, n - window_size + 1, step_size):
            end = start + window_size
            w = session_df.iloc[start:end]

            # Safety (shouldn’t happen given loop stop)
            if len(w) != window_size:
                continue

            row = {
                "user": user,
                "window_start_time": w.iloc[0]["timestamp"],
                "session_id": int(session_id),
            }
            # Flatten axes into columns: x_0..x_{N-1}, y_*, z_*
            # Use .to_numpy() for speed
            x_vals = w[ax_x].to_numpy()
            y_vals = w[ax_y].to_numpy()
            z_vals = w[ax_z].to_numpy()
            for i in range(window_size):
                row[f"x_{i}"] = x_vals[i]
                row[f"y_{i}"] = y_vals[i]
                row[f"z_{i}"] = z_vals[i]
            segmented_rows.append(row)

    df_segmented = pd.DataFrame(segmented_rows)
    if df_segmented.empty:
        # still write an empty file with headers to keep pipeline deterministic
        acc_columns = [f"{axis}_{i}" for i in range(window_size) for axis in ["x", "y", "z"]]
        df_segmented = pd.DataFrame(columns=["user", "window_start_time", "session_id"] + acc_columns)

    # Column order
    acc_columns = [f"{axis}_{i}" for i in range(window_size) for axis in ["x", "y", "z"]]
    final_columns = ["user", "window_start_time", "session_id"] + acc_columns
    df_segmented = df_segmented.reindex(columns=final_columns)

    # Output path beside input unless overridden
    if output_path is None:
        output_path = file_path.with_name(file_path.stem + "_segmented.csv")
    output_path = Path(output_path)
    df_segmented.to_csv(output_path, index=False)
    print(f"Segmented file saved to: {output_path}")
    return df_segmented
