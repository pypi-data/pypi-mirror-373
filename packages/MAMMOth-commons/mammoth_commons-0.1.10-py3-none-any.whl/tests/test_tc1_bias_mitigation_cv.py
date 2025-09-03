from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.images import data_images
from mai_bias.catalogue.model_loaders.no_model import no_model
from mai_bias.catalogue.metrics.image_bias_analysis import image_bias_analysis


def test_facex():
    with testing.Env(data_images, no_model, image_bias_analysis) as env:
        target = "task"
        task = "face verification"  # "image classification" or "face verification"
        protected = "protected"
        data_dir = "./data/xai_images/race_per_7000"
        csv_dir = "./data/xai_images/bupt_anno.csv"

        dataset = env.data_images(
            path=csv_dir,
            image_root_dir=data_dir,
            target=target,
            data_transform_path="./data/xai_images/torch_transform.py",
            batch_size=1,
            shuffle=False,
        )
        model = env.no_model()
        html_result = env.image_bias_analysis(dataset, model, [protected], task)
        html_result.show()


if __name__ == "__main__":
    test_facex()
