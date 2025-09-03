from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.image_pairs import data_image_pairs
from mai_bias.catalogue.model_loaders.pytorch import model_torch
from mai_bias.catalogue.metrics.interactive_report import interactive_report


def test_bias_exploration():
    with testing.Env(data_image_pairs, model_torch, interactive_report) as env:
        target = "is_same"
        protected = "skintone"

        data_dir = "./data/xai_images/race_per_7000"
        csv_dir = "./data/xai_images/bupt_pairs_anno_skin_stringvals.csv"

        # additional arguements needed for faceX
        target_class = 1  # 1 if we want to find the activations indicating the same person. 0 if we want to find the activations indicating the diference between diferent persons.

        # model_path = "./data/torch_model/adaface.py"
        # model_dict = "./data/torch_model/ir50_adaface.pth"
        # target_layer = "body.23.res_layer.4"

        model_path = "./data/torch_model/adaface_toy.py"
        model_dict = "./data/torch_model/toy_adaface.pth"
        target_layer = "conv3"

        dataset = env.data_image_pairs(
            path=csv_dir,
            image_root_dir=data_dir,
            target=target,
            data_transform_path="./data/xai_images/torch_transform_fv.py",
            batch_size=1,
            shuffle=False,
        )

        model = env.model_torch(
            state_path=model_dict,
            model_path=model_path,
        )

        html_result = env.interactive_report(dataset, model, [protected])
        html_result.show()


if __name__ == "__main__":
    test_bias_exploration()
