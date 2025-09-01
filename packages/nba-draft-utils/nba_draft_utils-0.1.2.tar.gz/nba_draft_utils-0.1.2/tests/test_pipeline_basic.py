from nba_draft_utils.features import select_common_features, build_preprocessor
from nba_draft_utils.models import make_lgbm, make_pipeline
from nba_draft_utils.train import stratified_split_60_20_20, fit_pipeline
from nba_draft_utils.evaluate import auc_scores

def test_pipeline_train_eval(tiny_data):
    train, test = tiny_data
    feats = select_common_features(train, test, target="drafted", id_col="player_id")
    X = train[feats]; y = train["drafted"].astype(int)

    prep = build_preprocessor(X)
    model = make_lgbm(42)
    pipe = make_pipeline(prep, model)

    Xtr, Xv, Xt, ytr, yv, yt = stratified_split_60_20_20(X, y, random_state=42)
    pipe = fit_pipeline(pipe, Xtr, ytr)
    val_auc, hold_auc = auc_scores(pipe, Xv, yv, Xt, yt)

    assert 0.0 <= val_auc <= 1.0
    assert 0.0 <= hold_auc <= 1.0
