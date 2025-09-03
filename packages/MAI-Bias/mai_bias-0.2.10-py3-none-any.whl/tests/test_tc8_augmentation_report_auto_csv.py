from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.auto_csv import data_auto_csv
from mai_bias.catalogue.model_loaders.no_model import no_model
from mai_bias.catalogue.metrics.augmentation_report import (
    augmentation_report,
)


def test_augmentation_report():
    with testing.Env(no_model, data_auto_csv, augmentation_report) as env:
        sensitive = ["marital"]
        dataset_uri = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip/bank/bank.csv"
        dataset = env.data_auto_csv(dataset_uri)
        model = env.no_model()
        html_result = env.augmentation_report(dataset, model, sensitive=sensitive)
        html_result.show()


if __name__ == "__main__":
    test_augmentation_report()
