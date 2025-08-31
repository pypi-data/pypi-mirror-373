from detectron2.engine import DefaultTrainer, DefaultPredictor
from detectron2.evaluation import COCOEvaluator
from detectron2.data import build_detection_test_loader
import os
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import cv2
import random
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from objectscope import logger
from glob import glob
from typing import Union, List

class Evaluator(object):
    def __init__(self, cfg, test_data_name, 
                 roi_heads_score_threshold=0.5,
                 tasks=("bbox",),
                 output_dir="output/object_detector",
                 **kwargs
                 ):
        cfg.DATASETS.TEST = (test_data_name,)
        self.cfg = cfg
        self.test_data_name = test_data_name
        self.roi_heads_score_threshold = roi_heads_score_threshold
        self.output_dir = output_dir
        self.evaluator = COCOEvaluator(dataset_name=self.test_data_name,
                                        tasks=tasks,
                                        distributed=False,
                                        output_dir=os.path.join(self.output_dir, 'test_results')
                                        )
        self.dataset_nm = DatasetCatalog.get(test_data_name)
        self.metadata = MetadataCatalog.get(test_data_name)
    
    def get_model_paths(self, cfg=None):
        cfg = cfg if cfg else self.cfg
        self.model_paths = glob(f"{cfg.OUTPUT_DIR}/*.pth")
        return self.model_paths
    
    def evaluate_models(self, cfg=None, model_paths=None, 
                        roi_heads_score_threshold=None,
                        ) -> pd.DataFrame:
    
        model_eval_results = {}
        cfg = cfg if cfg else self.cfg
        if not model_paths:
            if not hasattr(self, "model_paths"):
                model_paths = self.get_model_paths(cfg)
            else:
                model_paths = self.model_paths
                        
        for model_path in model_paths:
            cfg.MODEL.WEIGHTS = model_path
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = roi_heads_score_threshold if roi_heads_score_threshold else self.roi_heads_score_threshold
            predictor = DefaultPredictor(self.cfg)
            trainer = DefaultTrainer(cfg)
            trainer.resume_or_load(True)
            x = trainer.test(cfg, predictor.model, evaluators=[self.evaluator])
            print(f"test output: {x}")
            model_eval_results[model_path] = x['bbox']
        self.eval_df = pd.DataFrame.from_dict(model_eval_results, orient='index')
        self.eval_df.index.name = 'model_name'                
        return self.eval_df
        
    def get_best_model(self, eval_df=None, 
                        metric='AP50'
                        ):
        if  eval_df is None:
            if hasattr(self, "eval_df"):
                eval_df = self.eval_df
            else:
                logger.info(f"eval_df not passed to get_best_model hence evaluating models to create it...")
                eval_df = self.evaluate_models()
        if not isinstance(eval_df, pd.DataFrame):
            raise ValueError(f"eval_df must be a DataFrame not {type(eval_df)}")
        if metric not in eval_df.columns:
            raise ValueError(f"Metric '{metric}' not found in evaluation DataFrame columns.")
        if eval_df.empty:
            raise ValueError("Evaluation DataFrame is empty. No models to evaluate.")
        if eval_df.shape[0] == 1:
            logger.info("Only one model available for evaluation.")
            return eval_df.index[0], eval_df.iloc[0][metric]
        
        eval_df.sort_values(by=metric, ascending=False, inplace=True)
        self.best_model_name = eval_df.index[0]
        self.best_model_score = eval_df[metric].values[0]
        logger.info(f"Best model: {self.best_model_name} with score: {self.best_model_score}")
        self.best_model_results = {"best_model_name": self.best_model_name, 
                                    f"best_model_{metric}_score": self.best_model_score,
                                    }
        return self.best_model_results
                
    def plot_evaluation_results(self, df: Union[pd.DataFrame, None]=None, metric='AP50',
                                labels={"AP50": "Average Precision at IoU=0.5", "model_name": "Model Name"}
                                ):
        if  df is None:
            if hasattr(self, "eval_df"):
                df = self.eval_df
            else:
                logger.info(f"df not passed and eval_df not created so model evaluation will be done. This may take several minutes ...")
                df = self.evaluate_models()
        fig = px.line(df, x=df.index, y=metric, color=df.index, text=metric,
                    template="plotly_dark",
                    title="Model evaluation results",
                    labels=labels
                    )
        fig.update_traces(textposition="bottom right")
        fig.show()    
    
    def evaluate_confidence_thresholds(self,  
                                       thresholds: list,
                                       cfg=None,
                                        ) -> pd.DataFrame:
        if not cfg:
            cfg = self.cfg
        threshold_results = {}
        for threshold in thresholds:
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = threshold
            predictor = DefaultPredictor(cfg)
            x = DefaultTrainer.test(cfg, predictor.model, evaluators=[self.evaluator])
            threshold_results[threshold] = x['bbox']
        
        threshold_results_df = pd.DataFrame.from_dict(threshold_results, orient='index')
        threshold_results_df.index.name = 'threshold'
        return threshold_results_df  
        
    def get_best_threshold(self, threshold_df: Union[pd.DataFrame,None]=None,
                            metric="AP50", 
                            thresholds: Union[List,None] = None,
                            ) -> dict:
        if  threshold_df is None and thresholds is None:
            raise ValueError(f"thresholds cannot be {type(thresholds)} when threshold_df is {type(threshold_df)}")
        if not threshold_df:
            if hasattr(self, "threshold_df"):
                threshold_df = self.threshold_df
            else:
                logger.info(f"threshold_df not passed to get_best_threshold hence creating it...")
                threshold_df = self.evaluate_confidence_thresholds(thresholds=thresholds)
        if metric not in threshold_df.columns:
            raise ValueError(f"Metric '{metric}' not found in threshold DataFrame columns.")
        if threshold_df.empty:
            raise ValueError("Threshold DataFrame is empty. No thresholds to evaluate.")
        if threshold_df.shape[0] == 1:
            logger.info("Only one threshold available for evaluation.")
            return threshold_df.index[0], threshold_df.iloc[0][metric]
        threshold_df.sort_values(by=metric, ascending=False, inplace=True)
        best_threshold_value = threshold_df.index[0]
        best_threshold_score = threshold_df[metric].values[0]
        logger.info(f"Best threshold: {best_threshold_value} with score: {best_threshold_score}")
        self.best_threshold_results = {"best_threshold_value": best_threshold_value,
                                        f"best_threshold_{metric}_score": best_threshold_score,
                                        }
        return self.best_threshold_results
        
    def plot_random_samples(self, n=3):
        random.seed(42)
        nrows = int(-(-n/3)) 
        ncols = 3
        samples = random.sample(self.dataset_nm, n)
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(21, 7))
        
        # visualize ground-truths
        for i,s in enumerate(samples):
            ax = axs[i//ncols][i%ncols] if len(axs.shape) == 2 else axs[i]
            img = cv2.imread(s["file_name"])
            v = Visualizer(img[:,:, ::-1], 
                           metadata=self.metadata, 
                           scale=0.5
                           )
            v = v.draw_dataset_dict(s)
            ax.imshow(v.get_image())
            ax.axis("off")
        plt.tight_layout()
        plt.show()
        fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(21, 7))
        
        # visualize prediction results
        for i,s in enumerate(samples):
            ax = axs[i//ncols][i%ncols] if len(axs.shape) == 2 else axs[i]
            img = cv2.imread(s["file_name"])
            outputs = self.predictor(img)
            v = Visualizer(img[:,:, ::-1], metadata=self.metadata, scale=0.5)
            v = v.draw_instance_predictions(outputs["instances"].to("cpu"))
            ax.imshow(v.get_image())
            ax.axis("off")
        plt.tight_layout()
        plt.show()
        
    def __call__(self):
        return self.evaluator