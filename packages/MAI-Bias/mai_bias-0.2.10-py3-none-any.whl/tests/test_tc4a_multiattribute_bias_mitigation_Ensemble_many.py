from mammoth_commons import testing
from mai_bias.catalogue.model_loaders.onnx_ensemble import model_onnx_ensemble
from mai_bias.catalogue.dataset_loaders.uci_csv import data_uci
from mai_bias.catalogue.metrics.model_card import model_card


def test_multiattribute_bias_mitigation():
    # TODO: mmm-fair does not use this repo's data structures, but basically needs to call to_pred WITHOUT the sensitive attribute
    # TODO: if it's going to include that in training
    with testing.Env(model_onnx_ensemble, data_uci, model_card) as env:
        dataset_name = "bank"
        dataset = env.data_uci(dataset_name=dataset_name)
        model_path = "data/model_MMM_Fair.zip"
        model = env.model_onnx_ensemble(model_path)
        sensitive = ["age", "marital"]
        markdown_result = env.model_card(dataset, model, sensitive=sensitive)
        markdown_result.show()


if __name__ == "__main__":
    test_multiattribute_bias_mitigation()
