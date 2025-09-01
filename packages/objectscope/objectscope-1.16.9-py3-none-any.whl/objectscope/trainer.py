import os
from detectron2.data.datasets import register_coco_instances
import pickle
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.engine import DefaultTrainer
from objectscope import logger
from typing import Union, List

class TrainSession(object):
    def __init__(self,train_img_dir, train_coco_json_file, 
                    test_img_dir, test_coco_json_file, 
                    config_file_url, num_classes,
                    train_data_name=None, test_data_name=None,
                    train_metadata={}, test_metadata={},
                    output_dir="output/object_detector",device="cuda",
                    num_workers=12,imgs_per_batch=4, base_lr=0.00005,
                    max_iter=5000, checkpoint_period=50, #start_run=True,
                    **kwargs
                ):
        self.train_img_dir = train_img_dir
        self.train_coco_json_file = train_coco_json_file
        self.test_img_dir = test_img_dir
        self.test_coco_json_file = test_coco_json_file        
        self.train_metadata = train_metadata
        self.test_metadata = test_metadata
        self.config_file_url = config_file_url
        self.num_classes = num_classes
        self.output_dir = output_dir
        self.device = device
        self.num_workers = num_workers
        self.imgs_per_batch = imgs_per_batch
        self.base_lr = base_lr
        self.max_iter = max_iter
        self.checkpoint_period = checkpoint_period
        logger.info(f"num_classes: {num_classes}")
        if not test_data_name:
            test_data_name = os.path.basename(test_img_dir)
        if not train_data_name:
            train_data_name = os.path.basename(train_img_dir)
        self.test_data_name = test_data_name  
        self.train_data_name = train_data_name  
    
    def register_dataset(self, train_img_dir=None, 
                         train_coco_json_file=None,
                         test_img_dir=None, 
                         test_coco_json_file=None,
                         train_data_name=None, test_data_name=None,
                         train_metadata={}, test_metadata={}
                        ):
        register_coco_instances(name=train_data_name if train_data_name else self.train_data_name,
                                metadata=train_metadata if train_metadata else self.train_metadata,
                                json_file=train_coco_json_file if train_coco_json_file else self.train_coco_json_file,
                                image_root=train_img_dir if train_img_dir else self.train_img_dir
                                )
        register_coco_instances(name=test_data_name if test_data_name else self.test_data_name,
                                metadata=test_metadata if test_metadata else self.test_metadata,
                                json_file=test_coco_json_file if test_coco_json_file else self.test_coco_json_file,
                                image_root=test_img_dir if test_img_dir else self.test_img_dir
                                )
        
    
    def create_config(self, num_classes=None,
                      config_file_url=None,
                        num_workers=None,
                        imgs_per_batch=None, base_lr=None,
                        max_iter=None, checkpoint_period=None,
                        output_dir=None,
                        device=None, train_data_name=None, 
                        test_data_name=None,
                        anchor_ratios: Union[None, List[List]]=None,
                        anchor_sizes: Union[None, List[List]]=None,
                        evaluate_period=1
                        ):
        """_summary_

        Args:
            num_classes (_type_, optional): _description_. Defaults to None.
            config_file_url (_type_, optional): _description_. Defaults to None.
            num_workers (_type_, optional): _description_. Defaults to None.
            imgs_per_batch (_type_, optional): _description_. Defaults to None.
            base_lr (_type_, optional): _description_. Defaults to None.
            max_iter (_type_, optional): _description_. Defaults to None.
            checkpoint_period (_type_, optional): _description_. Defaults to None.
            output_dir (_type_, optional): _description_. Defaults to None.
            device (_type_, optional): _description_. Defaults to None.
            train_data_name (_type_, optional): _description_. Defaults to None.
            test_data_name (_type_, optional): _description_. Defaults to None.
            anchor_ratios (Union[None, List[List]], optional): Anchor ratios use for generating anchor boxes. Example [[0.7685566328549631, 1.8715268243900367, 1.1942387054643602]].
            anchor_sizes (list, optional): Anchor sizes use for generating anchor boxes and RPN. Example [[240.9236833908755], [59.864835712691715], [153.60699447681742], [434.33823627084996], [103.37411650130916]].
            evaluate_period (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        os.makedirs(name=output_dir if output_dir else self.output_dir, 
                    exist_ok=True
                    )
        self.output_cfg_path = os.path.join(output_dir if output_dir else self.output_dir, 
                                       "cfg.pickle"
                                       )
        self.cfg = get_cfg()
        config_file_url = config_file_url if config_file_url else self.config_file_url
        config_file = model_zoo.get_config_file(config_file_url)
        self.cfg.merge_from_file(config_file)
        self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(config_file_url)
        
        self.cfg.DATASETS.TRAIN = (train_data_name if train_data_name else self.train_data_name,)
        self.cfg.DATASETS.TEST = (test_data_name if test_data_name else self.test_data_name,)
        
        self.cfg.DATALOADER.NUM_WORKERS = num_workers if num_workers else self.num_workers
        self.cfg.SOLVER.IMS_PER_BATCH = imgs_per_batch if imgs_per_batch else self.imgs_per_batch
        self.cfg.SOLVER.BASE_LR = base_lr if base_lr else self.base_lr
        self.cfg.SOLVER.MAX_ITER = max_iter if max_iter else self.max_iter
        self.cfg.SOLVER.CHECKPOINT_PERIOD = checkpoint_period if checkpoint_period else self.checkpoint_period
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes if num_classes else self.num_classes
        self.cfg.MODEL.DEVICE = device if device else self.device
        self.cfg.OUTPUT_DIR = output_dir if output_dir else self.output_dir
        
        if evaluate_period > 0:
            logger.info(f"Setting evaluation period: {evaluate_period}")
            self.cfg.TEST.EVAL_PERIOD = evaluate_period
        if anchor_ratios:
            logger.info(f"Setting anchor ratios: {anchor_ratios}")
            self.cfg.MODEL.ANCHOR_GENERATOR.ASPECT_RATIOS = anchor_ratios
        if anchor_sizes:
            logger.info(f"Setting anchor sizes: {anchor_sizes}")
            self.cfg.MODEL.ANCHOR_GENERATOR.SIZES = anchor_sizes
        with open(self.output_cfg_path, "wb") as f:
            pickle.dump(self.cfg, f, protocol = pickle.HIGHEST_PROTOCOL)

        return self.cfg, self.output_cfg_path

    def get_trainer(self, cfg=None):
        self.trainer = DefaultTrainer(cfg if cfg else self.cfg)
        self.trainer.resume_or_load(True)
    
    def create_trainer(self):
        self.register_dataset()
        if hasattr(self, "cfg"):
            logger.info(f"Using existing config... during create_trainer")
            cfg = self.cfg
        else:
            logger.info(f"Creating new config... during create_trainer")
            cfg, _ = self.create_config()
        self.get_trainer(cfg=cfg)
        return self.trainer

    def run(self):
        logger.info("Creating trainer...")
        self.create_trainer()
        logger.info("Trainer created successfully.")
        logger.info("Starting training run...")
        self.trainer.train()
        logger.info("Training run completed successfully.")
        return self.trainer
        
