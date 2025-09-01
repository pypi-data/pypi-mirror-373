from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

def stratified_split_60_20_20(
    X: pd.DataFrame, y: pd.Series, random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    # 80/20 first
    Xtr, Xt, ytr, yt = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=random_state
    )
    # then 60/20/20 (i.e., 25% of 80% -> 20% total)
    Xtr, Xv, ytr, yv = train_test_split(
        Xtr, ytr, test_size=0.25, stratify=ytr, random_state=random_state
    )
    return Xtr, Xv, Xt, ytr, yv, yt

def fit_pipeline(pipeline: Pipeline, X, y) -> Pipeline:
    pipeline.fit(X, y)
    return pipeline
