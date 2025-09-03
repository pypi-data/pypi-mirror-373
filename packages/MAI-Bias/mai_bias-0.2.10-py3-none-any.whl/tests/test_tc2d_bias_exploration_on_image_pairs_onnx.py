from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.image_pairs import data_image_pairs
from mai_bias.catalogue.model_loaders.pytorch2onnx import model_torch2onnx
from mai_bias.catalogue.metrics.model_card import model_card


def test_bias_exploration():
    with testing.Env(data_image_pairs, model_torch2onnx, model_card) as env:
        target = "is_same"
        protected = "race"

        data_dir = "./data/xai_images/race_per_7000"
        csv_dir = "./data/xai_images/bupt_pairs_anno.csv"

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

        model = env.model_torch2onnx(
            state_path=model_dict,
            model_path=model_path,
            input_width=dataset.input_size[0],
            input_height=dataset.input_size[1],
        )

        result = env.model_card(dataset, model, [protected])
        print(result.text())


if __name__ == "__main__":
    test_bias_exploration()
