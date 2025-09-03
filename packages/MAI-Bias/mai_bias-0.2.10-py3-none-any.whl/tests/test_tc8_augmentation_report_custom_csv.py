from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.custom_csv import data_custom_csv
from mai_bias.catalogue.model_loaders.no_model import no_model
from mai_bias.catalogue.metrics.augmentation_report import (
    augmentation_report,
)


def test_augmentation_report():
    with testing.Env(no_model, data_custom_csv, augmentation_report) as env:
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
        model = env.no_model()
        html_result = env.augmentation_report(dataset, model, sensitive=sensitive)
        html_result.show()


if __name__ == "__main__":
    test_augmentation_report()
