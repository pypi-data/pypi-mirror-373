from objectscope.trainer import TrainSession
from objectscope.evaluator import Evaluator
from objectscope import logger
from argparse import ArgumentParser
import os
from objectscope.utils import (launch_tensorboard, run_optimize_model,
                               save_class_metadata
                               )
import subprocess
from decouple import config
from onnx import load
from onnxoptimizer import optimize
from objectscope.model_export_utils import OnnxModelExporter
import onnx

def parse_args():
    parser = ArgumentParser(description="Setup model training and evaluation parameters")
    parser.add_argument("--train_img_dir", type=str, required=True,
                        help="Directory containing training images"
                        )
    parser.add_argument("--train_coco_json_file", type=str, required=True,
                        help="Path to the COCO JSON file for training"
                        )
    parser.add_argument("--test_img_dir", type=str, required=True,
                        help="Directory containing test images"
                        )
    parser.add_argument("--test_coco_json_file", type=str, required=True,
                        help="Path to the COCO JSON file for testing"
                        )
    parser.add_argument("--config_file_url", type=str, required=True,
                        help="URL of the configuration file"
                        )
    parser.add_argument("--num_classes", type=int, required=True,
                        help="Number of classes in the dataset"
                        )
    parser.add_argument("--train_data_name", type=str,
                        help="Name of the training dataset"
                        )
    parser.add_argument("--test_data_name", type=str,
                        help="Name of the testing dataset"
                        )
    parser.add_argument("--train_metadata", type=dict, default={},
                        help="Metadata for the training dataset"
                        )
    parser.add_argument("--test_metadata", type=dict, default={},
                        help="Metadata for the testing dataset"
                        )
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Directory to save output files"
                        )
    parser.add_argument("--device", type=str, default="cuda",
                        help="Device to use for training (e.g., 'cuda' or 'cpu')")
    parser.add_argument("--num_workers", type=int, default=1,
                        help="Number of data loading workers"
                        )
    parser.add_argument("--imgs_per_batch", type=int, default=32,
                        help="Number of images per batch"
                        )
    parser.add_argument("--base_lr", type=float, default=0.00005,
                        help="Base learning rate for training"
                        )
    parser.add_argument("--max_iter", type=int, required=True,
                        help="Maximum number of iterations for training"
                        )
    parser.add_argument("--checkpoint_period", type=int, required=True,
                        help="Period for saving checkpoints"
                        )
    parser.add_argument("--roi_heads_score_threshold", type=float, default=0.5,
                        help="Score threshold for ROI heads during evaluation"
                        )
    parser.add_argument("--tensorboard_logdir", type=str, default="runs",
                        help="Directory for TensorBoard logs"
                        )
    parser.add_argument("--lauch_tensorboard", action="store_true",
                        help="Whether to launch TensorBoard after training. Launches when flag is used"
                        )
    parser.add_argument("--tensorboard_port_num", default="default")
    parser.add_argument("--optimize_model", action="store_true",
                        help="Whether to optimize the model after training"
                        )
    parser.add_argument("--save_class_metadata_as",
                        default="class_metadata_map.json"
                        )
    
    return parser.parse_args()

def main():
    args = parse_args()
    if args.train_data_name:
        train_data_name = args.train_data_name 
    else:
        try:
            train_data_name = config("TRAIN_DATA_NAME")
        except:
            train_data_name = None
    if args.test_data_name:
        test_data_name = args.test_data_name 
    else:
        try:
            test_data_name = config("TEST_DATA_NAME")
        except:
            test_data_name = None
    trainer = TrainSession(train_img_dir=args.train_img_dir if args.train_img_dir else config("TRAIN_IMG_DIR"),
                            train_coco_json_file=args.train_coco_json_file if args.train_coco_json_file else config("TRAIN_COCO_JSON_FILE"),
                            test_img_dir=args.test_img_dir if args.test_img_dir else config("TEST_IMG_DIR"),
                            test_coco_json_file=args.test_coco_json_file if args.test_coco_json_file else config("TEST_COCO_JSON_FILE"),
                            config_file_url=args.config_file_url if args.config_file_url else config("CONFIG_FILE_URL"),
                            num_classes=args.num_classes if args.num_classes else config("NUM_CLASSES"),
                            train_data_name=train_data_name,
                            test_data_name=test_data_name,
                            train_metadata=args.train_metadata if args.train_metadata else config("TRAIN_METADATA",default={}, cast=dict),
                            test_metadata=args.test_metadata if args.test_metadata else config("TEST_METADATA", default={}, cast=dict),
                            output_dir=args.output_dir if args.output_dir else config("OUTPUT_DIR"),
                            device=args.device if args.device else config("DEVICE"),
                            num_workers=args.num_workers if args.num_workers else config("NUM_WORKERS", cast=int),
                            imgs_per_batch=args.imgs_per_batch if args.imgs_per_batch else config("IMGS_PER_BATCH", cast=int),
                            base_lr=args.base_lr if args.base_lr else config("BASE_LR", cast=float),
                            max_iter=args.max_iter if args.max_iter else config("MAX_ITER", cast=int),
                            checkpoint_period=args.checkpoint_period if args.checkpoint_period else config("CHECKPOINT_PERIOD", cast=int),
                        )
    trainer.run()
    save_class_metadata(train_data_name=trainer.train_data_name,
                        save_metadata_as=os.path.join(trainer.output_dir, args.save_class_metadata_as)
                        )
    
    # to ensure tensorboard is launched whenever and wherever passed 
    if not args.lauch_tensorboard:
        try:
            lauch_tensorboard = config("LAUCH_TENSORBOARD")
        except:
            lauch_tensorboard = args.lauch_tensorboard
    else:
        lauch_tensorboard = args.lauch_tensorboard
    if lauch_tensorboard:
        tensorboard_port_num = args.tensorboard_port_num if args.tensorboard_port_num else config("TENSORBOARD_PORT_NUM", default="default")
        launch_tensorboard(logdir=args.tensorboard_logdir, 
                           port_num=tensorboard_port_num
                           )
        logger.info(f"TensorBoard launched at port {tensorboard_port_num}")
    evaluator = Evaluator(cfg=trainer.cfg,
                            test_data_name=trainer.test_data_name,
                            output_dir=args.output_dir if args.output_dir else config("output_dir"),
                            dataset_nm=trainer.test_data_name,
                            metadata=trainer.test_metadata,
                            roi_heads_score_threshold=args.roi_heads_score_threshold if args.roi_heads_score_threshold else config("ROI_HEADS_SCORE_THRESHOLD"),
                                
                            )
    eval_df = evaluator.evaluate_models(cfg=trainer.cfg)
    eval_df.to_csv(os.path.join(args.output_dir, 'evaluation_results.csv'))
    best_model_res = evaluator.get_best_model(eval_df)
    
    if not args.optimize_model:
        try:
            optimize_model = config("OPTIMIZE_MODEL")
        except:
            optimize_model = args.optimize_model
    else:
        optimize_model = args.optimize_model
    if optimize_model:
        onnx_exporter = OnnxModelExporter(cfg_path=trainer.output_cfg_path,
                                            model_path=best_model_res["best_model_name"],
                                            registered_dataset_name=trainer.test_data_name
                                            )
        onnx_exporter.export_to_onnx(save_onnx_as="onnx_sample_model.onnx")
        onnx_model = onnx.load("onnx_sample_model.onnx")
      
        optimize(onnx_model)
if __name__ == "__main__":
    main()
    logger.info("Training and evaluation completed successfully.")    
   
    