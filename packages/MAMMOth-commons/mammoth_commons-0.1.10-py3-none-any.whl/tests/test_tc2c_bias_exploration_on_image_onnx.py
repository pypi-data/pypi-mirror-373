from mammoth_commons import testing
from mai_bias.catalogue.dataset_loaders.images import data_images
from mai_bias.catalogue.model_loaders.pytorch2onnx import model_torch2onnx

# from mai_bias.catalogue.metrics.interactive_report import interactive_report
from mai_bias.catalogue.metrics.model_card import model_card


def test_bias_exploration():
    with testing.Env(data_images, model_torch2onnx, model_card) as env:
        target = "task"
        protected = "protected"
        model_path = "./data/torch_model/torch_model.py"
        model_dict = "./data/torch_model/resnet18.pt"
        data_dir = "./data/xai_images/race_per_7000"
        csv_dir = "./data/xai_images/bupt_anno.csv"

        dataset = env.data_images(
            path=csv_dir,
            image_root_dir=data_dir,
            target=target,
            data_transform_path="./data/xai_images/torch_transform.py",
            batch_size=4,
            shuffle=False,
        )

        model = env.model_torch2onnx(
            state_path=model_dict,
            model_path=model_path,
            input_width=dataset.input_size[0],
            input_height=dataset.input_size[1],
        )

        result = env.model_card(dataset, model, [protected], problematic_deviation=0)
        result.show()


if __name__ == "__main__":
    test_bias_exploration()
