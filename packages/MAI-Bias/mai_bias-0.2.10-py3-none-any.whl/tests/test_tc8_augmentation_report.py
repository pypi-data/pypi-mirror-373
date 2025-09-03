from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.uci_csv import data_uci
from mai_bias.catalogue.model_loaders.no_model import no_model
from mai_bias.catalogue.metrics.augmentation_report import (
    augmentation_report,
)


def test_augmentation_report():
    with testing.Env(no_model, data_uci, augmentation_report) as env:
        dataset = env.data_uci(dataset_name="credit")
        model = env.no_model()
        sensitive = ["X2", "X4"]
        html_result = env.augmentation_report(dataset, model, sensitive=sensitive)
        html_result.show()


if __name__ == "__main__":
    test_augmentation_report()
