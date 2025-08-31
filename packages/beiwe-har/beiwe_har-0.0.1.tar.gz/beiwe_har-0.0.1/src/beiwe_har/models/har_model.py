import os
import pandas as pd
import joblib
from importlib.resources import files

# id <-> label mapping
_LABEL2ID = {"dws": 0, "ups": 1, "wlk": 2, "jog": 3, "std": 4, "sit": 5}
_ID2LABEL = {v: k for k, v in _LABEL2ID.items()}

def _to_label_str(y):
    # map numeric ids to string labels; pass through strings unchanged
    try:
        return _ID2LABEL[int(y)]
    except Exception:
        return str(y)

def predict_har_from_ecdf(beiwe_file: str) -> pd.DataFrame:
    """
    Predict HAR labels from an ECDF features CSV using the packaged model
    (beiwe_har/models/random_forest_ecdf.pkl).
    """
    # Load packaged model
    model_file = files("beiwe_har.models").joinpath("random_forest_ecdf.pkl")
    with model_file.open("rb") as f:
        model = joblib.load(f)

    # Load features
    df = pd.read_csv(beiwe_file)

    # Metadata to KEEP in output (exclude session_id)
    keep_meta = [c for c in ["user", "window_start_time"] if c in df.columns]
    meta_out = df[keep_meta].copy() if keep_meta else pd.DataFrame(index=df.index)

    # Columns to DROP from feature matrix (ensure session_id never reaches the model)
    drop_from_X = [c for c in ["user", "window_start_time", "session_id"] if c in df.columns]
    X = df.drop(columns=drop_from_X)

    # Predict
    y_pred = model.predict(X)

    # Convert to string labels
    y_pred_str = [ _to_label_str(y) for y in y_pred ]

    # Assemble and save
    out = meta_out.copy()
    out["predicted_label"] = y_pred_str

    base = os.path.splitext(beiwe_file)[0]
    if base.endswith("_ECDF_features"):
        base = base[:-len("_ECDF_features")]
    output_file = base + "_predictions.csv"

    out.to_csv(output_file, index=False)
    print(f"Predictions saved to: {output_file}")

    return out
