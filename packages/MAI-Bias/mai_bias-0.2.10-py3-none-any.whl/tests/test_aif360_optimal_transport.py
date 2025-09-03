import os
from mammoth_commons import testing

from mai_bias.catalogue.dataset_loaders.custom_csv import data_custom_csv
from mai_bias.catalogue.model_loaders.onnx import model_onnx
from mai_bias.catalogue.metrics.optimal_transport import optimal_transport


def test_optimal_transport():
    with testing.Env(data_custom_csv, model_onnx, optimal_transport) as env:
        numeric = ["age", "duration", "campaign", "pdays", "previous"]
        categorical = [
            "job",
            "marital",
            "education",
            "default",
            "housing",
            "loan",
            "contact",
            "poutcome",
        ]
        sensitive = ["marital"]
        dataset_uri = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip/bank/bank.csv"
        dataset = env.data_custom_csv(
            dataset_uri,
            categorical=categorical,
            numeric=numeric,
            label="y",
            delimiter=";",
        )

        model_path = "file://localhost//" + os.path.abspath("./data/model.onnx")
        model = env.model_onnx(model_path, trained_with_sensitive=True)

        markdown_result = env.optimal_transport(dataset, model, sensitive)
        markdown_result.show()


if __name__ == "__main__":
    test_optimal_transport()
