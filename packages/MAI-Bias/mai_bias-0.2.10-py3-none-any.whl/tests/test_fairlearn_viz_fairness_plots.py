from mammoth_commons import testing
from mai_bias.catalogue.model_loaders.onnx_ensemble import model_onnx_ensemble
from mai_bias.catalogue.dataset_loaders.data_any import data_read_any
from mai_bias.catalogue.metrics.viz_fairness_plots import viz_fairness_plots


def test_multiobjective_report():
    with testing.Env(model_onnx_ensemble, viz_fairness_plots, data_read_any) as env:
        dataset_name = "data/credit.csv"
        target = "class"
        dataset = env.data_read_any(dataset_path=dataset_name, target=target)
        model_path = "data/model_MMM_Fair_GBT.zip"
        model = env.model_onnx_ensemble(model_path)
        sensitive = ["SEX", "MARRIAGE"]
        html_result = env.viz_fairness_plots(dataset, model, sensitive=sensitive)
        html_result.show()


if __name__ == "__main__":
    test_multiobjective_report()
