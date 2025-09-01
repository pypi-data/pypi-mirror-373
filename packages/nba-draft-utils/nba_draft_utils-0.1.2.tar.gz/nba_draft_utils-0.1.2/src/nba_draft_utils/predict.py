import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

def align_like_training(pipe: Pipeline, df: pd.DataFrame) -> pd.DataFrame:
    """Reindex df to the columns seen by the preprocessor at fit-time."""
    prep = pipe.named_steps["prep"]
    if hasattr(prep, "feature_names_in_"):
        expected = list(prep.feature_names_in_)
        return df.reindex(columns=expected)
    # Fallback: assume same columns
    return df

def predict_proba_pipeline(pipe: Pipeline, X: pd.DataFrame) -> np.ndarray:
    pos = int(np.where(pipe.named_steps["clf"].classes_ == 1)[0][0])
    return pipe.predict_proba(X)[:, pos]

def make_submission(test_df: pd.DataFrame, proba: np.ndarray, id_col: str = "player_id") -> pd.DataFrame:
    sub = pd.DataFrame({id_col: test_df[id_col], "drafted": proba})
    return sub
