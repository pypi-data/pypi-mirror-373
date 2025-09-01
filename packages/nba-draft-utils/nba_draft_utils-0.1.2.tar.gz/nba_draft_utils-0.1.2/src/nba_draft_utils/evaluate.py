import numpy as np
from sklearn.metrics import roc_auc_score, RocCurveDisplay
import matplotlib.pyplot as plt

def positive_class_index(clf) -> int:
    return int(np.where(clf.classes_ == 1)[0][0])

def auc_scores(pipe, Xval, yval, Xtest, ytest) -> tuple[float, float]:
    pos = positive_class_index(pipe.named_steps["clf"])
    val_pred = pipe.predict_proba(Xval)[:, pos]
    hold_pred = pipe.predict_proba(Xtest)[:, pos]
    return roc_auc_score(yval, val_pred), roc_auc_score(ytest, hold_pred)

def plot_holdout_roc(ytest, hold_pred, title: str = "ROC Curve (Holdout)"):
    RocCurveDisplay.from_predictions(ytest, hold_pred)
    plt.title(title); plt.show()
