from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.images import data_images
from mai_bias.catalogue.model_loaders.pytorch import model_torch
from mai_bias.catalogue.metrics.xai_analysis import facex_regions


def test_facex():  # disable window visualization
    with testing.Env(data_images, model_torch, facex_regions) as env:
        target = "task"
        protected = "protected"
        model_path = "./data/torch_model/torch_model.py"
        model_dict = "./data/torch_model/resnet18.pt"
        data_dir = "./data/xai_images/race_per_7000"
        csv_dir = "./data/xai_images/bupt_anno.csv"

        # additional arguements needed for faceX
        target_class = 1
        target_layer = "layer4"

        dataset = env.data_images(
            path=csv_dir,
            image_root_dir=data_dir,
            target=target,
            data_transform_path="./data/xai_images/torch_transform.py",
            batch_size=1,
            shuffle=False,
        )

        model = env.model_torch(
            state_path=model_dict,
            model_path=model_path,
        )

        markdown_result = env.facex_regions(
            dataset, model, [protected], target_class, target_layer
        )
        markdown_result.show()


if __name__ == "__main__":
    test_facex()
