from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

def make_lgbm(random_state: int = 42) -> LGBMClassifier:
    return LGBMClassifier(
        n_estimators=1000, learning_rate=0.02, num_leaves=31,
        subsample=0.8, colsample_bytree=0.8, min_child_samples=50,
        random_state=random_state, n_jobs=-1
    )

def make_xgb(random_state: int = 42) -> XGBClassifier:
    return XGBClassifier(
        n_estimators=800, max_depth=6, learning_rate=0.03,
        subsample=0.9, colsample_bytree=0.9, eval_metric="logloss",
        random_state=random_state, n_jobs=-1, tree_method="hist", use_label_encoder=False
    )

def make_logreg(random_state: int = 42) -> LogisticRegression:
    return LogisticRegression(
        random_state=random_state, max_iter=3000, n_jobs=-1,
        C=1.0, penalty="l2", solver="lbfgs"
    )

def make_pipeline(prep: ColumnTransformer, clf) -> Pipeline:
    return Pipeline([("prep", prep), ("clf", clf)])
