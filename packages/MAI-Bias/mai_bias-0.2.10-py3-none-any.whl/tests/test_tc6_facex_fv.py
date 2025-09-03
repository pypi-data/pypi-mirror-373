from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.image_pairs import data_image_pairs
from mai_bias.catalogue.model_loaders.pytorch import model_torch
from mai_bias.catalogue.metrics.xai_analysis_embeddings import facex_embeddings


def test_facex():
    with testing.Env(data_image_pairs, model_torch, facex_embeddings) as env:
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

        model = env.model_torch(
            state_path=model_dict,
            model_path=model_path,
        )

        markdown_result = env.facex_embeddings(
            dataset, model, [protected], target_class, target_layer
        )
        markdown_result.show()


test_facex()
