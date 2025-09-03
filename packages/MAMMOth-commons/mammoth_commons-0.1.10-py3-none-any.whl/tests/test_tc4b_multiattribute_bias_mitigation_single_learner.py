from mammoth_commons import testing
from mai_bias.catalogue.model_loaders.onnx_ensemble import model_onnx_ensemble
from mai_bias.catalogue.dataset_loaders.data_any import data_read_any
from mai_bias.catalogue.metrics.model_card import model_card


def test_multiattribute_bias_mitigation():
    with testing.Env(model_onnx_ensemble, data_read_any, model_card) as env:
        dataset_name = "data/credit.csv"
        target = "class"
        dataset = env.data_read_any(dataset_path=dataset_name, target=target)
        model_path = "data/my_local_model.zip"  # "data/model_MMM_Fair_GBT.zip"
        model = env.model_onnx_ensemble(model_path)
        sensitive = ["SEX", "MARRIAGE"]  # None #["X2", "X4", "X5"]
        # X=dataset.to_pred(sensitive=sensitive)
        # preds=model.predict(X)
        markdown_result = env.model_card(dataset, model, sensitive=sensitive)
        markdown_result.show()


if __name__ == "__main__":
    test_multiattribute_bias_mitigation()
