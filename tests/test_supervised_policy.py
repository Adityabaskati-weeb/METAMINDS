from training.supervised_policy import build_training_matrix, default_eval_groups, train_and_save_policy


def test_training_matrix_has_examples() -> None:
    X, y_triage, y_resus, y_bed, groups = build_training_matrix()
    assert X.shape[0] > 0
    assert len(y_triage) == X.shape[0]
    assert len(groups) == X.shape[0]


def test_train_and_save_policy_creates_report() -> None:
    report = train_and_save_policy()
    assert report["training_examples"] > 0
    assert report["heldout_triage_accuracy"] >= 0.0
    assert len(report["eval_groups"]) == len(default_eval_groups())
