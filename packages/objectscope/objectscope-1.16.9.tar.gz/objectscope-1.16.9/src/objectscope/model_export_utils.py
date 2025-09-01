import torch
import pickle
from detectron2.engine import DefaultPredictor
from detectron2.data import build_detection_test_loader
from detectron2.export import TracingAdapter
from typing import Union
from objectscope import logger
from detectron2.export import scripting_with_instances
from torch import Tensor
from detectron2.structures import Boxes
from typing import Literal
from torch.onnx import TrainingMode

fields = {"proposal_boxes": Boxes,
    "objectness_logits": Tensor,
    "pred_boxes": Boxes,
    "scores": Tensor,
    "pred_classes": Tensor,
    "pred_masks": Tensor,
    "pred_keypoints": Tensor,
    "pred_keypoint_heatmaps": Tensor,
    }


class OnnxModelExporter(object):
    def __init__(self, cfg_path, model_path, 
                 registered_dataset_name
                 ):
        self.model_path = model_path
        self.registered_dataset_name = registered_dataset_name
        with open(cfg_path, "rb") as f:
            self.cfg = pickle.load(f)
        self.cfg.MODEL.WEIGHTS = self.model_path
    
    def get_traceadapted_model(self, 
                               model: Union[DefaultPredictor, None]=None,
                               inputs=None
                               ):
        if not model:
            if not hasattr(self, "model"):
                model = self.get_predictor()
            else:
                model = self.model
        if not inputs:
            if hasattr(self, "inputs"):
                inputs = self.inputs
            else:
                inputs = self.get_sample_model_inputs()
        self.wrapper = TracingAdapter(model.eval(), inputs=inputs)
        return self.wrapper
    
    def get_predictor(self, cfg=None):
        if not cfg:
            cfg = self.cfg
        predictor = DefaultPredictor(cfg)
        self.model = predictor.model
        return self.model
    
    def get_sample_model_inputs(self, cfg=None, 
                                registered_dataset_name=None
                                ):
        if not cfg:
            cfg = self.cfg
        if not registered_dataset_name:
            registered_dataset_name = self.registered_dataset_name
        dataloader = build_detection_test_loader(cfg, registered_dataset_name)
        loaded_data = iter(dataloader)
        self.inputs = next(loaded_data)
        self.inputs = [{"image": input["image"] for input in self.inputs}]
        return self.inputs
    
    def export_to_onnx(self, save_onnx_as, inputs=None,
                        model=None, 
                        torchscript_formart: Literal["trace", "script"] = "trace"
                        ):
        if torchscript_formart not in ["trace", "script"]:
            raise ValueError(f"torchscript_formart has to be either trace or script not {torchscript_formart}")
        if not model:
            if torchscript_formart == "trace":
                if hasattr(self, "wrapper"):
                    model = self.wrapper
                else:
                    model = self.get_traceadapted_model(inputs=inputs)
            else:
                if hasattr(self, "scripted_model"):
                    model = self.scripted_model
                else:
                    model = self.create_script_model()
        
        if not inputs:
            if hasattr(self, "inputs"):
                inputs = self.inputs
            else:
                inputs = self.get_sample_model_inputs()
            
        with open(save_onnx_as, "wb") as f:
            image = inputs[0]["image"]
            torch.onnx.export(model=model,
                            args = (image,),
                            f = f, opset_version=16,
                            export_params=True,
                            input_names=["input"],
                            output_names=["boxes", "classes", "scores"],
                            training=TrainingMode.PRESERVE,
                            do_constant_folding=True,
                            dynamic_axes={
                                "input": {0: "batch_size", 1:"height", 2: "width"},
                                "boxes": {0: "batch_size"},
                                "classes": {0: "batch_size"},
                                "scores": {0: "batch_size"},
                                }
                            )
        logger.info(f"Successfully exported model to onnx at: {save_onnx_as}")
        
    def create_script_model(self, 
                            model: Union[DefaultPredictor, None]=None,
                            fields=fields
                            ):
        if not model:
            if hasattr(self, "model"):
                model = self.model
            if not hasattr(self, "model"):
                model = self.get_predictor()
        self.scripted_model = scripting_with_instances(model.eval(), 
                                                  fields=fields
                                                  )
        return self.scripted_model
    
    def save_model(self, format=Literal["trace", "script"],
                   model: Union[DefaultPredictor, None]=None,
                    inputs=None, save_model_as="model.pt"
                    ):
        if format not in ["trace", "script"]:
            raise ValueError(f"format has to be either trace or script not {format}")
        if format == "trace":
            model = self.get_traceadapted_model(model=model,
                                                        inputs=inputs
                                                        )
            model.eval()
            model = torch.jit.trace(func=model, example_inputs=model.flattened_inputs
                                    )
        else:
            model = self.create_script_model(model=None)
            
        model.save(save_model_as)
