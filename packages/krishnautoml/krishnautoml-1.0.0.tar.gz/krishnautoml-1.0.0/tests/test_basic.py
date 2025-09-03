from krishnautoml import KrishnAutoML
import pandas as pd


def test_pipeline_runs(tmp_path):
    data = pd.DataFrame(
        {"feature1": list(range(10)), "feature2": ["a", "b"] * 5, "target": [0, 1] * 5}
    )
    automl = KrishnAutoML(target="target", n_splits=4)
    automl.load_data(data)
    automl.preprocess().train_models()
    metrics = automl.evaluate()
    assert isinstance(metrics, dict)
