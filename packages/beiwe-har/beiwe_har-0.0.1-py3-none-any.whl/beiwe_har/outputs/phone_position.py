# src/beiwe_har/outputs/phone_position.py
import os
import pandas as pd
import numpy as np

def compute_phone_position(accel_segmented_file: str,
                           gyro_segmented_file: str | None = None) -> pd.DataFrame:
    """
    Estimate per-window phone orientation from segmented accelerometer
    (and optional gyroscope) CSVs.
    """
    # ---- fixed parameters ----
    WINDOW_SIZE = 100   # 2 s @ 50 Hz
    FREQUENCY   = 50
    ALPHA       = 0.98
    dt = WINDOW_SIZE / float(FREQUENCY)

    # ---- load segmented data ----
    acc = pd.read_csv(accel_segmented_file)
    acc["window_start_time"] = pd.to_datetime(acc["window_start_time"], format="mixed")

    has_gyro = False
    if gyro_segmented_file:
        try:
            gyro = pd.read_csv(gyro_segmented_file)
            gyro["window_start_time"] = pd.to_datetime(gyro["window_start_time"], format="mixed")
            merged = pd.merge(acc, gyro, on=["user", "window_start_time"], suffixes=("_acc", "_gyro"))
            has_gyro = True
        except Exception:
            merged = acc.copy()
            has_gyro = False
    else:
        merged = acc.copy()

    # ---- expected columns for fixed window ----
    if has_gyro:
        acc_x_cols  = [f"x_{i}_acc" for i in range(WINDOW_SIZE)]
        acc_y_cols  = [f"y_{i}_acc" for i in range(WINDOW_SIZE)]
        acc_z_cols  = [f"z_{i}_acc" for i in range(WINDOW_SIZE)]
        gyro_x_cols = [f"x_{i}_gyro" for i in range(WINDOW_SIZE)]
        gyro_y_cols = [f"y_{i}_gyro" for i in range(WINDOW_SIZE)]
        needed = acc_x_cols + acc_y_cols + acc_z_cols + gyro_x_cols + gyro_y_cols
    else:
        acc_x_cols  = [f"x_{i}" for i in range(WINDOW_SIZE)]
        acc_y_cols  = [f"y_{i}" for i in range(WINDOW_SIZE)]
        acc_z_cols  = [f"z_{i}" for i in range(WINDOW_SIZE)]
        needed = acc_x_cols + acc_y_cols + acc_z_cols

    missing = [c for c in needed if c not in merged.columns]
    if missing:
        raise ValueError(
            f"Segmented inputs do not match fixed window size ({WINDOW_SIZE}). "
            f"Missing columns like: {missing[:5]}{' ...' if len(missing) > 5 else ''}"
        )

    # ---- orientation math ----
    def accel_only_pitch_roll(ax, ay, az):
        pitch = np.degrees(np.arctan2(-ax, np.sqrt(ay**2 + az**2)))
        roll  = np.degrees(np.arctan2(ay, az))
        return pitch, roll

    def comp_filter_pitch_roll(ax, ay, az, gx, gy):
        acc_pitch, acc_roll = accel_only_pitch_roll(ax, ay, az)
        gyro_pitch = gy * dt   # deg/s * s = deg
        gyro_roll  = gx * dt
        pitch = ALPHA * gyro_pitch + (1 - ALPHA) * acc_pitch
        roll  = ALPHA * gyro_roll  + (1 - ALPHA) * acc_roll
        return pitch, roll

    def label_orientation(pitch, roll):
        if abs(pitch) < 10 and abs(roll) < 10:
            return "Flat_Facing_Up"
        elif abs(pitch) > 80:
            return "Upright"
        elif pitch < -170:
            return "Face_Down"
        elif abs(roll) > 45:
            return "On_Side"
        else:
            return "Unknown"

    def per_row(row):
        mean_ax = row[acc_x_cols].mean()
        mean_ay = row[acc_y_cols].mean()
        mean_az = row[acc_z_cols].mean()

        if has_gyro:
            mean_gx = row[gyro_x_cols].mean()
            mean_gy = row[gyro_y_cols].mean()
            pitch, roll = comp_filter_pitch_roll(mean_ax, mean_ay, mean_az, mean_gx, mean_gy)
        else:
            pitch, roll = accel_only_pitch_roll(mean_ax, mean_ay, mean_az)

        return pd.Series([pitch, roll, label_orientation(pitch, roll)])

    merged[["Pitch (°)", "Roll (°)", "Orientation_Label"]] = merged.apply(per_row, axis=1)

    out = merged[["user", "window_start_time", "Pitch (°)", "Roll (°)", "Orientation_Label"]].copy()
    out = out.rename(columns={"window_start_time": "Timestamp"})

    # save as phone_positions.csv in the same directory as the accel file
    out_dir = os.path.dirname(os.path.abspath(accel_segmented_file))
    output_file = os.path.join(out_dir, "phone_positions.csv")
    out.to_csv(output_file, index=False)
    print(f"Saved: {output_file}")

    return out
