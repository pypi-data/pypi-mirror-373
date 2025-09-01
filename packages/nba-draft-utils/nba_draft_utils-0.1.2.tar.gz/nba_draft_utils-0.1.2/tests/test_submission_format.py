import numpy as np
from nba_draft_utils.predict import make_submission

def test_submission_format(tiny_data):
    train, test = tiny_data
    proba = np.clip(np.random.randn(len(test))*0.1 + 0.2, 0, 1)
    sub = make_submission(test, proba, id_col="player_id")
    assert list(sub.columns) == ["player_id", "drafted"]
    assert len(sub) == len(test)
    assert sub["drafted"].between(0,1).all()
