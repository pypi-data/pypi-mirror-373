from mammoth_commons import testing
from mai_bias.catalogue.model_loaders.onnx_ensemble import model_onnx_ensemble
from mai_bias.catalogue.dataset_loaders.data_any import data_read_any
from mai_bias.catalogue.metrics.multi_objective_report import multi_objective_report


def test_multiobjective_report():
    with testing.Env(model_onnx_ensemble, multi_objective_report, data_read_any) as env:
        dataset_name = "data/credit.csv"
        target = "class"
        dataset = env.data_read_any(dataset_path=dataset_name, target=target)
        model_path = "data/model_MMM_Fair_GBT.zip"
        model = env.model_onnx_ensemble(model_path)
        sensitive = ["SEX", "MARRIAGE"]
        html_result = env.multi_objective_report(dataset, model, sensitive=sensitive)
        html_result.show()


if __name__ == "__main__":
    test_multiobjective_report()
