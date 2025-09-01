# objectscope
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/agbleze/objectscope/.github%2Fworkflows%2Fci-cd.yml)
![GitHub Tag](https://img.shields.io/github/v/tag/agbleze/objectscope)
![GitHub Release](https://img.shields.io/github/v/release/agbleze/objectscope)
![GitHub License](https://img.shields.io/github/license/agbleze/objectscope)

ObjectScope is an extension of Detectron2 that streamlines model training and evaluation by adapting to the structure of your data and the workflows you rely on most. It offers high-level abstractions and utilities that automate key steps—such as dataset registration, anchor box refinement, model optimization, and quantization— out of the box all accessible through a single command. 

## Installation

To install and run objectscope successfully, you need to have Detectron2 installed. Incase you are using a gpu enabled device, then install objectscope with the appropriate CUDA version of PyTorch.

##### Install Detectron2 

```bash
pip install git+https://github.com/facebookresearch/detectron2.git
```

##### Install objectscope with CUDA-enabled Pytorch

```bash
pip install objectscope --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cu118

```

## Usage

Objectscope can run from the terminal, Python script or Jupyter notebook.

### Train model in python file / Jupyter notebook

```python
from objectscope.trainer import TrainSession

trainer = TrainSession(train_img_dir="TRAIN_IMG_DIR",
                            train_coco_json_file="TRAIN_COCO_JSON_FILE",
                            test_img_dir="TEST_IMG_DIR",
                            test_coco_json_file="TEST_COCO_JSON_FILE",
                            config_file_url="CONFIG_FILE_URL",
                            num_classes="NUM_CLASSES",
                            train_data_name="train_data_name",
                            test_data_name="test_data_name",
                            train_metadata={},
                            test_metadata={},
                            output_dir="OUTPUT_DIR",
                            device="cuda,
                            num_workers=4,
                            imgs_per_batch=8,
                            base_lr=0.0001,
                            max_iter=5,
                            checkpoint_period=1,
                        )
    trainer.run()
```

### Train model using Terminal command

ObjectScope supports training, evaluation, optimization, ONNX export, and TensorBoard visualization—all from a single CLI command.

You can pass parameters via:

- Command-line arguments
- Environment variables
- A .env file

Command-line arguments take precedence when duplicates exist.

Example of training model from the terminal is as follows:

```bash
objectscope --train_img_dir "train"\
            --test_img_dir "test" \
            --output_dir "output_dir" \
            --train_coco_json_file "train_annotations.coco.json" \
            --test_coco_json_file "test_annotations.coco.json" \
            --max_iter 5 --num_classes 15 --checkpoint_period 1  --roi_heads_score_threshold 0.5 \
            --imgs_per_batch 4 --num_workers 10 --config_file_url "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml" \
            --device "cuda" --base_lr 0.00005 \
            --show_tensorboard --optimize_model
```

#### Example .env file

```.env
TRAIN_IMG_DIR="train_images"\
test_img_dir="test_images" \
OUTPUT_DIR="output_dir" \
TRAIN_COCO_JSON_FILE="train_annotations.coco.json" \
TEST_COCO_JSON_FILE="test_annotations.coco.json" \
MAX_ITER=100000 
NUM_CLASSES=15 
CHECKPOINT_PERIOD=100  
ROI_HEADS_SCORE_THRESHOLD=0.5
IMGS_PER_BATCH=4 
NUM_WORKERS=10 
CONFIG_FILE_URL="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"
DEVICE="cuda" 
BASE_LR=0.00005
SHOW_TENSORBOARD=true
OPTIMIZE_MODEL=true
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`objectscope` was created by Agbleze. It is licensed under the terms of the MIT license.

## Credits

`objectscope` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
